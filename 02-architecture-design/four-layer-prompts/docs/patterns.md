# Four-Layer Prompt Architecture Patterns

## Pattern 1: Basic Builder Pattern

The builder pattern provides a fluent interface for constructing prompts.

```python
from dataclasses import dataclass, field

@dataclass
class PromptBuilder:
    """Fluent builder for four-layer prompts."""

    _system: str = ""
    _context: str = ""
    _instruction: str = ""
    _constraint: str = ""
    _separator: str = "\n\n"

    def system(self, text: str) -> "PromptBuilder":
        self._system = text
        return self

    def context(self, text: str) -> "PromptBuilder":
        self._context = text
        return self

    def instruction(self, text: str) -> "PromptBuilder":
        self._instruction = text
        return self

    def constraint(self, text: str) -> "PromptBuilder":
        self._constraint = text
        return self

    def build(self) -> str:
        layers = [
            self._system,
            self._context,
            self._instruction,
            self._constraint,
        ]
        return self._separator.join(layer for layer in layers if layer)


# Usage
prompt = (
    PromptBuilder()
    .system("You are a Python expert.")
    .context("User is working on a FastAPI application.")
    .instruction("Review this code for best practices.")
    .constraint("List issues as bullet points.")
    .build()
)
```

**When to use**: When building prompts programmatically with clear, readable code.

## Pattern 2: Template Registry Pattern

Maintain a registry of reusable layer templates.

```python
from typing import Protocol
from string import Template

class LayerTemplate(Protocol):
    """Protocol for layer templates."""

    def render(self, **kwargs: str) -> str:
        ...

class StringTemplate:
    """Simple string template wrapper."""

    def __init__(self, template: str):
        self._template = Template(template)

    def render(self, **kwargs: str) -> str:
        return self._template.safe_substitute(**kwargs)


class TemplateRegistry:
    """Registry for prompt layer templates."""

    def __init__(self):
        self._systems: dict[str, LayerTemplate] = {}
        self._contexts: dict[str, LayerTemplate] = {}
        self._instructions: dict[str, LayerTemplate] = {}
        self._constraints: dict[str, LayerTemplate] = {}

    def register_system(self, name: str, template: LayerTemplate) -> None:
        self._systems[name] = template

    def register_context(self, name: str, template: LayerTemplate) -> None:
        self._contexts[name] = template

    def get_system(self, name: str) -> LayerTemplate:
        return self._systems[name]

    def get_context(self, name: str) -> LayerTemplate:
        return self._contexts[name]


# Setup registry
registry = TemplateRegistry()
registry.register_system(
    "code_reviewer",
    StringTemplate("You are an expert $language code reviewer with $years years of experience.")
)
registry.register_context(
    "code_review",
    StringTemplate("Code to review:\n```$language\n$code\n```")
)

# Usage
system = registry.get_system("code_reviewer").render(language="Python", years="10")
context = registry.get_context("code_review").render(language="python", code="def foo(): pass")
```

**When to use**: When managing many prompt templates across an application.

## Pattern 3: Composition Pipeline Pattern

Chain transformations to build complex prompts.

```python
from typing import Callable

LayerTransform = Callable[[str], str]

class PromptPipeline:
    """Pipeline for transforming and composing prompts."""

    def __init__(self):
        self._transforms: list[LayerTransform] = []

    def add_transform(self, transform: LayerTransform) -> "PromptPipeline":
        self._transforms.append(transform)
        return self

    def execute(self, initial: str = "") -> str:
        result = initial
        for transform in self._transforms:
            result = transform(result)
        return result


# Transform functions
def add_system(role: str) -> LayerTransform:
    def transform(prompt: str) -> str:
        system = f"You are a {role}."
        return f"{system}\n\n{prompt}" if prompt else system
    return transform

def add_context(data: str) -> LayerTransform:
    def transform(prompt: str) -> str:
        return f"{prompt}\n\nContext:\n{data}"
    return transform

def add_instruction(task: str) -> LayerTransform:
    def transform(prompt: str) -> str:
        return f"{prompt}\n\nTask: {task}"
    return transform

def add_constraint(constraint: str) -> LayerTransform:
    def transform(prompt: str) -> str:
        return f"{prompt}\n\nConstraints: {constraint}"
    return transform


# Usage
prompt = (
    PromptPipeline()
    .add_transform(add_system("technical writer"))
    .add_transform(add_context("API endpoint documentation"))
    .add_transform(add_instruction("Write user-friendly documentation"))
    .add_transform(add_constraint("Use markdown, max 500 words"))
    .execute()
)
```

