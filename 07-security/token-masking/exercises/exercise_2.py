"""Exercise 2: Custom Logging Formatter.

Create a configurable logging formatter that:
1. Masks secrets based on configurable rules
2. Supports different masking levels (full, partial, none)
3. Allows per-field configuration
4. Includes audit mode that logs what was masked

Expected usage:
    formatter = ConfigurableMaskingFormatter(
        format="%(asctime)s - %(message)s",
        rules={
            "password": MaskingRule(strategy="full"),
            "api_key": MaskingRule(strategy="partial", show=4),
            "username": MaskingRule(strategy="none"),
        }
    )

    handler = logging.StreamHandler()
    handler.setFormatter(formatter)

Hints:
- Extend logging.Formatter
- Use regex to find field patterns
- Consider thread safety for audit mode
"""

from __future__ import annotations

import logging
from dataclasses import dataclass, field
from enum import Enum
from typing import Any


class MaskingStrategy(Enum):
    """Available masking strategies."""
    FULL = "full"      # Replace entirely
    PARTIAL = "partial"  # Show some characters
    NONE = "none"      # Don't mask


@dataclass
class MaskingRule:
    """Configuration for masking a field.

    Attributes:
        strategy: How to mask the value
        show: Characters to show for partial masking
        placeholder: Replacement for full masking
        pattern: Optional regex pattern to match values
    """
    strategy: MaskingStrategy = MaskingStrategy.PARTIAL
    show: int = 4
    placeholder: str = "***MASKED***"
    pattern: str | None = None


@dataclass
class MaskingAuditEntry:
    """Record of a masking operation.

    TODO: Add fields:
    - timestamp: datetime
    - field_name: str
    - original_length: int
    - strategy_used: MaskingStrategy
    - logger_name: str
    """
    pass


class ConfigurableMaskingFormatter(logging.Formatter):
    """Logging formatter with configurable masking rules.

    TODO: Implement this class with:
    - __init__(fmt, datefmt, style, rules, audit_mode)
    - format(record) -> str
    - add_rule(field_name, rule)
    - remove_rule(field_name)
    - get_audit_log() -> list[MaskingAuditEntry]
    """

    def __init__(
        self,
        fmt: str | None = None,
        datefmt: str | None = None,
        style: str = "%",
        rules: dict[str, MaskingRule] | None = None,
        audit_mode: bool = False,
    ):
        """Initialize the formatter.

        Args:
            fmt: Log format string
            datefmt: Date format string
            style: Format style
            rules: Masking rules by field name
            audit_mode: Whether to record masking operations
        """
        # TODO: Initialize base class and store configuration
        super().__init__(fmt, datefmt, style)
        # TODO: Store rules and audit configuration
        raise NotImplementedError("Implement __init__")

    def add_rule(self, field_name: str, rule: MaskingRule) -> None:
        """Add or update a masking rule.

        Args:
            field_name: The field to mask
            rule: The masking rule to apply
        """
        # TODO: Add the rule
        raise NotImplementedError("Implement add_rule")

    def remove_rule(self, field_name: str) -> None:
        """Remove a masking rule.

        Args:
            field_name: The field to stop masking
        """
        # TODO: Remove the rule
        raise NotImplementedError("Implement remove_rule")

    def _apply_rule(self, value: str, rule: MaskingRule) -> str:
        """Apply a masking rule to a value.

        Args:
            value: The value to mask
            rule: The rule to apply

        Returns:
            Masked value
        """
        # TODO: Implement rule application
        raise NotImplementedError("Implement _apply_rule")

    def _mask_message(self, message: str) -> str:
        """Apply all masking rules to a message.

        Args:
            message: The log message

        Returns:
            Masked message
        """
        # TODO: Apply all rules to the message
        # Hint: Use regex to find patterns like field=value or "field": "value"
        raise NotImplementedError("Implement _mask_message")

    def format(self, record: logging.LogRecord) -> str:
        """Format a log record with masking.

        Args:
            record: The log record

        Returns:
            Formatted and masked log line
        """
        # TODO: Format with masking applied
        raise NotImplementedError("Implement format")

    def get_audit_log(self) -> list[MaskingAuditEntry]:
        """Get the audit log of masking operations.

        Returns:
            List of audit entries
        """
        # TODO: Return audit log (empty list if audit mode disabled)
        raise NotImplementedError("Implement get_audit_log")

    def clear_audit_log(self) -> None:
        """Clear the audit log."""
        # TODO: Clear the audit log
        raise NotImplementedError("Implement clear_audit_log")


def main() -> None:
    """Test your implementation."""
    print("Exercise 2: Custom Logging Formatter")
    print("See the solution in solutions/solution_2.py")

    # Uncomment to test your implementation:
    #
    # # Create formatter with rules
    # formatter = ConfigurableMaskingFormatter(
    #     fmt="%(asctime)s - %(levelname)s - %(message)s",
    #     datefmt="%H:%M:%S",
    #     rules={
    #         "password": MaskingRule(strategy=MaskingStrategy.FULL),
    #         "api_key": MaskingRule(strategy=MaskingStrategy.PARTIAL, show=4),
    #         "token": MaskingRule(
    #             strategy=MaskingStrategy.PARTIAL,
    #             show=8,
    #             pattern=r"ghp_[A-Za-z0-9]+"
    #         ),
    #     },
    #     audit_mode=True,
    # )
    #
    # # Set up logger
    # logger = logging.getLogger("test")
    # logger.setLevel(logging.DEBUG)
    # handler = logging.StreamHandler()
    # handler.setFormatter(formatter)
    # logger.addHandler(handler)
    #
    # # Log messages with secrets
    # logger.info("Login with password=secret123")
    # logger.info("Using api_key=sk_example_FAKE")
    # logger.info('Config: {"token": "ghp_xxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxx"}')
    #
    # # Check audit log
    # print("\nAudit log:")
    # for entry in formatter.get_audit_log():
    #     print(f"  - {entry}")


if __name__ == "__main__":
    main()
