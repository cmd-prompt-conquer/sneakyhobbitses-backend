import cv2
import os
import base64
import tempfile
from fastapi import APIRouter, File, Form, UploadFile
from app.api.deps import (
    SessionDep,
)
from moviepy.editor import VideoFileClip
from app.services.openai import OpenAIService
from app.models import GenOptions, Topic, Question


router = APIRouter()


@router.post(
    "",
)
async def generate(
    session: SessionDep,
    ai: OpenAIService,
    file: UploadFile = File(...),
    options: GenOptions = Form(GenOptions),
    ):
    """
    Generate content
    """

    if file.content_type == "video/mp4":
        f = tempfile.NamedTemporaryFile(
            suffix=f"_{file.filename.lower()}", delete=False
        )
        f.write(file.file.read())
        file.file.close()
        f.close()
        content = await process_video(f.name, ai)
        os.unlink(f.name)
    else:
        content = file.file.read()

    questions = await ai.generate_questions(content)
    questions = []
    qs = []
    for q in questions:
        qs.append(Question(
            question=q.get("question"),
            answer=q.get("correctAnswer"),
            options=q.get("answers"),
        ))

    topic = Topic(
        name=options.name,
        description=options.description,
        reward=options.reward,
        email=options.email,
        questions=qs,
    )
    session.add(topic)
    session.commit()
    return topic.model_dump_json()


async def process_video(file, ai: OpenAIService):
    frames = generate_frames(file)
    audio_path = generate_audio(file)
    transcription = await ai.generate_transcription(audio_path)
    result = await ai.generate_from_video(frames, transcription)
    return result

def generate_frames(path: str):
    frames = []
    video = cv2.VideoCapture(path)
    total_frames = int(video.get(cv2.CAP_PROP_FRAME_COUNT))
    fps = video.get(cv2.CAP_PROP_FPS)
    frames_to_skip = int(fps * 16)
    curr_frame = 0

    # Loop through the video and extract frames at specified sampling rate
    while curr_frame < total_frames - 1:
        video.set(cv2.CAP_PROP_POS_FRAMES, curr_frame)
        success, frame = video.read()
        if not success:
            break
        _, buffer = cv2.imencode(".jpg", frame)
        frames.append(base64.b64encode(buffer).decode("utf-8"))
        curr_frame += frames_to_skip
    video.release()
    return frames

def generate_audio(video_path: str) -> str:
    audio_path = video_path.replace(".mp4", ".mp3")
    clip = VideoFileClip(video_path)
    clip.audio.write_audiofile(audio_path, bitrate="32k")
    clip.audio.close()
    clip.close()
    return audio_path

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