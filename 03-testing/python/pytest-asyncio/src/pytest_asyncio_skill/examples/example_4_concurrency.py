"""Example 4: Testing Concurrency Patterns

This example demonstrates how to test concurrent async operations,
including gather, timeouts, task groups, and semaphores.
"""

import asyncio


async def fetch_user(user_id: int, delay: float = 0.01) -> dict[str, int | str]:
    """Simulate fetching a user from API."""
    await asyncio.sleep(delay)
    return {"id": user_id, "name": f"User {user_id}"}


async def fetch_users_concurrently(user_ids: list[int]) -> list[dict[str, int | str]]:
    """Fetch multiple users concurrently."""
    return await asyncio.gather(*[fetch_user(uid) for uid in user_ids])


async def fetch_with_timeout(
    user_id: int, timeout: float
) -> dict[str, int | str] | None:
    """Fetch user with timeout."""
    try:
        async with asyncio.timeout(timeout):
            return await fetch_user(user_id, delay=0.05)
    except asyncio.TimeoutError:
        return None


async def fetch_with_semaphore(
    user_ids: list[int], max_concurrent: int = 3
) -> list[dict[str, int | str]]:
    """Fetch users with limited concurrency."""
    semaphore = asyncio.Semaphore(max_concurrent)

    async def fetch_one(uid: int) -> dict[str, int | str]:
        async with semaphore:
            return await fetch_user(uid)

    return await asyncio.gather(*[fetch_one(uid) for uid in user_ids])


async def fetch_first_successful(
    user_ids: list[int],
) -> dict[str, int | str] | None:
    """Return the first successful result, cancel others."""

    async def try_fetch(uid: int) -> dict[str, int | str]:
        # Add varying delays so results come back at different times
        await asyncio.sleep(0.01 * uid)
        return await fetch_user(uid)

    tasks = [asyncio.create_task(try_fetch(uid)) for uid in user_ids]

    try:
        done, pending = await asyncio.wait(
            tasks, return_when=asyncio.FIRST_COMPLETED
        )
        result = done.pop().result()

        # Cancel remaining tasks
        for task in pending:
            task.cancel()

        return result
    except Exception:
        for task in tasks:
            task.cancel()
        return None


