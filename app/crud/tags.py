from typing import Optional, Union

from sqlmodel import Session, select
from structlog import get_logger

from app.core.exceptions import ConditionError
from app.models import Tag, TagCreate, TagUpdate

_LOGGER = get_logger()


def create_tag(session: Session, tag: TagCreate) -> Tag:
    db_tag = Tag.model_validate(tag)
    session.add(db_tag)
    session.commit()
    session.refresh(db_tag)
    return db_tag


def select_tag_by_id(session: Session, tag_id: int) -> Tag | None:
    statement = select(Tag).where(Tag.id == tag_id)
    tag = session.exec(statement).first()
    return tag


def update_tag(session: Session, tag: Tag, tag_in: TagUpdate) -> Tag:
    tag_dict = tag_in.model_dump()
    tag.sqlmodel_update(tag_dict)
    session.add(tag)
    session.commit()
    session.refresh(tag)
    return tag


def integrity_check_tag(
    session: Session,
    tag_in: Union[TagCreate, TagUpdate],
    tag_update_id: Optional[int] = None,
) -> bool:
    # check if display name is used
    statement = select(Tag).where(Tag.display_name == tag_in.display_name)
    tag = session.exec(statement).first()
    if (tag is not None and tag_update_id is None) or (
        tag is not None and tag.id != tag_update_id
    ):
        _LOGGER.info(
            "Display name already exists",
            display_name=tag_in.display_name,
            tag_id=tag.id,
        )
        raise ConditionError(
            condition="Display name already exists",
        )
    return True
