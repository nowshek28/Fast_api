import logging

from fastapi import FastAPI
from app.api.v1.router import router as api_router
from app.auth.router import router as auth_router

from app.core.config import settings
from app.core.logging import setup_logging
from app.core.exception_handlers import register_exception_handlers
from app.core.middleware import register_middleware

setup_logging()

logger = logging.getLogger(__name__)

app = FastAPI(
    title=settings.APP_NAME,
    version=settings.APP_VERSION,
)

register_exception_handlers(app)
register_middleware(app)
app.include_router(auth_router)
app.include_router(api_router)


@app.get("/")
def root():
    """Root endpoint for the FastAPI application."""
    return {
        "name": settings.APP_NAME,
        "version": settings.APP_VERSION,
        "status": "running",
        "docs": "/docs",
    }