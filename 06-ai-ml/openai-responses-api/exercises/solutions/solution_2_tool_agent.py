"""
Solution 2: Tool-Using Agent for Task Management

A complete implementation of a task management agent using function calling.
"""

import os
import json
from datetime import datetime
from dotenv import load_dotenv

load_dotenv()


# In-memory task storage
TASKS = {}
NEXT_ID = 1


def create_task(title: str, description: str = "", priority: str = "medium") -> dict:
    """Create a new task."""
    global NEXT_ID

    task = {
        "id": NEXT_ID,
        "title": title,
        "description": description,
        "priority": priority,
        "status": "pending",
        "created_at": datetime.now().isoformat()
    }

    TASKS[NEXT_ID] = task
    NEXT_ID += 1

    return {
        "success": True,
        "message": f"Task '{title}' created successfully",
        "task": task
    }


def list_tasks(status_filter: str = None) -> dict:
    """List all tasks, optionally filtered by status."""
    tasks = list(TASKS.values())

    if status_filter:
        tasks = [t for t in tasks if t["status"] == status_filter]

    return {
        "success": True,
        "count": len(tasks),
        "tasks": tasks,
        "filter_applied": status_filter
    }


def update_task_status(task_id: int, new_status: str) -> dict:
    """Update the status of a task."""
    if task_id not in TASKS:
        return {
            "success": False,
            "error": f"Task with ID {task_id} not found"
        }

    valid_statuses = ["pending", "in_progress", "completed"]
    if new_status not in valid_statuses:
        return {
            "success": False,
            "error": f"Invalid status. Must be one of: {valid_statuses}"
        }

    TASKS[task_id]["status"] = new_status
    TASKS[task_id]["updated_at"] = datetime.now().isoformat()

    return {
        "success": True,
        "message": f"Task {task_id} status updated to '{new_status}'",
        "task": TASKS[task_id]
    }


# Tool definitions
TOOLS = [
    {
        "type": "function",
        "function": {
            "name": "create_task",
            "description": "Create a new task with a title, optional description, and priority level",
            "parameters": {
                "type": "object",
                "properties": {
                    "title": {
                        "type": "string",
                        "description": "The title of the task"
                    },
                    "description": {
                        "type": "string",
                        "description": "Optional detailed description of the task"
                    },
                    "priority": {
                        "type": "string",
                        "enum": ["low", "medium", "high"],
                        "description": "Priority level of the task"
                    }
                },
                "required": ["title"]
            }
        }
    },
    {
        "type": "function",
        "function": {
            "name": "list_tasks",
            "description": "List all tasks, optionally filtered by status",
            "parameters": {
                "type": "object",
                "properties": {
                    "status_filter": {
                        "type": "string",
                        "enum": ["pending", "in_progress", "completed"],
                        "description": "Filter tasks by status"
                    }
                }
            }
        }
    },
    {
        "type": "function",
        "function": {
            "name": "update_task_status",
            "description": "Update the status of an existing task",
            "parameters": {
                "type": "object",
                "properties": {
                    "task_id": {
                        "type": "integer",
                        "description": "The ID of the task to update"
                    },
                    "new_status": {
                        "type": "string",
                        "enum": ["pending", "in_progress", "completed"],
                        "description": "The new status for the task"
                    }
                },
                "required": ["task_id", "new_status"]
            }
        }
    }
]


TOOL_FUNCTIONS = {
    "create_task": create_task,
    "list_tasks": list_tasks,
    "update_task_status": update_task_status,
}


