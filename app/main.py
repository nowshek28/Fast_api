import logging
from contextlib import asynccontextmanager

from fastapi import FastAPI
from app.api.v1.router import router as api_v1_router
from app.auth.router import router as auth_router
from app.api.v2.router import router as transcript_router

from app.core.config import settings
from app.core.logging import setup_logging
from app.core.exception_handlers import register_exception_handlers
from app.core.middleware import register_middleware
from app.core.startup_check import check_database_health, check_s3_health

setup_logging()

logger = logging.getLogger(__name__)


@asynccontextmanager
async def lifespan(app: FastAPI):
    """
    Lifespan context manager for the FastAPI application.
    Performs startup checks for database and S3 health.
    """
    try:
        check_database_health()
        check_s3_health()
        logger.info("Startup checks passed. Application is ready.")
        yield
    except Exception as e:
        logger.error(f"Startup checks failed: {e}")
        raise RuntimeError("Startup checks failed") from e



app = FastAPI(
    title=settings.APP_NAME,
    version=settings.APP_VERSION,
    lifespan=lifespan
)

register_exception_handlers(app)
register_middleware(app)
app.include_router(auth_router)
app.include_router(api_v1_router)
app.include_router(transcript_router)



@app.get("/")
def root():
    """Root endpoint for the FastAPI application."""
    return {
        "name": settings.APP_NAME,
        "version": settings.APP_VERSION,
        "status": "running",
        "docs": "/docs",
    }
