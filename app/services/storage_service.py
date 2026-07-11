import logging
from fastapi import UploadFile
from pathlib import Path
from uuid import UUID, uuid4

from botocore.exceptions import ClientError

from app.core.config import settings
from app.database.s3storage import s3_client


logger = logging.getLogger(__name__)


class StorageService:
    """
    Service responsible for all S3 storage operations.
    """

    def __init__(self):
        self.s3 = s3_client
        self.bucket_name = settings.AWS_S3_BUCKET_NAME

    def generate_s3_key(
        self,
        todo_id: UUID,
        filename: str,
    ) -> str:
        """
        Generate a unique S3 object key.

        Example:
        transcripts/{todo_id}/{uuid}_meeting.pdf
        """

        extension = Path(filename).suffix

        unique_filename = f"{uuid4()}{extension}"

        return f"transcripts/{todo_id}/{unique_filename}"

    async def upload_transcript(
        self,
        todo_id: UUID,
        file: UploadFile,
    ) -> str:
        """
        Upload transcript to S3.

        Returns:
            Generated S3 object key.
        """

        if not file.filename:
            raise ValueError("Uploaded file must have a filename.")
        
        # allowed_types = {
        #     "application/pdf",
        #     "text/plain",
        #     "text/markdown",
        #     "application/vnd.openxmlformats-officedocument.wordprocessingml.document",
        # }
        #
        # if file.content_type not in allowed_types:
        #     raise ValueError("Unsupported file type.")

        s3_key = self.generate_s3_key(
            todo_id=todo_id,
            filename=file.filename,
        )

        try:
            contents = await file.read()

            file.file.seek(0)   # Reset the file pointer to the beginning of the file before uploading

            self.s3.upload_fileobj(
                Fileobj=file.file,
                Bucket=self.bucket_name,
                Key=s3_key,
                ExtraArgs={
                    "ContentType": file.content_type,
                },
            )

            logger.info(
                "Transcript uploaded successfully to %s.",
                s3_key,
            )

            return s3_key,len(contents)

        except ClientError as exc:
            logger.exception(
                "Failed to upload transcript."
            )
            raise RuntimeError(
                "Transcript upload failed."
            ) from exc

    def delete_transcript(
        self,
        s3_key: str,
    ) -> bool:
        """
        Delete transcript from S3.
        """

        try:

            self.s3.delete_object(
                Bucket=self.bucket_name,
                Key=s3_key,
            )

            logger.info(
                "Deleted transcript %s.",
                s3_key,
            )

            return True

        except ClientError as exc:

            logger.exception(
                "Failed to delete transcript."
            )

            raise RuntimeError(
                "Transcript deletion failed."
            ) from exc

    def object_exists(
        self,
        s3_key: str,
    ) -> bool:
        """
        Check whether an object exists in S3.
        """

        try:

            self.s3.head_object(
                Bucket=self.bucket_name,
                Key=s3_key,
            )

            return True

        except ClientError:
            return False