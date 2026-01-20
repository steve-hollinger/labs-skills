"""Solution for Exercise 3: File Upload API

This is the reference solution for the file upload exercise.
"""

from datetime import datetime
from uuid import uuid4

from fastapi import FastAPI, File, HTTPException, Query, UploadFile, status
from fastapi.responses import Response
from fastapi.testclient import TestClient
from pydantic import BaseModel, Field


# Configuration
MAX_FILE_SIZE = 5 * 1024 * 1024  # 5MB
ALLOWED_IMAGE_TYPES = {"image/jpeg", "image/png", "image/gif"}
ALLOWED_DOCUMENT_TYPES = {"application/pdf", "text/plain"}
ALLOWED_TYPES = ALLOWED_IMAGE_TYPES | ALLOWED_DOCUMENT_TYPES


# Models
class FileMetadata(BaseModel):
    """File metadata model."""

    id: str
    filename: str
    content_type: str
    size: int
    description: str | None
    upload_time: datetime

    model_config = {"from_attributes": True}


class FileUploadResponse(BaseModel):
    """Response after file upload."""

    metadata: FileMetadata
    download_url: str


class FileListResponse(BaseModel):
    """List of files."""

    files: list[FileMetadata]
    total: int


# Simulated file storage
files_db: dict[str, dict] = {}  # id -> {"metadata": dict, "content": bytes}


# Create the app
app = FastAPI(
    title="File Upload API",
    description="API for uploading and managing files",
    version="1.0.0",
)


# Helper functions
def validate_file(file: UploadFile, content: bytes) -> None:
    """Validate file size and type. Raise HTTPException if invalid."""
    # Check size
    if len(content) > MAX_FILE_SIZE:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"File too large. Max size is {MAX_FILE_SIZE // (1024 * 1024)}MB",
        )

    # Check type
    if file.content_type not in ALLOWED_TYPES:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"File type '{file.content_type}' not allowed. "
            f"Allowed types: {', '.join(ALLOWED_TYPES)}",
        )


def generate_file_id() -> str:
    """Generate a unique file ID."""
    return str(uuid4())[:8]


def get_file_or_404(file_id: str) -> dict:
    """Get file from storage or raise 404."""
    if file_id not in files_db:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"File {file_id} not found",
        )
    return files_db[file_id]


@app.post("/files/upload", response_model=FileUploadResponse, status_code=status.HTTP_201_CREATED)
async def upload_file(
    file: UploadFile = File(...),
    description: str | None = Query(None, max_length=500),
):
    """Upload a single file."""
    # Read content
    content = await file.read()

    # Validate
    validate_file(file, content)

    # Generate ID and store
    file_id = generate_file_id()
    metadata = {
        "id": file_id,
        "filename": file.filename,
        "content_type": file.content_type,
        "size": len(content),
        "description": description,
        "upload_time": datetime.now(),
    }

    files_db[file_id] = {
        "metadata": metadata,
        "content": content,
    }

    return FileUploadResponse(
        metadata=FileMetadata(**metadata),
        download_url=f"/files/{file_id}/download",
    )


@app.post(
    "/files/upload-multiple",
    response_model=list[FileUploadResponse],
    status_code=status.HTTP_201_CREATED,
)
async def upload_multiple_files(files: list[UploadFile] = File(...)):
    """Upload multiple files."""
    results = []

    for file in files:
        content = await file.read()
        validate_file(file, content)

        file_id = generate_file_id()
        metadata = {
            "id": file_id,
            "filename": file.filename,
            "content_type": file.content_type,
            "size": len(content),
            "description": None,
            "upload_time": datetime.now(),
        }

        files_db[file_id] = {
            "metadata": metadata,
            "content": content,
        }

        results.append(
            FileUploadResponse(
                metadata=FileMetadata(**metadata),
                download_url=f"/files/{file_id}/download",
            )
        )

    return results


@app.get("/files/", response_model=FileListResponse)
def list_files(
    content_type: str | None = Query(None, description="Filter by content type prefix"),
    skip: int = Query(0, ge=0),
    limit: int = Query(10, ge=1, le=100),
):
    """List all uploaded files."""
    files = [f["metadata"] for f in files_db.values()]

    # Filter by content type
    if content_type:
        files = [f for f in files if f["content_type"].startswith(content_type)]

    total = len(files)

    # Paginate
    files = files[skip : skip + limit]

    return FileListResponse(files=files, total=total)


