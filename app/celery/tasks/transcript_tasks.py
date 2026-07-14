from datetime import datetime, timezone
import time
import logging 

from app.celery.celery_app import celery_app
from app.database.database import get_db

from app.repositories.transcript_repository import TranscriptRepository

logger = logging.getLogger(__name__)


@celery_app.task(name="process_transcript")
def process_transcript(transcript_id: str, user_id: str):
    """
    Celery task to process a transcript.

    Args:
        transcript_id (str): The ID of the transcript to process.
        user_id (str): The ID of the user who submitted the transcript.
    """

    try:
        # Initialize the TranscriptRepository with a database session
        db = next(get_db())
        transcript_repository = TranscriptRepository(db=db)
    
    
        transcript_repository.update_processing_status(
            transcript_id=transcript_id,
            user_id=user_id,
            status="PROCESSING",
            started_at=datetime.now(timezone.utc)
        )

        try:
            # Simulate transcript processing
            # Simulate ETL
            for i in range(10):
                logger.info("Processing transcript %s (%d/10)", transcript_id, i + 1)
                time.sleep(1)

            # Add your transcript processing logic here
            logger.info("Processing transcript with ID: %s for user ID: %s", transcript_id, user_id)

            
            # Update the processing status to "READY" and set the completed_at timestamp
            transcript_repository.update_processing_status(
                transcript_id=transcript_id,
                user_id=user_id,
                status="READY",
                completed_at=datetime.now(timezone.utc)
            )

        except Exception as e:
            logger.error("Error processing transcript %s: %s", transcript_id, str(e))
            # Update the processing status to "FAILED" and set the completed_at timestamp
            transcript_repository.update_processing_status(
                transcript_id=transcript_id,
                user_id=user_id,
                status="FAILED",
                completed_at=datetime.now(timezone.utc),
                error_message=str(e)
            )
            raise e
    
    except Exception as e:
        logger.error("Error initializing TranscriptRepository: %s", str(e))
        raise e
    
    finally:
        if db:
            db.close()

    return {
        "status": "success",
        "transcript_id": transcript_id,
    }