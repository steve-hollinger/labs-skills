"""Solution for Exercise 3: API Response Models

This is the reference solution for the API response models exercise.
"""

from datetime import datetime
from typing import Generic, Optional, TypeVar

from pydantic import (
    BaseModel,
    ConfigDict,
    Field,
    ValidationError,
    computed_field,
    field_serializer,
    model_validator,
)


T = TypeVar("T")


class PaginationMeta(BaseModel):
    """Pagination metadata for list responses."""

    model_config = ConfigDict(
        populate_by_name=True,
    )

    page: int = Field(gt=0, alias="page")
    page_size: int = Field(gt=0, le=100, alias="pageSize")
    total_items: int = Field(ge=0, alias="totalItems")

    @computed_field(alias="totalPages")
    @property
    def total_pages(self) -> int:
        """Calculate total number of pages."""
        if self.page_size == 0:
            return 0
        return (self.total_items + self.page_size - 1) // self.page_size

    @computed_field(alias="hasNext")
    @property
    def has_next(self) -> bool:
        """Check if there's a next page."""
        return self.page < self.total_pages

    @computed_field(alias="hasPrevious")
    @property
    def has_previous(self) -> bool:
        """Check if there's a previous page."""
        return self.page > 1


class ErrorDetail(BaseModel):
    """Error detail for API error responses."""

    model_config = ConfigDict(
        populate_by_name=True,
    )

    code: str
    message: str
    field: Optional[str] = None


class APIResponse(BaseModel, Generic[T]):
    """Generic API response wrapper."""

    model_config = ConfigDict(
        populate_by_name=True,
    )

    success: bool
    data: Optional[T] = None
    errors: Optional[list[ErrorDetail]] = None
    meta: Optional[PaginationMeta] = None
    timestamp: datetime = Field(default_factory=datetime.now)

    @model_validator(mode="after")
    def validate_response_consistency(self) -> "APIResponse[T]":
        """Ensure success flag is consistent with data/errors."""
        if self.success:
            if self.data is None:
                raise ValueError("Success response must include data")
            if self.errors is not None:
                raise ValueError("Success response cannot include errors")
        else:
            if self.errors is None or len(self.errors) == 0:
                raise ValueError("Error response must include errors")
            if self.data is not None:
                raise ValueError("Error response cannot include data")
        return self

    @field_serializer("timestamp")
    def serialize_timestamp(self, dt: datetime) -> str:
        """Serialize timestamp to ISO format."""
        return dt.isoformat()


class UserResponse(BaseModel):
    """User response model for API output."""

    model_config = ConfigDict(
        populate_by_name=True,
    )

    id: int
    username: str = Field(alias="userName")
    email: str
    created_at: datetime = Field(alias="createdAt")

    @field_serializer("created_at")
    def serialize_created_at(self, dt: datetime) -> str:
        """Serialize datetime to ISO format."""
        return dt.isoformat()


# Type alias for common response types
UserAPIResponse = APIResponse[UserResponse]
UserListAPIResponse = APIResponse[list[UserResponse]]


def test_api_responses() -> None:
    """Test the API response implementation."""
    print("Testing API Response implementation...")

    # Test 1: Pagination meta computed fields
    meta = PaginationMeta(page=1, page_size=10, total_items=95)
    assert meta.total_pages == 10
    assert meta.has_next is True
    assert meta.has_previous is False
    print("  Test 1 passed: PaginationMeta computed fields work")

    # Test 2: Last page pagination
    meta_last = PaginationMeta(page=10, page_size=10, total_items=95)
    assert meta_last.has_next is False
    assert meta_last.has_previous is True
    print("  Test 2 passed: Last page pagination correct")

    # Test 3: Pagination with aliases
    meta_dict = meta.model_dump(by_alias=True)
    assert "pageSize" in meta_dict
    assert "totalItems" in meta_dict
    assert "totalPages" in meta_dict
    print("  Test 3 passed: Pagination camelCase aliases work")

    # Test 4: Success response with data
    user = UserResponse(
        id=1,
        username="alice",
        email="alice@example.com",
        created_at=datetime.now(),
    )
    response = APIResponse[UserResponse](success=True, data=user)
    assert response.success is True
    assert response.data is not None
    assert response.errors is None
    print("  Test 4 passed: Success response created")

    # Test 5: Error response
    error = ErrorDetail(code="NOT_FOUND", message="User not found")
    error_response = APIResponse[UserResponse](success=False, errors=[error])
    assert error_response.success is False
    assert error_response.errors is not None
    assert len(error_response.errors) == 1
    print("  Test 5 passed: Error response created")

    # Test 6: Success response must have data
    try:
        APIResponse[UserResponse](success=True, data=None)
        raise AssertionError("Should reject success=True without data")
    except ValidationError as e:
        assert "must include data" in str(e)
        print("  Test 6 passed: Success without data rejected")

    # Test 7: Error response must have errors
    try:
        APIResponse[UserResponse](success=False, errors=None)
        raise AssertionError("Should reject success=False without errors")
    except ValidationError as e:
        assert "must include errors" in str(e)
        print("  Test 7 passed: Error without errors rejected")

    # Test 8: Success response cannot have errors
    try:
        APIResponse[UserResponse](
            success=True, data=user, errors=[error]
        )
        raise AssertionError("Should reject success=True with errors")
    except ValidationError as e:
        assert "cannot include errors" in str(e)
        print("  Test 8 passed: Success with errors rejected")

    # Test 9: Error response cannot have data
    try:
        APIResponse[UserResponse](
            success=False, errors=[error], data=user
        )
        raise AssertionError("Should reject success=False with data")
    except ValidationError as e:
        assert "cannot include data" in str(e)
        print("  Test 9 passed: Error with data rejected")

    # Test 10: List response with pagination
    users = [
        UserResponse(
            id=i,
            username=f"user{i}",
            email=f"user{i}@example.com",
            created_at=datetime.now(),
        )
        for i in range(1, 11)
    ]
    list_response = APIResponse[list[UserResponse]](
        success=True,
        data=users,
        meta=PaginationMeta(page=1, page_size=10, total_items=100),
    )
    assert list_response.meta is not None
    assert list_response.meta.total_pages == 10
    assert len(list_response.data) == 10
    print("  Test 10 passed: List response with pagination works")

    # Test 11: JSON serialization with camelCase
    json_output = response.model_dump_json(by_alias=True)
    assert "userName" in json_output
    assert "createdAt" in json_output
    print("  Test 11 passed: JSON output uses camelCase aliases")

    # Test 12: Timestamp serialization
    response_dict = response.model_dump()
    # The timestamp should be serialized to ISO string
    assert isinstance(response_dict["timestamp"], str)
    print("  Test 12 passed: Timestamp serialized to ISO format")

    # Test 13: Error with field reference
    field_error = ErrorDetail(
        code="VALIDATION_ERROR",
        message="Username too short",
        field="username",
    )
    field_error_response = APIResponse[UserResponse](
        success=False, errors=[field_error]
    )
    assert field_error_response.errors[0].field == "username"
    print("  Test 13 passed: Error with field reference works")

    # Test 14: Parse from camelCase input
    user_from_camel = UserResponse.model_validate({
        "id": 1,
        "userName": "bob",
        "email": "bob@example.com",
        "createdAt": "2024-01-15T10:30:00",
    })
    assert user_from_camel.username == "bob"
    print("  Test 14 passed: Parse from camelCase input works")

    print("\nAll tests passed!")


if __name__ == "__main__":
    test_api_responses()
