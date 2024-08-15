from datetime import datetime
from typing import Dict, Optional

from pydantic import HttpUrl, field_validator
from sqlalchemy.sql import func
from sqlalchemy.sql.sqltypes import JSON, DateTime
from sqlmodel import Column, Field, Relationship, Session, SQLModel

from app import crud


# Generic message
class Message(SQLModel):
    message: str


class ContributionContributorLink(SQLModel, table=True):
    # __table_args__ = (
    #     UniqueConstraint(
    #         "contribution_id",
    #         "contributor_order",
    #         name="contributor_order_constraint"
    #     ),
    # )

    contribution_id: str | None = Field(
        default=None, foreign_key="contribution.id", primary_key=True
    )
    contributor_id: int | None = Field(
        default=None, foreign_key="contributor.id", primary_key=True
    )
    contributor_order: int

    contribution: "Contribution" = Relationship(back_populates="contributors")
    contributor: "Contributor" = Relationship(back_populates="contributions")


class ContributionTagLink(SQLModel, table=True):
    contribution_id: str | None = Field(
        default=None, foreign_key="contribution.id", primary_key=True
    )
    tag_id: int | None = Field(default=None, foreign_key="tag.id", primary_key=True)


class ContributorReviewLink(SQLModel, table=True):
    contributor_id: int | None = Field(
        default=None, foreign_key="contributor.id", primary_key=True
    )
    review_id: int | None = Field(
        default=None, foreign_key="review.id", primary_key=True
    )


class ContributionDependencyLink(SQLModel, table=True):
    dependency_id: str | None = Field(
        default=None, foreign_key="contribution.id", primary_key=True
    )
    dependent_id: str | None = Field(
        default=None, foreign_key="contribution.id", primary_key=True
    )


class ContributorBase(SQLModel):
    local_handle: str = Field(unique=True)
    display_name: str | None = Field(default=None, unique=True)
    discord_handle: str | None = None
    # TODO: create a custom validator for the following fields
    # https://github.com/tiangolo/sqlmodel/discussions/956
    github_account: str | None = Field(default=None)
    discourse_account: str | None = Field(default=None)
    wiki_account: str | None = Field(default=None)
    website: str | None = Field(default=None)
    extra_info: Dict[str, str] | None = Field(sa_type=JSON, default=None)


class ContributorUpsert(ContributorBase):
    @field_validator(
        "display_name",
        "discord_handle",
        "github_account",
        "discourse_account",
        "wiki_account",
        "website",
        mode="before",
    )
    @classmethod
    def empty_string_to_none(cls, v: str):
        if v == "":
            return None
        return v


class Contributor(ContributorBase, table=True):
    id: int | None = Field(default=None, primary_key=True)
    created_at: datetime | None = Field(
        default=None,
        sa_column=Column(
            DateTime(timezone=True), nullable=False, server_default=func.now()
        ),
    )
    updated_at: datetime | None = Field(
        default=None,
        sa_column=Column(
            DateTime(timezone=True),
            nullable=False,
            server_default=func.now(),
            onupdate=func.now(),
        ),
    )

    contributions: list[ContributionContributorLink] = Relationship(
        back_populates="contributor"
    )
    reviews: list["Review"] = Relationship(
        back_populates="reviewers", link_model=ContributorReviewLink
    )


class ContributorShort(SQLModel):
    id: int
    local_handle: str
    display_name: str | None = None


class ContributorWithAttributesShortPublic(ContributorBase):
    """Public view of a contributor, including contributions.
    Used to display all contributors."""

    id: int
    created_at: datetime
    updated_at: datetime
    contributions: list["ContributionShort"] = []

    @classmethod
    def from_contributor(cls, session: Session, db_contributor: Contributor):
        assert db_contributor.id is not None
        contributions = [
            ContributionShort.from_contribution(session, contribution)
            for contribution in crud.select_contributor_contributions(
                session=session, contributor_id=db_contributor.id
            )
        ]
        return cls.model_validate(
            db_contributor, update={"contributions": contributions}
        )


