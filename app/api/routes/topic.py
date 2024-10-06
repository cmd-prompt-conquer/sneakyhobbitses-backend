from fastapi import APIRouter
from app.api.deps import (
    SessionDep,
)
from sqlmodel import select
from app.models import Topic, TopicsOut, Question, TopicOut


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
    response_model=TopicOut,
)
async def get_topic(
    session: SessionDep,
    id: int,
    ):
    """
    Get questions for topic
    """

    topic = session.exec(select(Topic).where(Topic.id == id)).one()
    questions = session.exec(select(Question).where(Question.topic_id == id)).all()
    return TopicOut(topic=topic, questions=questions)
