"""
Exercise 2: Progress Streaming

Create an SSE endpoint that streams progress updates for a long-running task.

Requirements:
1. Create POST /tasks to start a new background task
2. Create GET /tasks/{task_id}/progress to stream progress updates
3. Track task state: pending, running, completed, failed
4. Stream progress percentage and status messages
5. Handle task not found errors

Task simulation:
- Task runs for 10 seconds
- Updates progress every second
- 10% chance of failure for testing error handling

Hints:
- Use FastAPI BackgroundTasks or asyncio.create_task()
- Store task state in a dictionary
- Use event types for different update kinds
"""

from fastapi import FastAPI, BackgroundTasks, HTTPException
from fastapi.responses import StreamingResponse
import asyncio
import json
import uuid
from datetime import datetime

app = FastAPI(title="Progress Streaming Exercise")

# Task storage
tasks = {}


# TODO: Define Task state model
class TaskState:
    """Task state container."""
    def __init__(self):
        self.status = "pending"
        self.progress = 0
        self.message = "Waiting to start"
        self.created_at = datetime.now().isoformat()
        self.completed_at = None
        self.error = None


# TODO: Implement the background task
async def run_task(task_id: str):
    """
    Simulate a long-running task.

    Updates task state as it progresses.
    Should update progress from 0-100 over ~10 seconds.
    10% chance of failure for testing.
    """
    # TODO: Implement
    # 1. Set status to "running"
    # 2. Loop through steps, updating progress
    # 3. Include random failure chance
    # 4. Set status to "completed" or "failed" at end
    pass


# TODO: Implement progress generator
async def progress_generator(task_id: str):
    """
    Generate SSE events for task progress.

    Args:
        task_id: The task to monitor

    Yields:
        SSE formatted progress updates
    """
    # TODO: Implement
    # 1. Check task exists
    # 2. Poll task state and yield updates
    # 3. Use different event types: progress, completed, failed
    # 4. End when task completes or fails
    pass


# TODO: Create task endpoint
@app.post("/tasks")
async def create_task(background_tasks: BackgroundTasks):
    """
    Create and start a new task.

    Returns the task ID for tracking.
    """
    # TODO: Implement
    # 1. Generate unique task ID
    # 2. Create TaskState and store
    # 3. Add run_task to background_tasks
    # 4. Return task_id
    pass


# TODO: Create progress streaming endpoint
@app.get("/tasks/{task_id}/progress")
async def task_progress(task_id: str):
    """
    Stream progress updates for a task.

    Returns SSE stream of progress events.
    """
    # TODO: Implement
    # 1. Check task exists (404 if not)
    # 2. Return StreamingResponse with progress_generator
    pass


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
        "message": task.message
    }


@app.get("/")
async def info():
    return {
        "exercise": "Progress Streaming",
        "endpoints": {
            "POST /tasks": "Create new task",
            "GET /tasks/{id}/progress": "Stream progress",
            "GET /tasks/{id}": "Get task state"
        }
    }


# Test your implementation
if __name__ == "__main__":
    import uvicorn

    print("Exercise 2: Progress Streaming")
    print("=" * 50)
    print("\nTest sequence:")
    print('  1. Create task: curl -X POST "http://localhost:8011/tasks"')
    print('  2. Stream progress: curl -N "http://localhost:8011/tasks/{id}/progress"')
    print("\nExpected events:")
    print('  event: progress')
    print('  data: {"progress": 10, "message": "Step 1/10"}')
    print('  ')
    print('  event: completed')
    print('  data: {"message": "Task finished"}')

    uvicorn.run(app, host="0.0.0.0", port=8011)