class TaskAgent:
    """An agent that helps manage tasks using function calling."""

    def __init__(self):
        """Initialize the task agent."""
        self._client = self._get_client()
        self.messages = [
            {
                "role": "system",
                "content": """You are a helpful task management assistant.
You can create tasks, list tasks, and update task statuses.
Always use the available tools to manage tasks.
Provide clear, friendly responses about task operations."""
            }
        ]

    def _get_client(self):
        """Get OpenAI client or None for mock mode."""
        if not os.getenv("OPENAI_API_KEY"):
            return None
        from openai import OpenAI
        return OpenAI()

    def process(self, user_message: str) -> str:
        """Process a user message, handling any tool calls."""
        self.messages.append({"role": "user", "content": user_message})

        if self._client is None:
            return self._mock_process(user_message)

        # First API call
        response = self._client.chat.completions.create(
            model="gpt-4o-mini",
            messages=self.messages,
            tools=TOOLS,
            tool_choice="auto"
        )

        message = response.choices[0].message

        # If no tool calls, return content directly
        if not message.tool_calls:
            self.messages.append({"role": "assistant", "content": message.content})
            return message.content

        # Handle tool calls
        self.messages.append({
            "role": "assistant",
            "content": message.content,
            "tool_calls": [
                {
                    "id": tc.id,
                    "type": "function",
                    "function": {
                        "name": tc.function.name,
                        "arguments": tc.function.arguments
                    }
                } for tc in message.tool_calls
            ]
        })

        # Execute each tool call
        for tool_call in message.tool_calls:
            function_name = tool_call.function.name
            arguments = json.loads(tool_call.function.arguments)

            # Execute function
            if function_name in TOOL_FUNCTIONS:
                result = TOOL_FUNCTIONS[function_name](**arguments)
            else:
                result = {"error": f"Unknown function: {function_name}"}

            # Add tool result
            self.messages.append({
                "role": "tool",
                "tool_call_id": tool_call.id,
                "content": json.dumps(result)
            })

        # Get final response
        final_response = self._client.chat.completions.create(
            model="gpt-4o-mini",
            messages=self.messages
        )

        final_content = final_response.choices[0].message.content
        self.messages.append({"role": "assistant", "content": final_content})

        return final_content

    def _mock_process(self, user_message: str) -> str:
        """Mock processing for demonstration."""
        user_lower = user_message.lower()

        if "create" in user_lower:
            # Extract title from message
            title = user_message.split("'")[1] if "'" in user_message else "New Task"
            priority = "high" if "high" in user_lower else "medium"
            result = create_task(title, priority=priority)
            return f"[Mock] Created task: {result['task']['title']} (ID: {result['task']['id']})"

        elif "list" in user_lower or "show" in user_lower:
            status = None
            if "pending" in user_lower:
                status = "pending"
            elif "completed" in user_lower:
                status = "completed"
            result = list_tasks(status)
            if result["count"] == 0:
                return f"[Mock] No tasks found{' with status ' + status if status else ''}"
            task_list = "\n".join(
                f"  [{t['id']}] {t['title']} - {t['status']}"
                for t in result["tasks"]
            )
            return f"[Mock] Found {result['count']} tasks:\n{task_list}"

        elif "mark" in user_lower or "update" in user_lower:
            # Try to extract task ID
            import re
            id_match = re.search(r'task\s*(\d+)', user_lower)
            if id_match:
                task_id = int(id_match.group(1))
                new_status = "completed" if "completed" in user_lower else "in_progress"
                result = update_task_status(task_id, new_status)
                if result["success"]:
                    return f"[Mock] Updated task {task_id} to {new_status}"
                return f"[Mock] Error: {result['error']}"
            return "[Mock] Please specify a task ID"

        return "[Mock] I can help you create, list, or update tasks."


# Test the implementation
if __name__ == "__main__":
    print("Testing Task Agent Implementation")
    print("=" * 50)

    # Reset tasks for clean test
    TASKS.clear()
    NEXT_ID = 1

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
        print(f"Agent: {response}")

    print("\n" + "=" * 50)
    print(f"Total tasks created: {len(TASKS)}")
    print("\nFinal task list:")
    for task_id, task in TASKS.items():
        print(f"  [{task_id}] {task['title']} - {task['status']} ({task['priority']} priority)")
