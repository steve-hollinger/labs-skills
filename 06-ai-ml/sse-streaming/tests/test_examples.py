"""Tests for SSE Streaming examples."""

import pytest
import httpx
from fastapi.testclient import TestClient


class TestServer:
    """Tests for the main SSE server."""

    def test_server_import(self):
        """Test server module can be imported."""
        from sse_streaming.server import app
        assert app is not None

    def test_root_endpoint(self):
        """Test root endpoint returns info."""
        from sse_streaming.server import app

        with TestClient(app) as client:
            response = client.get("/")
            assert response.status_code == 200
            data = response.json()
            assert "endpoints" in data

    def test_stream_endpoint_returns_sse(self):
        """Test stream endpoint returns SSE content type."""
        from sse_streaming.server import app

        with TestClient(app) as client:
            with client.stream("GET", "/stream?count=3&delay=0.1") as response:
                assert response.status_code == 200
                assert "text/event-stream" in response.headers["content-type"]

    def test_stream_endpoint_data_format(self):
        """Test stream returns proper SSE format."""
        from sse_streaming.server import app

        with TestClient(app) as client:
            with client.stream("GET", "/stream?count=3&delay=0.1") as response:
                lines = list(response.iter_lines())

                # Should have data lines
                data_lines = [l for l in lines if l.startswith("data: ")]
                assert len(data_lines) > 0

                # Should end with [DONE]
                assert any("[DONE]" in l for l in data_lines)

    def test_chat_endpoint_returns_sse(self):
        """Test chat endpoint returns SSE."""
        from sse_streaming.server import app

        with TestClient(app) as client:
            with client.stream("GET", "/chat?prompt=Hello") as response:
                assert response.status_code == 200
                assert "text/event-stream" in response.headers["content-type"]

    def test_chat_streams_content(self):
        """Test chat endpoint streams content."""
        from sse_streaming.server import app

        with TestClient(app) as client:
            with client.stream("GET", "/chat?prompt=Hello") as response:
                lines = list(response.iter_lines())
                data_lines = [l for l in lines if l.startswith("data: ") and "[DONE]" not in l]

                # Should have content events
                assert len(data_lines) > 0


class TestClient:
    """Tests for the SSE client."""

    def test_client_import(self):
        """Test client module can be imported."""
        from sse_streaming.client import consume_sse_sync, consume_sse_async, SSEClient
        assert consume_sse_sync is not None
        assert consume_sse_async is not None
        assert SSEClient is not None

    def test_sse_client_class(self):
        """Test SSEClient class initialization."""
        from sse_streaming.client import SSEClient

        client = SSEClient(base_url="http://localhost:8000")
        assert client.base_url == "http://localhost:8000"


class TestBasicSSE:
    """Tests for Example 1: Basic SSE."""

    def test_basic_sse_import(self):
        """Test basic SSE module can be imported."""
        from sse_streaming.examples.example_1_basic_sse import app
        assert app is not None

    def test_simple_endpoint(self):
        """Test simple message endpoint."""
        from sse_streaming.examples.example_1_basic_sse import app

        with TestClient(app) as client:
            with client.stream("GET", "/simple") as response:
                assert response.status_code == 200
                lines = list(response.iter_lines())
                data_lines = [l for l in lines if l.startswith("data: ")]
                assert len(data_lines) > 0

    def test_json_endpoint(self):
        """Test JSON data endpoint."""
        from sse_streaming.examples.example_1_basic_sse import app
        import json

        with TestClient(app) as client:
            with client.stream("GET", "/json") as response:
                lines = list(response.iter_lines())

                for line in lines:
                    if line.startswith("data: ") and "[DONE]" not in line:
                        data = line[6:]
                        # Should be valid JSON
                        parsed = json.loads(data)
                        assert "id" in parsed or "timestamp" in parsed

    def test_custom_events_endpoint(self):
        """Test custom events endpoint."""
        from sse_streaming.examples.example_1_basic_sse import app

        with TestClient(app) as client:
            with client.stream("GET", "/events") as response:
                lines = list(response.iter_lines())

                # Should have event type lines
                event_lines = [l for l in lines if l.startswith("event: ")]
                assert len(event_lines) > 0

                # Should have specific events
                event_types = [l.replace("event: ", "") for l in event_lines]
                assert "connected" in event_types or "start" in event_types


class TestLLMStreaming:
    """Tests for Example 2: LLM Streaming."""

    def test_llm_streaming_import(self):
        """Test LLM streaming module can be imported."""
        from sse_streaming.examples.example_2_llm_streaming import app
        assert app is not None

    def test_chat_endpoint(self):
        """Test chat endpoint returns streaming response."""
        from sse_streaming.examples.example_2_llm_streaming import app

        with TestClient(app) as client:
            with client.stream("GET", "/chat?prompt=Hello") as response:
                assert response.status_code == 200
                lines = list(response.iter_lines())

                # Should have content events
                content_found = False
                for line in lines:
                    if line.startswith("data: ") and "content" in line:
                        content_found = True
                        break
                assert content_found


class TestProductionPatterns:
    """Tests for Example 4: Production Patterns."""

    def test_production_import(self):
        """Test production patterns module can be imported."""
        from sse_streaming.examples.example_4_production_patterns import app
        assert app is not None

    def test_status_endpoint(self):
        """Test status endpoint."""
        from sse_streaming.examples.example_4_production_patterns import app

        with TestClient(app) as client:
            response = client.get("/status")
            assert response.status_code == 200
            data = response.json()
            assert "status" in data
            assert "active_connections" in data

    def test_robust_stream(self):
        """Test robust stream endpoint."""
        from sse_streaming.examples.example_4_production_patterns import app

        with TestClient(app) as client:
            with client.stream("GET", "/stream/robust?count=5") as response:
                assert response.status_code == 200
                lines = list(response.iter_lines())
                # Should have some data
                data_lines = [l for l in lines if l.startswith("data: ")]
                assert len(data_lines) > 0


class TestSolutions:
    """Tests for exercise solutions."""

    def test_solution_1_chat(self):
        """Test chat endpoint solution."""
        from sse_streaming.exercises.solutions.solution_1_chat_endpoint import app

        with TestClient(app) as client:
            with client.stream("GET", "/chat?prompt=Test") as response:
                assert response.status_code == 200
                assert "text/event-stream" in response.headers["content-type"]

                lines = list(response.iter_lines())
                data_lines = [l for l in lines if l.startswith("data: ")]
                assert len(data_lines) > 0

    def test_solution_2_progress(self):
        """Test progress streaming solution."""
        from sse_streaming.exercises.solutions.solution_2_progress_streaming import app

        with TestClient(app) as client:
            # Create a task
            response = client.post("/tasks")
            assert response.status_code == 200
            task_id = response.json()["task_id"]

            # Get task state
            response = client.get(f"/tasks/{task_id}")
            assert response.status_code == 200

    def test_solution_3_multi_source(self):
        """Test multi-source aggregation solution."""
        from sse_streaming.exercises.solutions.solution_3_multi_source import app

        with TestClient(app) as client:
            # Test individual source
            with client.stream("GET", "/stream/weather") as response:
                assert response.status_code == 200
                lines = list(response.iter_lines())
                data_lines = [l for l in lines if l.startswith("data: ") and "[DONE]" not in l]
                assert len(data_lines) > 0

            # Test aggregated - just check it starts
            with client.stream("GET", "/stream/all") as response:
                assert response.status_code == 200
                # Read just a few lines to verify it works
                count = 0
                for line in response.iter_lines():
                    count += 1
                    if count >= 3:
                        break
                assert count >= 1
