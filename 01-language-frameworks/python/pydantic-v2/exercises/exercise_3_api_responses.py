"""Exercise 3: API Response Models

Create a set of API response models with proper serialization.

Requirements:
1. Create a generic PaginationMeta model:
   - page: positive integer
   - page_size: positive integer, 1-100
   - total_items: non-negative integer
   - Add computed fields: total_pages, has_next, has_previous

2. Create an ErrorDetail model:
   - code: string (e.g., "VALIDATION_ERROR", "NOT_FOUND")
   - message: string
   - field: optional string (for field-specific errors)

3. Create a generic APIResponse[T] model using Generic[T]:
   - success: boolean
   - data: optional T (the actual response data)
   - errors: optional list of ErrorDetail
   - meta: optional PaginationMeta (for list responses)
   - timestamp: datetime, defaults to now

   Add a model_validator:
   - If success is True, data must be present and errors must be None
   - If success is False, errors must be present and data must be None

4. Create specific response models:
   - UserResponse: for single user (id, username, email, created_at)
   - UserListResponse: list of UserResponse with pagination

5. Implement serialization:
   - Serialize timestamp as ISO format string
   - Use camelCase aliases for JSON output (e.g., page_size -> pageSize)
   - Exclude None values from output (exclude_none=True behavior)

Expected behavior:
    # Success response
    response = APIResponse[UserResponse](
        success=True,
        data=UserResponse(id=1, username="alice", email="a@b.com", created_at=datetime.now())
    )
    print(response.model_dump_json(by_alias=True))
    # {"success": true, "data": {"id": 1, "username": "alice", ...}, "timestamp": "..."}

    # Error response
    error_response = APIResponse[UserResponse](
        success=False,
        errors=[ErrorDetail(code="NOT_FOUND", message="User not found")]
    )

    # Paginated list response
    list_response = APIResponse[list[UserResponse]](
        success=True,
        data=[...],
        meta=PaginationMeta(page=1, page_size=10, total_items=100)
    )
    print(list_response.meta.total_pages)  # 10
    print(list_response.meta.has_next)  # True

Hints:
- Use Generic[T] and TypeVar for generic models
- Use Field(alias="camelCase") for JSON field names
- Use ConfigDict(populate_by_name=True) to allow both aliases
- Use @field_serializer for custom datetime serialization
"""

from datetime import datetime
from typing import Generic, Optional, TypeVar

from pydantic import BaseModel


T = TypeVar("T")


class PaginationMeta(BaseModel):
    """Pagination metadata - implement this!"""

    # TODO: Add fields and computed fields
    pass


class ErrorDetail(BaseModel):
    """Error detail - implement this!"""

    # TODO: Add fields
    pass


class APIResponse(BaseModel, Generic[T]):
    """Generic API response - implement this!"""

    # TODO: Add fields and validators
    pass


class UserResponse(BaseModel):
    """User response model - implement this!"""

    # TODO: Add fields with camelCase aliases
    pass


def test_api_responses() -> None:
    """Test your API response implementation."""
    # TODO: Implement tests

    print("\nAll tests passed!")


if __name__ == "__main__":
    test_api_responses()
