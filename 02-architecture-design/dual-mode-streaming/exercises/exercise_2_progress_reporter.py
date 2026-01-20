"""Exercise 2: Build a Progress Reporter.

In this exercise, you'll create a streaming endpoint that reports progress
for a simulated file upload/processing operation.

Requirements:
1. Create a POST endpoint at /process
2. Accept a JSON body with 'filename' and 'size_mb' fields
3. Stream progress updates as SSE events
4. Progress events should include:
   - task_id: unique identifier for the task
   - status: "starting", "processing", "completed", or "failed"
   - progress: float from 0.0 to 1.0
   - message: human-readable status message
   - bytes_processed: (optional) bytes processed so far
5. Simulate processing at 10 MB per second
6. Send updates every 10% of progress

Example SSE output:
    data: {"task_id": "abc123", "status": "starting", "progress": 0.0, "message": "Starting..."}

    data: {"task_id": "abc123", "status": "processing", "progress": 0.1, "message": "10% complete"}

    ... more updates ...

    data: {"task_id": "abc123", "status": "completed", "progress": 1.0, "message": "Done!"}

Run your solution with:
    uvicorn exercises.exercise_2_progress_reporter:app --reload

Test with:
    curl -X POST localhost:8000/process \\
        -H "Content-Type: application/json" \\
        -d '{"filename": "data.csv", "size_mb": 50}'
"""

import asyncio
from typing import AsyncGenerator
from uuid import uuid4

from fastapi import FastAPI
from pydantic import BaseModel

app = FastAPI(title="Exercise 2: Progress Reporter")


class ProcessRequest(BaseModel):
    """Request model for file processing."""

    filename: str
    size_mb: float


class ProgressEvent(BaseModel):
    """Progress event model."""

    task_id: str
    status: str  # "starting", "processing", "completed", "failed"
    progress: float  # 0.0 to 1.0
    message: str
    bytes_processed: int | None = None


# TODO: Implement the progress streaming generator
async def process_file(
    task_id: str,
    filename: str,
    size_mb: float,
) -> AsyncGenerator[str, None]:
    """Stream progress updates for file processing.

    Args:
        task_id: Unique task identifier.
        filename: Name of file being processed.
        size_mb: Size of file in megabytes.

    Yields:
        SSE-formatted progress events.

    Hints:
    - Calculate total bytes: size_mb * 1024 * 1024
    - Processing speed: 10 MB/second
    - Send update every 10% (or every second, whichever is more frequent)
    - Use ProgressEvent model and call .model_dump_json()
    - Remember SSE format: f"data: {json_string}\\n\\n"
    """
    # Your implementation here
    raise NotImplementedError("Implement the progress generator")


# TODO: Implement the /process endpoint
@app.post("/process")
async def process_endpoint(request: ProcessRequest):
    """Process a file with streaming progress updates.

    Args:
        request: Processing request with filename and size.

    Returns:
        StreamingResponse with progress events.
    """
    # Your implementation here
    # 1. Generate a task_id
    # 2. Return StreamingResponse with process_file generator
    raise NotImplementedError("Implement this endpoint")


# Bonus Challenge: Add error handling
# - Simulate random failures (10% chance)
# - On failure, send an error event with status="failed"
# - Include error message in the event


if __name__ == "__main__":
    import uvicorn

    uvicorn.run(app, host="0.0.0.0", port=8000)
