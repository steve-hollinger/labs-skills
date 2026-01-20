"""Exercise 1: Build a Code Review Prompt.

In this exercise, you'll create a four-layer prompt for conducting code reviews.
The prompt should be configurable for different programming languages and review focuses.

Requirements:
1. Create a PromptBuilder or PromptLayers for code review
2. System layer should define the reviewer's expertise and style
3. Context layer should include the code, language, and file information
4. Instruction layer should specify what aspects to review
5. Constraint layer should define the output format

Your prompt should work with these parameters:
- language: Programming language of the code
- code: The actual code to review
- filename: Name of the file
- focus: List of review focuses (e.g., ["security", "performance"])

Expected output format:
- Summary (1-2 sentences)
- Issues Found (categorized by focus area)
- Suggestions for Improvement

Test your implementation by creating prompts for:
1. A Python function with security focus
2. A JavaScript function with performance focus
"""

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

    TODO: Implement this function using PromptBuilder or PromptLayers

    Hints:
    - Use PromptBuilder for fluent construction
    - Format focus list as bullet points in the instruction
    - Include language-specific hints in the system layer
    """
    # Your implementation here
    raise NotImplementedError("Implement the code review prompt")


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

    # Verify key elements are present
    assert "security" in prompt.lower()
    assert code in prompt
    assert "auth.py" in prompt


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

    # Verify key elements
    assert "performance" in prompt.lower()
    assert "javascript" in prompt.lower()


if __name__ == "__main__":
    test_python_security_review()
    test_javascript_performance_review()
    print("\nAll tests passed!")
