from fastapi import APIRouter
from sqlalchemy.sql import select

from app import crud
from app.api.deps import SessionDep
from app.core.exceptions import NotFoundError
from app.models import (
    Contribution,
    ContributionCreate,
    ContributionShort,
    ContributionUpdate,
    ContributionWithAttributesShortPublic,
    ContributorShort,
)

router = APIRouter()


@router.post("/contributions", response_model=ContributionWithAttributesShortPublic)
def create_contribution(session: SessionDep, contribution: ContributionCreate):
    db_contribution, contributors = crud.create_contribution(
        session=session, contribution=contribution
    )
    return ContributionWithAttributesShortPublic.from_contribution(
        session, db_contribution, contributors
    )


@router.get(
    "/contributions/{contribution_id}",
    response_model=ContributionWithAttributesShortPublic,
)
def read_contribution(session: SessionDep, contribution_id: str):
    contribution = crud.select_contribution_by_id(
        session=session, contribution_id=contribution_id
    )
    if contribution is None:
        raise NotFoundError(what="Contribution")
    return ContributionWithAttributesShortPublic.from_contribution(
        session, contribution
    )


@router.put(
    "/contributions/{contribution_id}",
    response_model=ContributionWithAttributesShortPublic,
)
def update_contribution(
    session: SessionDep,
    contribution_id: str,
    contribution_in: ContributionUpdate,
):
    db_contribution = session.get(Contribution, contribution_id)
    if not db_contribution:
        raise NotFoundError(what="Contribution")
    db_contribution, contributors = crud.update_contribution(
        session=session, contribution=db_contribution, contribution_in=contribution_in
    )
    return ContributionWithAttributesShortPublic.from_contribution(
        session, db_contribution, contributors
    )


@router.get(
    "/contributions",
    response_model=list[ContributionWithAttributesShortPublic],
)
def read_contributions(session: SessionDep, skip: int = 0, limit: int = 100):
    statement = select(Contribution).offset(skip).limit(limit)
    contributions = session.exec(statement).all()
    return [
        ContributionWithAttributesShortPublic.from_contribution(
            session, contribution[0]
        )
        for contribution in contributions
    ]


@router.get(
    "/contributions/{contribution_id}/children",
    response_model=list[ContributionShort],
)
def read_contribution_children(session: SessionDep, contribution_id: str):
    contribution = crud.select_contribution_by_id(
        session=session, contribution_id=contribution_id
    )
    if contribution is None:
        raise NotFoundError(what="Contribution")
    return [
        ContributionShort.from_contribution(session, dependent)
        for dependent in contribution.dependents
    ]


@router.get(
    "/contributions/{contribution_id}/contributors",
    response_model=list[ContributorShort],
)
def read_contribution_contributors(session: SessionDep, contribution_id: str):
    contribution = crud.select_contribution_by_id(
        session=session, contribution_id=contribution_id
    )
    if contribution is None:
        raise NotFoundError(what="Contribution")
    contributors = crud.select_contribution_contributors(
        session=session, contribution_id=contribution_id
    )
    return contributors
