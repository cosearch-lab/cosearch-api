from fastapi import APIRouter
from sqlalchemy import select

from app import crud
from app.api.deps import SessionDep
from app.core.exceptions import NotFoundError
from app.models import (
    Contributor,
    ContributorReviewedContributions,
    ContributorUpsert,
    ContributorViewPublic,
    ContributorWithAttributesShortPublic,
)

router = APIRouter()


@router.post("/contributors", response_model=ContributorWithAttributesShortPublic)
def create_contributor(session: SessionDep, contributor_in: ContributorUpsert):
    if crud.integrity_check_contributor(session=session, contributor_in=contributor_in):
        return crud.create_contributor(session=session, contributor_in=contributor_in)


@router.get(
    "/contributors/{contributor_id}",
    response_model=ContributorViewPublic,
)
def read_contributor(session: SessionDep, contributor_id: int):
    db_contributor = crud.select_contributor_by_id(
        session=session, contributor_id=contributor_id
    )
    if db_contributor is None:
        raise NotFoundError(what="Contributor")
    assert db_contributor.id is not None
    contributor_public = ContributorViewPublic.model_validate(db_contributor)
    contributor_public.reviewed_contributions = (
        crud.select_contributor_reviewed_contributions(
            session=session, contributor_id=db_contributor.id
        )
    )
    return contributor_public


@router.get(
    "/contributors/local_handle/{local_handle}",
    response_model=ContributorViewPublic,
)
def read_contributor_by_local_handle(session: SessionDep, local_handle: str):
    db_contributor = crud.select_contributor_by_local_handle(
        session=session, local_handle=local_handle
    )
    if db_contributor is None:
        raise NotFoundError(what="Contributor")
    assert db_contributor.id is not None
    contributor_public = ContributorViewPublic.model_validate(db_contributor)
    contributor_public.reviewed_contributions = (
        crud.select_contributor_reviewed_contributions(
            session=session, contributor_id=db_contributor.id
        )
    )
    return contributor_public


@router.put(
    "/contributors/{contributor_id}",
    response_model=ContributorWithAttributesShortPublic,
)
def update_contributor(
    session: SessionDep,
    contributor_id: int,
    contributor_in: ContributorUpsert,
):
    db_contributor = crud.select_contributor_by_id(
        session, contributor_id=contributor_id
    )
    if db_contributor is None:
        raise NotFoundError(what="Contributor")
    if crud.integrity_check_contributor(
        session=session,
        contributor_in=contributor_in,
        contributor_update_id=contributor_id,
    ):
        return crud.update_contributor(
            session=session, contributor=db_contributor, contributor_in=contributor_in
        )


@router.get("/contributors", response_model=list[ContributorWithAttributesShortPublic])
def read_contributors(session: SessionDep, skip: int = 0, limit: int = 100):
    statement = select(Contributor).offset(skip).limit(limit)
    contributors = session.exec(statement).all()
    return [contributor[0] for contributor in contributors]


@router.get(
    "/contributors/{contributor_id}/reviewed_contributions",
    response_model=ContributorReviewedContributions,
)
def read_contributor_reviewed_contributions(session: SessionDep, contributor_id: int):
    db_contributor = crud.select_contributor_by_id(
        session=session, contributor_id=contributor_id
    )
    if db_contributor is None:
        raise NotFoundError(what="Contributor")
    reviewed_contributions = crud.select_contributor_reviewed_contributions(
        session=session, contributor_id=contributor_id
    )
    return ContributorReviewedContributions(
        reviewed_contributions=reviewed_contributions
    )
