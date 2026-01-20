"""Solution for Exercise 3: Test an Async Message Queue Consumer"""

import asyncio
from dataclasses import dataclass
from typing import Any, Callable, Coroutine

import pytest


@dataclass
class Message:
    """Message to be processed."""

    id: str
    payload: dict[str, Any]


class MessageConsumer:
    """Async message consumer with concurrency control."""

    def __init__(
        self,
        queue: asyncio.Queue[Message],
        handler: Callable[[Message], Coroutine[Any, Any, None]],
        max_concurrent: int = 5,
    ) -> None:
        self.queue = queue
        self.handler = handler
        self.max_concurrent = max_concurrent
        self._running = False
        self._semaphore = asyncio.Semaphore(max_concurrent)
        self._tasks: set[asyncio.Task[None]] = set()
        self.processed_count = 0
        self.error_count = 0

    async def start(self) -> None:
        """Start consuming messages."""
        self._running = True
        while self._running:
            try:
                message = await asyncio.wait_for(self.queue.get(), timeout=0.1)
                task = asyncio.create_task(self._process_message(message))
                self._tasks.add(task)
                task.add_done_callback(self._tasks.discard)
            except asyncio.TimeoutError:
                continue

    async def stop(self) -> None:
        """Stop consuming and wait for pending tasks."""
        self._running = False
        if self._tasks:
            await asyncio.gather(*self._tasks, return_exceptions=True)

    async def _process_message(self, message: Message) -> None:
        """Process a single message with semaphore."""
        async with self._semaphore:
            try:
                await self.handler(message)
                self.processed_count += 1
            except Exception:
                self.error_count += 1
            finally:
                self.queue.task_done()


# =============================================================================
# Fixtures
# =============================================================================


@pytest.fixture
def message_queue() -> asyncio.Queue[Message]:
    """Provide a fresh message queue."""
    return asyncio.Queue()


@pytest.fixture
def processed_messages() -> list[Message]:
    """Track processed messages."""
    return []


@pytest.fixture
def message_handler(
    processed_messages: list[Message],
) -> Callable[[Message], Coroutine[Any, Any, None]]:
    """Handler that tracks processed messages."""

    async def handler(message: Message) -> None:
        await asyncio.sleep(0.01)
        processed_messages.append(message)

    return handler


# =============================================================================
# Tests (Solutions)
# =============================================================================


async def test_process_single_message(
    message_queue: asyncio.Queue[Message],
    processed_messages: list[Message],
    message_handler: Callable[[Message], Coroutine[Any, Any, None]],
) -> None:
    """Test consumer processes a single message."""
    consumer = MessageConsumer(message_queue, message_handler)

    # Put one message
    message = Message(id="msg1", payload={"data": "test"})
    await message_queue.put(message)

    # Start consumer in background
    consumer_task = asyncio.create_task(consumer.start())

    # Wait for processing
    await message_queue.join()

    # Stop consumer
    await consumer.stop()
    consumer_task.cancel()
    try:
        await consumer_task
    except asyncio.CancelledError:
        pass

    # Verify
    assert len(processed_messages) == 1
    assert processed_messages[0].id == "msg1"
    assert consumer.processed_count == 1


async def test_process_multiple_messages(
    message_queue: asyncio.Queue[Message],
    processed_messages: list[Message],
    message_handler: Callable[[Message], Coroutine[Any, Any, None]],
) -> None:
    """Test consumer processes multiple messages."""
    consumer = MessageConsumer(message_queue, message_handler)

    # Put 5 messages
    for i in range(5):
        await message_queue.put(Message(id=f"msg{i}", payload={"index": i}))

    # Start consumer
    consumer_task = asyncio.create_task(consumer.start())

    # Wait for all messages
    await message_queue.join()

    # Stop
    await consumer.stop()
    consumer_task.cancel()
    try:
        await consumer_task
    except asyncio.CancelledError:
        pass

    # Verify
    assert len(processed_messages) == 5
    assert consumer.processed_count == 5


