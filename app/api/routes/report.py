import json
from fastapi import APIRouter, Form
from app.api.deps import (
    SessionDep,
)
from sqlmodel import select
from app.models import Report, Leaderboard, EmailScore, Answers


router = APIRouter()


@router.post(
    "",
    response_model=Report,
)
async def post_result(
    session: SessionDep,
    email: str = Form(...),
    score: int = Form(...),
    topic_id: int = Form(...),
    answers: list[str] = Form(...)
    ):

    answers = Answers(
        email=email,
        topic_id=topic_id,
        answers=answers,
    )
    session.add(answers)
    session.commit()
    report = Report(
        email=email,
        score=score,
        topic_id=topic_id,
    )
    session.add(report)
    session.commit()
    session.refresh(report)
    return report

@router.get(
    "",
    response_model=Leaderboard,
)
async def get_leaderboard(
    session: SessionDep,
    ):

    reports = session.exec(select(Report)).all()
    email_scores = {}
    for r in reports:
        if email_scores.get(r.email):
            email_scores[r.email] += r.score
        else:
            email_scores[r.email] = r.score

    data = []
    for email, score in email_scores.items():
        data.append(EmailScore(email=email, score=score))
    
    return Leaderboard(data=data, count=len(data))


@router.get(
    "/{id}",
    response_model=Leaderboard,
)
async def get_leaderboard_for_topic(
    session: SessionDep,
    id: int,
    ):

    reports = session.exec(select(Report).where(Report.topic_id == id)).all()
    email_scores = {}
    for r in reports:
        if email_scores.get(r.email):
            email_scores[r.email] += r.score
        else:
            email_scores[r.email] = r.score

    data = []
    for email, score in email_scores.items():
        data.append(EmailScore(email=email, score=score))
    
    return Leaderboard(data=data, count=len(data))
