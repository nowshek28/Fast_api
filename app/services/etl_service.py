from app.celery.tasks.transcript_tasks import process_transcript


class ETLService:

    def submit_transcript(self, transcript_id: str, user_id: str) -> None:
        """
        Submits a transcript for processing.
        """
        # Call the Celery task to process the transcript
        process_transcript.delay(transcript_id, user_id)
