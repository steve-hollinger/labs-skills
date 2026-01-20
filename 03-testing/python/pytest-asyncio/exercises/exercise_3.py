"""Exercise 3: Test an Async Message Queue Consumer

Your task is to test the MessageConsumer class that processes messages
from an async queue with error handling and concurrency control.

Instructions:
1. Implement the missing test functions
2. Test message processing, error handling, and concurrency
3. Test the consumer lifecycle (start/stop)

Expected Tests:
- test_process_single_message: Consumer processes one message
- test_process_multiple_messages: Consumer processes a batch
- test_error_handling: Errors don't stop the consumer
- test_concurrent_processing: Messages processed concurrently
- test_consumer_stop: Consumer stops gracefully

Hints:
- Use asyncio.Queue for the message source
- Use asyncio.Event or Task cancellation to test stopping
- Track processed messages to verify behavior

Run your tests with:
    pytest exercises/exercise_3.py -v
"""

import asyncio
from dataclasses import dataclass
from typing import Any, Callable, Coroutine

import pytest  # noqa: F401


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
# TODO: Implement the tests below
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
def message_handler(processed_messages: list[Message]):
    """Handler that tracks processed messages."""

    async def handler(message: Message) -> None:
        await asyncio.sleep(0.01)  # Simulate processing
        processed_messages.append(message)

    return handler


async def test_process_single_message(
    message_queue: asyncio.Queue[Message],
    processed_messages: list[Message],
    message_handler: Callable[[Message], Coroutine[Any, Any, None]],
) -> None:
    """Test consumer processes a single message.

    TODO:
    1. Create a MessageConsumer with the queue and handler
    2. Put one message in the queue
    3. Start the consumer (use asyncio.create_task)
    4. Wait for the queue to be processed (queue.join())
    5. Stop the consumer
    6. Verify the message was processed
    """
    pass


async def test_process_multiple_messages(
    message_queue: asyncio.Queue[Message],
    processed_messages: list[Message],
    message_handler: Callable[[Message], Coroutine[Any, Any, None]],
) -> None:
    """Test consumer processes multiple messages.

    TODO:
    1. Put 5 messages in the queue
    2. Start the consumer
    3. Wait for all messages to be processed
    4. Stop the consumer
    5. Verify all messages were processed
    """
    pass


async def test_error_handling(message_queue: asyncio.Queue[Message]) -> None:
    """Test consumer continues after handler errors.

    TODO:
    1. Create a handler that raises an exception for message id "fail"
    2. Put messages including one that will fail
    3. Start the consumer and wait for processing
    4. Verify error_count is correct
    5. Verify other messages were still processed
    """
    pass


async def test_concurrent_processing(message_queue: asyncio.Queue[Message]) -> None:
    """Test consumer respects max_concurrent limit.

    TODO:
    1. Track concurrent execution count in the handler
    2. Create consumer with max_concurrent=2
    3. Put 5+ messages in the queue
    4. Verify that concurrent execution never exceeds 2
    """
    pass


async def test_consumer_stop(
    message_queue: asyncio.Queue[Message],
    message_handler: Callable[[Message], Coroutine[Any, Any, None]],
) -> None:
    """Test consumer stops gracefully.

    TODO:
    1. Start the consumer
    2. Put some messages in the queue
    3. Stop the consumer while messages are processing
    4. Verify stop() completes without hanging
    """
    pass


async def test_empty_queue_no_block(
    message_queue: asyncio.Queue[Message],
    message_handler: Callable[[Message], Coroutine[Any, Any, None]],
) -> None:
    """Test consumer doesn't block on empty queue.

    TODO:
    1. Start the consumer with an empty queue
    2. Verify the consumer can be stopped quickly
    (should not hang waiting for messages)
    """
    pass


if __name__ == "__main__":
    import subprocess

    subprocess.run(["pytest", __file__, "-v"])
