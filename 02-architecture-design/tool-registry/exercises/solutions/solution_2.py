"""Solution for Exercise 2: Build a File Operations Tool Set with Permissions"""

import asyncio
from typing import Any

from tool_registry import ToolRegistry, tool
from tool_registry.exceptions import PermissionDeniedError


# Simulated filesystem
FILES: dict[str, str] = {
    "readme.txt": "Welcome to the file system!",
    "config.json": '{"version": "1.0"}',
}


@tool(
    name="read_file",
    description="Read contents of a file",
    permissions=["file:read"],
)
async def read_file(path: str) -> dict[str, Any]:
    """Read a file by path."""
    if path not in FILES:
        return {
            "success": False,
            "error": f"File not found: {path}",
        }

    return {
        "success": True,
        "path": path,
        "content": FILES[path],
    }


@tool(
    name="write_file",
    description="Write contents to a file",
    permissions=["file:write"],
)
async def write_file(path: str, content: str) -> dict[str, Any]:
    """Write content to a file."""
    is_new = path not in FILES
    FILES[path] = content

    return {
        "success": True,
        "path": path,
        "created": is_new,
        "message": f"{'Created' if is_new else 'Updated'} {path}",
    }


@tool(
    name="delete_file",
    description="Delete a file",
    permissions=["file:delete"],
)
async def delete_file(path: str) -> dict[str, Any]:
    """Delete a file by path."""
    if path not in FILES:
        return {
            "success": False,
            "error": f"File not found: {path}",
        }

    del FILES[path]

    return {
        "success": True,
        "path": path,
        "message": f"Deleted {path}",
    }


@tool(
    name="list_files",
    description="List all files",
    permissions=["file:read"],
)
async def list_files() -> list[str]:
    """List all available files."""
    return list(FILES.keys())


async def test_with_permissions(
    registry: ToolRegistry,
    user_name: str,
    permissions: list[str],
) -> None:
    """Test various operations with given permissions."""
    print(f"\n--- Testing as {user_name} ---")
    print(f"Permissions: {permissions}")

    # Test list_files
    print("\n  list_files():")
    try:
        result = await registry.invoke("list_files", {}, user_permissions=permissions)
        print(f"    Result: {result}")
    except PermissionDeniedError as e:
        print(f"    Permission denied: {e}")

    # Test read_file
    print("\n  read_file('readme.txt'):")
    try:
        result = await registry.invoke(
            "read_file", {"path": "readme.txt"}, user_permissions=permissions
        )
        print(f"    Result: {result}")
    except PermissionDeniedError as e:
        print(f"    Permission denied: {e}")

    # Test write_file
    print("\n  write_file('test.txt', 'Hello!'):")
    try:
        result = await registry.invoke(
            "write_file",
            {"path": "test.txt", "content": "Hello!"},
            user_permissions=permissions,
        )
        print(f"    Result: {result}")
    except PermissionDeniedError as e:
        print(f"    Permission denied: {e}")

    # Test delete_file
    print("\n  delete_file('test.txt'):")
    try:
        result = await registry.invoke(
            "delete_file", {"path": "test.txt"}, user_permissions=permissions
        )
        print(f"    Result: {result}")
    except PermissionDeniedError as e:
        print(f"    Permission denied: {e}")


async def main() -> None:
    """Test file operations with different permissions."""
    print("Solution 2: File Operations with Permissions")
    print("=" * 50)

    registry = ToolRegistry()

    # Register all tools
    registry.register(read_file)
    registry.register(write_file)
    registry.register(delete_file)
    registry.register(list_files)

    # Show initial files
    print("\nInitial files:", list(FILES.keys()))

    # Define user permission sets
    reader_permissions = ["file:read"]
    writer_permissions = ["file:read", "file:write"]
    admin_permissions = ["file:read", "file:write", "file:delete"]

    # Test as reader
    await test_with_permissions(registry, "Reader", reader_permissions)

    # Reset test file if created
    if "test.txt" in FILES:
        del FILES["test.txt"]

    # Test as writer
    await test_with_permissions(registry, "Writer", writer_permissions)

    # Note: test.txt was created by writer, now test deletion

    # Test as admin
    await test_with_permissions(registry, "Admin", admin_permissions)

    # Show final files
    print("\n" + "=" * 50)
    print("Final files:", list(FILES.keys()))
    print("\nSolution demonstration complete!")


if __name__ == "__main__":
    asyncio.run(main())