class ContributorViewPublic(ContributorWithAttributesShortPublic):
    """Public view of a contributor, including contributions and reviewed contributions.
    Used to display a contributor's profile.
    Requires one additional query to get reviewed contributions."""

    reviewed_contributions: list["ContributionShort"] = []

    @classmethod
    def from_contributor(cls, session: Session, db_contributor: Contributor):
        assert db_contributor.id is not None
        contributions = [
            ContributionShort.from_contribution(session, contribution)
            for contribution in crud.select_contributor_contributions(
                session=session, contributor_id=db_contributor.id
            )
        ]
        reviewed_contributions = [
            ContributionShort.from_contribution(session, contribution)
            for contribution in crud.select_contributor_reviewed_contributions(
                session=session, contributor_id=db_contributor.id
            )
        ]
        return cls.model_validate(
            db_contributor,
            update={
                "contributions": contributions,
                "reviewed_contributions": reviewed_contributions,
            },
        )


class ContributorReviewedContributions(SQLModel):
    reviewed_contributions: list["ContributionShort"] = []


class TagBase(SQLModel):
    display_name: str = Field(unique=True)
    color: str


class TagCreate(TagBase):
    pass


class Tag(TagBase, table=True):
    id: int | None = Field(default=None, primary_key=True)
    created_at: datetime | None = Field(
        default=None,
        sa_column=Column(
            DateTime(timezone=True), nullable=False, server_default=func.now()
        ),
    )
    updated_at: datetime | None = Field(
        default=None,
        sa_column=Column(
            DateTime(timezone=True),
            nullable=False,
            server_default=func.now(),
            onupdate=func.now(),
        ),
    )

    contributions: list["Contribution"] = Relationship(
        back_populates="tags", link_model=ContributionTagLink
    )


class TagUpdate(TagBase):
    pass


class TagPublic(TagBase):
    id: int
    created_at: datetime
    updated_at: datetime


class TagViewPublic(TagBase):
    id: int
    created_at: datetime
    updated_at: datetime
    contributions: list["ContributionShort"] = []


class ReviewBase(SQLModel):
    notes: str | None = None


class ReviewCreate(ReviewBase):
    link: HttpUrl | None = None
    contribution_id: str
    reviewers: list[int]

    @field_validator(
        "link",
        "notes",
        mode="before",
    )
    @classmethod
    def empty_string_to_none(cls, v: str):
        if v == "":
            return None
        return v


class Review(ReviewBase, table=True):
    id: int | None = Field(default=None, primary_key=True)
    created_at: datetime | None = Field(
        default=None,
        sa_column=Column(
            DateTime(timezone=True), nullable=False, server_default=func.now()
        ),
    )
    updated_at: datetime | None = Field(
        default=None,
        sa_column=Column(
            DateTime(timezone=True),
            nullable=False,
            server_default=func.now(),
            onupdate=func.now(),
        ),
    )

    link: str | None = None
    contribution_id: str = Field(foreign_key="contribution.id")
    contribution: "Contribution" = Relationship(back_populates="reviews")
    reviewers: list["Contributor"] = Relationship(
        back_populates="reviews", link_model=ContributorReviewLink
    )


class ReviewUpdate(ReviewBase):
    link: HttpUrl | None = None
    contribution_id: str
    reviewers: list[int]

    @field_validator(
        "link",
        "notes",
        mode="before",
    )
    @classmethod
    def empty_string_to_none(cls, v: str):
        if v == "":
            return None
        return v


class ReviewShort(SQLModel):
    id: int


class ReviewPublic(ReviewBase):
    id: int
    created_at: datetime
    updated_at: datetime

    link: str | None = None
    contribution_id: str
    reviewers: list[ContributorShort] = []


class ContributionLinks(SQLModel):
    description: str
    url: HttpUrl


class ContributionBase(SQLModel):
    title: str
    short_title: str | None = None
    date: datetime
    links: list[ContributionLinks] = Field(sa_type=JSON)
    description: str
    # attachments
    archived_at: datetime | None = None
    archive_reason: str | None = None


class ContributionCreate(ContributionBase):
    discord_chat_link: HttpUrl | None = Field(default=None)
    github_link: HttpUrl | None = Field(default=None)
    forum_link: HttpUrl | None = Field(default=None)
    wiki_link: HttpUrl | None = Field(default=None)
    contributors: list[int]
    tags: list[int]
    dependencies: list[str] = []

    @field_validator(
        "short_title",
        "discord_chat_link",
        "github_link",
        "forum_link",
        "wiki_link",
        mode="before",
    )
    @classmethod
    def empty_string_to_none(cls, v: str):
        if v == "":
            return None
        return v


