import json
from fastapi import APIRouter
from app.api.deps import (
    SessionDep,
)
from sqlmodel import select
from app.models import Topic, TopicsOut, Question, TopicOut, Answers


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

@router.get(
    "/stats/{id}",
)
async def get_stats(
    session: SessionDep,
    id: int,
    ):

    answer = session.exec(select(Answers).where(Answers.topic_id == id)).all()
    answers = answer.answers
    questions = session.exec(select(Question).where(Question.topic_id == id)).all()
    stats = {}
    for i, q in enumerate(questions):
        qt = q.question
        if not stats.get(qt, None):
            stats[qt] = [0, 0]

        if answers[i] == q.answer:
            stats[qt][0] += 1
        else:
            stats[qt][1] += 1

    qtop = sorted(stats.items(), key=lambda x: x[1][0])[0][0]
    qbottom = sorted(stats.items(), key=lambda x: x[1][1])[0][0]

    return json.dumps({
        "top": qtop,
        "bottom": qbottom,
    })
