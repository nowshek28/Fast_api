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
        )

        self.db.add(transcript)
        self.db.commit()
        self.db.refresh(transcript)

        return transcript

    def get_by_id(self, transcript_id: UUID) -> TranscriptModel | None:
        """
        Retrieve transcript by transcript ID.
        """

        return (
            self.db.query(TranscriptModel)
            .filter(TranscriptModel.id == str(transcript_id))
            .first()
        )

    def get_by_todo_id(self, todo_id: UUID) -> TranscriptModel | None:
        """
        Retrieve transcript attached to a todo.
        """

        return (
            self.db.query(TranscriptModel)
            .filter(TranscriptModel.todo_id == str(todo_id))
            .first()
        )

    def exists_for_todo(self, todo_id: UUID, user_id: UUID) -> bool:
        """
        Check whether a transcript already exists for a todo.
        """

        return (
            self.db.query(TranscriptModel)
            .filter(TranscriptModel.todo_id == str(todo_id))
            .first()
            is not None
        )

    def delete(self, transcript_id: UUID) -> None:
        """
        Delete a transcript record.
        """

        transcript = self.get_by_id(transcript_id)
        if transcript is None:
            return


        self.db.delete(transcript)
        self.db.commit()

    def get_file_name(self, transcript_id: UUID) -> str | None:
        """
        Retrieve the original filename of a transcript by its ID.
        """

        transcript = self.get_by_id(transcript_id)
        if transcript:
            return transcript.s3_key