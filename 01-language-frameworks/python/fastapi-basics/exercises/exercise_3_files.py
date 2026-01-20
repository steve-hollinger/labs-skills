"""Exercise 3: File Upload API

Create an API for uploading and managing files with validation.

Requirements:
1. Create models:
   - FileMetadata: id, filename, content_type, size, upload_time
   - FileUploadResponse: metadata + download_url

2. Implement endpoints:
   - POST /files/upload - Upload a single file
   - POST /files/upload-multiple - Upload multiple files
   - GET /files/ - List all uploaded files
   - GET /files/{file_id} - Get file metadata
   - GET /files/{file_id}/download - Download the file
   - DELETE /files/{file_id} - Delete a file

3. Add validation:
   - File size limit (max 5MB)
   - Allowed file types (images: jpg, png, gif; documents: pdf, txt)
   - File type detection from content (not just extension)

4. Add features:
   - Generate unique file IDs
   - Track upload timestamps
   - Return proper content-type for downloads
   - Support for file metadata (description, tags)

Expected behavior:
    # Upload a file
    POST /files/upload
    Content-Type: multipart/form-data
    file: <image.jpg>
    -> 201 Created, {"id": "abc123", "filename": "image.jpg", ...}

    # List files
    GET /files/?content_type=image
    -> 200 OK, [{"id": "abc123", ...}, ...]

    # Download file
    GET /files/abc123/download
    -> 200 OK, Content-Type: image/jpeg, <binary data>

    # Upload too large file
    POST /files/upload
    file: <huge_file.zip>
    -> 400 Bad Request, {"detail": "File too large. Max size is 5MB"}

Hints:
- Use UploadFile and File from fastapi
- Use uuid4 for generating file IDs
- Store file content in memory (dict) for this exercise
- Check file.content_type for MIME type
- Use await file.read() to get file contents
"""

from datetime import datetime
from typing import Optional
from uuid import uuid4

from fastapi import FastAPI, File, HTTPException, Query, UploadFile, status
from fastapi.responses import Response
from pydantic import BaseModel, Field


# Configuration
MAX_FILE_SIZE = 5 * 1024 * 1024  # 5MB
ALLOWED_IMAGE_TYPES = {"image/jpeg", "image/png", "image/gif"}
ALLOWED_DOCUMENT_TYPES = {"application/pdf", "text/plain"}
ALLOWED_TYPES = ALLOWED_IMAGE_TYPES | ALLOWED_DOCUMENT_TYPES


# TODO: Define your models here
class FileMetadata(BaseModel):
    """File metadata model."""
    pass


class FileUploadResponse(BaseModel):
    """Response after file upload."""
    pass


# Simulated file storage
files_db: dict = {}  # id -> {"metadata": FileMetadata, "content": bytes}


# Create the app
app = FastAPI(title="File Upload API")


# TODO: Implement helper functions
def validate_file(file: UploadFile, content: bytes) -> None:
    """Validate file size and type. Raise HTTPException if invalid."""
    pass


def generate_file_id() -> str:
    """Generate a unique file ID."""
    pass


# TODO: Implement your endpoints here
@app.post("/files/upload", status_code=status.HTTP_201_CREATED)
async def upload_file(
    file: UploadFile = File(...),
    description: str = Query(None, max_length=500),
):
    """Upload a single file."""
    pass


@app.post("/files/upload-multiple", status_code=status.HTTP_201_CREATED)
async def upload_multiple_files(files: list[UploadFile] = File(...)):
    """Upload multiple files."""
    pass


@app.get("/files/")
def list_files(
    content_type: str | None = Query(None, description="Filter by content type prefix"),
):
    """List all uploaded files."""
    pass


@app.get("/files/{file_id}")
def get_file_metadata(file_id: str):
    """Get file metadata."""
    pass


@app.get("/files/{file_id}/download")
def download_file(file_id: str):
    """Download a file."""
    pass


@app.delete("/files/{file_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_file(file_id: str):
    """Delete a file."""
    pass


def test_file_api():
    """Test your File Upload API implementation."""
    from fastapi.testclient import TestClient
    import io

    client = TestClient(app)

    # Create a fake image file
    fake_image = io.BytesIO(b"fake image content")
    fake_image.name = "test.jpg"

    # Test upload
    response = client.post(
        "/files/upload",
        files={"file": ("test.jpg", fake_image, "image/jpeg")},
        data={"description": "Test image"},
    )
    print(f"Upload: {response.status_code}")

    # TODO: Add more tests

    print("\nAll tests passed!")


if __name__ == "__main__":
    test_file_api()
