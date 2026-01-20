"""
Exercise 2: Build a Tool-Using Agent

Create an agent that uses function calling to help users with tasks
in a specific domain (e.g., task management, file operations, or data lookup).

Requirements:
1. Define at least 3 tools with proper JSON schemas
2. Implement the actual tool functions
3. Handle tool calls and return results
4. Support multi-turn conversations with tool results
5. Handle cases where no tool is needed

Domain: Task Management
Tools to implement:
- create_task(title, description, priority)
- list_tasks(status_filter)
- update_task_status(task_id, new_status)

Hints:
- Use an in-memory dictionary to store tasks
- Tools need clear descriptions for the model
- Handle the full tool calling loop
"""

import os
import json
from datetime import datetime
from dotenv import load_dotenv

load_dotenv()


# In-memory task storage
TASKS = {}
NEXT_ID = 1


# TODO: Implement tool functions

def create_task(title: str, description: str = "", priority: str = "medium") -> dict:
    """Create a new task.

    Args:
        title: Task title
        description: Task description (optional)
        priority: Priority level (low, medium, high)

    Returns:
        Created task details
    """
    # TODO: Implement task creation
    # - Generate unique ID
    # - Store task in TASKS dict
    # - Return task details including id, created_at
    pass


def list_tasks(status_filter: str = None) -> dict:
    """List all tasks, optionally filtered by status.

    Args:
        status_filter: Optional status to filter by (pending, in_progress, completed)

    Returns:
        List of tasks matching the filter
    """
    # TODO: Implement task listing
    # - Filter by status if provided
    # - Return list of tasks
    pass


def update_task_status(task_id: int, new_status: str) -> dict:
    """Update the status of a task.

    Args:
        task_id: ID of the task to update
        new_status: New status (pending, in_progress, completed)

    Returns:
        Updated task details or error
    """
    # TODO: Implement status update
    # - Find task by ID
    # - Update status
    # - Return updated task or error if not found
    pass


# TODO: Define tool schemas
TOOLS = [
    # {
    #     "type": "function",
    #     "function": {
    #         "name": "create_task",
    #         "description": "...",
    #         "parameters": {...}
    #     }
    # },
    # ... define all three tools
]


# Map function names to implementations
TOOL_FUNCTIONS = {
    "create_task": create_task,
    "list_tasks": list_tasks,
    "update_task_status": update_task_status,
}


class TaskAgent:
    """An agent that helps manage tasks using function calling."""

    def __init__(self):
        """Initialize the task agent."""
        # TODO: Initialize OpenAI client
        # Store conversation history
        pass

    def process(self, user_message: str) -> str:
        """Process a user message, handling any tool calls.

        Args:
            user_message: The user's request

        Returns:
            The agent's response
        """
        # TODO: Implement the full tool calling loop
        # 1. Add user message to history
        # 2. Call API with tools
        # 3. If tool_calls:
        #    a. Execute each tool
        #    b. Add tool results to messages
        #    c. Call API again for final response
        # 4. Return final response
        pass


# Test your implementation
if __name__ == "__main__":
    print("Testing Task Agent Implementation")
    print("=" * 50)

    agent = TaskAgent()

    test_queries = [
        "Create a task called 'Review PR' with high priority",
        "Add a task to 'Update documentation' with description 'Add API examples'",
        "Show me all my tasks",
        "Mark task 1 as completed",
        "What tasks are still pending?",
        "Create a low priority task to 'Clean up code'",
        "List all completed tasks",
    ]

    for query in test_queries:
        print(f"\nUser: {query}")
        response = agent.process(query)
        print(f"Agent: {response}" if response else "Agent: [Not implemented]")

    print("\n" + "=" * 50)
    print(f"Total tasks created: {len(TASKS)}")
    print("\nAll tasks:")
    for task_id, task in TASKS.items():
        print(f"  [{task_id}] {task.get('title', 'Unknown')} - {task.get('status', 'Unknown')}")
