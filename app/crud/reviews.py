from sqlmodel import Session, select
from structlog import get_logger

from app.core.exceptions import NotFoundError
from app.crud.contributions import select_contribution_by_id
from app.crud.contributors import select_contributor_by_id
from app.crud.utils import update_links
from app.models import Review, ReviewCreate

_LOGGER = get_logger()


def select_review_by_id(session: Session, review_id: int) -> Review | None:
    statement = select(Review).where(Review.id == review_id)
    review = session.exec(statement).first()
    return review


def create_review(session: Session, review_in: ReviewCreate) -> Review:
    _LOGGER.info("Creating new review")
    contribution = select_contribution_by_id(session, review_in.contribution_id)
    if contribution is None:
        raise NotFoundError(what=f"Contribution ID {review_in.contribution_id}")
    reviewers = []
    for reviewer_id in review_in.reviewers:
        reviewer = select_contributor_by_id(session, reviewer_id)
        if reviewer is None:
            raise NotFoundError(what=f"Reviewer ID {reviewer_id}")
        reviewers.append(reviewer)

    db_review = Review(
        contribution_id=contribution.id,
        reviewers=reviewers,
        link=review_in.link,
        notes=review_in.notes,
    )
    session.add(db_review)
    session.commit()
    session.refresh(db_review)
    _LOGGER.info("Review created", review_id=db_review.id)
    return db_review


def update_review(session: Session, review: Review, review_in: ReviewCreate):
    review_link = (
        "reviewers",
        review.reviewers,
        review_in.reviewers,
        select_contributor_by_id,
    )
    update_links(session, review, "review", *review_link)

    update_dict = review_in.model_dump()
    review.sqlmodel_update(update_dict)
    session.commit()
    session.refresh(review)
    return review
