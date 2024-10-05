import json
from typing import Annotated

from fastapi import Depends
from openai import AsyncOpenAI


QUESTION_KEYWORD_PROMT_V3 = """
Generate 10 questions based on the provided text.
The question should have a topic. There should be exactly 2 questions for each topic.
Each question should have 4 possible answers. Each question should have exactly 1 correct answer.
The output should be in strict minified json format:
{
  "questions":[
    {
      "question": "",
      "topic": "",
      "correctAnswer": "",
      "answers": []
    }
  ]
}
"""

VIDEO_SUMMARY_PROMT = """
Create a summary of the provided video and its transcript.
Respond with a text that is less than 5000 characters, containing as much information about the video and its transcript as possible.
"""

class OpenAIService:
    text_model: str
    image_model: str
    video_model: str
    audio_model: str

    def __init__(self):
        self.client = AsyncOpenAI()
        self.text_model = "gpt-4o-mini"
        self.video_model = "gpt-4o-mini"
        self.audio_model = "whisper-1"
        self.image_model = "dall-e-3"

    async def generate_questions(self, content: str):
        result = await self._generate(QUESTION_KEYWORD_PROMT_V3, content)
        return result.get("questions", "")

    async def generate_transcription(self, path: str):
        transcription = await self.client.audio.transcriptions.create(
            model=self.audio_model,
            file=open(path, "rb"),
        )
        return transcription.text

    async def generate_from_video(self, frames: str, transcription: str):
        content = [
            {
                "type": "text",
                "text": "These are the frames from the video.",
            },
            *[
                {
                    "type": "image_url",
                    "image_url": {
                        "url": f"data:image/jpg;base64,{x}",
                        "detail": "low",
                    },
                }
                for x in frames
            ],
            {
                "type": "text",
                "text": f"The audio transcription is: {transcription}",
            },
        ]
        content = await self._generate_from_video(VIDEO_SUMMARY_PROMT, content)
        return content

    async def _generate_from_video(self, promt: str, content: list[dict]):
        response = await self.client.chat.completions.create(
            model=self.video_model,
            messages=[
                {
                    "role": "system",
                    "content": promt,
                },
                {"role": "user", "content": content},
            ],
            temperature=0,
        )
        return response.choices[0].message.content

    async def _generate(self, promt: str, content: str, response_format="json_object"):
        completion = await self.client.chat.completions.create(
            model=self.text_model,
            messages=[
                {"role": "system", "content": promt},
                {"role": "user", "content": content},
            ],
            response_format="json_object",
            temperature=0,
            max_tokens=4096,
        )
        self.real_tokens += completion.usage.total_tokens
        if response_format == "text":
            return completion.choices[0].message.content
        return json.loads(completion.choices[0].message.content)

    async def text_to_speach(self, content: str, output: str):
        content = content[:4096]
        response = await self.client.audio.speech.create(
            model="tts-1",
            voice="alloy",
            response_format="mp3",
            input=content,
        )
        response.write_to_file(output)
        return output


OpenAIService = Annotated[OpenAIService, Depends(OpenAIService)]
