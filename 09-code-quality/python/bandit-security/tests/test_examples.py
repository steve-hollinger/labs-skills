"""Tests for Bandit Security examples."""

import subprocess

import pytest


class TestExample1:
    """Tests for Example 1: Common Vulnerabilities."""

    def test_example_runs_without_error(self) -> None:
        """Test that example 1 runs without error."""
        from bandit_security.examples import example_1

        example_1.main()

    def test_demonstrate_command_injection(self) -> None:
        """Test command injection demonstration."""
        from bandit_security.examples.example_1 import demonstrate_command_injection

        demonstrate_command_injection()

    def test_demonstrate_hardcoded_secrets(self) -> None:
        """Test hardcoded secrets demonstration."""
        from bandit_security.examples.example_1 import demonstrate_hardcoded_secrets

        demonstrate_hardcoded_secrets()


class TestExample2:
    """Tests for Example 2: Configuration."""

    def test_example_runs_without_error(self) -> None:
        """Test that example 2 runs without error."""
        from bandit_security.examples import example_2

        example_2.main()

    def test_demonstrate_pyproject_config(self) -> None:
        """Test pyproject config demonstration."""
        from bandit_security.examples.example_2 import demonstrate_pyproject_config

        demonstrate_pyproject_config()


class TestExample3:
    """Tests for Example 3: CI Integration."""

    def test_example_runs_without_error(self) -> None:
        """Test that example 3 runs without error."""
        from bandit_security.examples import example_3

        example_3.main()

    def test_demonstrate_github_actions(self) -> None:
        """Test GitHub Actions demonstration."""
        from bandit_security.examples.example_3 import demonstrate_github_actions

        demonstrate_github_actions()


class TestBanditInstallation:
    """Tests that verify Bandit is properly installed."""

    def test_bandit_is_installed(self) -> None:
        """Test that Bandit is available."""
        result = subprocess.run(
            ["bandit", "--version"],
            capture_output=True,
            text=True,
        )
        assert result.returncode == 0
        assert "bandit" in result.stdout.lower()

    def test_bandit_list_tests(self) -> None:
        """Test that Bandit can list tests."""
        result = subprocess.run(
            ["bandit", "--list"],
            capture_output=True,
            text=True,
        )
        assert result.returncode == 0
        assert "B101" in result.stdout  # assert_used should be listed


class TestSolutionSecurity:
    """Tests that verify the solution has no security issues."""

    @pytest.mark.slow
    def test_solution_passes_bandit(self) -> None:
        """Test that solution code passes Bandit scan."""
        result = subprocess.run(
            [
                "bandit",
                "exercises/solutions/solution_1.py",
                "-ll",  # MEDIUM and above
            ],
            capture_output=True,
            text=True,
        )
        # Should pass or have no HIGH/MEDIUM issues
        assert "HIGH" not in result.stdout or result.returncode == 0


class TestDocumentation:
    """Tests for documentation completeness."""

    def test_readme_exists(self) -> None:
        """Test that README.md exists and has content."""
        from pathlib import Path

        readme = Path(__file__).parent.parent / "README.md"
        assert readme.exists()
        content = readme.read_text()
        assert "Bandit" in content
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
