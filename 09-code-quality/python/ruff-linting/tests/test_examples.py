"""Tests for Ruff Linting examples."""

import subprocess

import pytest


class TestExample1:
    """Tests for Example 1: Basic Linting and Formatting."""

    def test_example_runs_without_error(self) -> None:
        """Test that example 1 runs without error."""
        from ruff_linting.examples import example_1

        example_1.main()

    def test_demonstrate_ruff_check(self) -> None:
        """Test the ruff check demonstration."""
        from ruff_linting.examples.example_1 import demonstrate_ruff_check

        demonstrate_ruff_check()

    def test_demonstrate_ruff_format(self) -> None:
        """Test the ruff format demonstration."""
        from ruff_linting.examples.example_1 import demonstrate_ruff_format

        demonstrate_ruff_format()


class TestExample2:
    """Tests for Example 2: Rule Selection."""

    def test_example_runs_without_error(self) -> None:
        """Test that example 2 runs without error."""
        from ruff_linting.examples import example_2

        example_2.main()

    def test_demonstrate_rule_categories(self) -> None:
        """Test the rule categories demonstration."""
        from ruff_linting.examples.example_2 import demonstrate_rule_categories

        demonstrate_rule_categories()


class TestExample3:
    """Tests for Example 3: Editor and CI Integration."""

    def test_example_runs_without_error(self) -> None:
        """Test that example 3 runs without error."""
        from ruff_linting.examples import example_3

        example_3.main()

    def test_demonstrate_vscode_integration(self) -> None:
        """Test VS Code integration demonstration."""
        from ruff_linting.examples.example_3 import demonstrate_vscode_integration

        demonstrate_vscode_integration()


class TestRuffInstallation:
    """Tests that verify Ruff is properly installed."""

    def test_ruff_is_installed(self) -> None:
        """Test that Ruff is available."""
        result = subprocess.run(
            ["ruff", "--version"],
            capture_output=True,
            text=True,
        )
        assert result.returncode == 0
        assert "ruff" in result.stdout.lower()

    def test_ruff_check_works(self) -> None:
        """Test that ruff check command works."""
        result = subprocess.run(
            ["ruff", "check", "--help"],
            capture_output=True,
            text=True,
        )
        assert result.returncode == 0

    def test_ruff_format_works(self) -> None:
        """Test that ruff format command works."""
        result = subprocess.run(
            ["ruff", "format", "--help"],
            capture_output=True,
            text=True,
        )
        assert result.returncode == 0


class TestRuffOnProject:
    """Tests that run Ruff on this project."""

    @pytest.mark.slow
    def test_ruff_check_passes(self) -> None:
        """Test that ruff check passes on this project."""
        result = subprocess.run(
            ["ruff", "check", "src/", "tests/"],
            capture_output=True,
            text=True,
        )
        assert result.returncode == 0, f"Ruff check failed:\n{result.stdout}"

    @pytest.mark.slow
    def test_ruff_format_check_passes(self) -> None:
        """Test that ruff format --check passes on this project."""
        result = subprocess.run(
            ["ruff", "format", "--check", "src/", "tests/"],
            capture_output=True,
            text=True,
        )
        assert result.returncode == 0, f"Ruff format check failed:\n{result.stdout}"


class TestDocumentation:
    """Tests for documentation completeness."""

    def test_readme_exists(self) -> None:
        """Test that README.md exists and has content."""
        from pathlib import Path

        readme = Path(__file__).parent.parent / "README.md"
        assert readme.exists()
        content = readme.read_text()
        assert "Ruff" in content
        assert "Quick Start" in content

    def test_claude_md_exists(self) -> None:
        """Test that CLAUDE.md exists and has content."""
        from pathlib import Path

        claude_md = Path(__file__).parent.parent / "CLAUDE.md"
        assert claude_md.exists()
        content = claude_md.read_text()
        assert "Key Concepts" in content

    def test_concepts_doc_exists(self) -> None:
        """Test that concepts.md exists."""
        from pathlib import Path

        concepts = Path(__file__).parent.parent / "docs" / "concepts.md"
        assert concepts.exists()

    def test_patterns_doc_exists(self) -> None:
        """Test that patterns.md exists."""
        from pathlib import Path

        patterns = Path(__file__).parent.parent / "docs" / "patterns.md"
        assert patterns.exists()
