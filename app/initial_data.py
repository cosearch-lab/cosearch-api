from sqlmodel import Session
from structlog import get_logger

from app import crud
from app.core.db import engine, init_db
from app.core.exceptions import ConditionError
from app.models import ContributorUpsert, TagCreate

_LOGGER = get_logger()


"""
Upserted functions are not used by the application, but are useful for
initializing the database with data.
"""


def upsert_contributor(session: Session, contributor_in: ContributorUpsert):
    try:
        crud.integrity_check_contributor(session, contributor_in)
    except ConditionError as e:
        _LOGGER.error("Contributor integrity check failed, insertion aborted", error=e)
        return None
    return crud.create_contributor(session, contributor_in)


def upsert_tag(session: Session, tag_in: TagCreate):
    try:
        crud.integrity_check_tag(session, tag_in)
    except ConditionError as e:
        _LOGGER.error("Tag integrity check failed, insertion aborted", error=e)
        return None
    return crud.create_tag(session, tag_in)


def init_data() -> None:
    from app.models import ContributorUpsert, TagCreate

    _LOGGER.info("Creating initial data")

    contributor_1 = ContributorUpsert(
        local_handle="cosmo", display_name="Tristan Stérin"
    )
    contributor_2 = ContributorUpsert(local_handle="mxdys")

    tag_1 = TagCreate(display_name="Decider", color="#991b1b")
    tag_2 = TagCreate(display_name="Formal Verification", color="#3730a3")
    tag_3 = TagCreate(display_name="Individual Machine", color="#115e59")
    tag_4 = TagCreate(display_name="Meta", color="#1f2937")

    with Session(engine) as session:
        upsert_contributor(session, contributor_1)
        upsert_contributor(session, contributor_2)

        upsert_tag(session, tag_1)
        upsert_tag(session, tag_2)
        upsert_tag(session, tag_3)
        upsert_tag(session, tag_4)

    _LOGGER.info("Initial data created")


def init() -> None:
    with Session(engine) as session:
        init_db(session)


def main() -> None:
    _LOGGER.info("Initializing database")
    init()
    _LOGGER.info("Database initialized")


if __name__ == "__main__":
    main()
