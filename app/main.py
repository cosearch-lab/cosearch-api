from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from structlog import get_logger

from app.api.routes import contributions, contributors, reviews, tags
from app.core.config import settings

_LOGGER = get_logger()


# from app.initial_data import init, init_data
# init()
# init_data()


_LOGGER.info("Creating FastAPI app", settings=settings)
app = FastAPI()

origins = ["*"]

app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(contributors.router, tags=["Contributors"])
app.include_router(contributions.router, tags=["Contributions"])
app.include_router(tags.router, tags=["Tags"])
app.include_router(reviews.router, tags=["Reviews"])
