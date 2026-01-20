"""Logging integration for token masking.

This module provides filters and formatters for automatically masking
sensitive data in log output.
"""

from __future__ import annotations

import logging
from typing import Any

from token_masking.masker import TokenMasker


class MaskingFilter(logging.Filter):
    """Filter that masks sensitive data in log records.

    This filter processes log messages and arguments to mask any
    detected secrets before they're written to log output.
    """

    def __init__(
        self,
        masker: TokenMasker | None = None,
        name: str = "",
    ):
        """Initialize the masking filter.

        Args:
            masker: TokenMasker instance to use, creates default if None
            name: Filter name
        """
        super().__init__(name)
        self.masker = masker or TokenMasker()

    def filter(self, record: logging.LogRecord) -> bool:
        """Filter and mask the log record.

        Args:
            record: The log record to process

        Returns:
            Always True (we modify, not filter out)
        """
        # Mask the message
        if isinstance(record.msg, str):
            record.msg = self.masker.mask_text(record.msg)

        # Mask string arguments
        if record.args:
            if isinstance(record.args, dict):
                record.args = {
                    k: self.masker.mask_text(str(v)) if isinstance(v, str) else v
                    for k, v in record.args.items()
                }
            else:
                record.args = tuple(
                    self.masker.mask_text(str(arg)) if isinstance(arg, str) else arg
                    for arg in record.args
                )

        return True


class MaskingFormatter(logging.Formatter):
    """Formatter that masks sensitive data in the final output.

    This formatter applies masking after formatting, ensuring any
    secrets in the final log line are masked.
    """

    def __init__(
        self,
        masker: TokenMasker | None = None,
        fmt: str | None = None,
        datefmt: str | None = None,
        style: str = "%",
    ):
        """Initialize the masking formatter.

        Args:
            masker: TokenMasker instance to use
            fmt: Log format string
            datefmt: Date format string
            style: Format style (%, {, or $)
        """
        super().__init__(fmt, datefmt, style)
        self.masker = masker or TokenMasker()

    def format(self, record: logging.LogRecord) -> str:
        """Format the log record and mask any secrets.

        Args:
            record: The log record to format

        Returns:
            Formatted and masked log line
        """
        # Get the formatted message
        formatted = super().format(record)

        # Apply masking
        return self.masker.mask_text(formatted)


class SafeLoggerAdapter(logging.LoggerAdapter):
    """Logger adapter that masks data before logging.

    This adapter provides a safer interface for logging by masking
    sensitive data at the point of logging.
    """

    def __init__(
        self,
        logger: logging.Logger,
        masker: TokenMasker | None = None,
        extra: dict[str, Any] | None = None,
    ):
        """Initialize the adapter.

        Args:
            logger: The underlying logger
            masker: TokenMasker instance to use
            extra: Extra context to include in all logs
        """
        super().__init__(logger, extra or {})
        self.masker = masker or TokenMasker()

    def process(
        self,
        msg: str,
        kwargs: dict[str, Any],
    ) -> tuple[str, dict[str, Any]]:
        """Process the logging call to mask sensitive data.

        Args:
            msg: The log message
            kwargs: Keyword arguments

        Returns:
            Processed (masked) message and kwargs
        """
        # Mask the message
        masked_msg = self.masker.mask_text(str(msg))

        # Mask any extra data
        if "extra" in kwargs:
            kwargs["extra"] = self.masker.mask_data(kwargs["extra"])

        return masked_msg, kwargs


def setup_masked_logging(
    logger: logging.Logger | str | None = None,
    level: int = logging.INFO,
    format_string: str | None = None,
    masker: TokenMasker | None = None,
    use_filter: bool = True,
    use_formatter: bool = False,
) -> logging.Logger:
    """Set up logging with automatic secret masking.

    Args:
        logger: Logger instance or name, None for root logger
        level: Logging level
        format_string: Custom format string
        masker: TokenMasker instance to use
        use_filter: Whether to add MaskingFilter
        use_formatter: Whether to use MaskingFormatter

    Returns:
        Configured logger instance
    """
    if logger is None:
        log = logging.getLogger()
    elif isinstance(logger, str):
        log = logging.getLogger(logger)
    else:
        log = logger

    log.setLevel(level)

    # Create handler if none exists
    if not log.handlers:
        handler = logging.StreamHandler()
        handler.setLevel(level)
        log.addHandler(handler)

    masker = masker or TokenMasker()

    # Apply masking filter
    if use_filter:
        log.addFilter(MaskingFilter(masker))

    # Apply masking formatter
    if use_formatter:
        format_str = format_string or "%(asctime)s - %(name)s - %(levelname)s - %(message)s"
        formatter = MaskingFormatter(masker, fmt=format_str)
        for handler in log.handlers:
            handler.setFormatter(formatter)

    return log


class ContextMaskingHandler(logging.Handler):
    """Handler that masks context-aware sensitive data.

    This handler maintains a list of known sensitive values and masks
    them even if they don't match predefined patterns.
    """

    def __init__(
        self,
        target_handler: logging.Handler,
        masker: TokenMasker | None = None,
    ):
        """Initialize the handler.

        Args:
            target_handler: The handler to wrap
            masker: TokenMasker instance to use
        """
        super().__init__()
        self.target_handler = target_handler
        self.masker = masker or TokenMasker()
        self._sensitive_values: set[str] = set()

    def add_sensitive_value(self, value: str) -> None:
        """Add a value to the list of sensitive values.

        Args:
            value: A value that should be masked when logged
        """
        if value and len(value) > 3:  # Don't mask very short strings
            self._sensitive_values.add(value)

    def remove_sensitive_value(self, value: str) -> None:
        """Remove a value from the sensitive values list.

        Args:
            value: The value to remove
        """
        self._sensitive_values.discard(value)

    def emit(self, record: logging.LogRecord) -> None:
        """Process and emit a log record.

        Args:
            record: The log record to emit
        """
        # Create a copy of the record
        masked_record = logging.LogRecord(
            record.name,
            record.levelno,
            record.pathname,
            record.lineno,
            record.msg,
            record.args,
            record.exc_info,
            record.funcName,
            record.stack_info,
        )

        # First mask using pattern detection
        if isinstance(masked_record.msg, str):
            masked_record.msg = self.masker.mask_text(masked_record.msg)

        # Then mask known sensitive values
        msg_str = str(masked_record.msg)
        for value in self._sensitive_values:
            if value in msg_str:
                masked = self.masker.mask_secret(value)
                msg_str = msg_str.replace(value, masked)
        masked_record.msg = msg_str

        # Emit to target handler
        self.target_handler.emit(masked_record)
