"""Exercise 1: Test an Async HTTP Client Wrapper

Your task is to implement tests for the AsyncAPIClient class below.
The client wraps async HTTP operations with retry logic.

Instructions:
1. Complete the test functions marked with TODO
2. Test successful requests, failures, and retries
3. Test timeout handling
4. Use appropriate async testing patterns

Expected Behavior:
- test_successful_request: Should return data on success
- test_request_failure: Should raise APIError on failure
- test_retry_on_transient_error: Should retry and succeed
- test_timeout_handling: Should raise TimeoutError on timeout

Hints:
- Use AsyncMock to mock the _make_request method
- Remember to await async function calls
- Use side_effect for multiple return values or exceptions

Run your tests with:
    pytest exercises/exercise_1.py -v
"""

import asyncio
from dataclasses import dataclass
from typing import Any
from unittest.mock import AsyncMock  # noqa: F401

import pytest  # noqa: F401


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
        # In real code, this would use aiohttp or similar
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
                        # Transient error, retry
                        last_error = APIError(
                            f"Server error: {response.status_code}",
                            response.status_code,
                        )
                        await asyncio.sleep(0.1 * (attempt + 1))  # Backoff
                        continue
                    else:
                        # Client error, don't retry
                        raise APIError(
                            f"Client error: {response.status_code}",
                            response.status_code,
                        )
            except asyncio.TimeoutError:
                raise

        # All retries exhausted
        if last_error:
            raise last_error
        raise APIError("Request failed after retries", 500)


# =============================================================================
# TODO: Implement the tests below
# =============================================================================


async def test_successful_request() -> None:
    """Test that a successful request returns data.

    TODO:
    1. Create an AsyncAPIClient instance
    2. Mock _make_request to return a successful response
    3. Call client.get() and verify the result
    """
    pass


async def test_request_failure() -> None:
    """Test that a client error (4xx) raises APIError immediately.

    TODO:
    1. Create an AsyncAPIClient instance
    2. Mock _make_request to return a 404 response
    3. Verify that APIError is raised with correct status_code
    4. Verify that _make_request was called only once (no retries)
    """
    pass


async def test_retry_on_transient_error() -> None:
    """Test that transient errors (5xx) trigger retries.

    TODO:
    1. Create an AsyncAPIClient instance with max_retries=3
    2. Mock _make_request to fail twice (500), then succeed
    3. Verify the final result is successful
    4. Verify _make_request was called 3 times
    """
    pass


async def test_timeout_handling() -> None:
    """Test that timeout raises TimeoutError.

    TODO:
    1. Create an AsyncAPIClient instance
    2. Mock _make_request to sleep longer than the timeout
    3. Call client.get() with a short timeout
    4. Verify TimeoutError is raised
    """
    pass


async def test_retries_exhausted() -> None:
    """Test that exhausting all retries raises the last error.

    TODO:
    1. Create an AsyncAPIClient instance with max_retries=2
    2. Mock _make_request to always return 500
    3. Verify APIError is raised after retries exhausted
    """
    pass


if __name__ == "__main__":
    import subprocess

    subprocess.run(["pytest", __file__, "-v"])
