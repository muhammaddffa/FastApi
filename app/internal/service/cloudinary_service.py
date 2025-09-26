import cloudinary
import cloudinary.uploader
import cloudinary.api
from typing import Optional, Dict, Any
from fastapi import HTTPException, status, UploadFile
import uuid
import os
from pathlib import Path

class CloudinaryService:
    def __init__(self):
        # Configure Cloudinary (ambil dari environment variables)
        cloudinary.config(
            cloud_name=os.getenv("CLOUDINARY_CLOUD_NAME"),
            api_key=os.getenv("CLOUDINARY_API_KEY"),
            api_secret=os.getenv("CLOUDINARY_API_SECRET"),
            secure=True
        )
        
    async def upload_employee_photo(
        self, 
        file: UploadFile, 
        employee_id: str,
        folder: str = "intern"
    ) -> Dict[str, Any]:
        try:
            # Validate file type
            allowed_types = ["image/jpeg", "image/png", "image/jpg", "image/webp"]
            if file.content_type not in allowed_types:
                raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    detail="Only JPEG, PNG, and WebP images are allowed"
                )
            
            # Validate file size (10MB max untuk Cloudinary)
            if file.size and file.size > 10 * 1024 * 1024:
                raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    detail="File size must be less than 10MB"
                )
            
            # Generate unique public_id
            unique_id = f"{employee_id}_{uuid.uuid4().hex}"
            public_id = f"{folder}/{unique_id}"
            
            # Read file content
            file_content = await file.read()
            
            # Upload to Cloudinary
            upload_result = cloudinary.uploader.upload(
                file_content,
                public_id=public_id,
                folder=folder,
                overwrite=True,  # Replace if exists
                resource_type="image",
                # Transformations for optimization
                transformation=[
                    {"width": 400, "height": 400, "crop": "fill", "quality": "auto"},
                    {"format": "webp"}  # Convert to WebP for better compression
                ]
            )
            
            return {
                "url": upload_result.get("secure_url"),
                "public_id": upload_result.get("public_id"),
                "width": upload_result.get("width"),
                "height": upload_result.get("height"),
                "format": upload_result.get("format"),
                "bytes": upload_result.get("bytes")
            }
            
        except cloudinary.exceptions.Error as e:
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail=f"Cloudinary upload failed: {str(e)}"
            )
        except Exception as e:
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail=f"Photo upload failed: {str(e)}"
            )
    
    async def delete_employee_photo(self, public_id: str) -> bool:
        # Delete photo from Cloudinary
        try:
            result = cloudinary.uploader.destroy(public_id)
            return result.get("result") == "ok"
        except Exception as e:
            print(f"Failed to delete photo from Cloudinary: {e}")
            return False
    
    def extract_public_id_from_url(self, url: str) -> Optional[str]:
        # Extract public_id from Cloudinary URL
        try:
            # Format Cloudinary URL: https://res.cloudinary.com/{cloud_name}/image/upload/v{version}/{public_id}.{format}
            if "res.cloudinary.com" in url:
                # Split URL and get public_id part
                parts = url.split("/")
                if len(parts) >= 7:
                    # Get everything after "/upload/" and remove file extension
                    upload_index = parts.index("upload")
                    public_id_with_ext = "/".join(parts[upload_index + 2:])  # Skip version
                    # Remove file extension
                    public_id = public_id_with_ext.rsplit(".", 1)[0]
                    return public_id
            return None
        except Exception:
            return None