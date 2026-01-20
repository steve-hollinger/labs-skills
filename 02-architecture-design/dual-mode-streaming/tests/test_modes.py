"""Tests for mode detection functionality."""

import pytest
from unittest.mock import MagicMock

from dual_mode_streaming.modes import (
    ResponseMode,
    detect_response_mode,
    ModeDetector,
)


class TestResponseMode:
    """Tests for ResponseMode enum."""

    def test_mode_values(self) -> None:
        """Test that modes have expected string values."""
        assert ResponseMode.BATCH.value == "batch"
        assert ResponseMode.STREAM.value == "stream"

    def test_mode_comparison(self) -> None:
        """Test mode comparison."""
        assert ResponseMode.BATCH == ResponseMode.BATCH
        assert ResponseMode.BATCH != ResponseMode.STREAM


class TestDetectResponseMode:
    """Tests for detect_response_mode function."""

    def create_mock_request(self, accept_header: str) -> MagicMock:
        """Create a mock request with given Accept header."""
        request = MagicMock()
        request.headers = {"accept": accept_header}
        return request

    def test_detects_stream_from_sse_header(self) -> None:
        """Test that text/event-stream triggers streaming mode."""
        request = self.create_mock_request("text/event-stream")
        mode = detect_response_mode(request)
        assert mode == ResponseMode.STREAM

    def test_detects_batch_from_json_header(self) -> None:
        """Test that application/json triggers batch mode."""
        request = self.create_mock_request("application/json")
        mode = detect_response_mode(request)
        assert mode == ResponseMode.BATCH

    def test_defaults_to_batch_for_unknown_header(self) -> None:
        """Test that unknown Accept headers default to batch."""
        request = self.create_mock_request("text/html")
        mode = detect_response_mode(request)
        assert mode == ResponseMode.BATCH

    def test_detects_stream_in_multiple_types(self) -> None:
        """Test that SSE is detected when mixed with other types."""
        request = self.create_mock_request("application/json, text/event-stream")
        mode = detect_response_mode(request)
        assert mode == ResponseMode.STREAM

    def test_handles_missing_accept_header(self) -> None:
        """Test handling when Accept header is missing."""
        request = MagicMock()
        request.headers = {}
        request.headers.get = lambda key, default="": default
        mode = detect_response_mode(request)
        assert mode == ResponseMode.BATCH


class TestModeDetector:
    """Tests for ModeDetector class."""

    def create_mock_request(self, accept_header: str) -> MagicMock:
        """Create a mock request with given Accept header."""
        request = MagicMock()
        request.headers = {"accept": accept_header}
        request.headers.get = lambda key, default="": request.headers.get(key, default)
        return request

    def test_default_configuration(self) -> None:
        """Test detector with default configuration."""
        detector = ModeDetector()
        assert detector.default_mode == ResponseMode.BATCH

    def test_custom_default_mode(self) -> None:
        """Test detector with custom default mode."""
        detector = ModeDetector(default_mode=ResponseMode.STREAM)
        request = self.create_mock_request("text/html")
        mode = detector.detect(request)
        assert mode == ResponseMode.STREAM

    def test_custom_stream_headers(self) -> None:
        """Test detector with custom streaming headers."""
        detector = ModeDetector(stream_headers=["application/x-ndjson"])
        request = self.create_mock_request("application/x-ndjson")
        mode = detector.detect(request)
        assert mode == ResponseMode.STREAM

    def test_callable_as_dependency(self) -> None:
        """Test that detector can be called directly."""
        detector = ModeDetector()
        request = self.create_mock_request("text/event-stream")
        mode = detector(request)
        assert mode == ResponseMode.STREAM

    def test_batch_headers_override(self) -> None:
        """Test explicit batch headers take precedence."""
        detector = ModeDetector(
            batch_headers=["application/json"],
            stream_headers=["text/event-stream"],
        )
        request = self.create_mock_request("application/json")
        mode = detector.detect(request)
        assert mode == ResponseMode.BATCH
