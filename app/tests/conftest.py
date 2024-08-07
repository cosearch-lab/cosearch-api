import os
from collections.abc import Generator
from datetime import datetime

import pytest
from fastapi.testclient import TestClient
from sqlmodel import Session, delete
from structlog import get_logger

os.environ["POSTGRES_DB"] = "cosearch-db-test"

from app.core.db import engine, init_db  # noqa E402
from app.main import app  # noqa E402
from app.models import (  # noqa E402
    Contribution,
    ContributionContributorLink,
    ContributionDependencyLink,
    ContributionLinks,
    ContributionTagLink,
    Contributor,
    ContributorReviewLink,
    Review,
    Tag,
)

_LOGGER = get_logger()


@pytest.fixture(scope="function", autouse=True)
def db() -> Generator[Session, None, None]:
    with Session(engine) as session:
        init_db(session)
        yield session
        _LOGGER.info("Cleaning up database")
        # links must be deleted first
        statement = delete(ContributionContributorLink)
        session.execute(statement)
        statement = delete(ContributionTagLink)
        session.execute(statement)
        statement = delete(ContributorReviewLink)
        session.execute(statement)
        statement = delete(ContributionDependencyLink)
        session.execute(statement)
        statement = delete(Contributor)
        session.execute(statement)
        # delete reviews before contributions to avoid foreign key constraint violation
        statement = delete(Review)
        session.execute(statement)
        statement = delete(Contribution)
        session.execute(statement)
        statement = delete(Tag)
        session.execute(statement)
        session.commit()


@pytest.fixture(scope="module")
def client() -> Generator[TestClient, None, None]:
    with TestClient(app) as c:
        yield c


@pytest.fixture(scope="function")
def add_contributors(db: Session) -> tuple[Contributor, Contributor]:
    from app import crud
    from app.models import ContributorUpsert

    contributor = ContributorUpsert(
        local_handle="test_contributor",
        display_name="Test Contributor",
        discord_handle="test_contributor#1234",
    )
    db_contributor_1 = crud.create_contributor(session=db, contributor_in=contributor)

    contributor = ContributorUpsert(
        local_handle="test_contributor2",
        display_name="Test Contributor 2",
        discord_handle="test_contributor2#1234",
    )
    db_contributor_2 = crud.create_contributor(session=db, contributor_in=contributor)

    return db_contributor_1, db_contributor_2


@pytest.fixture(scope="function")
def add_contribution(
    db: Session, add_contributors
) -> tuple[Contribution, Contributor, Contributor]:
    from app import crud
    from app.models import ContributionCreate

    contributor_1, contributor_2 = add_contributors

    contribution = ContributionCreate(
        title="Test Contribution",
        short_title="Test Contrib",
        date=datetime(2021, 1, 1, 0, 0, 0),
        links=[ContributionLinks(description="Test link", url="https://example.com")],
        description="Test description",
        contributors=[contributor_1.id],
        tags=[],
    )
    db_contribution, _ = crud.create_contribution(session=db, contribution=contribution)

    return db_contribution, contributor_1, contributor_2


@pytest.fixture(scope="function")
def add_contribution_with_dependency(
    db: Session, add_contribution
) -> tuple[Contribution, Contribution, Contributor, Contributor]:
    from app import crud
    from app.models import ContributionCreate

    contribution_1, contributor_1, contributor_2 = add_contribution

    contribution_2 = ContributionCreate(
        title="Test Contribution 2",
        short_title="Test Contrib 2",
        date=datetime(2021, 1, 1, 0, 0, 0),
        links=[
            ContributionLinks(description="Test link 2", url="https://example2.com")
        ],
        description="Test description 2",
        contributors=[contributor_1.id],
        tags=[],
        dependencies=[contribution_1.id],
    )
    contribution_2, _ = crud.create_contribution(
        session=db, contribution=contribution_2
    )

    return contribution_1, contribution_2, contributor_1, contributor_2


@pytest.fixture(scope="function")
def add_review(
    db: Session, add_contribution_with_dependency
) -> tuple[Review, Contribution, Contribution, Contributor, Contributor]:
    from app import crud
    from app.models import ReviewCreate

    (
        contribution_1,
        contribution_2,
        contributor_1,
        contributor_2,
    ) = add_contribution_with_dependency

    review = ReviewCreate(
        contribution_id=contribution_2.id,
        reviewers=[contributor_1.id],
        link="https://example.com",
        notes="Test review notes",
    )
    db_review = crud.create_review(session=db, review_in=review)

    return db_review, contribution_1, contribution_2, contributor_1, contributor_2
