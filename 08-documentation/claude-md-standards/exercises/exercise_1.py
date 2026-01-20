"""Exercise 1: Write a CLAUDE.md for a Flask API

You've been given a Flask API project for a todo list application.
Write a complete CLAUDE.md file that would help an AI assistant
understand and work with this codebase.

Project Details:
- Framework: Flask with Flask-SQLAlchemy
- Database: PostgreSQL
- Authentication: JWT tokens
- Testing: pytest with pytest-flask
- Deployment: Docker + Kubernetes

Endpoints:
- POST /auth/register - Create new user
- POST /auth/login - Get JWT token
- GET /todos - List user's todos
- POST /todos - Create a todo
- PUT /todos/<id> - Update a todo
- DELETE /todos/<id> - Delete a todo

Project Structure:
app/
├── __init__.py
├── models/
│   ├── user.py
│   └── todo.py
├── routes/
│   ├── auth.py
│   └── todos.py
├── services/
│   └── todo_service.py
└── config.py
tests/
├── conftest.py
├── test_auth.py
└── test_todos.py

Instructions:
1. Write a complete CLAUDE.md with all essential sections
2. Include specific commands for setup, testing, and deployment
3. Document the code patterns used in this project
4. Add common mistakes and troubleshooting

Expected Output:
- A valid CLAUDE.md that scores 80+ on validation
- Contains at least 5 major sections
- Includes code examples for patterns

Hints:
- Start with the standard structure from Example 1
- Be specific about Flask-SQLAlchemy patterns
- Include JWT authentication guidance
- Document the test fixtures in conftest.py
"""


def exercise() -> str:
    """Write your CLAUDE.md content here.

    Returns:
        The complete CLAUDE.md content as a string.
    """
    # TODO: Replace this placeholder with your CLAUDE.md content
    claude_md_content = """# CLAUDE.md - Todo List API

    TODO: Complete this CLAUDE.md file

    ## Overview

    TODO: Describe the project

    ## Key Commands

    TODO: Add commands

    """

    return claude_md_content


def validate_solution() -> None:
    """Validate your solution."""
    from claude_md_standards.validator import validate_claude_md
    from rich.console import Console

    console = Console()
    content = exercise()

    result = validate_claude_md(content)

    console.print(f"\n[bold]Validation Score:[/bold] {result.score}/100")

    if result.score >= 80:
        console.print("[green]Excellent! Your CLAUDE.md meets the quality bar.[/green]")
    elif result.score >= 60:
        console.print("[yellow]Good start, but there's room for improvement.[/yellow]")
    else:
        console.print("[red]Needs more work. Review the issues below.[/red]")

    if result.issues:
        console.print("\n[bold]Issues to address:[/bold]")
        for issue in result.issues:
            console.print(f"  - {issue}")


if __name__ == "__main__":
    validate_solution()