**When to use**: When prompts need complex, conditional transformations.

## Pattern 4: Domain-Specific Layer Factory

Create factories for domain-specific prompt layers.

```python
from enum import Enum
from abc import ABC, abstractmethod

class UserLevel(Enum):
    BEGINNER = "beginner"
    INTERMEDIATE = "intermediate"
    EXPERT = "expert"

class LayerFactory(ABC):
    """Abstract factory for prompt layers."""

    @abstractmethod
    def create_system(self) -> str:
        pass

    @abstractmethod
    def create_context(self, data: dict) -> str:
        pass

    @abstractmethod
    def create_instruction(self, task: str) -> str:
        pass

    @abstractmethod
    def create_constraint(self, user_level: UserLevel) -> str:
        pass


class CodeReviewFactory(LayerFactory):
    """Factory for code review prompts."""

    def create_system(self) -> str:
        return """
You are a senior software engineer conducting code reviews.
You focus on code quality, security, performance, and maintainability.
You provide constructive feedback with specific suggestions.
"""

    def create_context(self, data: dict) -> str:
        return f"""
Code Review Context:
- Language: {data.get('language', 'Unknown')}
- Project: {data.get('project', 'Unknown')}
- File: {data.get('filename', 'Unknown')}

Code:
```{data.get('language', '')}
{data.get('code', '')}
```
"""

    def create_instruction(self, task: str) -> str:
        base = "Review this code and provide feedback on:\n"
        aspects = [
            "1. Code correctness and potential bugs",
            "2. Security vulnerabilities",
            "3. Performance considerations",
            "4. Code style and readability",
            "5. Test coverage suggestions",
        ]
        return base + "\n".join(aspects)

    def create_constraint(self, user_level: UserLevel) -> str:
        base = "Format your review as:\n- Summary\n- Issues (categorized)\n- Suggestions\n"

        if user_level == UserLevel.BEGINNER:
            return base + "Explain issues in simple terms with examples."
        elif user_level == UserLevel.EXPERT:
            return base + "Be concise, focus on non-obvious issues."
        return base


# Usage
factory = CodeReviewFactory()
prompt = "\n\n".join([
    factory.create_system(),
    factory.create_context({
        "language": "python",
        "project": "api-service",
        "filename": "auth.py",
        "code": "def login(user, pwd): ..."
    }),
    factory.create_instruction("security review"),
    factory.create_constraint(UserLevel.INTERMEDIATE),
])
```

**When to use**: When you have distinct domains requiring different prompt structures.

## Pattern 5: Version-Controlled Prompts

Track prompt versions for reproducibility and A/B testing.

```python
from datetime import datetime
from dataclasses import dataclass, field
from typing import Optional
import hashlib

@dataclass
class PromptVersion:
    """Version-controlled prompt with metadata."""

    system: str
    context_template: str
    instruction: str
    constraint: str
    version: str
    created_at: datetime = field(default_factory=datetime.now)
    description: str = ""

    @property
    def hash(self) -> str:
        """Generate hash of prompt content."""
        content = f"{self.system}{self.context_template}{self.instruction}{self.constraint}"
        return hashlib.sha256(content.encode()).hexdigest()[:12]

    def render(self, context_data: dict) -> str:
        """Render prompt with context data."""
        from string import Template
        context = Template(self.context_template).safe_substitute(**context_data)
        return f"{self.system}\n\n{context}\n\n{self.instruction}\n\n{self.constraint}"


class PromptVersionManager:
    """Manage multiple prompt versions."""

    def __init__(self):
        self._versions: dict[str, PromptVersion] = {}
        self._active_version: Optional[str] = None

    def register(self, version: PromptVersion) -> None:
        self._versions[version.version] = version

    def set_active(self, version: str) -> None:
        if version not in self._versions:
            raise ValueError(f"Version {version} not found")
        self._active_version = version

    def get_active(self) -> PromptVersion:
        if not self._active_version:
            raise ValueError("No active version set")
        return self._versions[self._active_version]

    def get_version(self, version: str) -> PromptVersion:
        return self._versions[version]

    def list_versions(self) -> list[str]:
        return list(self._versions.keys())


# Usage
manager = PromptVersionManager()

v1 = PromptVersion(
    system="You are a helpful assistant.",
    context_template="User question: $question",
    instruction="Answer the question thoroughly.",
    constraint="Use clear, simple language.",
    version="1.0.0",
    description="Initial version"
)

v2 = PromptVersion(
    system="You are an expert assistant with deep knowledge.",
    context_template="User question: $question\nUser level: $level",
    instruction="Provide a comprehensive answer.",
    constraint="Adjust complexity based on user level.",
    version="2.0.0",
    description="Added user level awareness"
)

manager.register(v1)
manager.register(v2)
manager.set_active("2.0.0")

prompt = manager.get_active().render({
    "question": "What is Python?",
    "level": "intermediate"
})
```

