"""Tests for System Prompts examples and core functionality."""

import pytest

from system_prompts.models import (
    SystemPrompt,
    PromptComponent,
    PromptIssue,
    AnalysisResult,
    IssueSeverity,
    PromptTemplate,
)
from system_prompts.builder import PromptBuilder, quick_prompt
from system_prompts.analyzer import analyze_prompt, analyze_text, quick_score
from system_prompts.templates import (
    code_reviewer_template,
    technical_writer_template,
    coding_assistant_template,
    data_analyst_template,
)


class TestSystemPromptModel:
    """Tests for SystemPrompt data model."""

    def test_create_system_prompt(self) -> None:
        """Test creating a SystemPrompt."""
        prompt = SystemPrompt(
            role="You are a Python expert.",
            context="Working on a web application.",
            instructions="Review the code for bugs.",
            constraints="Don't be too harsh.",
        )

        assert prompt.role == "You are a Python expert."
        assert prompt.has_component(PromptComponent.ROLE)

    def test_render_prompt(self) -> None:
        """Test rendering a prompt to string."""
        prompt = SystemPrompt(
            role="Expert",
            context="Web app",
            instructions="Review code",
            constraints="Be nice",
        )

        rendered = prompt.render()
        assert "ROLE:" in rendered
        assert "CONTEXT:" in rendered
        assert "INSTRUCTIONS:" in rendered
        assert "CONSTRAINTS:" in rendered

    def test_render_compact(self) -> None:
        """Test rendering without headers."""
        prompt = SystemPrompt(
            role="Expert",
            context="Web app",
            instructions="Review code",
            constraints="Be nice",
        )

        rendered = prompt.render_compact()
        assert "ROLE:" not in rendered
        assert "Expert" in rendered

    def test_word_count(self) -> None:
        """Test word count calculation."""
        prompt = SystemPrompt(
            role="one two three",
            context="four five",
            instructions="six seven eight nine",
            constraints="ten",
        )

        # Components: 3 + 2 + 4 + 1 = 10 words in components
        # Plus headers in render
        assert prompt.word_count > 10

    def test_missing_components(self) -> None:
        """Test detecting missing components."""
        prompt = SystemPrompt(
            role="Expert",
            context="",
            instructions="Do something",
            constraints="",
        )

        missing = prompt.missing_components
        assert PromptComponent.CONTEXT in missing
        assert PromptComponent.CONSTRAINTS in missing
        assert PromptComponent.ROLE not in missing


class TestPromptBuilder:
    """Tests for PromptBuilder fluent interface."""

    def test_basic_build(self) -> None:
        """Test building a basic prompt."""
        prompt = (
            PromptBuilder()
            .with_role("Python developer")
            .with_task("review code")
            .build()
        )

        assert "Python developer" in prompt.role
        assert "review code" in prompt.instructions

    def test_full_build(self) -> None:
        """Test building a complete prompt."""
        prompt = (
            PromptBuilder()
            .with_role("security engineer")
            .with_expertise(["penetration testing", "code review"])
            .with_experience(10, "application security")
            .with_context("fintech startup", "reviewing code for vulnerabilities")
            .with_audience("development team", "intermediate")
            .with_task("identify security issues")
            .with_output_format("markdown with severity ratings")
            .with_constraint("be constructive")
            .with_constraint("focus on security")
            .build()
        )

        assert "security engineer" in prompt.role
        assert "10+ years" in prompt.role
        assert "fintech startup" in prompt.context
        assert "identify security issues" in prompt.instructions
        assert "constructive" in prompt.constraints

    def test_build_requires_role(self) -> None:
        """Test that build fails without role."""
        builder = PromptBuilder().with_task("do something")

        with pytest.raises(ValueError, match="Role is required"):
            builder.build()

    def test_quick_prompt(self) -> None:
        """Test quick_prompt convenience function."""
        prompt = quick_prompt(
            role="Python developer",
            task="write unit tests",
            constraints=["use pytest", "mock external services"],
        )

        assert "Python developer" in prompt.role
        assert "unit tests" in prompt.instructions
        assert "pytest" in prompt.constraints


class TestAnalyzer:
    """Tests for prompt analyzer."""

    def test_analyze_good_prompt(self) -> None:
        """Test analyzing a well-structured prompt."""
        prompt = SystemPrompt(
            role="You are a senior Python developer with 10+ years of experience.",
            context="You are reviewing code for a fintech startup.",
            instructions="""Review the code for:
1. Security vulnerabilities
2. Performance issues
3. Code quality""",
            constraints="""- Don't be harsh
- Focus on important issues
- Provide code examples""",
        )

        result = analyze_prompt(prompt)

        assert result.score >= 60
        assert len(result.components_found) == 4

    def test_analyze_bad_prompt(self) -> None:
        """Test analyzing a poor prompt."""
        prompt = SystemPrompt(
            role="You are helpful.",
            context="",
            instructions="Help.",
            constraints="",
        )

        result = analyze_prompt(prompt)

        assert result.score < 50
        assert len(result.errors) > 0

    def test_analyze_detects_vague_language(self) -> None:
        """Test that vague language is flagged."""
        prompt = SystemPrompt(
            role="You are a helpful assistant who follows best practices.",
            context="You help appropriately.",
            instructions="Do good work properly.",
            constraints="Be appropriate.",
        )

        result = analyze_prompt(prompt)

        # Should have warnings about vague language
        vague_issues = [i for i in result.warnings if "vague" in i.message.lower()]
        assert len(vague_issues) > 0

    def test_quick_score(self) -> None:
        """Test quick_score function."""
        prompt = SystemPrompt(
            role="Expert developer",
            context="Tech company",
            instructions="Review code for bugs",
            constraints="Be nice",
        )

        score = quick_score(prompt)
        assert 0 <= score <= 100

    def test_analyze_text(self) -> None:
        """Test analyzing raw text."""
        text = """You are a Python expert.
Help with coding questions.
Don't be rude.
Focus on practical solutions."""

        result = analyze_text(text)
        assert result.score > 0
        assert result.word_count > 0


