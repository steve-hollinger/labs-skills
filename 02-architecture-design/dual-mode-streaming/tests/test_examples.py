"""Tests for example modules."""

import json
import pytest


class TestExample1BasicStreaming:
    """Tests for Example 1: Basic Streaming."""

    @pytest.mark.asyncio
    async def test_number_generator(self) -> None:
        """Test simple number generator produces correct output."""
        from dual_mode_streaming.examples.example_1_basic_streaming import (
            simple_number_generator,
        )

        results = []
        async for chunk in simple_number_generator():
            results.append(chunk)

        assert len(results) == 10

        # Parse first event
        first_chunk = results[0]
        assert first_chunk.startswith("data: ")
        data = json.loads(first_chunk[6:].strip())
        assert data["number"] == 1
        assert data["squared"] == 1

        # Parse last event
        last_chunk = results[-1]
        data = json.loads(last_chunk[6:].strip())
        assert data["number"] == 10
        assert data["squared"] == 100

    @pytest.mark.asyncio
    async def test_event_with_metadata_generator(self) -> None:
        """Test event generator with metadata."""
        from dual_mode_streaming.examples.example_1_basic_streaming import (
            event_with_metadata_generator,
        )

        results = []
        async for chunk in event_with_metadata_generator():
            results.append(chunk)

        assert len(results) == 5

        # First event should be "start"
        first = results[0]
        assert "event: start" in first
        assert "id: 1" in first

        # Last event should be "end"
        last = results[-1]
        assert "event: end" in last

    @pytest.mark.asyncio
    async def test_countdown_generator(self) -> None:
        """Test countdown generator."""
        from dual_mode_streaming.examples.example_1_basic_streaming import (
            countdown_generator,
        )

        results = []
        async for chunk in countdown_generator(start=3):
            results.append(chunk)

        # 3 countdown ticks + 1 complete event
        assert len(results) == 4

        # Verify countdown values
        assert "countdown" in results[0]
        assert '"countdown": 3' in results[0]

        # Verify completion
        assert "event: complete" in results[-1]


class TestExample2ModeDetection:
    """Tests for Example 2: Mode Detection."""

    @pytest.mark.asyncio
    async def test_data_service_batch(self) -> None:
        """Test DataService batch mode."""
        from dual_mode_streaming.examples.example_2_mode_detection import DataService

        service = DataService()
        items = await service.get_batch()

        assert len(items) == 5
        assert items[0]["id"] == 1
        assert items[0]["name"] == "Product 1"

    @pytest.mark.asyncio
    async def test_data_service_stream(self) -> None:
        """Test DataService stream mode."""
        from dual_mode_streaming.examples.example_2_mode_detection import DataService

        service = DataService()
        items = []

        async for item in service.get_stream():
            items.append(item)

        assert len(items) == 5
        assert items[0]["id"] == 1


class TestExample3LLMStreaming:
    """Tests for Example 3: LLM Streaming."""

    @pytest.mark.asyncio
    async def test_stream_tokens(self) -> None:
        """Test token streaming."""
        from dual_mode_streaming.examples.example_3_llm_streaming import (
            stream_tokens,
            ChatMessage,
        )

        messages = [ChatMessage(role="user", content="Hello")]
        completion_id = "test-123"

        chunks = []
        async for chunk in stream_tokens(messages, completion_id):
            chunks.append(chunk)

        # Should have multiple chunks + [DONE]
        assert len(chunks) > 2

        # All non-DONE chunks should be valid JSON
        for chunk in chunks[:-1]:
            assert chunk.startswith("data: ")
            data = json.loads(chunk[6:].strip())
            assert data["id"] == completion_id
            assert data["object"] == "chat.completion.chunk"

        # Last chunk should be [DONE]
        assert chunks[-1].strip() == "data: [DONE]"

    def test_get_response_text(self) -> None:
        """Test response selection based on prompt."""
        from dual_mode_streaming.examples.example_3_llm_streaming import (
            get_response_text,
            ChatMessage,
            DEMO_RESPONSES,
        )

        # Test hello response
        messages = [ChatMessage(role="user", content="Hello there!")]
        response = get_response_text(messages)
        assert response == DEMO_RESPONSES["hello"]

        # Test explain response
        messages = [ChatMessage(role="user", content="Please explain this")]
        response = get_response_text(messages)
        assert response == DEMO_RESPONSES["explain"]

        # Test default response
        messages = [ChatMessage(role="user", content="Random query")]
        response = get_response_text(messages)
        assert response == DEMO_RESPONSES["default"]


class TestExample4Backpressure:
    """Tests for Example 4: Backpressure."""

    @pytest.mark.asyncio
    async def test_bounded_stream_producer(self) -> None:
        """Test bounded queue producer/consumer."""
        from dual_mode_streaming.examples.example_4_backpressure import (
            BoundedStreamProducer,
        )
        import asyncio

        producer = BoundedStreamProducer(max_pending=3)

        # Start producer
        produce_task = asyncio.create_task(producer.produce(5))

        # Consume items
        items = []
        async for chunk in producer.consume():
            items.append(chunk)

        await produce_task

        assert len(items) == 5

    @pytest.mark.asyncio
    async def test_rate_limited_generator(self) -> None:
        """Test rate-limited generator."""
        from dual_mode_streaming.examples.example_4_backpressure import (
            rate_limited_generator,
        )

        results = []
        async for chunk in rate_limited_generator(max_concurrent=2):
            results.append(chunk)
            if len(results) >= 5:
                break

        assert len(results) >= 5

        # Verify format
        first_chunk = results[0]
        assert first_chunk.startswith("data: ")
        data = json.loads(first_chunk[6:].strip())
        assert "id" in data
        assert "result" in data

    @pytest.mark.asyncio
    async def test_timeout_controlled_generator(self) -> None:
        """Test timeout-controlled generator."""
        from dual_mode_streaming.examples.example_4_backpressure import (
            timeout_controlled_generator,
        )

        results = []
        timeout_count = 0

        async for chunk in timeout_controlled_generator(item_timeout=0.5):
            results.append(chunk)
            if "event: timeout" in chunk:
                timeout_count += 1

        # Should have some results
        assert len(results) == 10

        # Some items should timeout (those with id % 3 == 0)
        assert timeout_count > 0
