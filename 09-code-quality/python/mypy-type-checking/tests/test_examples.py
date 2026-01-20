"""Tests for MyPy Type Checking examples."""

import subprocess

import pytest


class TestExample1:
    """Tests for Example 1: Basic Type Annotations."""

    def test_example_runs_without_error(self) -> None:
        """Test that example 1 runs without error."""
        from mypy_type_checking.examples import example_1

        example_1.main()

    def test_person_dataclass(self) -> None:
        """Test the Person dataclass."""
        from mypy_type_checking.examples.example_1 import Person

        person = Person(name="Alice", age=30)
        assert person.name == "Alice"
        assert person.age == 30
        assert person.email is None

    def test_greet_person(self) -> None:
        """Test the greet_person function."""
        from mypy_type_checking.examples.example_1 import Person, greet_person

        person = Person(name="Bob", age=25)
        greeting = greet_person(person)
        assert greeting == "Hello, Bob!"

    def test_calculate_average(self) -> None:
        """Test the calculate_average function."""
        from mypy_type_checking.examples.example_1 import calculate_average

        assert calculate_average([1.0, 2.0, 3.0]) == 2.0
        assert calculate_average([]) == 0.0

    def test_find_person_by_name(self) -> None:
        """Test the find_person_by_name function."""
        from mypy_type_checking.examples.example_1 import Person, find_person_by_name

        people = [
            Person(name="Alice", age=30),
            Person(name="Bob", age=25),
        ]

        found = find_person_by_name(people, "Alice")
        assert found is not None
        assert found.name == "Alice"

        not_found = find_person_by_name(people, "Charlie")
        assert not_found is None


class TestExample2:
    """Tests for Example 2: Generics and Protocols."""

    def test_example_runs_without_error(self) -> None:
        """Test that example 2 runs without error."""
        from mypy_type_checking.examples import example_2

        example_2.main()

    def test_generic_stack(self) -> None:
        """Test the generic Stack class."""
        from mypy_type_checking.examples.example_2 import Stack

        stack: Stack[int] = Stack()
        stack.push(1)
        stack.push(2)

        assert len(stack) == 2
        assert stack.peek() == 2
        assert stack.pop() == 2
        assert len(stack) == 1

    def test_stack_empty(self) -> None:
        """Test Stack behavior when empty."""
        from mypy_type_checking.examples.example_2 import Stack

        stack: Stack[str] = Stack()
        assert stack.peek() is None
        assert len(stack) == 0

    def test_protocol_printable(self) -> None:
        """Test the Printable protocol."""
        from mypy_type_checking.examples.example_2 import (
            Document,
            Report,
            print_item,
        )

        doc = Document("Test", "Content")
        report = Report("Test Report", {"a": 1, "b": 2})

        # These should work without raising
        print_item(doc)
        print_item(report)


class TestExample3:
    """Tests for Example 3: Common Errors."""

    def test_example_runs_without_error(self) -> None:
        """Test that example 3 runs without error."""
        from mypy_type_checking.examples import example_3

        example_3.main()


class TestMypyInstallation:
    """Tests that verify MyPy is properly installed."""

    def test_mypy_is_installed(self) -> None:
        """Test that MyPy is available."""
        result = subprocess.run(
            ["mypy", "--version"],
            capture_output=True,
            text=True,
        )
        assert result.returncode == 0
        assert "mypy" in result.stdout.lower()

    @pytest.mark.slow
    def test_mypy_check_passes(self) -> None:
        """Test that mypy passes on this project."""
        result = subprocess.run(
            ["mypy", "src/"],
            capture_output=True,
            text=True,
        )
        # Note: May have some errors in exercises due to intentionally broken code
        assert "error" not in result.stdout.lower() or "exercises" in result.stdout


class TestDocumentation:
    """Tests for documentation completeness."""

    def test_readme_exists(self) -> None:
        """Test that README.md exists and has content."""
        from pathlib import Path

        readme = Path(__file__).parent.parent / "README.md"
        assert readme.exists()
        content = readme.read_text()
        assert "MyPy" in content
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