class TestTemplates:
    """Tests for built-in templates."""

    def test_code_reviewer_template(self) -> None:
        """Test code reviewer template generation."""
        prompt = code_reviewer_template(
            language="Python",
            focus_areas="security and performance",
            tone="constructive",
        )

        assert "Python" in prompt.role
        assert "security" in prompt.instructions
        result = analyze_prompt(prompt)
        assert result.score >= 70

    def test_technical_writer_template(self) -> None:
        """Test technical writer template generation."""
        prompt = technical_writer_template(
            doc_type="API documentation",
            audience="developers",
            style="concise",
        )

        assert "technical writer" in prompt.role.lower()
        assert "API" in prompt.context or "API" in prompt.role
        result = analyze_prompt(prompt)
        assert result.score >= 70

    def test_coding_assistant_template(self) -> None:
        """Test coding assistant template generation."""
        prompt = coding_assistant_template(
            language="Python",
            frameworks="FastAPI",
            skill_level="intermediate",
        )

        assert "Python" in prompt.role
        assert "FastAPI" in prompt.context or "FastAPI" in prompt.role
        result = analyze_prompt(prompt)
        assert result.score >= 70

    def test_data_analyst_template(self) -> None:
        """Test data analyst template generation."""
        prompt = data_analyst_template(
            data_type="sales metrics",
            tools="SQL and Python",
        )

        assert "data analyst" in prompt.role.lower()
        result = analyze_prompt(prompt)
        assert result.score >= 70


class TestPromptTemplate:
    """Tests for PromptTemplate model."""

    def test_template_render(self) -> None:
        """Test rendering a template with variables."""
        template = PromptTemplate(
            name="test",
            description="A test template",
            role_template="You are a {role}.",
            context_template="Working on {project}.",
            instructions_template="Do {task}.",
            constraints_template="Be {tone}.",
            variables=["role", "project", "task", "tone"],
        )

        prompt = template.render(
            role="developer",
            project="web app",
            task="coding",
            tone="helpful",
        )

        assert "developer" in prompt.role
        assert "web app" in prompt.context
        assert "coding" in prompt.instructions
        assert "helpful" in prompt.constraints

    def test_template_missing_variables(self) -> None:
        """Test that missing variables raise an error."""
        template = PromptTemplate(
            name="test",
            description="A test template",
            role_template="You are a {role}.",
            context_template="Working on {project}.",
            instructions_template="Do something.",
            constraints_template="Be nice.",
            variables=["role", "project"],
        )

        with pytest.raises(ValueError, match="Missing required variables"):
            template.render(role="developer")  # Missing 'project'


class TestExampleContent:
    """Tests for example content quality."""

    def test_example_1_prompt_quality(self) -> None:
        """Test that Example 1's prompt is high quality."""
        from system_prompts.examples.example_1 import EXAMPLE_PROMPT

        result = analyze_prompt(EXAMPLE_PROMPT)
        assert result.score >= 70
        assert len(result.components_found) == 4

    def test_example_3_bad_prompt_is_bad(self) -> None:
        """Test that Example 3's bad prompt scores poorly."""
        from system_prompts.examples.example_3 import BAD_PROMPT

        result = analyze_prompt(BAD_PROMPT)
        assert result.score < 60

    def test_example_3_improved_prompt_is_better(self) -> None:
        """Test that Example 3's improved prompt scores well."""
        from system_prompts.examples.example_3 import IMPROVED_PROMPT

        result = analyze_prompt(IMPROVED_PROMPT)
        assert result.score >= 70


class TestSolutions:
    """Tests for exercise solutions."""

    def test_solution_1_quality(self) -> None:
        """Test that Solution 1 meets requirements."""
        from system_prompts.exercises.solutions.solution_1 import solution

        prompt = solution()
        result = analyze_prompt(prompt)

        assert result.score >= 75
        assert 150 <= result.word_count <= 500
        assert len(result.components_found) == 4

    def test_solution_3_templates(self) -> None:
        """Test that Solution 3's templates work."""
        from system_prompts.exercises.solutions.solution_3 import solution

        registry = solution()
        templates = registry.list_templates()

        assert len(templates) >= 3

        for name in templates:
            template = registry.get(name)
            assert template is not None
            assert len(template.variables) >= 4

            # Test rendering with sample values
            values = {var: f"sample_{var}" for var in template.variables}
            prompt = template.render(**values)
            result = analyze_prompt(prompt)
            assert result.score >= 50  # Sample values won't be perfect
