from fastapi import APIRouter, Depends, HTTPException, status, UploadFile, File
from fastapi.responses import Response
from uuid import UUID

from app.schemas.transcript import TranscriptResponse
from app.schemas.user import CurrentUserResponse
from app.services.todo_service import TodoService
from app.core.dependencies import get_service
from app.auth.dependencies import get_current_db_user
from app.core.dependencies import get_transcript_service
from app.core.dependencies import get_s3_storage_service


router = APIRouter()

@router.post(
        "/todos/{todo_id}/transcript",
        response_model=TranscriptResponse,
        status_code=201,
        )
async def upload_transcript(
    todo_id: UUID,
    file: UploadFile = File(...),
    transcript_service=Depends(get_transcript_service),
    service: TodoService = Depends(get_service),
    current_user: CurrentUserResponse = Depends(get_current_db_user),
):
    """
    Create a transcript for a specific Todo.
    """
    # Ensure the todo exists and belongs to the current user
    todo = service.get_by_id(todo_id, user_id=current_user.id)
    if not todo:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Todo not found."
        )

    # Create the transcript
    transcript = await transcript_service.create(
        todo_id=todo_id, 
        file=file,
        user_id=current_user.id)
    
    if not transcript:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Failed to create transcript."
        )

    return transcript

@router.get(
        "/todos/{todo_id}/transcript",
        response_model=TranscriptResponse,
        status_code=200,
        )
def get_transcript_for_todo(
    todo_id: UUID,
    transcript_service=Depends(get_transcript_service),
    service: TodoService = Depends(get_service),
    current_user: CurrentUserResponse = Depends(get_current_db_user),
):
    """
    Get the transcript for a specific Todo.
    """
    # Ensure the todo exists and belongs to the current user
    todo = service.get_by_id(todo_id, user_id=current_user.id)
    if not todo:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Todo not found."
        )

    # Get the transcript
    transcript = transcript_service.get_by_todo_id(todo_id, user_id=current_user.id)
    if not transcript:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Transcript not found."
        )

    return transcript

@router.delete(
        "/transcripts/{transcript_id}",
        status_code=status.HTTP_204_NO_CONTENT,
        )
def delete_transcript_for_todo(
    transcript_id: UUID,
    transcript_service=Depends(get_transcript_service),
    current_user: CurrentUserResponse = Depends(get_current_db_user),
):
    """
    Delete the transcript for a specific Todo.
    """

    # Get the transcript
    transcript = transcript_service.get_by_id(transcript_id,current_user.id)
    if not transcript:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Transcript not found."
        )

    # Delete the transcript
    success = transcript_service.delete(transcript_id,current_user.id)
    if not success:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to delete transcript."
        )

@router.get(
        "/transcripts/{transcript_id}",
        response_model=TranscriptResponse,
        status_code=200,
        )   
def get_transcript_by_id(
    transcript_id: UUID,
    transcript_service=Depends(get_transcript_service),
    current_user: CurrentUserResponse = Depends(get_current_db_user),
):
    """
    Get a transcript by its ID.
    """
    transcript = transcript_service.get_by_id(transcript_id, user_id=current_user.id)
    if not transcript:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, 
            detail="Transcript not found."
        )

    return transcript
                                        

@router.get(
    "/transcripts/user/all_transcripts",
    response_model=list[TranscriptResponse],
    status_code=200,
)
def get_transcripts_by_user(
    transcript_service=Depends(get_transcript_service),
    current_user: CurrentUserResponse = Depends(get_current_db_user),
):
    """
    Get all transcripts for a specific user.
    """

    transcripts = transcript_service.get_by_user_id(current_user.id)
    
    if not transcripts:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="No transcripts found for this user."
        )
    
    return transcripts

@router.get(
    "/transcripts/{transcript_id}/download",
    status_code=200,
)   
def download_transcript(
    transcript_id: UUID,
    local_file_path: str,
    transcript_service=Depends(get_transcript_service),
    current_user: CurrentUserResponse = Depends(get_current_db_user),
):
    """
    Download a transcript file by its ID.
    """
    # Get the S3 key for the transcript
    local_file_path = transcript_service.get_download_transcript_file(transcript_id, local_file_path, current_user.id)
    if not local_file_path:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Transcript not found."
        )

    return {"message": "Transcript downloaded successfully.", "file_path": local_file_path}