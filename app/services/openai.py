import json
from typing import Annotated

from fastapi import Depends
from openai import AsyncOpenAI


QUESTION_KEYWORD_PROMT_V3 = """
Generate 10 questions based on the provided text.
Each question should have 4 possible answers. Each question should have exactly 1 correct answer.
The output should be in strict minified json format:
{
  "questions":[
    {
      "question": "",
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
        return DUMMY_QUESTIONS
        result = await self._generate(QUESTION_KEYWORD_PROMT_V3, content)
        return result.get("questions", "")

    async def generate_transcription(self, path: str):
        return """Uh, let's talk about the severity of the... No, no, that's for another time. Okay, now let's switch to the other side. Okay, now let's go switch to the other side. Okay, go. Die, God, no, no, no. Bitch. You're awesome. I'm good. I'm evil. Bye. Hi, we are all orcs and... Sorry. Stop. We are building a platform for competitors. Hi, we are all orcs. Uh, we're in a company. No, that's awesome. Uh, we are, uh... Hey, we are all orcs and we are building a platform for competitors. Okay, we are building a platform for competitors. Done. Don't shoot yourself. We are building a learning platform for competitors. Hi, we are all orcs and we are building a learning platform for the company. My name is Nikolai and I've been working as a software engineer for the past 12 years. During that time I've worked on numerous projects and each time I had to join an ongoing one. I had to read dozens of documents and code in order to catch up with the rest of the team. Hey, everyone, I'm Georgi and I've spent the last eight years working for Uber and in that period I went through many different projects from various fields. Many accounting, marketing, compliance, working with multiple teams with our background. Working in a new domain is a tough process, so a little help is always needed. Great. How much do you want to pay? I mean, I'm asking you. I don't know, maybe 25,000. Okay, that's what I need. That's the biggest challenge, Lukas. Yes, okay. I don't want to say just, why am I building it? In multiple projects that I've been, it's always the pain to learn new stuff. Literally, that's what I need. Okay, that's it. Yes. Hi, we are Allport and we are building a platform for learning for companies. I'm Lukai and each time I joined an ongoing project, I've been struggling with learning dozens of documents in order to catch up with the rest of the team. Hey, everyone, I'm Georgi. I've spent the last eight years working for Uber and in that period I went through many different projects with various fields. Many accounting, marketing, compliance, working with multiple teams with other backgrounds. Working with many is a tough process, so a little help is always needed. And I'm Stefan, so you've heard what the why is and what we are building is basically a Duolingo for business or Duolingo for company knowledge. It doesn't matter what the group or the team that learns it. We believe that in the future, cross-team collaboration is going to be way better because people can empathize and understand the knowledge that the others have so that they can build better and higher quality products. That's the question I'm looking for. Is there a question? Yes, there is a question. Yes. Okay, I'm just going to... Sure. Okay. I'm just going to... Okay. I'm just going to... Okay. Okay. Okay. Okay."""
        transcription = await self.client.audio.transcriptions.create(
            model=self.audio_model,
            file=open(path, "rb"),
        )
        # print(transcription)
        return transcription.text

    async def generate_from_video(self, frames: str, transcription: str):
        return """
            The video features a discussion among three individuals—Nikolai, Georgi, and Stefan—who are introducing their project, a learning platform designed for companies. The setting appears casual, with the participants seated in a room, engaging in a conversation about their experiences and the challenges they face in onboarding and learning within new projects.
            ### Key Points from the Video:
            1. **Introduction of the Project**:
            - The group refers to themselves as "Allport" and describes their platform as a "Duolingo for business" aimed at facilitating learning within companies.
            2. **Personal Experiences**:
            - **Nikolai** shares his background as a software engineer with 12 years of experience, highlighting the difficulties he faces when joining ongoing projects, particularly the need to read extensive documentation to catch up.
            - **Georgi** mentions his eight years at Uber, where he worked on various projects across different fields, emphasizing the challenges of adapting to new domains and the necessity for support during this process.
            3. **Purpose of the Platform**:
            - The platform aims to improve cross-team collaboration by enabling employees to understand each other's knowledge and expertise, ultimately leading to better product development.
            4. **Challenges Addressed**:
            - The discussion touches on the common pain points of learning new information quickly and effectively when starting new projects, which the platform seeks to alleviate.
            5. **Engagement and Interaction**:
            - The conversation includes light-hearted moments and informal exchanges, indicating a friendly rapport among the participants.
            6. **Future Vision**:
            - Stefan articulates a vision for enhanced collaboration in the future, driven by improved understanding among team members.
            Overall, the video serves as an introduction to the team and their innovative approach to corporate learning, highlighting their backgrounds, the challenges they aim to solve, and their vision for the future of workplace collaboration.
            """
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
        # print(content)
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

    async def _generate(self, promt: str, content: str):
        completion = await self.client.chat.completions.create(
            model=self.text_model,
            messages=[
                {"role": "system", "content": promt},
                {"role": "user", "content": content},
            ],
            response_format={"type": "json_object"},
            temperature=0,
            max_tokens=4096,
        )
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

