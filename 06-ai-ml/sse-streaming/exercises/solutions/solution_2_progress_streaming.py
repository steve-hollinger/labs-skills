"""
Solution 2: Progress Streaming

Complete implementation of progress streaming for background tasks.
"""

import json
import asyncio
import uuid
import random
from datetime import datetime
from fastapi import FastAPI, BackgroundTasks, HTTPException
from fastapi.responses import StreamingResponse

app = FastAPI(title="Progress Streaming Solution")

# Task storage
tasks = {}


class TaskState:
    """Task state container."""
    def __init__(self):
        self.status = "pending"
        self.progress = 0
        self.message = "Waiting to start"
        self.created_at = datetime.now().isoformat()
        self.completed_at = None
        self.error = None


async def run_task(task_id: str):
    """Simulate a long-running task with progress updates."""
    task = tasks[task_id]
    task.status = "running"
    task.message = "Starting task..."

    try:
        steps = 10
        for i in range(steps):
            # 10% chance of failure for testing
            if random.random() < 0.1:
                raise Exception(f"Simulated failure at step {i + 1}")

            progress = int((i + 1) / steps * 100)
            task.progress = progress
            task.message = f"Processing step {i + 1}/{steps}"

            await asyncio.sleep(1)

        task.status = "completed"
        task.progress = 100
        task.message = "Task completed successfully"
        task.completed_at = datetime.now().isoformat()

    except Exception as e:
        task.status = "failed"
        task.error = str(e)
        task.message = f"Task failed: {e}"
        task.completed_at = datetime.now().isoformat()


async def progress_generator(task_id: str):
    """Generate SSE events for task progress."""
    if task_id not in tasks:
        error = json.dumps({"error": "Task not found"})
        yield f"event: error\ndata: {error}\n\n"
        return

    task = tasks[task_id]
    last_progress = -1

    # Send initial state
    initial = json.dumps({
        "status": task.status,
        "progress": task.progress,
        "message": task.message
    })
    yield f"event: status\ndata: {initial}\n\n"

    while True:
        # Check for progress update
        if task.progress != last_progress:
            last_progress = task.progress
            update = json.dumps({
                "progress": task.progress,
                "message": task.message,
                "status": task.status
            })
            yield f"event: progress\ndata: {update}\n\n"

        # Check for completion
        if task.status == "completed":
            complete = json.dumps({
                "status": "completed",
                "message": task.message,
                "completed_at": task.completed_at
            })
            yield f"event: completed\ndata: {complete}\n\n"
            break

        # Check for failure
        if task.status == "failed":
            failed = json.dumps({
                "status": "failed",
                "error": task.error,
                "message": task.message
            })
            yield f"event: failed\ndata: {failed}\n\n"
            break

        await asyncio.sleep(0.5)

    yield "data: [DONE]\n\n"


@app.post("/tasks")
async def create_task(background_tasks: BackgroundTasks):
    """Create and start a new task."""
    task_id = str(uuid.uuid4())
    tasks[task_id] = TaskState()

    # Start the background task
    background_tasks.add_task(run_task, task_id)

    return {
        "task_id": task_id,
        "status": "created",
        "progress_url": f"/tasks/{task_id}/progress"
    }


@app.get("/tasks/{task_id}/progress")
async def task_progress(task_id: str):
    """Stream progress updates for a task."""
    if task_id not in tasks:
        raise HTTPException(status_code=404, detail="Task not found")

    return StreamingResponse(
        progress_generator(task_id),
        media_type="text/event-stream",
        headers={
            "Cache-Control": "no-cache",
            "Connection": "keep-alive",
            "X-Accel-Buffering": "no",
        }
    )


@app.get("/tasks/{task_id}")
async def get_task(task_id: str):
    """Get current task state."""
    if task_id not in tasks:
        raise HTTPException(status_code=404, detail="Task not found")

    task = tasks[task_id]
    return {
        "task_id": task_id,
        "status": task.status,
        "progress": task.progress,
        "message": task.message,
        "created_at": task.created_at,
        "completed_at": task.completed_at,
        "error": task.error
    }


@app.get("/tasks")
async def list_tasks():
    """List all tasks."""
    return {
        "count": len(tasks),
        "tasks": [
            {"task_id": tid, "status": t.status, "progress": t.progress}
            for tid, t in tasks.items()
        ]
    }


@app.get("/")
async def info():
    return {
        "solution": "Progress Streaming",
        "endpoints": {
            "POST /tasks": "Create new task",
            "GET /tasks/{id}/progress": "Stream progress",
            "GET /tasks/{id}": "Get task state",
            "GET /tasks": "List all tasks"
        }
    }


if __name__ == "__main__":
    import uvicorn
    print("Solution 2: Progress Streaming")
    print("=" * 50)
    print('Create: curl -X POST "http://localhost:8011/tasks"')
    print('Stream: curl -N "http://localhost:8011/tasks/{id}/progress"')
    uvicorn.run(app, host="0.0.0.0", port=8011)