**When to use**: When you need to track, compare, and roll back prompt changes.

## Pattern 6: Conditional Layer Assembly

Assemble prompts conditionally based on runtime parameters.

```python
from typing import Optional
from enum import Enum, auto

class TaskType(Enum):
    SUMMARIZE = auto()
    ANALYZE = auto()
    GENERATE = auto()
    TRANSLATE = auto()

class ConditionalPromptAssembler:
    """Assemble prompts based on conditions."""

    def __init__(self):
        self._system_variants: dict[str, str] = {}
        self._context_builders: dict[TaskType, callable] = {}
        self._instruction_templates: dict[TaskType, str] = {}
        self._constraint_sets: dict[str, list[str]] = {}

    def register_system(self, name: str, system: str) -> None:
        self._system_variants[name] = system

    def register_context_builder(self, task: TaskType, builder: callable) -> None:
        self._context_builders[task] = builder

    def register_instruction(self, task: TaskType, instruction: str) -> None:
        self._instruction_templates[task] = instruction

    def register_constraints(self, name: str, constraints: list[str]) -> None:
        self._constraint_sets[name] = constraints

    def assemble(
        self,
        task_type: TaskType,
        system_variant: str = "default",
        context_data: Optional[dict] = None,
        constraint_set: str = "default",
        extra_constraints: Optional[list[str]] = None,
    ) -> str:
        # Get system
        system = self._system_variants.get(system_variant, "")

        # Build context
        context = ""
        if task_type in self._context_builders and context_data:
            context = self._context_builders[task_type](context_data)

        # Get instruction
        instruction = self._instruction_templates.get(task_type, "")

        # Assemble constraints
        constraints = self._constraint_sets.get(constraint_set, []).copy()
        if extra_constraints:
            constraints.extend(extra_constraints)
        constraint = "\n".join(f"- {c}" for c in constraints)

        # Compose
        parts = [p for p in [system, context, instruction, constraint] if p]
        return "\n\n".join(parts)


# Setup
assembler = ConditionalPromptAssembler()

assembler.register_system("default", "You are a helpful AI assistant.")
assembler.register_system("expert", "You are an expert analyst with deep domain knowledge.")

assembler.register_context_builder(
    TaskType.SUMMARIZE,
    lambda d: f"Document to summarize:\n{d.get('document', '')}"
)
assembler.register_context_builder(
    TaskType.ANALYZE,
    lambda d: f"Data to analyze:\n{d.get('data', '')}\nAnalysis type: {d.get('type', 'general')}"
)

assembler.register_instruction(TaskType.SUMMARIZE, "Provide a concise summary of the document.")
assembler.register_instruction(TaskType.ANALYZE, "Perform a thorough analysis of the data.")

assembler.register_constraints("default", ["Be concise", "Use clear language"])
assembler.register_constraints("detailed", ["Be thorough", "Include examples", "Cite sources"])

# Usage
prompt = assembler.assemble(
    task_type=TaskType.ANALYZE,
    system_variant="expert",
    context_data={"data": "sales figures...", "type": "trend analysis"},
    constraint_set="detailed",
    extra_constraints=["Format as bullet points"]
)
```

**When to use**: When prompts need to adapt significantly based on runtime conditions.

## Anti-Pattern: Prompt String Concatenation

```python
# BAD: Hard to maintain and test
prompt = "You are " + role + ". " + context + " " + task + " " + format_instructions

# GOOD: Use structured approach
prompt = PromptBuilder().system(role).context(context).instruction(task).constraint(format_instructions).build()
```

## Anti-Pattern: Embedded Format Instructions

```python
# BAD: Format mixed with instruction
instruction = "Write a summary in markdown format with bullet points under 100 words."

# GOOD: Separated concerns
instruction = "Write a summary of the key points."
constraint = "Format: Markdown with bullet points. Maximum: 100 words."
```
