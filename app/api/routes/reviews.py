from fastapi import APIRouter
from sqlalchemy import select

from app import crud
from app.api.deps import SessionDep
from app.core.exceptions import NotFoundError
from app.models import Message, Review, ReviewCreate, ReviewPublic, ReviewUpdate

router = APIRouter()


@router.post("/reviews", response_model=ReviewPublic)
def create_review(session: SessionDep, review: ReviewCreate):
    return crud.create_review(session=session, review_in=review)


@router.get("/reviews/{review_id}", response_model=ReviewPublic)
def read_review(session: SessionDep, review_id: int):
    review = crud.select_review_by_id(session=session, review_id=review_id)
    if review is None:
        raise NotFoundError(what=f"Review ID {review_id}")
    return review


@router.put("/reviews/{review_id}", response_model=ReviewPublic)
def update_review(session: SessionDep, review_id: int, review_in: ReviewUpdate):
    db_review = session.get(Review, review_id)
    if not db_review:
        raise NotFoundError(what="Review")
    db_review = crud.update_review(
        session=session, review=db_review, review_in=review_in
    )
    return db_review


@router.get("/reviews", response_model=list[ReviewPublic])
def read_reviews(session: SessionDep, skip: int = 0, limit: int = 100):
    statement = select(Review).offset(skip).limit(limit)
    reviews = session.exec(statement).all()
    return [review[0] for review in reviews]


@router.delete("/reviews/{review_id}", response_model=Message)
def delete_review(session: SessionDep, review_id: int):
    review = crud.select_review_by_id(session, review_id)
    if not review:
        raise NotFoundError(what="Review")
    session.delete(review)
    session.commit()
    return Message(message="Review deleted successfully")
