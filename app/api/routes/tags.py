from fastapi import APIRouter
from sqlalchemy import select

from app import crud
from app.api.deps import SessionDep
from app.core.exceptions import NotFoundError
from app.models import Message, Tag, TagCreate, TagPublic, TagUpdate, TagViewPublic

router = APIRouter()


@router.post("/tags", response_model=TagPublic)
def create_tag(session: SessionDep, tag: TagCreate):
    if crud.integrity_check_tag(session, tag):
        return crud.create_tag(session, tag)


@router.get("/tags/{tag_id}", response_model=TagViewPublic)
def read_tag(session: SessionDep, tag_id: int):
    tag = crud.select_tag_by_id(session, tag_id)
    if tag is None:
        raise NotFoundError(what="Tag")
    return tag


@router.put("/tags/{tag_id}", response_model=TagPublic)
def update_tag(session: SessionDep, tag_id: int, tag_in: TagUpdate):
    tag = session.get(Tag, tag_id)
    if not tag:
        raise NotFoundError(what="Tag")
    if crud.integrity_check_tag(session, tag_in, tag_id):
        return crud.update_tag(session, tag, tag_in)


@router.delete("/tags/{tag_id}", response_model=Message)
def delete_tag(session: SessionDep, tag_id: int):
    tag = crud.select_tag_by_id(session, tag_id)
    if not tag:
        raise NotFoundError(what="Tag")
    session.delete(tag)
    session.commit()
    return Message(message="Tag deleted successfully")


@router.get("/tags", response_model=list[TagPublic])
def read_tags(session: SessionDep, skip: int = 0, limit: int = 100):
    statement = select(Tag).offset(skip).limit(limit)
    tags = session.exec(statement).all()
    return [tag[0] for tag in tags]
