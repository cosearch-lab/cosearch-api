from datetime import datetime
from typing import Dict

from pydantic import HttpUrl, field_validator
from sqlalchemy.sql import func
from sqlalchemy.sql.sqltypes import JSON, DateTime
from sqlmodel import Column, Field, Relationship, SQLModel


# Generic message
class Message(SQLModel):
    message: str


class ContributionContributorLink(SQLModel, table=True):
    contribution_id: str | None = Field(
        default=None, foreign_key="contribution.id", primary_key=True
    )
    contributor_id: int | None = Field(
        default=None, foreign_key="contributor.id", primary_key=True
    )


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

    contributions: list["Contribution"] = Relationship(
        back_populates="contributors", link_model=ContributionContributorLink
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


class ContributorViewPublic(ContributorWithAttributesShortPublic):
    """Public view of a contributor, including contributions and reviewed contributions.
    Used to display a contributor's profile.
    Requires one additional query to get reviewed contributions."""

    reviewed_contributions: list["ContributionShort"] = []


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
    contributions: list["TaggedContributionShort"] = []


class ReviewBase(SQLModel):
    link: str
    notes: str


class ReviewCreate(ReviewBase):
    contribution_id: str
    reviewers: list[int]


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

    contribution_id: str = Field(foreign_key="contribution.id")
    contribution: "Contribution" = Relationship(back_populates="reviews")
    reviewers: list["Contributor"] = Relationship(
        back_populates="reviews", link_model=ContributorReviewLink
    )


class ReviewUpdate(ReviewBase):
    contribution_id: str
    reviewers: list[int]


class ReviewShort(SQLModel):
    id: int


class ReviewPublic(ReviewBase):
    id: int
    contribution_id: str
    created_at: datetime
    updated_at: datetime
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

    contributors: list["Contributor"] = Relationship(
        back_populates="contributions", link_model=ContributionContributorLink
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
    short_title: str


class ContributionShort(SQLModel):
    id: str
    title: str
    short_title: str
    date: datetime
    contributors: list[ContributorShort] = []
    tags: list[TagPublic] = []
    reviews: list[ReviewShort] = []
    dependencies: list[ContributionDependency] = []


class TaggedContributionShort(ContributionShort):
    """Used to display contribution for a specific tag.
    Type of attribute `tags` is Tag instead of TagPublic to avoid infinite recursion."""

    tags: list[Tag] = []


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
    reviews: list[ReviewShort] = []
    dependencies: list[ContributionShort] = []
