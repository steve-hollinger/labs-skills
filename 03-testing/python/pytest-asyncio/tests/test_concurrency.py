"""Tests demonstrating concurrency testing with pytest-asyncio."""

import asyncio

import pytest


# =============================================================================
# Async Functions for Concurrency Testing
# =============================================================================


async def fetch_user(user_id: int, delay: float = 0.01) -> dict[str, int | str]:
    """Simulate fetching a user."""
    await asyncio.sleep(delay)
    return {"id": user_id, "name": f"User {user_id}"}


async def maybe_fail(value: int, fail_on: int | None = None) -> int:
    """Operation that may fail based on input."""
    await asyncio.sleep(0.01)
    if fail_on is not None and value == fail_on:
        raise ValueError(f"Failed on {value}")
    return value * 2


# =============================================================================
# asyncio.gather Tests
# =============================================================================


async def test_gather_basic() -> None:
    """Test basic asyncio.gather usage."""
    results = await asyncio.gather(
        fetch_user(1),
        fetch_user(2),
        fetch_user(3),
    )

    assert len(results) == 3
    assert results[0]["id"] == 1
    assert results[1]["id"] == 2
    assert results[2]["id"] == 3


async def test_gather_with_list() -> None:
    """Test gather with list of coroutines."""
    user_ids = [1, 2, 3, 4, 5]
    results = await asyncio.gather(*[fetch_user(uid) for uid in user_ids])

    assert len(results) == 5
    ids = {r["id"] for r in results}
    assert ids == {1, 2, 3, 4, 5}


async def test_gather_exception_propagates() -> None:
    """Test that gather propagates first exception."""
    with pytest.raises(ValueError, match="Failed on 2"):
        await asyncio.gather(
            maybe_fail(1),
            maybe_fail(2, fail_on=2),  # This fails
            maybe_fail(3),
        )


async def test_gather_return_exceptions() -> None:
    """Test gather with return_exceptions=True."""
    results = await asyncio.gather(
        maybe_fail(1),
        maybe_fail(2, fail_on=2),  # This fails
        maybe_fail(3),
        return_exceptions=True,
    )

    assert results[0] == 2  # 1 * 2
    assert isinstance(results[1], ValueError)
    assert results[2] == 6  # 3 * 2


async def test_gather_all_fail() -> None:
    """Test gather when all operations fail."""
    results = await asyncio.gather(
        maybe_fail(1, fail_on=1),
        maybe_fail(2, fail_on=2),
        maybe_fail(3, fail_on=3),
        return_exceptions=True,
    )

    assert all(isinstance(r, ValueError) for r in results)


# =============================================================================
# Timeout Tests
# =============================================================================


async def test_timeout_success() -> None:
    """Test operation completes within timeout."""
    async with asyncio.timeout(1.0):
        result = await fetch_user(1)

    assert result["id"] == 1


async def test_timeout_exceeded() -> None:
    """Test TimeoutError when timeout exceeded."""
    with pytest.raises(asyncio.TimeoutError):
        async with asyncio.timeout(0.01):
            await asyncio.sleep(1.0)


async def test_wait_for_success() -> None:
    """Test asyncio.wait_for success."""
    result = await asyncio.wait_for(fetch_user(1), timeout=1.0)
    assert result["id"] == 1


async def test_wait_for_timeout() -> None:
    """Test asyncio.wait_for timeout."""
    with pytest.raises(asyncio.TimeoutError):
        await asyncio.wait_for(asyncio.sleep(1.0), timeout=0.01)


# =============================================================================
# Semaphore Tests
# =============================================================================


async def test_semaphore_limits_concurrency() -> None:
    """Test that semaphore limits concurrent operations."""
    concurrent_count = 0
    max_concurrent_seen = 0

    async def tracked_operation(n: int) -> int:
        nonlocal concurrent_count, max_concurrent_seen
        concurrent_count += 1
        max_concurrent_seen = max(max_concurrent_seen, concurrent_count)
        try:
            await asyncio.sleep(0.02)
            return n
        finally:
            concurrent_count -= 1

    semaphore = asyncio.Semaphore(3)

    async def limited_operation(n: int) -> int:
        async with semaphore:
            return await tracked_operation(n)

    results = await asyncio.gather(*[limited_operation(i) for i in range(10)])

    assert len(results) == 10
    assert max_concurrent_seen <= 3


async def test_semaphore_with_exception() -> None:
    """Test semaphore releases on exception."""
    semaphore = asyncio.Semaphore(1)

    async def failing_operation() -> None:
        async with semaphore:
            raise ValueError("Test error")

    # First call fails
    with pytest.raises(ValueError):
        await failing_operation()

    # Semaphore should be released, so this should not hang
    async with asyncio.timeout(0.1):
        async with semaphore:
            pass  # Should acquire successfully


