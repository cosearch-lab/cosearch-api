from collections.abc import Generator
from typing import Annotated

from discord import SyncWebhook
from fastapi import Depends
from sqlmodel import Session

from app.core.config import settings
from app.core.db import engine


def get_db() -> Generator[Session, None, None]:
    with Session(engine) as session:
        yield session


SessionDep = Annotated[Session, Depends(get_db)]


def get_discord_webhook() -> SyncWebhook | None:
    discord_webhook = None
    if settings.DISCORD_WEBHOOK_URL is not None and settings.ENVIRONMENT != "local":
        discord_webhook = SyncWebhook.from_url(
            str(settings.DISCORD_WEBHOOK_URL),
        )

    return discord_webhook