@app.get("/files/{file_id}", response_model=FileMetadata)
def get_file_metadata(file_id: str):
    """Get file metadata."""
    file_data = get_file_or_404(file_id)
    return FileMetadata(**file_data["metadata"])


@app.get("/files/{file_id}/download")
def download_file(file_id: str):
    """Download a file."""
    file_data = get_file_or_404(file_id)

    return Response(
        content=file_data["content"],
        media_type=file_data["metadata"]["content_type"],
        headers={
            "Content-Disposition": f'attachment; filename="{file_data["metadata"]["filename"]}"'
        },
    )


@app.delete("/files/{file_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_file(file_id: str):
    """Delete a file."""
    get_file_or_404(file_id)  # Check exists
    del files_db[file_id]


def test_file_api():
    """Test the File Upload API implementation."""
    global files_db
    files_db = {}

    client = TestClient(app)
    print("Testing File Upload API...")

    # Test 1: Upload a file
    response = client.post(
        "/files/upload",
        files={"file": ("test.jpg", b"fake image content", "image/jpeg")},
        data={"description": "Test image"},
    )
    assert response.status_code == 201
    data = response.json()
    assert "metadata" in data
    assert data["metadata"]["filename"] == "test.jpg"
    assert data["metadata"]["content_type"] == "image/jpeg"
    file_id = data["metadata"]["id"]
    print("  Test 1 passed: File upload")

    # Test 2: Get file metadata
    response = client.get(f"/files/{file_id}")
    assert response.status_code == 200
    assert response.json()["filename"] == "test.jpg"
    print("  Test 2 passed: Get file metadata")

    # Test 3: Download file
    response = client.get(f"/files/{file_id}/download")
    assert response.status_code == 200
    assert response.content == b"fake image content"
    assert response.headers["content-type"] == "image/jpeg"
    print("  Test 3 passed: Download file")

    # Test 4: List files
    response = client.get("/files/")
    assert response.status_code == 200
    assert response.json()["total"] == 1
    print("  Test 4 passed: List files")

    # Test 5: Filter by content type
    # Upload a PDF
    client.post(
        "/files/upload",
        files={"file": ("doc.pdf", b"fake pdf content", "application/pdf")},
    )

    response = client.get("/files/?content_type=image")
    assert response.status_code == 200
    assert response.json()["total"] == 1
    assert response.json()["files"][0]["content_type"] == "image/jpeg"
    print("  Test 5 passed: Filter by content type")

    # Test 6: Upload multiple files
    response = client.post(
        "/files/upload-multiple",
        files=[
            ("files", ("file1.jpg", b"content1", "image/jpeg")),
            ("files", ("file2.png", b"content2", "image/png")),
        ],
    )
    assert response.status_code == 201
    assert len(response.json()) == 2
    print("  Test 6 passed: Upload multiple files")

    # Test 7: File too large
    large_content = b"x" * (MAX_FILE_SIZE + 1)
    response = client.post(
        "/files/upload",
        files={"file": ("large.jpg", large_content, "image/jpeg")},
    )
    assert response.status_code == 400
    assert "too large" in response.json()["detail"].lower()
    print("  Test 7 passed: Reject large file")

    # Test 8: Invalid file type
    response = client.post(
        "/files/upload",
        files={"file": ("script.exe", b"malicious", "application/x-executable")},
    )
    assert response.status_code == 400
    assert "not allowed" in response.json()["detail"].lower()
    print("  Test 8 passed: Reject invalid file type")

    # Test 9: Delete file
    response = client.delete(f"/files/{file_id}")
    assert response.status_code == 204
    response = client.get(f"/files/{file_id}")
    assert response.status_code == 404
    print("  Test 9 passed: Delete file")

    # Test 10: Get non-existent file
    response = client.get("/files/nonexistent")
    assert response.status_code == 404
    print("  Test 10 passed: 404 for non-existent file")

    print("\nAll tests passed!")


if __name__ == "__main__":
    test_file_api()
