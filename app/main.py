import sentry_sdk
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from structlog import get_logger

from app.api.routes import contributions, contributors, reviews, tags
from app.core.config import settings

_LOGGER = get_logger()


# from app.initial_data import init, init_data
# init()
# init_data()

if settings.SENTRY_DSN and settings.ENVIRONMENT != "local":
    sentry_sdk.init(
        dsn=str(settings.SENTRY_DSN),
        environment=settings.ENVIRONMENT,
        enable_tracing=True,
        traces_sample_rate=1.0,
    )


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


@app.get("/sentry-debug")
async def trigger_error():
    division_by_zero = 1 / 0
    return division_by_zero
