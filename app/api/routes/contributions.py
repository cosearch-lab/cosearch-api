from urllib.parse import urljoin

from discord import Colour, Embed
from fastapi import APIRouter
from sqlalchemy.sql import select
from structlog import get_logger

from app import crud
from app.api.deps import SessionDep, get_discord_webhook
from app.core.config import settings
from app.core.exceptions import NotFoundError
from app.models import (
    Contribution,
    ContributionCreate,
    ContributionShort,
    ContributionUpdate,
    ContributionWithAttributesShortPublic,
    ContributorShort,
)

_LOGGER = get_logger()

router = APIRouter()


@router.post("/contributions", response_model=ContributionWithAttributesShortPublic)
def create_contribution(session: SessionDep, contribution: ContributionCreate):
    db_contribution, contributors = crud.create_contribution(
        session=session, contribution=contribution
    )

    discord_webhook = get_discord_webhook()
    if discord_webhook is not None:
        _LOGGER.info("Sending contribution created message to Discord")
        embed = Embed(
            title="Contribution created!",
            description=db_contribution.title,
            color=Colour.blue(),
        )
        embed.add_field(
            name="Link",
            value=urljoin(
                str(settings.COSEARCH_URL), f"contribution/{db_contribution.id}"
            ),
        )
        discord_webhook.send(embed=embed)
        _LOGGER.info("Sent contribution created message to Discord")
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
