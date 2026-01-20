"""Solution 2: Custom Logging Formatter.

This solution demonstrates a configurable logging formatter with:
- Per-field masking rules
- Multiple masking strategies
- Audit logging of masking operations
- Thread-safe implementation
"""

from __future__ import annotations

import logging
import re
import threading
from dataclasses import dataclass, field
from datetime import datetime
from enum import Enum
from typing import Any


class MaskingStrategy(Enum):
    """Available masking strategies."""
    FULL = "full"
    PARTIAL = "partial"
    NONE = "none"


@dataclass
class MaskingRule:
    """Configuration for masking a field."""
    strategy: MaskingStrategy = MaskingStrategy.PARTIAL
    show: int = 4
    placeholder: str = "***MASKED***"
    pattern: str | None = None


@dataclass
class MaskingAuditEntry:
    """Record of a masking operation."""
    timestamp: datetime
    field_name: str
    original_length: int
    strategy_used: MaskingStrategy
    logger_name: str


class ConfigurableMaskingFormatter(logging.Formatter):
    """Logging formatter with configurable masking rules."""

    # Default patterns for finding field=value pairs
    FIELD_PATTERNS = [
        r"(\w+)\s*=\s*([^\s,;]+)",           # field=value
        r'"(\w+)"\s*:\s*"([^"]+)"',          # "field": "value"
        r"'(\w+)'\s*:\s*'([^']+)'",          # 'field': 'value'
        r"(\w+)\s*:\s*([^\s,;}\]]+)",        # field: value (YAML-style)
    ]

    def __init__(
        self,
        fmt: str | None = None,
        datefmt: str | None = None,
        style: str = "%",
        rules: dict[str, MaskingRule] | None = None,
        audit_mode: bool = False,
    ):
        """Initialize the formatter."""
        super().__init__(fmt, datefmt, style)

        self._rules: dict[str, MaskingRule] = rules or {}
        self._audit_mode = audit_mode
        self._audit_log: list[MaskingAuditEntry] = []
        self._lock = threading.Lock()

        # Compile field patterns
        self._compiled_patterns = [
            re.compile(pattern) for pattern in self.FIELD_PATTERNS
        ]

        # Compile custom patterns from rules
        self._custom_patterns: dict[str, re.Pattern] = {}
        for name, rule in self._rules.items():
            if rule.pattern:
                self._custom_patterns[name] = re.compile(rule.pattern)

    def add_rule(self, field_name: str, rule: MaskingRule) -> None:
        """Add or update a masking rule."""
        with self._lock:
            self._rules[field_name] = rule
            if rule.pattern:
                self._custom_patterns[field_name] = re.compile(rule.pattern)

    def remove_rule(self, field_name: str) -> None:
        """Remove a masking rule."""
        with self._lock:
            self._rules.pop(field_name, None)
            self._custom_patterns.pop(field_name, None)

    def _apply_rule(self, value: str, rule: MaskingRule) -> str:
        """Apply a masking rule to a value."""
        if rule.strategy == MaskingStrategy.NONE:
            return value

        if rule.strategy == MaskingStrategy.FULL:
            return rule.placeholder

        # Partial masking
        if len(value) <= rule.show:
            return rule.placeholder

        return value[:rule.show] + "***"

    def _record_audit(
        self,
        field_name: str,
        original_length: int,
        strategy: MaskingStrategy,
        logger_name: str,
    ) -> None:
        """Record a masking operation in the audit log."""
        if not self._audit_mode:
            return

        entry = MaskingAuditEntry(
            timestamp=datetime.now(),
            field_name=field_name,
            original_length=original_length,
            strategy_used=strategy,
            logger_name=logger_name,
        )

        with self._lock:
            self._audit_log.append(entry)

    def _mask_message(self, message: str, logger_name: str = "") -> str:
        """Apply all masking rules to a message."""
        result = message

        # Apply custom patterns first
        for name, pattern in self._custom_patterns.items():
            rule = self._rules.get(name)
            if rule:
                def replace_custom(match: re.Match, r: MaskingRule = rule, n: str = name) -> str:
                    original = match.group()
                    masked = self._apply_rule(original, r)
                    if original != masked:
                        self._record_audit(n, len(original), r.strategy, logger_name)
                    return masked

                result = pattern.sub(replace_custom, result)

        # Apply field-based patterns
        for pattern in self._compiled_patterns:
            def replace_field(match: re.Match) -> str:
                field_name = match.group(1).lower()
                field_value = match.group(2)

                rule = self._rules.get(field_name)
                if rule:
                    masked_value = self._apply_rule(field_value, rule)
                    if field_value != masked_value:
                        self._record_audit(
                            field_name, len(field_value), rule.strategy, logger_name
                        )
                    # Preserve original format
                    original = match.group()
                    return original.replace(field_value, masked_value)

                return match.group()

            result = pattern.sub(replace_field, result)

        return result

    def format(self, record: logging.LogRecord) -> str:
        """Format a log record with masking."""
        # First, format the record normally
        formatted = super().format(record)

        # Then apply masking
        return self._mask_message(formatted, record.name)

    def get_audit_log(self) -> list[MaskingAuditEntry]:
        """Get the audit log of masking operations."""
        with self._lock:
            return list(self._audit_log)

    def clear_audit_log(self) -> None:
        """Clear the audit log."""
        with self._lock:
            self._audit_log.clear()


