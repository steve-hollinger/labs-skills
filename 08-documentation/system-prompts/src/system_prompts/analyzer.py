"""Analyzer for evaluating system prompt quality."""

import re
from typing import Optional

from system_prompts.models import (
    AnalysisResult,
    IssueSeverity,
    PromptComponent,
    SystemPrompt,
)


# Vague phrases that should be more specific
VAGUE_PHRASES = [
    (r"\bhelpful\b", "Define what 'helpful' means specifically"),
    (r"\bappropriate\b", "Specify what is appropriate"),
    (r"\bbest practices\b", "List the specific practices"),
    (r"\bproperly\b", "Define what 'properly' means"),
    (r"\bas needed\b", "Specify when it's needed"),
    (r"\bgood\b(?! example)", "Define what makes something 'good'"),
    (r"\bbad\b(?! example)", "Define what makes something 'bad'"),
    (r"\bcorrect\b", "Show what correct looks like"),
    (r"\bclean code\b", "Specify what makes code 'clean'"),
]

# Words that suggest the prompt has good specificity
SPECIFIC_INDICATORS = [
    r"\b\d+\b",  # Numbers
    r"```",  # Code blocks
    r"\bstep \d\b",  # Numbered steps
    r"\bfor example\b",  # Examples
    r"\bsuch as\b",  # Examples
    r"\bspecifically\b",  # Specific language
    r"\bexactly\b",  # Precise language
    r"\bmust\b",  # Strong requirements
    r"\bnever\b",  # Clear prohibitions
    r"\balways\b",  # Clear requirements
]


def analyze_prompt(
    prompt: SystemPrompt,
    strict: bool = False,
) -> AnalysisResult:
    """Analyze a system prompt for quality and completeness.

    Args:
        prompt: The SystemPrompt to analyze.
        strict: If True, apply stricter quality standards.

    Returns:
        AnalysisResult with score and issues.
    """
    result = AnalysisResult(score=100)
    full_text = prompt.render()

    # Track which components exist
    result.components_found = [c for c in PromptComponent if prompt.has_component(c)]

    # Calculate metrics
    result.word_count = prompt.word_count
    result.estimated_tokens = int(result.word_count * 1.3)  # Rough estimate

    # Check for missing components
    _check_components(prompt, result)

    # Check for vague language
    _check_vague_language(prompt, result)

    # Check for specificity
    _check_specificity(prompt, result, strict)

    # Check length
    _check_length(prompt, result)

    # Check structure
    _check_structure(prompt, result)

    # Ensure score stays in bounds
    result.score = max(0, min(100, result.score))

    return result


def _check_components(prompt: SystemPrompt, result: AnalysisResult) -> None:
    """Check for missing or weak components."""
    missing = prompt.missing_components

    if PromptComponent.ROLE in missing:
        result.add_issue(
            message="Missing role definition",
            severity=IssueSeverity.ERROR,
            component=PromptComponent.ROLE,
            suggestion="Add a clear role like 'You are a senior Python developer...'",
        )
        result.score -= 25

    if PromptComponent.INSTRUCTIONS in missing:
        result.add_issue(
            message="Missing instructions",
            severity=IssueSeverity.ERROR,
            component=PromptComponent.INSTRUCTIONS,
            suggestion="Add specific instructions for what the AI should do",
        )
        result.score -= 20

    if PromptComponent.CONTEXT in missing:
        result.add_issue(
            message="Missing context",
            severity=IssueSeverity.WARNING,
            component=PromptComponent.CONTEXT,
            suggestion="Add context about the environment and situation",
        )
        result.score -= 10

    if PromptComponent.CONSTRAINTS in missing:
        result.add_issue(
            message="Missing constraints",
            severity=IssueSeverity.WARNING,
            component=PromptComponent.CONSTRAINTS,
            suggestion="Add constraints for what the AI should avoid",
        )
        result.score -= 10

    # Check for weak components (present but too short)
    counts = prompt.component_counts

    if prompt.has_component(PromptComponent.ROLE) and counts[PromptComponent.ROLE] < 10:
        result.add_issue(
            message="Role definition is too brief",
            severity=IssueSeverity.WARNING,
            component=PromptComponent.ROLE,
            suggestion="Expand role with expertise areas and experience level",
        )
        result.score -= 5

    if prompt.has_component(PromptComponent.INSTRUCTIONS) and counts[PromptComponent.INSTRUCTIONS] < 15:
        result.add_issue(
            message="Instructions are too brief",
            severity=IssueSeverity.WARNING,
            component=PromptComponent.INSTRUCTIONS,
            suggestion="Add more detail about expected steps and output format",
        )
        result.score -= 5


