"""Code documentation analysis utilities."""

import re
import ast
import inspect
from typing import Callable, Optional, Any

from component_documentation.models import DocstringInfo, DocumentationScore


def analyze_docstring(docstring: Optional[str]) -> DocstringInfo:
    """Parse and analyze a docstring.

    Args:
        docstring: The docstring to analyze.

    Returns:
        DocstringInfo with parsed components.
    """
    if not docstring:
        return DocstringInfo(summary="")

    lines = docstring.strip().split("\n")

    # Extract summary (first non-empty line)
    summary = ""
    description_lines = []
    args: dict[str, str] = {}
    returns: Optional[str] = None
    raises: dict[str, str] = {}
    examples: list[str] = []

    current_section = "description"
    current_item = ""
    current_content: list[str] = []

    for line in lines:
        stripped = line.strip()

        # Check for section headers
        if stripped.lower().startswith("args:"):
            current_section = "args"
            continue
        elif stripped.lower().startswith("returns:"):
            current_section = "returns"
            continue
        elif stripped.lower().startswith("raises:"):
            current_section = "raises"
            continue
        elif stripped.lower().startswith("example:") or stripped.lower().startswith("examples:"):
            current_section = "examples"
            continue
        elif stripped.lower().startswith("note:"):
            current_section = "note"
            continue

        # Process content based on section
        if current_section == "description":
            if not summary and stripped:
                summary = stripped
            elif stripped:
                description_lines.append(stripped)

        elif current_section == "args":
            # Check for new argument
            match = re.match(r"^(\w+):\s*(.*)$", stripped)
            if match:
                if current_item and current_content:
                    args[current_item] = " ".join(current_content)
                current_item = match.group(1)
                current_content = [match.group(2)] if match.group(2) else []
            elif current_item and stripped:
                current_content.append(stripped)

        elif current_section == "returns":
            if stripped:
                if returns is None:
                    returns = stripped
                else:
                    returns += " " + stripped

        elif current_section == "raises":
            match = re.match(r"^(\w+):\s*(.*)$", stripped)
            if match:
                if current_item and current_content:
                    raises[current_item] = " ".join(current_content)
                current_item = match.group(1)
                current_content = [match.group(2)] if match.group(2) else []
            elif current_item and stripped:
                current_content.append(stripped)

        elif current_section == "examples":
            if stripped:
                examples.append(stripped)

    # Don't forget the last item in args/raises
    if current_section == "args" and current_item and current_content:
        args[current_item] = " ".join(current_content)
    elif current_section == "raises" and current_item and current_content:
        raises[current_item] = " ".join(current_content)

    return DocstringInfo(
        summary=summary,
        description=" ".join(description_lines) if description_lines else "",
        args=args,
        returns=returns,
        raises=raises,
        examples=examples,
    )


def check_documentation(func: Callable[..., Any]) -> DocumentationScore:
    """Check documentation quality for a function.

    Args:
        func: The function to check.

    Returns:
        DocumentationScore with issues and suggestions.
    """
    score = DocumentationScore(score=100)

    # Check docstring exists
    docstring = func.__doc__
    if not docstring:
        score.add_issue("Missing docstring", penalty=30)
        return score

    # Parse docstring
    doc_info = analyze_docstring(docstring)

    # Check summary
    if not doc_info.summary:
        score.add_issue("Missing summary line", penalty=15)

    # Check for vague summary
    vague_patterns = ["does stuff", "handles", "processes", "function to"]
    if any(p in doc_info.summary.lower() for p in vague_patterns):
        score.add_suggestion("Consider making summary more specific")

    # Get function signature
    try:
        sig = inspect.signature(func)
        params = [
            name for name, param in sig.parameters.items()
            if name != "self" and param.kind not in (
                inspect.Parameter.VAR_POSITIONAL,
                inspect.Parameter.VAR_KEYWORD,
            )
        ]
    except (ValueError, TypeError):
        params = []

    # Check parameter documentation
    for param in params:
        if param not in doc_info.args:
            score.add_issue(f"Missing documentation for parameter '{param}'", penalty=5)

    # Check for undocumented params in docstring
    for arg_name in doc_info.args:
        if arg_name not in params and arg_name not in ["self", "cls"]:
            score.add_issue(f"Documented parameter '{arg_name}' not in signature", penalty=3)

    # Check return documentation
    try:
        return_annotation = sig.return_annotation
        has_return = return_annotation != inspect.Signature.empty and return_annotation is not None
        if has_return and not doc_info.returns:
            score.add_issue("Missing Returns documentation", penalty=10)
    except (ValueError, TypeError):
        pass

    # Check examples
    if not doc_info.examples:
        score.add_suggestion("Consider adding usage examples")

    # Check type hints
    try:
        hints = func.__annotations__
        if not hints:
            score.add_suggestion("Consider adding type hints")
    except AttributeError:
        pass

    return score


def generate_docstring(
    func_name: str,
    params: list[tuple[str, str, str]],  # (name, type, description)
    returns: Optional[tuple[str, str]] = None,  # (type, description)
    raises: Optional[list[tuple[str, str]]] = None,  # (exception, description)
    example: Optional[str] = None,
) -> str:
    """Generate a docstring template.

    Args:
        func_name: Name of the function.
        params: List of (name, type, description) tuples.
        returns: Optional (type, description) tuple.
        raises: Optional list of (exception, description) tuples.
        example: Optional example code.

    Returns:
        Formatted docstring string.
    """
    lines = [f'"""Brief description of {func_name}.', ""]

    if params:
        lines.append("Args:")
        for name, ptype, desc in params:
            lines.append(f"    {name}: {desc}")
        lines.append("")

    if returns:
        rtype, rdesc = returns
        lines.append("Returns:")
        lines.append(f"    {rdesc}")
        lines.append("")

    if raises:
        lines.append("Raises:")
        for exc, desc in raises:
            lines.append(f"    {exc}: {desc}")
        lines.append("")

    if example:
        lines.append("Example:")
        for line in example.strip().split("\n"):
            lines.append(f"    {line}")
        lines.append("")

    lines.append('"""')

    return "\n".join(lines)


def check_module_documentation(source_code: str) -> DocumentationScore:
    """Check documentation quality for a Python module.

    Args:
        source_code: Python source code as string.

    Returns:
        DocumentationScore for the module.
    """
    score = DocumentationScore(score=100)

    try:
        tree = ast.parse(source_code)
    except SyntaxError as e:
        score.add_issue(f"Syntax error in source: {e}", penalty=50)
        return score

    # Check module docstring
    if not (tree.body and isinstance(tree.body[0], ast.Expr) and isinstance(tree.body[0].value, ast.Constant)):
        score.add_issue("Missing module docstring", penalty=10)

    # Check function and class docstrings
    for node in ast.walk(tree):
        if isinstance(node, (ast.FunctionDef, ast.AsyncFunctionDef)):
            # Skip private functions
            if node.name.startswith("_") and not node.name.startswith("__"):
                continue

            docstring = ast.get_docstring(node)
            if not docstring:
                score.add_issue(f"Missing docstring for function '{node.name}'", penalty=5)
            else:
                doc_info = analyze_docstring(docstring)
                if doc_info.completeness_score < 50:
                    score.add_suggestion(
                        f"Docstring for '{node.name}' could be more complete"
                    )

        elif isinstance(node, ast.ClassDef):
            docstring = ast.get_docstring(node)
            if not docstring:
                score.add_issue(f"Missing docstring for class '{node.name}'", penalty=5)

    return score
