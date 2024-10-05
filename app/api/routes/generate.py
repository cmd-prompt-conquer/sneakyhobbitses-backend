import cv2
import base64
from fastapi import APIRouter, File, Form, HTTPException, UploadFile, Message

from app.api.deps import (
    CurrentUser,
    SessionDep,
)
from moviepy.editor import VideoFileClip
from app.services.openai import OpenAIService


router = APIRouter()


@router.post(
    "",
)
async def generate(
    # session: SessionDep,
    # current_user: CurrentUser,
    ai: OpenAIService,
    file: UploadFile = File(None)):
    """
    Generate content
    """
    if not file:
        raise HTTPException(status_code=400, detail="No resources provided")

    if file.content_type == "video/mp4":
        content = await process_video(f, ai)
    else:
        content = file.read()

    questions = await ai.generate_questions(content)

    return questions


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

def generate_audio(self, video_path: str) -> str:
    audio_path = video_path.replace(".mp4", ".mp3")
    clip = VideoFileClip(video_path)
    clip.audio.write_audiofile(audio_path, bitrate="32k")
    clip.audio.close()
    clip.close()
    return audio_path
