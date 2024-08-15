from typing import Optional

from sqlmodel import Session, select
from structlog import get_logger

from app.core.exceptions import ConditionError
from app.models import (
    Contribution,
    ContributionContributorLink,
    Contributor,
    ContributorUpsert,
    Review,
)

_LOGGER = get_logger()


def create_contributor(
    session: Session, contributor_in: ContributorUpsert
) -> Contributor:
    _LOGGER.info("Creating new contributor", contributor=contributor_in)
    db_contributor = Contributor.model_validate(contributor_in)
    session.add(db_contributor)
    session.commit()
    session.refresh(db_contributor)
    _LOGGER.info("Contributor created", contributor_id=db_contributor.id)
    return db_contributor


def update_contributor(
    session: Session, contributor: Contributor, contributor_in: ContributorUpsert
) -> Contributor:
    update_dict = contributor_in.model_dump()
    contributor.sqlmodel_update(update_dict)
    session.add(contributor)
    session.commit()
    session.refresh(contributor)
    _LOGGER.info("Contributor updated", contributor_id=contributor.id)
    return contributor


def select_contributor_by_id(
    session: Session, contributor_id: int
) -> Contributor | None:
    statement = select(Contributor).where(Contributor.id == contributor_id)
    contributor = session.exec(statement).first()
    return contributor


def select_contributor_by_local_handle(
    session: Session, local_handle: str
) -> Contributor | None:
    statement = select(Contributor).where(Contributor.local_handle == local_handle)
    contributor = session.exec(statement).first()
    return contributor


def integrity_check_contributor(
    session: Session,
    contributor_in: ContributorUpsert,
    contributor_update_id: Optional[int] = None,
) -> bool:
    # check if local handle is used
    contributor = select_contributor_by_local_handle(
        session, contributor_in.local_handle
    )
    if (contributor is not None and contributor_update_id is None) or (
        contributor is not None and contributor.id != contributor_update_id
    ):
        _LOGGER.info(
            "Local handle already exists",
            local_handle=contributor_in.local_handle,
            contributor_id=contributor.id,
        )
        raise ConditionError(
            condition="Local handle already exists",
        )
    # check if local handle is used as display name
    statement = select(Contributor).where(
        Contributor.display_name == contributor_in.local_handle
    )
    contributor = session.exec(statement).first()
    if (contributor is not None and contributor_update_id is None) or (
        contributor is not None and contributor.id != contributor_update_id
    ):
        _LOGGER.info(
            "Local handle already used as display name",
            local_handle=contributor_in.local_handle,
            contributor_id=contributor.id,
        )
        raise ConditionError(
            condition="Local handle already used as display name",
        )

    if contributor_in.display_name is not None:
        # check if display name is used
        statement = select(Contributor).where(
            Contributor.display_name == contributor_in.display_name
        )
        contributor = session.exec(statement).first()
        if (contributor is not None and contributor_update_id is None) or (
            contributor is not None and contributor.id != contributor_update_id
        ):
            _LOGGER.info(
                "Display name already exists",
                display_name=contributor_in.display_name,
                contributor_id=contributor.id,
            )
            raise ConditionError(
                condition="Display name already exists",
            )
        # check if display name is used as local handle
        statement = select(Contributor).where(
            Contributor.local_handle == contributor_in.display_name
        )
        contributor = session.exec(statement).first()
        if (contributor is not None and contributor_update_id is None) or (
            contributor is not None and contributor.id != contributor_update_id
        ):
            _LOGGER.info(
                "Display name already used as local handle",
                display_name=contributor_in.display_name,
                contributor_id=contributor.id,
            )
            raise ConditionError(
                condition="Display name already used as local handle",
            )
    return True


def select_contributor_reviewed_contributions(
    session: Session, contributor_id: int
) -> list[Contribution]:
    statement = select(Review).where(
        Review.reviewers.any(Contributor.id == contributor_id)
    )
    reviews = session.exec(statement).all()
    contribution_ids = [review.contribution_id for review in reviews]
    statement = select(Contribution).where(Contribution.id.in_(contribution_ids))
    contributions = session.exec(statement).all()
    return contributions


def select_contributor_contributions(
    session: Session, contributor_id: int
) -> list[Contribution]:
    statement = select(ContributionContributorLink).where(
        ContributionContributorLink.contributor_id == contributor_id
    )
    links = session.exec(statement).all()
    return [link.contribution for link in links]
