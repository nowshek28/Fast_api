import logging
from sqlalchemy import text

from app.core.config import settings
from app.database.database import SessionLocal
from app.database.s3storage import s3_client as s3
from app.database.chroma import chroma_client

logger = logging.getLogger(__name__)

def check_database_health():
    try:
        # Perform a simple query to check database connectivity
        db = SessionLocal()
        db.execute(text("SELECT 1"))
        logger.info("Database health check passed.")
        return True
    except Exception as e:
        logger.info(f"Database health check failed: {e}")
        logger.error(f"Database health check failed: {e}")
        raise RuntimeError("Database health check failed")

def check_s3_health():
    try:
        s3.head_bucket(Bucket=settings.AWS_S3_BUCKET_NAME)
        logger.info("S3 health check passed.")
        return True
    except Exception as e:
        logger.info(f"S3 health check failed: {e}")
        logger.error(f"S3 health check failed: {e}")
        raise RuntimeError("S3 health check failed")
    
def check_chroma_connection() -> None:
    """
    validates the connection to the Chroma database by attempting to retrieve the collection.
    """
    try:
        chroma_client.heartbeat()

        logger.info("Successfully connected to Chroma database.")

    except Exception as exc:
        logger.exception("Failed to connect to Chroma database.")
        raise ConnectionError("Failed to connect to Chroma database.") from exc