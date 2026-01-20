"""Exercise 3: Configuration File Scanner.

Build a scanner that:
1. Scans configuration files for secrets
2. Supports multiple formats (JSON, YAML, .env, INI)
3. Reports findings with severity levels
4. Suggests remediation actions

Expected usage:
    scanner = ConfigScanner()
    results = scanner.scan_file("config.json")

    for finding in results:
        print(f"{finding.severity}: {finding.description}")
        print(f"  Location: {finding.location}")
        print(f"  Remediation: {finding.remediation}")

Hints:
- Use different parsers for different formats
- Combine pattern matching with key name analysis
- Consider context (is it a template? a test file?)
"""

from __future__ import annotations

from dataclasses import dataclass, field
from enum import Enum
from pathlib import Path
from typing import Any


class Severity(Enum):
    """Severity levels for findings."""
    CRITICAL = "critical"  # Definitely a secret
    HIGH = "high"          # Likely a secret
    MEDIUM = "medium"      # Possibly sensitive
    LOW = "low"            # Worth reviewing
    INFO = "info"          # Informational


class FileFormat(Enum):
    """Supported file formats."""
    JSON = "json"
    YAML = "yaml"
    ENV = "env"
    INI = "ini"
    UNKNOWN = "unknown"


@dataclass
class Finding:
    """A security finding in a configuration file.

    Attributes:
        severity: How serious is this finding
        description: What was found
        location: Where it was found (file:line or file:key.path)
        value_masked: The masked sensitive value
        remediation: Suggested fix
        secret_type: Type of secret detected
    """
    severity: Severity
    description: str
    location: str
    value_masked: str
    remediation: str
    secret_type: str


@dataclass
class ScanResult:
    """Result of scanning a file.

    Attributes:
        file_path: Path to the scanned file
        file_format: Detected file format
        findings: List of security findings
        scan_duration_ms: How long the scan took
    """
    file_path: str
    file_format: FileFormat
    findings: list[Finding] = field(default_factory=list)
    scan_duration_ms: float = 0.0

    @property
    def has_critical(self) -> bool:
        """Check if any critical findings exist."""
        return any(f.severity == Severity.CRITICAL for f in self.findings)

    @property
    def finding_count(self) -> dict[Severity, int]:
        """Count findings by severity."""
        counts = {s: 0 for s in Severity}
        for f in self.findings:
            counts[f.severity] += 1
        return counts


