"""Tests for UV Package Manager examples."""

import subprocess

import pytest


class TestExample1:
    """Tests for Example 1: Basic Project Setup."""

    def test_example_runs_without_error(self) -> None:
        """Test that example 1 runs without error."""
        from uv_package_manager.examples import example_1

        # The example prints educational content, should not raise
        example_1.main()

    def test_run_command_helper(self) -> None:
        """Test the run_command helper function."""
        from uv_package_manager.examples.example_1 import run_command

        # Test with a simple command
        exit_code, stdout, stderr = run_command(["echo", "hello"])
        assert exit_code == 0
        assert "hello" in stdout


class TestExample2:
    """Tests for Example 2: Lock Files."""

    def test_example_runs_without_error(self) -> None:
        """Test that example 2 runs without error."""
        from uv_package_manager.examples import example_2

        example_2.main()

    def test_demonstrates_lock_structure(self) -> None:
        """Test that lock structure demonstration runs."""
        from uv_package_manager.examples.example_2 import demonstrate_lock_file_structure

        # Should not raise
        demonstrate_lock_file_structure()


class TestExample3:
    """Tests for Example 3: Multi-Environment."""

    def test_example_runs_without_error(self) -> None:
        """Test that example 3 runs without error."""
        from uv_package_manager.examples import example_3

        example_3.main()

    def test_demonstrates_optional_dependencies(self) -> None:
        """Test optional dependencies demonstration."""
        from uv_package_manager.examples.example_3 import demonstrate_optional_dependencies

        demonstrate_optional_dependencies()

    def test_demonstrates_python_version_management(self) -> None:
        """Test Python version management demonstration."""
        from uv_package_manager.examples.example_3 import (
            demonstrate_python_version_management,
        )

        demonstrate_python_version_management()


class TestUVInstallation:
    """Tests that verify UV is properly installed."""

    def test_uv_is_installed(self) -> None:
        """Test that UV is available in PATH."""
        result = subprocess.run(
            ["uv", "--version"],
            capture_output=True,
            text=True,
        )
        assert result.returncode == 0
        assert "uv" in result.stdout.lower()

    @pytest.mark.slow
    def test_uv_can_sync(self) -> None:
        """Test that UV can sync this project."""
        result = subprocess.run(
            ["uv", "sync", "--all-extras"],
            capture_output=True,
            text=True,
        )
        assert result.returncode == 0


class TestDocumentation:
    """Tests for documentation completeness."""

    def test_readme_exists(self) -> None:
        """Test that README.md exists and has content."""
        from pathlib import Path

        readme = Path(__file__).parent.parent / "README.md"
        assert readme.exists()
        content = readme.read_text()
        assert "UV Package Manager" in content
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
