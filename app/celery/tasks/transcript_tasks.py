from datetime import datetime, timezone
import time
import logging 

from app.celery.celery_app import celery_app
from app.database.database import get_db

from app.repositories.transcript_repository import TranscriptRepository
from app.services.storage_service import StorageService
from app.services.etl.text_extractor import TextExtractor
from app.services.etl.text_cleaner import TextCleaner
from app.services.etl.chunk_service import ChunkService
from app.services.etl.embedding_service import EmbeddingService
from app.services.etl.vectorstore_service import VectorStoreService

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
        text_extractor = TextExtractor()
        text_cleaner = TextCleaner()
        chunk_service = ChunkService()
        embedding_service = EmbeddingService()
        vector_store = VectorStoreService()
    
        transcript_repository.update_processing_status(
            transcript_id=transcript_id,
            user_id=user_id,
            status="PROCESSING",
            started_at=datetime.now(timezone.utc)
        )

        try:
            # Simulate transcript processing
            # Simulate ETL
            transcript = transcript_repository.get_by_id(transcript_id=transcript_id, user_id=user_id)


            file_bytes = StorageService().download_transcript(
                s3_key=transcript.s3_key
            )

            logger.info("Downloaded transcript with ID: %s for user ID: %s", transcript_id, user_id)

            text = text_extractor.extract(
                file_bytes=file_bytes, 
                file_type=transcript.file_type,
            )

            logger.info("Extracting text from transcript with ID: %s for user ID: %s", transcript_id, user_id)

            transcript_repository.update_processing_status(
                transcript_id=transcript_id,
                user_id=user_id,
                status="EXTRACTING",
                completed_at=datetime.now(timezone.utc)
            )

            # Check if text extraction has any content or not
            if not text:
                raise ValueError("No text extracted from the transcript.")
            

            # Clean the text
            cleaned_text = text_cleaner.clean_text(text, transcript.file_type)

            logger.info("Cleaning text from transcript with ID: %s for user ID: %s", transcript_id, user_id)

            transcript_repository.update_processing_status(
                transcript_id=transcript_id,
                user_id=user_id,
                status="NORMALIZING",
                completed_at=datetime.now(timezone.utc)
            )

            if not cleaned_text:
                raise ValueError("No text after cleaning the transcript.")
            
            # Chunk the text
            chunks = chunk_service.chunk_text(cleaned_text)

            logger.info("Chunking text from transcript with ID: %s for user ID: %s", transcript_id, user_id)

            transcript_repository.update_processing_status(
                transcript_id=transcript_id,
                user_id=user_id,
                status="CHUNKING",
                completed_at=datetime.now(timezone.utc)
            )


            # embeddings conversion
            embeddings = embedding_service.generate_embeddings(chunks)

            logger.info("Generating embeddings from transcript with ID: %s for user ID: %s", transcript_id, user_id)

            transcript_repository.update_processing_status(
                transcript_id=transcript_id,
                user_id=user_id,
                status="EMBEDDING",
                completed_at=datetime.now(timezone.utc)
            )

            logger.info("Generated Metadata and embeddings for transcript with ID: %s for user ID: %s", transcript_id, user_id)
            # prepare records for vector store insertion
            records = vector_store.prepare_records(
                transcript=transcript,
                chunks=chunks,
                embeddings=embeddings
            )

            # Store the processed data in the vector database
            vector_store.store_records(records)

            logger.info("Successfully stored records in vector store for transcript with ID: %s for user ID: %s", transcript_id, user_id)

            
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