class Contribution(ContributionBase, table=True):
    id: str = Field(primary_key=True)
    created_at: datetime | None = Field(
        default=None,
        sa_column=Column(
            DateTime(timezone=True), nullable=False, server_default=func.now()
        ),
    )
    updated_at: datetime | None = Field(
        default=None,
        sa_column=Column(
            DateTime(timezone=True),
            nullable=False,
            server_default=func.now(),
            onupdate=func.now(),
        ),
    )

    discord_chat_link: str | None = None
    github_link: str | None = None
    forum_link: str | None = None
    wiki_link: str | None = None

    contributors: list[ContributionContributorLink] = Relationship(
        back_populates="contribution"
    )
    tags: list["Tag"] = Relationship(
        back_populates="contributions", link_model=ContributionTagLink
    )
    reviews: list["Review"] = Relationship(back_populates="contribution")
    dependencies: list["Contribution"] = Relationship(
        back_populates="dependents",
        link_model=ContributionDependencyLink,
        sa_relationship_kwargs=dict(
            primaryjoin="Contribution.id==ContributionDependencyLink.dependent_id",
            secondaryjoin="Contribution.id==ContributionDependencyLink.dependency_id",
        ),
    )
    dependents: list["Contribution"] = Relationship(
        back_populates="dependencies",
        link_model=ContributionDependencyLink,
        sa_relationship_kwargs=dict(
            primaryjoin="Contribution.id==ContributionDependencyLink.dependency_id",
            secondaryjoin="Contribution.id==ContributionDependencyLink.dependent_id",
        ),
    )


class ContributionUpdate(ContributionBase):
    discord_chat_link: HttpUrl | None = Field(default=None)
    github_link: HttpUrl | None = Field(default=None)
    forum_link: HttpUrl | None = Field(default=None)
    wiki_link: HttpUrl | None = Field(default=None)
    contributors: list[int]
    tags: list[int]
    dependencies: list[str] = []

    @field_validator(
        "short_title",
        "discord_chat_link",
        "github_link",
        "forum_link",
        "wiki_link",
        mode="before",
    )
    @classmethod
    def empty_string_to_none(cls, v: str):
        if v == "":
            return None
        return v


class ContributionDependency(SQLModel):
    id: str
    title: str
    short_title: str | None = None


class ContributionShort(SQLModel):
    id: str
    title: str
    short_title: str | None = None
    date: datetime

    discord_chat_link: str | None = None
    github_link: str | None = None
    forum_link: str | None = None
    wiki_link: str | None = None

    archived_at: datetime | None = None
    archive_reason: str | None = None

    contributors: list[ContributorShort] = []
    tags: list[TagPublic] = []
    reviews: list[ReviewShort] = []
    dependencies: list[ContributionDependency] = []

    @classmethod
    def from_contribution(cls, session: Session, db_contribution: Contribution):
        contributors = crud.select_contribution_contributors(
            session=session, contribution_id=db_contribution.id
        )
        return cls.model_validate(
            db_contribution, update={"contributors": contributors}
        )


class ContributionWithAttributesShortPublic(ContributionBase):
    id: str
    created_at: datetime
    updated_at: datetime

    discord_chat_link: str | None = None
    github_link: str | None = None
    forum_link: str | None = None
    wiki_link: str | None = None

    contributors: list[ContributorShort] = []
    tags: list[TagPublic] = []
    reviews: list[ReviewPublic] = []
    dependencies: list[ContributionShort] = []

    @classmethod
    def from_contribution(
        cls,
        session: Session,
        db_contribution: Contribution,
        contributors: Optional[list[Contributor]] = None,
    ):
        if contributors is None:
            contributors = crud.select_contribution_contributors(
                session=session, contribution_id=db_contribution.id
            )
        dependencies = [
            ContributionShort.from_contribution(session, dependency)
            for dependency in db_contribution.dependencies
        ]
        return cls.model_validate(
            db_contribution,
            update={"contributors": contributors, "dependencies": dependencies},
        )
