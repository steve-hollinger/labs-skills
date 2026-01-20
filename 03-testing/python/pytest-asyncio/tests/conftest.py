"""Pytest configuration for pytest-asyncio skill tests."""

import asyncio

import pytest


@pytest.fixture
def event_loop_policy() -> asyncio.AbstractEventLoopPolicy:
    """Use the default event loop policy."""
    return asyncio.DefaultEventLoopPolicy()


@pytest.fixture
async def slow_resource() -> str:
    """Fixture that simulates slow resource setup."""
    await asyncio.sleep(0.05)
    return "slow_resource_data"


@pytest.fixture
async def cancellable_task() -> asyncio.Task[None]:
    """Fixture that provides a cancellable background task."""

    async def background_work() -> None:
        while True:
            await asyncio.sleep(0.1)

    task = asyncio.create_task(background_work())
    yield task

    task.cancel()
    try:
        await task
    except asyncio.CancelledError:
        pass
