from structlog import get_logger

from app.core.exceptions import NotFoundError

_LOGGER = get_logger()


def update_links(
    session, obj, obj_name, link_name, previous_links, new_links, select_function
):
    previous_links_ids = [link.id for link in previous_links]
    for link_in_id in new_links:
        if link_in_id not in previous_links_ids:
            link = select_function(session, link_in_id)
            if link is None:
                raise NotFoundError(
                    what=f"{link_name.capitalize()} with ID {link_in_id}"
                )
            _LOGGER.debug(
                f"Adding {link_name[:-1]} to {obj_name}.",
                link_id=link_in_id,
                contribution_id=obj.id,
            )
            previous_links.append(link)
            session.add(obj)
            session.commit()
            _LOGGER.debug(
                f"{link_name[:-1].capitalize()} added.",
                link_id=link_in_id,
                contribution_id=obj.id,
            )
    for link_id in previous_links_ids:
        if link_id not in new_links:
            link = select_function(session, link_id)
            if link is None:
                raise NotFoundError(what=f"{link_name.capitalize()} with ID {link_id}")
            previous_links.remove(link)
            _LOGGER.debug(
                f"Removing {link_name[:-1]} from {obj_name}.",
                link_id=link.id,
                contribution_id=obj.id,
            )
            session.add(obj)
            session.commit()
            _LOGGER.debug(
                f"{link_name[:-1].capitalize()} removed.",
                link_id=link.id,
                contribution_id=obj.id,
            )
