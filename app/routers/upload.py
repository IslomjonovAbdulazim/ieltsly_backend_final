from fastapi import APIRouter, UploadFile, File, HTTPException, Depends
from fastapi.security import HTTPBearer
from typing import Dict, Any
from app.services.upload import upload_service
from app.auth import get_current_user

router = APIRouter(
    prefix="/upload",
    tags=["upload"]
)

security = HTTPBearer()

@router.post("/audio", response_model=Dict[str, Any])
async def upload_audio(
    file: UploadFile = File(...),
    current_user: dict = Depends(get_current_user)
):
    """
    Upload an audio file to Supabase storage.
    
    Supported formats: MP3, WAV, M4A, OGG, WebM
    Maximum file size: 20MB
    """
    if not file.filename:
        raise HTTPException(status_code=400, detail="No file provided")
    
    try:
        result = await upload_service.upload_file(
            file=file,
            file_type="audio",
            folder="audio"
        )
        
        return {
            "message": "Audio file uploaded successfully",
            "data": result
        }
        
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Audio upload failed: {str(e)}"
        )

@router.post("/image", response_model=Dict[str, Any])
async def upload_image(
    file: UploadFile = File(...),
    current_user: dict = Depends(get_current_user)
):
    """
    Upload an image file to Supabase storage.
    
    Supported formats: JPEG, PNG, WebP
    Maximum file size: 5MB
    """
    if not file.filename:
        raise HTTPException(status_code=400, detail="No file provided")
    
    try:
        result = await upload_service.upload_file(
            file=file,
            file_type="image",
            folder="images"
        )
        
        return {
            "message": "Image file uploaded successfully",
            "data": result
        }
        
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Image upload failed: {str(e)}"
        )

@router.delete("/file/{file_path:path}")
async def delete_file(
    file_path: str,
    current_user: dict = Depends(get_current_user)
):
    """
    Delete a file from Supabase storage.
    """
    try:
        result = await upload_service.delete_file(file_path)
        return {
            "message": "File deleted successfully",
            "data": result
        }
        
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"File deletion failed: {str(e)}"
        )