def _check_vague_language(prompt: SystemPrompt, result: AnalysisResult) -> None:
    """Check for vague phrases that should be more specific."""
    full_text = prompt.render().lower()

    for pattern, suggestion in VAGUE_PHRASES:
        if re.search(pattern, full_text, re.IGNORECASE):
            # Find which component contains this
            component = None
            for comp in PromptComponent:
                comp_text = getattr(prompt, comp.value).lower()
                if re.search(pattern, comp_text, re.IGNORECASE):
                    component = comp
                    break

            result.add_issue(
                message=f"Vague language: '{pattern.replace(chr(92), '').replace('b', '')}'",
                severity=IssueSeverity.WARNING,
                component=component,
                suggestion=suggestion,
            )
            result.score -= 3


def _check_specificity(prompt: SystemPrompt, result: AnalysisResult, strict: bool) -> None:
    """Check that the prompt is specific enough."""
    full_text = prompt.render()

    # Count specificity indicators
    specificity_count = sum(
        1 for pattern in SPECIFIC_INDICATORS if re.search(pattern, full_text, re.IGNORECASE)
    )

    # Should have at least a few specific elements
    if specificity_count < 2:
        result.add_issue(
            message="Prompt lacks specific details",
            severity=IssueSeverity.WARNING if not strict else IssueSeverity.ERROR,
            suggestion="Add numbers, examples, or explicit requirements",
        )
        result.score -= 10 if strict else 5

    # Check for examples (highly valuable)
    has_example = bool(re.search(r"example|for instance|such as", full_text, re.IGNORECASE))
    has_code = "```" in full_text

    if not has_example and not has_code:
        result.add_issue(
            message="No examples provided",
            severity=IssueSeverity.SUGGESTION,
            suggestion="Include input/output examples to clarify expectations",
        )
        result.score -= 5


def _check_length(prompt: SystemPrompt, result: AnalysisResult) -> None:
    """Check prompt length is appropriate."""
    word_count = prompt.word_count

    if word_count < 30:
        result.add_issue(
            message="Prompt is too short",
            severity=IssueSeverity.ERROR,
            suggestion="Expand with more detail in role, context, and instructions",
        )
        result.score -= 15

    elif word_count < 75:
        result.add_issue(
            message="Prompt may be too brief",
            severity=IssueSeverity.WARNING,
            suggestion="Consider adding more context or examples",
        )
        result.score -= 5

    elif word_count > 1000:
        result.add_issue(
            message="Prompt may be too long",
            severity=IssueSeverity.WARNING,
            suggestion="Consider condensing or splitting into multiple prompts",
        )
        result.score -= 5


def _check_structure(prompt: SystemPrompt, result: AnalysisResult) -> None:
    """Check prompt structure and formatting."""
    full_text = prompt.render()

    # Check for numbered lists (good for instructions)
    if prompt.has_component(PromptComponent.INSTRUCTIONS):
        instructions = prompt.instructions
        has_list = bool(re.search(r"^\s*[\d\-\*]\.", instructions, re.MULTILINE))
        if len(instructions.split()) > 50 and not has_list:
            result.add_issue(
                message="Long instructions without numbered steps",
                severity=IssueSeverity.SUGGESTION,
                component=PromptComponent.INSTRUCTIONS,
                suggestion="Consider using numbered steps for clarity",
            )

    # Check for conflicting constraints
    constraints = prompt.constraints.lower()
    if "always" in constraints and "never" in constraints:
        # This is fine, but check for direct conflicts
        pass  # Would need more sophisticated analysis


def quick_score(prompt: SystemPrompt) -> int:
    """Get just the quality score without detailed analysis.

    Args:
        prompt: The SystemPrompt to score.

    Returns:
        Quality score from 0-100.
    """
    return analyze_prompt(prompt).score


def analyze_text(text: str) -> AnalysisResult:
    """Analyze raw prompt text (not structured).

    This tries to identify components in unstructured prompt text.

    Args:
        text: Raw prompt text.

    Returns:
        AnalysisResult with detected structure and issues.
    """
    # Try to detect components
    role = ""
    context = ""
    instructions = ""
    constraints = ""

    lines = text.split("\n")
    current_section = "role"  # Default to role

    for line in lines:
        line_lower = line.lower().strip()

        # Detect section headers
        if "role:" in line_lower or line_lower.startswith("you are"):
            current_section = "role"
        elif "context:" in line_lower or "working" in line_lower:
            current_section = "context"
        elif "instruct" in line_lower or "task:" in line_lower or "step" in line_lower:
            current_section = "instructions"
        elif "constraint" in line_lower or "don't" in line_lower or "never" in line_lower:
            current_section = "constraints"

        # Add line to appropriate section
        if current_section == "role":
            role += line + "\n"
        elif current_section == "context":
            context += line + "\n"
        elif current_section == "instructions":
            instructions += line + "\n"
        elif current_section == "constraints":
            constraints += line + "\n"

    prompt = SystemPrompt(
        role=role.strip(),
        context=context.strip(),
        instructions=instructions.strip(),
        constraints=constraints.strip(),
    )

    return analyze_prompt(prompt)
