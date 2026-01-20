"""Exercise 2: Build a File Operations Tool Set with Permissions

Create a set of file operation tools with permission-based access control.
Users should only be able to perform operations they have permissions for.

Instructions:
1. Create tools for: read_file, write_file, delete_file, list_files
2. Assign permissions:
   - read_file: "file:read" permission
   - write_file: "file:write" permission
   - delete_file: "file:delete" permission
   - list_files: "file:read" permission
3. Simulate file operations (don't actually touch the filesystem)
4. Test with different user permission sets

Expected Output:
- User with "file:read" can read and list but not write or delete
- User with "file:write" can write but not delete
- Admin with all permissions can do everything

Hints:
- Use the permissions parameter in @tool decorator
- Use registry.invoke() with user_permissions parameter
- Store files in a simple in-memory dictionary
"""

import asyncio
from typing import Any

from tool_registry import ToolRegistry, tool
from tool_registry.exceptions import PermissionDeniedError


# Simulated filesystem
FILES: dict[str, str] = {
    "readme.txt": "Welcome to the file system!",
    "config.json": '{"version": "1.0"}',
}


# TODO: Implement file operation tools with permissions


@tool(
    name="read_file",
    description="Read contents of a file",
    # TODO: Add permissions
)
async def read_file(path: str) -> dict[str, Any]:
    """Read a file by path.

    TODO: Implement this function:
    1. Check if file exists
    2. Return file contents or error
    """
    pass


@tool(
    name="write_file",
    description="Write contents to a file",
    # TODO: Add permissions
)
async def write_file(path: str, content: str) -> dict[str, Any]:
    """Write content to a file.

    TODO: Implement this function:
    1. Write content to FILES dict
    2. Return success message
    """
    pass


@tool(
    name="delete_file",
    description="Delete a file",
    # TODO: Add permissions
)
async def delete_file(path: str) -> dict[str, Any]:
    """Delete a file by path.

    TODO: Implement this function:
    1. Check if file exists
    2. Delete from FILES dict
    3. Return success/error message
    """
    pass


@tool(
    name="list_files",
    description="List all files",
    # TODO: Add permissions
)
async def list_files() -> list[str]:
    """List all available files.

    TODO: Return list of file paths
    """
    pass


async def main() -> None:
    """Test file operations with different permissions."""
    print("Testing File Operations with Permissions...")

    registry = ToolRegistry()

    # Register all tools
    registry.register(read_file)
    registry.register(write_file)
    registry.register(delete_file)
    registry.register(list_files)

    # Define user permission sets
    reader_permissions = ["file:read"]
    writer_permissions = ["file:read", "file:write"]
    admin_permissions = ["file:read", "file:write", "file:delete"]

    # Test as reader
    print("\n--- Testing as Reader ---")
    print(f"Permissions: {reader_permissions}")

    # Should work
    try:
        result = await registry.invoke("list_files", {}, user_permissions=reader_permissions)
        print(f"list_files(): {result}")
    except PermissionDeniedError as e:
        print(f"list_files(): Permission denied - {e}")

    # Should fail
    try:
        result = await registry.invoke(
            "write_file",
            {"path": "test.txt", "content": "test"},
            user_permissions=reader_permissions,
        )
        print(f"write_file(): {result}")
    except PermissionDeniedError as e:
        print(f"write_file(): Permission denied - {e}")

    # Test as writer
    print("\n--- Testing as Writer ---")
    print(f"Permissions: {writer_permissions}")

    # TODO: Add test cases for writer

    # Test as admin
    print("\n--- Testing as Admin ---")
    print(f"Permissions: {admin_permissions}")

    # TODO: Add test cases for admin


if __name__ == "__main__":
    asyncio.run(main())
