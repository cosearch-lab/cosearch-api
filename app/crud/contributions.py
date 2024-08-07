import random
import string

from sqlmodel import Session, select
from structlog import get_logger

from app.core.exceptions import NotFoundError
from app.crud.contributors import select_contributor_by_id
from app.crud.tags import select_tag_by_id
from app.crud.utils import update_links
from app.models import Contribution, ContributionCreate, ContributionUpdate

_LOGGER = get_logger()


def create_contribution(
    session: Session, contribution: ContributionCreate
) -> Contribution:
    _LOGGER.info("Creating new contribution")
    contributors = []
    for contributor_id in contribution.contributors:
        contributor = select_contributor_by_id(session, contributor_id)
        if contributor is None:
            raise NotFoundError(what=f"Contributor ID {contributor_id}")
        # contributor = Contributor(id=contributor_id)
        contributors.append(contributor)

    tags = []
    for tag_id in contribution.tags:
        tag = select_tag_by_id(session, tag_id)
        if tag is None:
            raise NotFoundError(what=f"Tag ID {tag_id}")
        tags.append(tag)

    dependencies = []
    for dependency_id in contribution.dependencies:
        dependency = select_contribution_by_id(session, dependency_id)
        if dependency is None:
            raise NotFoundError(what=f"Dependency ID {dependency_id}")
        dependencies.append(dependency)

    # generate 8 length string for contribution ID
    contribution_id = "".join(
        random.choices(string.ascii_lowercase + string.digits, k=8)
    )

    # as its a many to many relationship, we create the object differently
    # https://sqlmodel.tiangolo.com/tutorial/many-to-many/create-data/
    contribution_db = Contribution(
        id=contribution_id,
        title=contribution.title,
        short_title=contribution.short_title,
        date=contribution.date,
        discord_chat_link=str(contribution.discord_chat_link)
        if contribution.discord_chat_link is not None
        else None,
        github_link=str(contribution.github_link)
        if contribution.github_link is not None
        else None,
        forum_link=str(contribution.forum_link)
        if contribution.forum_link is not None
        else None,
        wiki_link=str(contribution.wiki_link)
        if contribution.wiki_link is not None
        else None,
        links=[link.model_dump(mode="json") for link in contribution.links],
        description=contribution.description,
        contributors=contributors,
        tags=tags,
        dependencies=dependencies,
    )
    session.add(contribution_db)
    session.commit()
    session.refresh(contribution_db)
    _LOGGER.info("Contribution created", contribution_id=contribution_db.id)
    return contribution_db


def select_contribution_by_id(
    session: Session, contribution_id: str
) -> Contribution | None:
    statement = select(Contribution).where(Contribution.id == contribution_id)
    contribution = session.exec(statement).first()
    return contribution


def update_contribution(
    session: Session, contribution: Contribution, contribution_in: ContributionUpdate
) -> Contribution:

    contribution_links = [
        (
            "contributors",
            contribution.contributors,
            contribution_in.contributors,
            select_contributor_by_id,
        ),
        ("tags", contribution.tags, contribution_in.tags, select_tag_by_id),
        (
            "dependencies",
            contribution.dependencies,
            contribution_in.dependencies,
            select_contribution_by_id,
        ),
    ]

    for link in contribution_links:
        update_links(session, contribution, "contribution", *link)

    update_dict = contribution_in.model_dump(
        exclude={"discord_chat_link", "github_link", "forum_link", "wiki_link", "links"}
    )
    update_dict.update(
        {
            k: str(v)
            for k, v in contribution_in.model_dump(
                include={"discord_chat_link", "github_link", "forum_link", "wiki_link"}
            ).items()
            if v is not None
        }
    )
    update_dict["links"] = [
        link.model_dump(mode="json") for link in contribution_in.links
    ]
    contribution.sqlmodel_update(update_dict)
    session.commit()
    session.refresh(contribution)
    return contribution