async def test_error_handling(message_queue: asyncio.Queue[Message]) -> None:
    """Test consumer continues after handler errors."""
    processed: list[str] = []

    async def failing_handler(message: Message) -> None:
        if message.id == "fail":
            raise ValueError("Handler error")
        await asyncio.sleep(0.01)
        processed.append(message.id)

    consumer = MessageConsumer(message_queue, failing_handler)

    # Put messages including one that will fail
    await message_queue.put(Message(id="msg1", payload={}))
    await message_queue.put(Message(id="fail", payload={}))
    await message_queue.put(Message(id="msg2", payload={}))

    # Start consumer
    consumer_task = asyncio.create_task(consumer.start())

    # Wait for processing
    await message_queue.join()

    # Stop
    await consumer.stop()
    consumer_task.cancel()
    try:
        await consumer_task
    except asyncio.CancelledError:
        pass

    # Verify
    assert consumer.error_count == 1
    assert consumer.processed_count == 2
    assert "msg1" in processed
    assert "msg2" in processed


async def test_concurrent_processing(message_queue: asyncio.Queue[Message]) -> None:
    """Test consumer respects max_concurrent limit."""
    concurrent_count = 0
    max_concurrent_seen = 0
    lock = asyncio.Lock()

    async def tracking_handler(message: Message) -> None:
        nonlocal concurrent_count, max_concurrent_seen
        async with lock:
            concurrent_count += 1
            max_concurrent_seen = max(max_concurrent_seen, concurrent_count)
        try:
            await asyncio.sleep(0.02)  # Hold for a bit
        finally:
            async with lock:
                concurrent_count -= 1

    consumer = MessageConsumer(message_queue, tracking_handler, max_concurrent=2)

    # Put many messages
    for i in range(10):
        await message_queue.put(Message(id=f"msg{i}", payload={}))

    # Start consumer
    consumer_task = asyncio.create_task(consumer.start())

    # Wait for processing
    await message_queue.join()

    # Stop
    await consumer.stop()
    consumer_task.cancel()
    try:
        await consumer_task
    except asyncio.CancelledError:
        pass

    # Verify concurrency was limited
    assert max_concurrent_seen <= 2
    assert consumer.processed_count == 10


async def test_consumer_stop(
    message_queue: asyncio.Queue[Message],
    message_handler: Callable[[Message], Coroutine[Any, Any, None]],
) -> None:
    """Test consumer stops gracefully."""
    consumer = MessageConsumer(message_queue, message_handler)

    # Put some messages
    for i in range(3):
        await message_queue.put(Message(id=f"msg{i}", payload={}))

    # Start consumer
    consumer_task = asyncio.create_task(consumer.start())

    # Give it time to start processing
    await asyncio.sleep(0.05)

    # Stop should complete within timeout
    async with asyncio.timeout(1.0):
        await consumer.stop()
        consumer_task.cancel()
        try:
            await consumer_task
        except asyncio.CancelledError:
            pass


async def test_empty_queue_no_block(
    message_queue: asyncio.Queue[Message],
    message_handler: Callable[[Message], Coroutine[Any, Any, None]],
) -> None:
    """Test consumer doesn't block on empty queue."""
    consumer = MessageConsumer(message_queue, message_handler)

    # Start consumer with empty queue
    consumer_task = asyncio.create_task(consumer.start())

    # Should be able to stop quickly
    await asyncio.sleep(0.15)  # Let it loop a couple times

    async with asyncio.timeout(0.5):
        await consumer.stop()
        consumer_task.cancel()
        try:
            await consumer_task
        except asyncio.CancelledError:
            pass

    # Consumer should not have processed anything
    assert consumer.processed_count == 0


if __name__ == "__main__":
    import subprocess

    subprocess.run(["pytest", __file__, "-v"])
