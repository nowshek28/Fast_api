from datetime import datetime
from uuid import UUID

from sqlalchemy.orm import Session

from app.database.models import TranscriptModel


class TranscriptRepository:
    def __init__(self, db: Session):
        self.db = db

    def create(
        self,
        *,
        todo_id: UUID,
        s3_key: str,
        original_filename: str,
        file_type: str,
        file_size: int,
        user_id: UUID,
        processing_status: str
    ) -> TranscriptModel:
        """
        Create a new transcript record.
        """

        transcript = TranscriptModel(
            todo_id=str(todo_id),
            s3_key=s3_key,
            original_filename=original_filename,
            file_type=file_type,
            file_size=file_size,
            user_id=str(user_id),
            processing_status=processing_status
        )

        self.db.add(transcript)
        self.db.commit()
        self.db.refresh(transcript)

        return transcript

    def get_by_id(self, transcript_id: UUID, user_id: UUID) -> TranscriptModel | None:
        """
        Retrieve transcript by transcript ID.
        """

        return (
            self.db.query(TranscriptModel)
            .filter(TranscriptModel.id == str(transcript_id))
            .filter(TranscriptModel.user_id == str(user_id))
            .first()
        )

    def get_by_todo_id(self, todo_id: UUID, user_id: UUID) -> TranscriptModel | None:
        """
        Retrieve transcript attached to a todo.
        """

        return (
            self.db.query(TranscriptModel)
            .filter(TranscriptModel.todo_id == str(todo_id))
            .filter(TranscriptModel.user_id == str(user_id))
            .first()
        )

    def exists_for_todo(self, todo_id: UUID, user_id: UUID) -> bool:
        """
        Check whether a transcript already exists for a todo.
        """

        return (
            self.db.query(TranscriptModel)
            .filter(TranscriptModel.todo_id == str(todo_id))
            .filter(TranscriptModel.user_id == str(user_id))
            .first()
            is not None
        )

    def delete(self, transcript_id: UUID, user_id: UUID) -> None:
        """
        Delete a transcript record.
        """

        transcript = self.get_by_id(transcript_id, user_id)
        if transcript is None:
            return


        self.db.delete(transcript)
        self.db.commit()

    def get_file_name(self, transcript_id: UUID, user_id: UUID) -> str | None:
        """
        Retrieve the original filename of a transcript by its ID.
        """

        transcript = self.get_by_id(transcript_id, user_id)
        if transcript:
            return transcript.s3_key
        
    def get_by_user_id(self, user_id: UUID) -> list[TranscriptModel]:
        """
        Retrieve all transcripts for a specific user.
        """
        return (
            self.db.query(TranscriptModel)
            .filter(TranscriptModel.user_id == str(user_id))
            .all()
        )

    def get_download_key_orignal(self, transcript_id: UUID, user_id: UUID) -> str | None:
        """
        Retrieve the S3_key & original filename of a transcript by its ID.
        """
        if str(user_id) != str(user_id):
            raise PermissionError("You do not have permission to access this transcript.")
        
        transcript = self.get_by_id(transcript_id, user_id)
        if transcript:
            return (transcript.s3_key, transcript.original_filename)
        return (None, None)
    
    def update_processing_status(self, transcript_id: UUID, user_id: UUID, status: str, started_at: datetime | None = None, completed_at: datetime| None = None, error_message: str | None = None) -> None:
        """
        Update the processing status of a transcript.
        """
        transcript = self.get_by_id(transcript_id, user_id)
        if transcript:
            transcript.processing_status = status
            if started_at:
                transcript.processing_started_at = started_at
            if completed_at:
                transcript.processing_completed_at = completed_at
            if error_message:
                transcript.error_message = error_message
            self.db.commit()