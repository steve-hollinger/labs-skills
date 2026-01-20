"""Exercise 2 Solution: Progress Reporter.

This solution demonstrates streaming progress updates for a
simulated file processing operation.
"""

import asyncio
import random
from typing import AsyncGenerator
from uuid import uuid4

from fastapi import FastAPI
from fastapi.responses import StreamingResponse
from pydantic import BaseModel

app = FastAPI(title="Exercise 2 Solution: Progress Reporter")


class ProcessRequest(BaseModel):
    """Request model for file processing."""

    filename: str
    size_mb: float


class ProgressEvent(BaseModel):
    """Progress event model."""

    task_id: str
    status: str
    progress: float
    message: str
    bytes_processed: int | None = None


async def process_file(
    task_id: str,
    filename: str,
    size_mb: float,
    simulate_failure: bool = False,
) -> AsyncGenerator[str, None]:
    """Stream progress updates for file processing.

    Args:
        task_id: Unique task identifier.
        filename: Name of file being processed.
        size_mb: Size of file in megabytes.
        simulate_failure: If True, may randomly fail.

    Yields:
        SSE-formatted progress events.
    """
    total_bytes = int(size_mb * 1024 * 1024)
    processing_speed_mbps = 10  # MB per second
    total_time = size_mb / processing_speed_mbps

    # Send starting event
    start_event = ProgressEvent(
        task_id=task_id,
        status="starting",
        progress=0.0,
        message=f"Starting to process {filename}",
        bytes_processed=0,
    )
    yield f"data: {start_event.model_dump_json()}\n\n"

    # Calculate update interval (10% increments or 1 second, whichever is shorter)
    update_interval = min(total_time / 10, 1.0)
    updates_needed = max(10, int(total_time / update_interval))

    try:
        for i in range(1, updates_needed + 1):
            # Simulate random failure (bonus feature)
            if simulate_failure and random.random() < 0.1:
                error_event = ProgressEvent(
                    task_id=task_id,
                    status="failed",
                    progress=i / updates_needed,
                    message=f"Error processing {filename}: Simulated failure",
                    bytes_processed=int(total_bytes * i / updates_needed),
                )
                yield f"event: error\ndata: {error_event.model_dump_json()}\n\n"
                return

            await asyncio.sleep(update_interval)

            progress = i / updates_needed
            bytes_done = int(total_bytes * progress)

            event = ProgressEvent(
                task_id=task_id,
                status="processing",
                progress=progress,
                message=f"Processing {filename}: {int(progress * 100)}% complete",
                bytes_processed=bytes_done,
            )
            yield f"data: {event.model_dump_json()}\n\n"

        # Send completion event
        complete_event = ProgressEvent(
            task_id=task_id,
            status="completed",
            progress=1.0,
            message=f"Successfully processed {filename}",
            bytes_processed=total_bytes,
        )
        yield f"event: complete\ndata: {complete_event.model_dump_json()}\n\n"

    except asyncio.CancelledError:
        # Handle client disconnect
        cancelled_event = ProgressEvent(
            task_id=task_id,
            status="cancelled",
            progress=i / updates_needed if "i" in dir() else 0.0,
            message="Processing cancelled by client",
        )
        yield f"event: cancelled\ndata: {cancelled_event.model_dump_json()}\n\n"
        raise


@app.post("/process")
async def process_endpoint(request: ProcessRequest):
    """Process a file with streaming progress updates.

    Args:
        request: Processing request with filename and size.

    Returns:
        StreamingResponse with progress events.
    """
    task_id = str(uuid4())

    return StreamingResponse(
        process_file(task_id, request.filename, request.size_mb),
        media_type="text/event-stream",
        headers={
            "Cache-Control": "no-cache",
            "X-Task-ID": task_id,
        },
    )


# Bonus: Endpoint with failure simulation
@app.post("/process/risky")
async def process_risky_endpoint(request: ProcessRequest):
    """Process with potential random failures.

    Args:
        request: Processing request.

    Returns:
        StreamingResponse that may include failure events.
    """
    task_id = str(uuid4())

    return StreamingResponse(
        process_file(task_id, request.filename, request.size_mb, simulate_failure=True),
        media_type="text/event-stream",
        headers={
            "Cache-Control": "no-cache",
            "X-Task-ID": task_id,
        },
    )


# Bonus: Batch processing multiple files
class BatchProcessRequest(BaseModel):
    """Request for processing multiple files."""

    files: list[ProcessRequest]


@app.post("/process/batch")
async def batch_process_endpoint(request: BatchProcessRequest):
    """Process multiple files with combined progress stream.

    Args:
        request: Batch of files to process.

    Returns:
        StreamingResponse with progress for all files.
    """
    async def batch_generator() -> AsyncGenerator[str, None]:
        total_files = len(request.files)

        for idx, file_req in enumerate(request.files):
            task_id = str(uuid4())

            # Send file start event
            file_start = {
                "type": "file_start",
                "file_index": idx,
                "total_files": total_files,
                "filename": file_req.filename,
                "task_id": task_id,
            }
            yield f"event: file_start\ndata: {file_start}\n\n"

            # Stream progress for this file
            async for event in process_file(task_id, file_req.filename, file_req.size_mb):
                yield event

        # Send batch complete event
        batch_complete = {
            "type": "batch_complete",
            "total_files": total_files,
            "message": "All files processed",
        }
        yield f"event: batch_complete\ndata: {batch_complete}\n\n"

    return StreamingResponse(
        batch_generator(),
        media_type="text/event-stream",
    )


if __name__ == "__main__":
    import uvicorn

    uvicorn.run(app, host="0.0.0.0", port=8000)