def main() -> None:
    """Demonstrate the configurable masking formatter."""
    print("=" * 60)
    print("Solution 2: Custom Logging Formatter")
    print("=" * 60)

    # Create formatter with rules
    formatter = ConfigurableMaskingFormatter(
        fmt="%(asctime)s - %(levelname)s - %(message)s",
        datefmt="%H:%M:%S",
        rules={
            "password": MaskingRule(strategy=MaskingStrategy.FULL),
            "api_key": MaskingRule(strategy=MaskingStrategy.PARTIAL, show=4),
            "token": MaskingRule(
                strategy=MaskingStrategy.PARTIAL,
                show=8,
                pattern=r"ghp_[A-Za-z0-9]+"
            ),
            "secret": MaskingRule(strategy=MaskingStrategy.FULL),
            "ssn": MaskingRule(strategy=MaskingStrategy.PARTIAL, show=0),
        },
        audit_mode=True,
    )

    # Set up logger
    logger = logging.getLogger("demo.formatter")
    logger.setLevel(logging.DEBUG)
    logger.handlers.clear()

    handler = logging.StreamHandler()
    handler.setFormatter(formatter)
    logger.addHandler(handler)

    print("\n1. Logging with Masking")
    print("-" * 40)

    # Log messages with secrets
    logger.info("User login with password=secret123 successful")
    logger.info("Using api_key=sk_example_FAKE for API call")
    logger.info('Request headers: {"token": "ghp_xxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxx"}')
    logger.warning("Config contains secret=supersecretvalue")
    logger.debug("Processing SSN ssn=123-45-6789")

    # Check audit log
    print("\n2. Audit Log")
    print("-" * 40)
    for entry in formatter.get_audit_log():
        print(f"  [{entry.timestamp.strftime('%H:%M:%S')}] "
              f"Field: {entry.field_name}, "
              f"Strategy: {entry.strategy_used.value}, "
              f"Original length: {entry.original_length}")

    # Add a new rule dynamically
    print("\n3. Dynamic Rule Addition")
    print("-" * 40)

    formatter.add_rule(
        "credit_card",
        MaskingRule(strategy=MaskingStrategy.PARTIAL, show=4)
    )
    logger.info("Payment with credit_card=4111111111111111")

    # Remove a rule
    formatter.remove_rule("ssn")
    logger.info("SSN is now: ssn=987-65-4321")  # Won't be masked

    # Clear and check audit log
    print("\n4. After Rule Changes")
    print("-" * 40)
    recent_entries = formatter.get_audit_log()[-2:]
    for entry in recent_entries:
        print(f"  Field: {entry.field_name}, Strategy: {entry.strategy_used.value}")

    print("\n" + "=" * 60)
    print("Solution 2 Complete!")
    print("=" * 60)


if __name__ == "__main__":
    main()
