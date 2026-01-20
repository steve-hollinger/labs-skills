"""Dual-Mode Streaming - Sync and Async Response Patterns.

This module provides utilities and patterns for building APIs that support
both synchronous batch responses and asynchronous streaming responses.
"""

from dual_mode_streaming.modes import ResponseMode, detect_response_mode, negotiate_mode
from dual_mode_streaming.streaming import (
    SSEEvent,
    format_sse_event,
    format_sse_data,
    create_streaming_response,
)

__all__ = [
    "ResponseMode",
    "detect_response_mode",
    "negotiate_mode",
    "SSEEvent",
    "format_sse_event",
    "format_sse_data",
    "create_streaming_response",
]
