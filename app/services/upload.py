import os
import uuid
from typing import Optional, Dict, Any
from fastapi import HTTPException, UploadFile
from supabase import create_client, Client
from PIL import Image
import io

class UploadService:
    def __init__(self):
        supabase_url = "https://bkvxbuidvwbqpqpxjwqf.supabase.co"
        supabase_key = os.getenv("SUPABASE_ANON_KEY")
        
        if not supabase_key:
            print("Warning: SUPABASE_ANON_KEY not set. Upload functionality will be limited.")
            supabase_key = "placeholder_key"
        
        try:
            self.supabase: Client = create_client(supabase_url, supabase_key)
            self.bucket_name = "uploads"
            self._ensure_bucket_exists()
        except Exception as e:
            print(f"Warning: Could not initialize Supabase client: {e}")
            self.supabase = None
    
    def _ensure_bucket_exists(self):
        try:
            # Try to create the bucket (will fail if it already exists, which is fine)
            self.supabase.storage.create_bucket(self.bucket_name, {"public": True})
            print(f"Created bucket: {self.bucket_name}")
        except Exception:
            # Bucket probably already exists
            pass
    
    def _validate_file_size(self, file: UploadFile, max_size_mb: int = 10) -> None:
        file.file.seek(0, 2)
        file_size = file.file.tell()
        file.file.seek(0)
        
        max_size_bytes = max_size_mb * 1024 * 1024
        if file_size > max_size_bytes:
            raise HTTPException(
                status_code=413,
                detail=f"File size exceeds {max_size_mb}MB limit"
            )
    
    def _validate_image(self, file: UploadFile) -> None:
        allowed_formats = {'image/jpeg', 'image/png', 'image/jpg', 'image/webp'}
        
        if file.content_type not in allowed_formats:
            raise HTTPException(
                status_code=400,
                detail="Invalid image format. Allowed: JPEG, PNG, WebP"
            )
        
        try:
            file_content = file.file.read()
            file.file.seek(0)
            
            image = Image.open(io.BytesIO(file_content))
            image.verify()
        except Exception:
            raise HTTPException(
                status_code=400,
                detail="Invalid or corrupted image file"
            )
    
    def _validate_audio(self, file: UploadFile) -> None:
        allowed_formats = {
            'audio/mpeg', 'audio/mp3', 'audio/wav', 'audio/x-wav',
            'audio/mp4', 'audio/m4a', 'audio/ogg', 'audio/webm'
        }
        
        if file.content_type not in allowed_formats:
            raise HTTPException(
                status_code=400,
                detail="Invalid audio format. Allowed: MP3, WAV, M4A, OGG, WebM"
            )
    
    async def upload_file(
        self, 
        file: UploadFile, 
        file_type: str, 
        folder: str = "general"
    ) -> Dict[str, Any]:
        try:
            if not self.supabase:
                raise HTTPException(
                    status_code=503,
                    detail="Supabase client not initialized. Please check SUPABASE_ANON_KEY"
                )
            
            if file_type == "image":
                self._validate_image(file)
                self._validate_file_size(file, max_size_mb=5)
            elif file_type == "audio":
                self._validate_audio(file)
                self._validate_file_size(file, max_size_mb=20)
            else:
                raise HTTPException(status_code=400, detail="Invalid file type")
            
            file_extension = file.filename.split('.')[-1] if '.' in file.filename else ''
            unique_filename = f"{folder}/{uuid.uuid4()}.{file_extension}"
            
            file_content = await file.read()
            
            result = self.supabase.storage.from_(self.bucket_name).upload(
                unique_filename,
                file_content,
                {
                    "content-type": file.content_type,
                    "cache-control": "3600"
                }
            )
            
            if hasattr(result, 'error') and result.error:
                raise HTTPException(
                    status_code=500,
                    detail=f"Upload failed: {result.error}"
                )
            
            public_url = self.supabase.storage.from_(self.bucket_name).get_public_url(unique_filename)
            
            return {
                "success": True,
                "file_url": public_url,
                "file_path": unique_filename,
                "file_size": len(file_content),
                "content_type": file.content_type,
                "original_filename": file.filename
            }
            
        except HTTPException:
            raise
        except Exception as e:
            raise HTTPException(
                status_code=500,
                detail=f"Upload error: {str(e)}"
            )
    
    async def delete_file(self, file_path: str) -> Dict[str, Any]:
        try:
            result = self.supabase.storage.from_(self.bucket_name).remove([file_path])
            
            if hasattr(result, 'error') and result.error:
                raise HTTPException(
                    status_code=500,
                    detail=f"Delete failed: {result.error}"
                )
            
            return {"success": True, "message": "File deleted successfully"}
            
        except HTTPException:
            raise
        except Exception as e:
            raise HTTPException(
                status_code=500,
                detail=f"Delete error: {str(e)}"
            )

upload_service = UploadService()