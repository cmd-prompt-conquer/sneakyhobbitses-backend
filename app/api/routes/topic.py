from fastapi import APIRouter
from app.api.deps import (
    SessionDep,
)
from sqlmodel import select
from app.models import Topic, TopicsOut, Question, QuestionsOut


router = APIRouter()


@router.get(
    "",
    response_model=TopicsOut,
)
async def all_topics(
    session: SessionDep,
    ):
    """
    Get all topics
    """

    topics = session.exec(select(Topic)).all()
    result = TopicsOut(topics=topics, count=len(topics))
    return result


@router.get(
    "/{id}",
    response_model=QuestionsOut,
)
async def get_topic(
    session: SessionDep,
    id: int,
    ):
    """
    Get questions for topic
    """

    questions = session.exec(select(Question).where(Question.topic_id == id)).all()
    return QuestionsOut(questions=questions, count=len(questions))