DUMMY_QUESTIONS = [
  {
    "question": "What is the name of the learning platform introduced by the group?",
    "correctAnswer": "Allport",
    "answers": [
      "Allport",
      "Duolingo",
      "UberLearn",
      "TeamSync"
    ]
  },
  {
    "question": "How does Nikolai describe his professional background?",
    "correctAnswer": "Software engineer with 12 years of experience",
    "answers": [
      "Project manager with 10 years of experience",
      "Software engineer with 12 years of experience",
      "Data analyst with 8 years of experience",
      "Designer with 5 years of experience"
    ]
  },
  {
    "question": "What company did Georgi work for before joining the project?",
    "correctAnswer": "Uber",
    "answers": [
      "Google",
      "Uber",
      "Microsoft",
      "Facebook"
    ]
  },
  {
    "question": "What is the primary aim of the Allport platform?",
    "correctAnswer": "Facilitating learning within companies",
    "answers": [
      "Facilitating learning within companies",
      "Reducing project costs",
      "Increasing employee turnover",
      "Enhancing marketing strategies"
    ]
  },
  {
    "question": "What common challenge does the platform seek to address?",
    "correctAnswer": "Learning new information quickly and effectively",
    "answers": [
      "Managing team conflicts",
      "Learning new information quickly and effectively",
      "Reducing project deadlines",
      "Improving customer service"
    ]
  },
  {
    "question": "What type of atmosphere is depicted in the video?",
    "correctAnswer": "Casual and friendly",
    "answers": [
      "Formal and serious",
      "Casual and friendly",
      "Competitive and tense",
      "Disorganized and chaotic"
    ]
  },
  {
    "question": "What does Stefan envision for the future of workplace collaboration?",
    "correctAnswer": "Enhanced collaboration driven by understanding",
    "answers": [
      "Increased competition among teams",
      "Enhanced collaboration driven by understanding",
      "More rigid project structures",
      "Less communication between teams"
    ]
  },
  {
    "question": "What is the analogy used to describe the Allport platform?",
    "correctAnswer": "Duolingo for business",
    "answers": [
      "LinkedIn for professionals",
      "Duolingo for business",
      "Facebook for teams",
      "Twitter for companies"
    ]
  },
  {
    "question": "How many years of experience does Georgi have?",
    "correctAnswer": "Eight years",
    "answers": [
      "Five years",
      "Eight years",
      "Ten years",
      "Twelve years"
    ]
  },
  {
    "question": "What is one of the key points discussed in the video?",
    "correctAnswer": "Cross-team collaboration",
    "answers": [
      "Individual performance metrics",
      "Cross-team collaboration",
      "Project budgeting",
      "Employee retention strategies"
    ]
  }
]