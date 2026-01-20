"""Exercise 1 Solution: Code Review Prompt."""

from four_layer_prompts.layers import PromptBuilder


def create_code_review_prompt(
    language: str,
    code: str,
    filename: str,
    focus: list[str],
) -> str:
    """Create a code review prompt using four-layer architecture.

    Args:
        language: Programming language (e.g., "python", "javascript")
        code: The code to review
        filename: Name of the source file
        focus: List of review focus areas

    Returns:
        Complete prompt string
    """
    # System layer - define reviewer identity and expertise
    system = f"""You are a senior {language.title()} developer conducting a thorough code review.
You have extensive experience in identifying {', '.join(focus)} issues.
You provide constructive, specific feedback with actionable suggestions.
You explain the reasoning behind your recommendations."""

    # Context layer - provide the code and metadata
    context = f"""Code to Review:
```{language}
{code}
```

File: {filename}
Language: {language.title()}
Review Focus Areas: {', '.join(focus)}"""

    # Instruction layer - specify what to do
    focus_items = '\n'.join(f"- {f.title()}" for f in focus)
    instruction = f"""Conduct a comprehensive code review focusing on:
{focus_items}

For each issue found:
1. Identify the specific location in the code
2. Explain why it's problematic
3. Provide a concrete fix or improvement"""

    # Constraint layer - define output format
    constraint = """Format your response as:

## Summary
(1-2 sentences overview of code quality)

## Issues Found
### [Category Name]
- **Issue**: [Description]
  - Location: [Line/Function]
  - Severity: [Critical/Warning/Info]
  - Fix: [Suggested solution]

## Suggestions for Improvement
- [Actionable improvement suggestions]

Keep the review focused and constructive. Maximum 500 words."""

    return (
        PromptBuilder()
        .system(system)
        .context(context)
        .instruction(instruction)
        .constraint(constraint)
        .build()
    )


# Alternative implementation using PromptLayers directly
def create_code_review_prompt_alt(
    language: str,
    code: str,
    filename: str,
    focus: list[str],
) -> str:
    """Alternative implementation using PromptLayers."""
    from four_layer_prompts.layers import PromptLayers

    focus_str = ", ".join(focus)

    layers = PromptLayers(
        system=f"You are an expert {language} code reviewer specializing in {focus_str}.",
        context=f"Review this code from {filename}:\n```{language}\n{code}\n```",
        instruction=f"Analyze the code for {focus_str} issues and provide specific feedback.",
        constraint="Use markdown formatting. List issues with severity and fixes.",
    )

    return layers.compose()


# Test cases
def test_python_security_review() -> None:
    """Test: Python code with security focus."""
    code = '''
def login(username, password):
    query = f"SELECT * FROM users WHERE username='{username}' AND password='{password}'"
    result = db.execute(query)
    return result.fetchone()
'''

    prompt = create_code_review_prompt(
        language="python",
        code=code,
        filename="auth.py",
        focus=["security", "best practices"],
    )

    print("Python Security Review Prompt:")
    print("-" * 50)
    print(prompt)
    print("-" * 50)

    assert "security" in prompt.lower()
    assert code in prompt
    assert "auth.py" in prompt
    print("Test passed!")


def test_javascript_performance_review() -> None:
    """Test: JavaScript code with performance focus."""
    code = '''
function processItems(items) {
    let results = [];
    for (let i = 0; i < items.length; i++) {
        for (let j = 0; j < items.length; j++) {
            if (items[i].id === items[j].relatedId) {
                results.push({...items[i], related: items[j]});
            }
        }
    }
    return results;
}
'''

    prompt = create_code_review_prompt(
        language="javascript",
        code=code,
        filename="processor.js",
        focus=["performance", "readability"],
    )

    print("\nJavaScript Performance Review Prompt:")
    print("-" * 50)
    print(prompt)
    print("-" * 50)

    assert "performance" in prompt.lower()
    assert "javascript" in prompt.lower()
    print("Test passed!")


if __name__ == "__main__":
    test_python_security_review()
    test_javascript_performance_review()
    print("\nAll tests passed!")