class ConfigScanner:
    """Scanner for detecting secrets in configuration files.

    TODO: Implement this class with:
    - scan_file(path: str | Path) -> ScanResult
    - scan_content(content: str, format: FileFormat) -> list[Finding]
    - scan_directory(path: str | Path, recursive: bool) -> list[ScanResult]
    """

    def __init__(
        self,
        custom_patterns: dict[str, str] | None = None,
        sensitive_key_patterns: list[str] | None = None,
    ):
        """Initialize the scanner.

        Args:
            custom_patterns: Additional regex patterns to detect
            sensitive_key_patterns: Key names that indicate sensitive data
        """
        # TODO: Initialize patterns and configuration
        # Default sensitive key patterns: password, secret, key, token, etc.
        pass

    def _detect_format(self, path: Path) -> FileFormat:
        """Detect file format from extension.

        Args:
            path: Path to the file

        Returns:
            Detected FileFormat
        """
        # TODO: Detect format from extension
        raise NotImplementedError("Implement _detect_format")

    def _parse_json(self, content: str) -> dict[str, Any]:
        """Parse JSON content.

        Args:
            content: JSON string

        Returns:
            Parsed data
        """
        # TODO: Parse JSON
        raise NotImplementedError("Implement _parse_json")

    def _parse_yaml(self, content: str) -> dict[str, Any]:
        """Parse YAML content.

        Args:
            content: YAML string

        Returns:
            Parsed data
        """
        # TODO: Parse YAML (may need to add pyyaml dependency)
        raise NotImplementedError("Implement _parse_yaml")

    def _parse_env(self, content: str) -> dict[str, str]:
        """Parse .env file content.

        Args:
            content: .env file content

        Returns:
            Parsed key-value pairs
        """
        # TODO: Parse .env format (KEY=value lines)
        raise NotImplementedError("Implement _parse_env")

    def _parse_ini(self, content: str) -> dict[str, dict[str, str]]:
        """Parse INI file content.

        Args:
            content: INI file content

        Returns:
            Parsed sections and values
        """
        # TODO: Parse INI format
        raise NotImplementedError("Implement _parse_ini")

    def _scan_value(
        self,
        key: str,
        value: Any,
        path: str,
    ) -> list[Finding]:
        """Scan a single value for secrets.

        Args:
            key: The configuration key
            value: The value to scan
            path: The location path (e.g., "config.database.password")

        Returns:
            List of findings for this value
        """
        # TODO: Implement value scanning
        # Check both the key name and the value content
        raise NotImplementedError("Implement _scan_value")

    def _scan_dict(
        self,
        data: dict[str, Any],
        base_path: str = "",
    ) -> list[Finding]:
        """Recursively scan a dictionary.

        Args:
            data: Dictionary to scan
            base_path: Current path prefix

        Returns:
            List of all findings
        """
        # TODO: Recursively scan dictionary
        raise NotImplementedError("Implement _scan_dict")

    def _get_remediation(self, secret_type: str, key: str) -> str:
        """Get remediation suggestion for a finding.

        Args:
            secret_type: Type of secret detected
            key: The configuration key

        Returns:
            Remediation suggestion
        """
        # TODO: Return appropriate remediation based on secret type
        # Examples:
        # - "Use environment variable: ${DB_PASSWORD}"
        # - "Store in secrets manager and reference: arn:aws:..."
        # - "Use parameter store: /myapp/production/api_key"
        raise NotImplementedError("Implement _get_remediation")

    def scan_file(self, path: str | Path) -> ScanResult:
        """Scan a configuration file for secrets.

        Args:
            path: Path to the file

        Returns:
            ScanResult with findings
        """
        # TODO: Implement file scanning
        raise NotImplementedError("Implement scan_file")

    def scan_content(
        self,
        content: str,
        format: FileFormat,
        source: str = "input",
    ) -> list[Finding]:
        """Scan content string for secrets.

        Args:
            content: The content to scan
            format: File format for parsing
            source: Source identifier for findings

        Returns:
            List of findings
        """
        # TODO: Implement content scanning
        raise NotImplementedError("Implement scan_content")

    def scan_directory(
        self,
        path: str | Path,
        recursive: bool = True,
        patterns: list[str] | None = None,
    ) -> list[ScanResult]:
        """Scan all configuration files in a directory.

        Args:
            path: Directory path
            recursive: Whether to scan subdirectories
            patterns: File patterns to match (e.g., ["*.json", "*.yaml"])

        Returns:
            List of ScanResults
        """
        # TODO: Implement directory scanning
        raise NotImplementedError("Implement scan_directory")


def main() -> None:
    """Test your implementation."""
    print("Exercise 3: Configuration File Scanner")
    print("See the solution in solutions/solution_3.py")

    # Uncomment to test your implementation:
    #
    # scanner = ConfigScanner()
    #
    # # Create a test config file
    # test_config = '''
    # {
    #     "database": {
    #         "host": "localhost",
    #         "password": "super_secret_123"
    #     },
    #     "api": {
    #         "key": "sk_example_FAKE",
    #         "timeout": 30
    #     },
    #     "aws": {
    #         "access_key": "AKIAIOSFODNN7EXAMPLE",
    #         "secret_key": "wJalrXUtnFEMI/K7MDENG/bPxRfiCYEXAMPLEKEY"
    #     }
    # }
    # '''
    #
    # findings = scanner.scan_content(test_config, FileFormat.JSON)
    #
    # print("\nFindings:")
    # for finding in findings:
    #     print(f"\n[{finding.severity.value.upper()}] {finding.description}")
    #     print(f"  Location: {finding.location}")
    #     print(f"  Value: {finding.value_masked}")
    #     print(f"  Remediation: {finding.remediation}")


if __name__ == "__main__":
    main()
