"""Response mode detection and management."""

from enum import Enum
from typing import Literal

from fastapi import Query, Request


class ResponseMode(Enum):
    """Enumeration of supported response modes."""

    BATCH = "batch"
    STREAM = "stream"


def detect_response_mode(request: Request) -> ResponseMode:
    """Detect response mode from HTTP Accept header.

    Args:
        request: The incoming FastAPI request.

    Returns:
        ResponseMode.STREAM if client accepts text/event-stream,
        ResponseMode.BATCH otherwise.
    """
    accept_header = request.headers.get("accept", "application/json")

    if "text/event-stream" in accept_header:
        return ResponseMode.STREAM

    return ResponseMode.BATCH


def negotiate_mode(
    request: Request,
    stream: bool | None = Query(default=None, description="Explicit stream mode override"),
    format: Literal["stream", "batch", "auto"] | None = Query(
        default=None, description="Response format"
    ),
) -> ResponseMode:
    """Negotiate response mode with explicit override support.

    Priority:
    1. Explicit 'stream' query parameter (bool)
    2. Explicit 'format' query parameter
    3. Accept header detection
    4. Default to BATCH

    Args:
        request: The incoming FastAPI request.
        stream: Optional boolean to explicitly request streaming.
        format: Optional format string for explicit mode selection.

    Returns:
        The negotiated ResponseMode.
    """
    # Explicit stream bool takes highest priority
    if stream is not None:
        return ResponseMode.STREAM if stream else ResponseMode.BATCH

    # Format parameter takes second priority
    if format is not None:
        if format == "stream":
            return ResponseMode.STREAM
        if format == "batch":
            return ResponseMode.BATCH
        # format == "auto" falls through to header detection

    # Detect from Accept header
    return detect_response_mode(request)


class ModeDetector:
    """Configurable mode detection with custom rules."""

    def __init__(
        self,
        default_mode: ResponseMode = ResponseMode.BATCH,
        stream_headers: list[str] | None = None,
        batch_headers: list[str] | None = None,
    ) -> None:
        """Initialize the mode detector.

        Args:
            default_mode: Default mode when no detection matches.
            stream_headers: Accept header values that trigger streaming.
            batch_headers: Accept header values that force batch mode.
        """
        self.default_mode = default_mode
        self.stream_headers = stream_headers or ["text/event-stream"]
        self.batch_headers = batch_headers or ["application/json"]

    def detect(self, request: Request) -> ResponseMode:
        """Detect response mode based on configured rules.

        Args:
            request: The incoming FastAPI request.

        Returns:
            The detected ResponseMode.
        """
        accept = request.headers.get("accept", "")

        # Check for streaming headers first
        for header in self.stream_headers:
            if header in accept:
                return ResponseMode.STREAM

        # Check for explicit batch headers
        for header in self.batch_headers:
            if header in accept:
                return ResponseMode.BATCH

        return self.default_mode

    def __call__(self, request: Request) -> ResponseMode:
        """Allow using detector as a FastAPI dependency.

        Args:
            request: The incoming FastAPI request.

        Returns:
            The detected ResponseMode.
        """
        return self.detect(request)
