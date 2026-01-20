"""Example 2: Logging Integration.

This example demonstrates integrating token masking with Python logging:
- MaskingFilter for log records
- MaskingFormatter for final output
- SafeLoggerAdapter for safe logging API
- Context-aware masking

Run with: make example-2
"""

from __future__ import annotations

import logging
import sys

from token_masking import (
    MaskingFilter,
    MaskingFormatter,
    TokenMasker,
    setup_masked_logging,
)
from token_masking.logging_filter import (
    ContextMaskingHandler,
    SafeLoggerAdapter,
)


def demo_basic_filter() -> None:
    """Demonstrate basic MaskingFilter usage."""
    print("\n1. Basic MaskingFilter")
    print("-" * 40)

    # Create a logger with masking filter
    logger = logging.getLogger("demo.filter")
    logger.setLevel(logging.DEBUG)
    logger.handlers.clear()
    logger.filters.clear()

    handler = logging.StreamHandler(sys.stdout)
    handler.setFormatter(logging.Formatter("%(name)s - %(message)s"))
    logger.addHandler(handler)

    # Add masking filter
    masker = TokenMasker()
    logger.addFilter(MaskingFilter(masker))

    # Log messages with secrets
    logger.info("Starting application...")
    logger.info("Using API key: sk_example_FAKE")
    logger.info("Connecting to postgres://user:password123@db.example.com")
    logger.warning("Failed to connect with token ghp_xxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxx")

    # Secrets are automatically masked!


def demo_masking_formatter() -> None:
    """Demonstrate MaskingFormatter for final output masking."""
    print("\n2. MaskingFormatter")
    print("-" * 40)

    logger = logging.getLogger("demo.formatter")
    logger.setLevel(logging.DEBUG)
    logger.handlers.clear()
    logger.filters.clear()

    # Create handler with masking formatter
    handler = logging.StreamHandler(sys.stdout)
    masker = TokenMasker()
    formatter = MaskingFormatter(
        masker,
        fmt="%(asctime)s - %(levelname)s - %(message)s",
        datefmt="%H:%M:%S",
    )
    handler.setFormatter(formatter)
    logger.addHandler(handler)

    # Log messages - formatter masks the final output
    logger.info("AWS Key: AKIAIOSFODNN7EXAMPLE")
    logger.debug("Secret config: {'password': 'secret123', 'key': 'abc'}")


def demo_safe_logger_adapter() -> None:
    """Demonstrate SafeLoggerAdapter for safe logging API."""
    print("\n3. SafeLoggerAdapter")
    print("-" * 40)

    # Create base logger
    base_logger = logging.getLogger("demo.adapter")
    base_logger.setLevel(logging.DEBUG)
    base_logger.handlers.clear()
    base_logger.filters.clear()

    handler = logging.StreamHandler(sys.stdout)
    handler.setFormatter(logging.Formatter("%(message)s"))
    base_logger.addHandler(handler)

    # Wrap with SafeLoggerAdapter
    masker = TokenMasker()
    safe_logger = SafeLoggerAdapter(base_logger, masker)

    # Log with confidence - secrets will be masked
    api_key = "sk_example_FAKE"
    safe_logger.info(f"Processing request with key {api_key}")
    safe_logger.warning("Token ghp_actualTokenValueHere123456789012 expired")


def demo_context_masking() -> None:
    """Demonstrate context-aware masking for known secrets."""
    print("\n4. Context-Aware Masking")
    print("-" * 40)

    # Create logger with context masking handler
    base_logger = logging.getLogger("demo.context")
    base_logger.setLevel(logging.DEBUG)
    base_logger.handlers.clear()
    base_logger.filters.clear()

    base_handler = logging.StreamHandler(sys.stdout)
    base_handler.setFormatter(logging.Formatter("%(message)s"))

    # Wrap handler with context masking
    masker = TokenMasker()
    context_handler = ContextMaskingHandler(base_handler, masker)
    base_logger.addHandler(context_handler)

    # Register known sensitive values
    database_password = "MySecretDbPass123!"
    api_secret = "custom-api-secret-that-doesnt-match-patterns"

    context_handler.add_sensitive_value(database_password)
    context_handler.add_sensitive_value(api_secret)

    # These will be masked even though they don't match predefined patterns
    base_logger.info(f"Database password is: {database_password}")
    base_logger.info(f"Using API secret: {api_secret}")
    base_logger.info("Normal message without secrets")


def demo_setup_helper() -> None:
    """Demonstrate the setup_masked_logging helper."""
    print("\n5. setup_masked_logging Helper")
    print("-" * 40)

    # Quick setup with helper function
    logger = setup_masked_logging(
        "demo.setup",
        level=logging.DEBUG,
        format_string="%(levelname)s: %(message)s",
        use_filter=True,
    )

    # Remove any duplicate handlers from previous runs
    while len(logger.handlers) > 1:
        logger.handlers.pop()

    logger.info("This is safe to log with sk_example_FAKE")
    logger.debug("JWT: eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJzdWIiOiIxMjM0NTY3ODkwIn0.dozjgNryP4J3jVmNHl0w5N_XgL0n3I9PlFUP0THsR8U")


def demo_exception_logging() -> None:
    """Demonstrate handling exceptions with secrets."""
    print("\n6. Exception Handling")
    print("-" * 40)

    logger = logging.getLogger("demo.exception")
    logger.setLevel(logging.DEBUG)
    logger.handlers.clear()
    logger.filters.clear()

    handler = logging.StreamHandler(sys.stdout)
    handler.setFormatter(logging.Formatter("%(message)s"))
    logger.addHandler(handler)

    masker = TokenMasker()
    logger.addFilter(MaskingFilter(masker))

    # Simulate an exception that might contain secrets
    connection_string = "postgres://admin:secretpass123@db.example.com/mydb"

    try:
        raise ConnectionError(f"Failed to connect to {connection_string}")
    except ConnectionError:
        # Exception message will be masked
        logger.exception("Database connection failed")


def main() -> None:
    """Demonstrate logging integration."""
    print("=" * 60)
    print("Example 2: Logging Integration")
    print("=" * 60)

    demo_basic_filter()
    demo_masking_formatter()
    demo_safe_logger_adapter()
    demo_context_masking()
    demo_setup_helper()
    demo_exception_logging()

    print("\n" + "=" * 60)
    print("Example 2 Complete!")
    print("=" * 60)
    print("\nKey Takeaways:")
    print("- Use MaskingFilter for log record processing")
    print("- Use MaskingFormatter for final output masking")
    print("- Use SafeLoggerAdapter for a safe logging API")
    print("- Use ContextMaskingHandler for known sensitive values")


if __name__ == "__main__":
    main()
