from enum import Enum

from pydantic import BaseModel, Field
from uuid import UUID

from datetime import datetime


class ProcessingStatus(str, Enum):
    UPLOADED = "UPLOADED"
    PROCESSING = "PROCESSING"
    READY = "READY"
    FAILED = "FAILED"

class TranscriptBase(BaseModel):
    """Base schema for transcript"""

    s3_key: str = Field(
        ...,
        description="S3 key for the transcript file"
    )

    original_filename: str = Field(
        ...,
        min_length=1,
        max_length=255,
        description="Original filename of the transcript"
    )

    file_type: str = Field(
        ...,
        description="File type of the transcript"
    )

    file_size: int = Field(
        ...,
        gt=0,
        description="File size of the transcript in bytes"
    )

    processing_status: ProcessingStatus = Field(
        default=ProcessingStatus.UPLOADED,
        description="Processing status of the transcript"
    )

    error_message: str | None = Field(
        None,
        description="Error message if processing failed"
    )



class TranscriptCreate(TranscriptBase):
    """Schema for creating a new transcript"""
    pass

class TranscriptResponse(TranscriptBase):
    """
    Schema for returning transcript data in responses.
    """

    id: UUID
    todo_id: UUID
    uploaded_at: datetime
    user_id: UUID