def main() -> None:
    """Demonstrate testing concurrency patterns."""
    print("Example 4: Testing Concurrency Patterns")
    print("=" * 50)
    print()

    # Testing with gather
    print("1. Testing with asyncio.gather")
    print("-" * 40)
    print("""
    async def test_concurrent_fetch():
        \"\"\"Test concurrent operations with gather.\"\"\"
        results = await fetch_users_concurrently([1, 2, 3])

        assert len(results) == 3
        assert all(isinstance(r, dict) for r in results)
        assert {r["id"] for r in results} == {1, 2, 3}


    async def test_gather_with_exception():
        \"\"\"Test gather when one operation fails.\"\"\"
        async def maybe_fail(n: int):
            if n == 2:
                raise ValueError("Failed!")
            return n

        # Without return_exceptions, first error propagates
        with pytest.raises(ValueError):
            await asyncio.gather(
                maybe_fail(1),
                maybe_fail(2),  # Raises
                maybe_fail(3),
            )


    async def test_gather_return_exceptions():
        \"\"\"Test gather with return_exceptions=True.\"\"\"
        async def maybe_fail(n: int):
            if n == 2:
                raise ValueError("Failed!")
            return n

        results = await asyncio.gather(
            maybe_fail(1),
            maybe_fail(2),
            maybe_fail(3),
            return_exceptions=True
        )

        assert results[0] == 1
        assert isinstance(results[1], ValueError)
        assert results[2] == 3
    """)

    # Testing timeouts
    print("2. Testing with Timeouts")
    print("-" * 40)
    print("""
    async def test_operation_completes_in_time():
        \"\"\"Test that operation completes within timeout.\"\"\"
        async with asyncio.timeout(1.0):
            result = await fetch_user(1)
        assert result["id"] == 1


    async def test_timeout_exceeded():
        \"\"\"Test that TimeoutError is raised when timeout exceeded.\"\"\"
        with pytest.raises(asyncio.TimeoutError):
            async with asyncio.timeout(0.01):
                await asyncio.sleep(1.0)


    async def test_fetch_with_timeout_success():
        \"\"\"Test fetch with generous timeout succeeds.\"\"\"
        result = await fetch_with_timeout(1, timeout=1.0)
        assert result is not None
        assert result["id"] == 1


    async def test_fetch_with_timeout_exceeded():
        \"\"\"Test fetch with tight timeout returns None.\"\"\"
        result = await fetch_with_timeout(1, timeout=0.001)
        assert result is None
    """)

    # Testing with semaphores
    print("3. Testing with Semaphores")
    print("-" * 40)
    print("""
    async def test_semaphore_limits_concurrency():
        \"\"\"Test that semaphore limits concurrent operations.\"\"\"
        # Track concurrent executions
        concurrent_count = 0
        max_concurrent_seen = 0

        async def tracked_fetch(uid: int) -> dict:
            nonlocal concurrent_count, max_concurrent_seen
            concurrent_count += 1
            max_concurrent_seen = max(max_concurrent_seen, concurrent_count)
            try:
                await asyncio.sleep(0.01)
                return {"id": uid}
            finally:
                concurrent_count -= 1

        # Fetch with max 2 concurrent
        semaphore = asyncio.Semaphore(2)

        async def limited_fetch(uid: int):
            async with semaphore:
                return await tracked_fetch(uid)

        await asyncio.gather(*[limited_fetch(i) for i in range(10)])

        assert max_concurrent_seen <= 2
    """)

    # Testing first-completed pattern
    print("4. Testing First-Completed Pattern")
    print("-" * 40)
    print("""
    async def test_first_successful():
        \"\"\"Test getting first successful result.\"\"\"
        result = await fetch_first_successful([3, 2, 1])

        # User 1 completes first (shortest delay)
        assert result is not None
        assert result["id"] == 1


    async def test_wait_with_timeout():
        \"\"\"Test asyncio.wait with timeout.\"\"\"
        async def slow_task():
            await asyncio.sleep(10)
            return "slow"

        async def fast_task():
            await asyncio.sleep(0.01)
            return "fast"

        tasks = [
            asyncio.create_task(slow_task()),
            asyncio.create_task(fast_task()),
        ]

        done, pending = await asyncio.wait(
            tasks,
            timeout=0.1,
            return_when=asyncio.ALL_COMPLETED
        )

        # Only fast task completed
        assert len(done) == 1
        assert len(pending) == 1

        # Clean up
        for task in pending:
            task.cancel()
            try:
                await task
            except asyncio.CancelledError:
                pass
    """)

    # Testing task groups (Python 3.11+)
    print("5. Testing Task Groups (Python 3.11+)")
    print("-" * 40)
    print("""
    async def test_task_group():
        \"\"\"Test asyncio.TaskGroup for structured concurrency.\"\"\"
        results = []

        async with asyncio.TaskGroup() as tg:
            tg.create_task(fetch_user(1))
            tg.create_task(fetch_user(2))
            tg.create_task(fetch_user(3))

        # TaskGroup doesn't return results directly
        # Use a different pattern for collecting results


    async def test_task_group_with_results():
        \"\"\"Collect results from TaskGroup.\"\"\"
        results = []

        async def fetch_and_store(uid: int):
            result = await fetch_user(uid)
            results.append(result)

        async with asyncio.TaskGroup() as tg:
            for uid in [1, 2, 3]:
                tg.create_task(fetch_and_store(uid))

        assert len(results) == 3


    async def test_task_group_exception():
        \"\"\"Test TaskGroup cancels all on exception.\"\"\"
        async def failing_task():
            raise ValueError("Oops!")

        async def slow_task():
            await asyncio.sleep(10)

        with pytest.raises(ExceptionGroup) as exc_info:
            async with asyncio.TaskGroup() as tg:
                tg.create_task(failing_task())
                tg.create_task(slow_task())  # Gets cancelled

        # ExceptionGroup contains our ValueError
        assert len(exc_info.value.exceptions) == 1
    """)

    # Demo
    print("6. Running Concurrency Patterns (Demo)")
    print("-" * 40)

    async def demo() -> None:
        print("Concurrent fetch (3 users):")
        results = await fetch_users_concurrently([1, 2, 3])
        for r in results:
            print(f"  {r}")

        print("\nFetch with timeout (generous):")
        result = await fetch_with_timeout(1, timeout=1.0)
        print(f"  Result: {result}")

        print("\nFetch with timeout (tight):")
        result = await fetch_with_timeout(1, timeout=0.001)
        print(f"  Result: {result}")

        print("\nFetch with semaphore (5 users, max 2 concurrent):")
        results = await fetch_with_semaphore([1, 2, 3, 4, 5], max_concurrent=2)
        print(f"  Got {len(results)} results")

        print("\nFirst successful fetch:")
        result = await fetch_first_successful([5, 3, 1])
        print(f"  First result: {result}")

    asyncio.run(demo())

    print()
    print("Run the tests with:")
    print("  pytest tests/test_concurrency.py -v")
    print()
    print("Example completed!")


if __name__ == "__main__":
    main()
