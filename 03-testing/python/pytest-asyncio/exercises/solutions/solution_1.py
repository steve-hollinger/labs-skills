"""Solution for Exercise 1: Test an Async HTTP Client Wrapper"""

import asyncio
from dataclasses import dataclass
from typing import Any
from unittest.mock import AsyncMock

import pytest


class APIError(Exception):
    """Custom API error."""

    def __init__(self, message: str, status_code: int) -> None:
        super().__init__(message)
        self.status_code = status_code


@dataclass
class APIResponse:
    """API response wrapper."""

    status_code: int
    data: dict[str, Any]


class AsyncAPIClient:
    """Async API client with retry logic."""

    def __init__(self, base_url: str, max_retries: int = 3) -> None:
        self.base_url = base_url
        self.max_retries = max_retries

    async def _make_request(self, endpoint: str) -> APIResponse:
        """Make the actual HTTP request (to be mocked in tests)."""
        await asyncio.sleep(0.1)
        return APIResponse(status_code=200, data={"endpoint": endpoint})

    async def get(self, endpoint: str, timeout: float = 5.0) -> dict[str, Any]:
        """GET request with retry logic and timeout."""
        last_error: Exception | None = None

        for attempt in range(self.max_retries):
            try:
                async with asyncio.timeout(timeout):
                    response = await self._make_request(endpoint)

                    if response.status_code == 200:
                        return response.data
                    elif response.status_code >= 500:
                        last_error = APIError(
                            f"Server error: {response.status_code}",
                            response.status_code,
                        )
                        await asyncio.sleep(0.1 * (attempt + 1))
                        continue
                    else:
                        raise APIError(
                            f"Client error: {response.status_code}",
                            response.status_code,
                        )
            except asyncio.TimeoutError:
                raise

        if last_error:
            raise last_error
        raise APIError("Request failed after retries", 500)


# =============================================================================
# Solutions
# =============================================================================


async def test_successful_request() -> None:
    """Test that a successful request returns data."""
    client = AsyncAPIClient("https://api.example.com")

    # Mock _make_request to return success
    client._make_request = AsyncMock(
        return_value=APIResponse(status_code=200, data={"user": "test"})
    )

    result = await client.get("/users/1")

    assert result == {"user": "test"}
    client._make_request.assert_awaited_once_with("/users/1")


async def test_request_failure() -> None:
    """Test that a client error (4xx) raises APIError immediately."""
    client = AsyncAPIClient("https://api.example.com")

    # Mock _make_request to return 404
    client._make_request = AsyncMock(
        return_value=APIResponse(status_code=404, data={"error": "Not found"})
    )

    with pytest.raises(APIError) as exc_info:
        await client.get("/users/999")

    assert exc_info.value.status_code == 404
    # Should not retry on client error - called only once
    assert client._make_request.await_count == 1


async def test_retry_on_transient_error() -> None:
    """Test that transient errors (5xx) trigger retries."""
    client = AsyncAPIClient("https://api.example.com", max_retries=3)

    # Mock to fail twice (500), then succeed
    client._make_request = AsyncMock(
        side_effect=[
            APIResponse(status_code=500, data={}),
            APIResponse(status_code=500, data={}),
            APIResponse(status_code=200, data={"success": True}),
        ]
    )

    result = await client.get("/users/1")

    assert result == {"success": True}
    assert client._make_request.await_count == 3


async def test_timeout_handling() -> None:
    """Test that timeout raises TimeoutError."""
    client = AsyncAPIClient("https://api.example.com")

    # Mock _make_request to sleep longer than timeout
    async def slow_request(endpoint: str) -> APIResponse:
        await asyncio.sleep(1.0)
        return APIResponse(status_code=200, data={})

    client._make_request = slow_request  # type: ignore

    with pytest.raises(asyncio.TimeoutError):
        await client.get("/slow", timeout=0.01)


async def test_retries_exhausted() -> None:
    """Test that exhausting all retries raises the last error."""
    client = AsyncAPIClient("https://api.example.com", max_retries=2)

    # Mock to always return 500
    client._make_request = AsyncMock(
        return_value=APIResponse(status_code=500, data={"error": "Server error"})
    )

    with pytest.raises(APIError) as exc_info:
        await client.get("/users/1")

    assert exc_info.value.status_code == 500
    assert client._make_request.await_count == 2


if __name__ == "__main__":
    import subprocess

    subprocess.run(["pytest", __file__, "-v"])