# =============================================================================
# Task Tests
# =============================================================================


async def test_create_task() -> None:
    """Test asyncio.create_task."""
    task = asyncio.create_task(fetch_user(1))

    # Task is running
    assert not task.done()

    result = await task

    assert task.done()
    assert result["id"] == 1


async def test_cancel_task() -> None:
    """Test task cancellation."""
    task = asyncio.create_task(asyncio.sleep(10))

    task.cancel()

    with pytest.raises(asyncio.CancelledError):
        await task


async def test_task_exception() -> None:
    """Test task with exception."""
    task = asyncio.create_task(maybe_fail(1, fail_on=1))

    with pytest.raises(ValueError):
        await task


# =============================================================================
# asyncio.wait Tests
# =============================================================================


async def test_wait_first_completed() -> None:
    """Test asyncio.wait with FIRST_COMPLETED."""
    tasks = [
        asyncio.create_task(fetch_user(1, delay=0.1)),
        asyncio.create_task(fetch_user(2, delay=0.01)),  # Fastest
        asyncio.create_task(fetch_user(3, delay=0.1)),
    ]

    done, pending = await asyncio.wait(tasks, return_when=asyncio.FIRST_COMPLETED)

    assert len(done) == 1
    assert len(pending) == 2

    # The fastest task should be done
    result = done.pop().result()
    assert result["id"] == 2

    # Clean up pending tasks
    for task in pending:
        task.cancel()
        try:
            await task
        except asyncio.CancelledError:
            pass


async def test_wait_all_completed() -> None:
    """Test asyncio.wait with ALL_COMPLETED."""
    tasks = [
        asyncio.create_task(fetch_user(1)),
        asyncio.create_task(fetch_user(2)),
        asyncio.create_task(fetch_user(3)),
    ]

    done, pending = await asyncio.wait(tasks, return_when=asyncio.ALL_COMPLETED)

    assert len(done) == 3
    assert len(pending) == 0


async def test_wait_with_timeout() -> None:
    """Test asyncio.wait with timeout."""
    tasks = [
        asyncio.create_task(asyncio.sleep(0.01)),  # Fast
        asyncio.create_task(asyncio.sleep(10)),  # Slow
    ]

    done, pending = await asyncio.wait(tasks, timeout=0.1)

    assert len(done) == 1  # Only fast task completed
    assert len(pending) == 1  # Slow task still pending

    # Clean up
    for task in pending:
        task.cancel()
        try:
            await task
        except asyncio.CancelledError:
            pass


# =============================================================================
# TaskGroup Tests (Python 3.11+)
# =============================================================================


async def test_task_group_basic() -> None:
    """Test basic TaskGroup usage."""
    results: list[dict[str, int | str]] = []

    async def fetch_and_store(uid: int) -> None:
        result = await fetch_user(uid)
        results.append(result)

    async with asyncio.TaskGroup() as tg:
        tg.create_task(fetch_and_store(1))
        tg.create_task(fetch_and_store(2))
        tg.create_task(fetch_and_store(3))

    assert len(results) == 3


async def test_task_group_exception() -> None:
    """Test TaskGroup cancels all on exception."""

    async def failing_task() -> None:
        await asyncio.sleep(0.01)
        raise ValueError("Task failed!")

    async def slow_task() -> None:
        await asyncio.sleep(10)

    with pytest.raises(ExceptionGroup) as exc_info:
        async with asyncio.TaskGroup() as tg:
            tg.create_task(failing_task())
            tg.create_task(slow_task())  # Should be cancelled

    # ExceptionGroup contains our ValueError
    assert len(exc_info.value.exceptions) == 1
    assert isinstance(exc_info.value.exceptions[0], ValueError)


# =============================================================================
# Concurrent State Tests
# =============================================================================


async def test_concurrent_counter() -> None:
    """Test concurrent operations on shared state."""
    counter = 0
    lock = asyncio.Lock()

    async def increment() -> None:
        nonlocal counter
        async with lock:
            current = counter
            await asyncio.sleep(0.01)  # Simulate work
            counter = current + 1

    await asyncio.gather(*[increment() for _ in range(10)])

    assert counter == 10


async def test_concurrent_queue() -> None:
    """Test concurrent producer-consumer with asyncio.Queue."""
    queue: asyncio.Queue[int] = asyncio.Queue()
    results: list[int] = []

    async def producer() -> None:
        for i in range(5):
            await queue.put(i)
            await asyncio.sleep(0.01)

    async def consumer() -> None:
        while True:
            try:
                item = await asyncio.wait_for(queue.get(), timeout=0.1)
                results.append(item)
                queue.task_done()
            except asyncio.TimeoutError:
                break

    await asyncio.gather(producer(), consumer())

    assert sorted(results) == [0, 1, 2, 3, 4]
