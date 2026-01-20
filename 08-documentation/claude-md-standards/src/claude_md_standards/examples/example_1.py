"""Example 1: Basic CLAUDE.md Structure

This example demonstrates the essential components every CLAUDE.md should have.
It shows how to structure sections, what content belongs in each, and how to
make guidance actionable for AI assistants.
"""

from rich.console import Console
from rich.markdown import Markdown
from rich.panel import Panel

from claude_md_standards.parser import parse_claude_md
from claude_md_standards.validator import validate_claude_md


# A well-structured CLAUDE.md example
GOOD_CLAUDE_MD = """# CLAUDE.md - User Authentication Service

A FastAPI-based authentication service handling user registration, login, and session management.

## Overview

This service provides:
- User registration with email verification
- JWT-based authentication
- Session management with Redis
- Password reset functionality

All endpoints are RESTful and return JSON responses.

## Key Commands

```bash
# Development
make setup          # Install dependencies with UV
make dev            # Start with hot-reload on port 8000
make test           # Run pytest with coverage

# Database
make db-migrate     # Apply pending migrations
make db-seed        # Populate test data

# Code Quality
make lint           # Ruff + mypy checks
make format         # Auto-format with ruff
```

## Architecture

### Why FastAPI?
- Async support for high concurrency
- Automatic OpenAPI documentation
- Native Pydantic integration

### Authentication Flow
1. User submits credentials to `/auth/login`
2. Service validates against database
3. JWT token returned with 24h expiry
4. Token required in Authorization header for protected routes

## Code Patterns

### Request Validation
```python
from pydantic import BaseModel, EmailStr

class UserCreate(BaseModel):
    email: EmailStr
    password: str = Field(min_length=8)
    name: str = Field(min_length=1, max_length=100)
```

### Error Responses
```python
from fastapi import HTTPException

# Good - specific error with context
raise HTTPException(
    status_code=404,
    detail={"error": "user_not_found", "user_id": user_id}
)

# Bad - generic error
raise HTTPException(status_code=404, detail="Not found")
```

## Common Mistakes

1. **Storing plain-text passwords**
   - Always use bcrypt via `passlib`
   - Never log password values

2. **Missing rate limiting**
   - All auth endpoints have rate limits
   - Check `app/middleware/rate_limit.py`

3. **JWT in URL parameters**
   - Always use Authorization header
   - Never pass tokens in query strings

## When Users Ask About...

### "How do I add a new endpoint?"
1. Add route in `app/routes/`
2. Add handler in `app/handlers/`
3. Add Pydantic models in `app/models/`
4. Add tests in `tests/api/`

### "Why is authentication failing?"
- Check Redis is running: `docker-compose ps`
- Verify JWT secret is set: `echo $JWT_SECRET`
- Check token expiry in response

### "How do I run just one test?"
```bash
pytest tests/api/test_auth.py::test_login_success -v
```

## Testing Notes

- Unit tests mock external services
- Integration tests require Redis (started by `make test`)
- E2E tests in `tests/e2e/` require full stack

## Dependencies

Key dependencies:
- fastapi: Web framework
- passlib[bcrypt]: Password hashing
- python-jose: JWT handling
- redis: Session storage
"""


def main() -> None:
    """Run the basic CLAUDE.md structure example."""
    console = Console()

    console.print(Panel.fit(
        "[bold blue]Example 1: Basic CLAUDE.md Structure[/bold blue]\n"
        "Learn the essential components every CLAUDE.md should have.",
        title="CLAUDE.md Standards"
    ))

    # Show the example document
    console.print("\n[bold]A Well-Structured CLAUDE.md:[/bold]\n")
    console.print(Markdown(GOOD_CLAUDE_MD))

    # Parse and analyze
    console.print("\n" + "=" * 60)
    console.print("[bold]Analysis of This CLAUDE.md:[/bold]\n")

    doc = parse_claude_md(GOOD_CLAUDE_MD)

    console.print(f"[cyan]Title:[/cyan] {doc.title}")
    console.print(f"[cyan]Total sections:[/cyan] {len(doc.sections)}")
    console.print(f"[cyan]Total words:[/cyan] {doc.total_words}")
    console.print(f"[cyan]Total lines:[/cyan] {doc.total_lines}")

    console.print("\n[cyan]Sections found:[/cyan]")
    for section in doc.sections:
        actionable = "[green]actionable[/green]" if section.is_actionable else "[yellow]informational[/yellow]"
        code = "[blue]has code[/blue]" if section.has_code_blocks else ""
        console.print(f"  {'#' * section.level} {section.title} - {actionable} {code}")

    # Validate
    console.print("\n[bold]Validation Results:[/bold]\n")
    result = validate_claude_md(GOOD_CLAUDE_MD)

    if result.is_valid:
        console.print(f"[green]Valid![/green] Quality score: {result.score}/100")
    else:
        console.print(f"[red]Invalid.[/red] Quality score: {result.score}/100")

    if result.issues:
        console.print("\n[yellow]Issues found:[/yellow]")
        for issue in result.issues:
            console.print(f"  - {issue}")
    else:
        console.print("\n[green]No issues found![/green]")

    # Key takeaways
    console.print("\n" + "=" * 60)
    console.print("[bold]Key Takeaways:[/bold]\n")
    takeaways = [
        "Start with a clear title and one-line description",
        "Include an Overview explaining what the project does",
        "Document Key Commands that AI can copy and run",
        "Explain Architecture decisions with the 'why'",
        "Show Code Patterns with good and bad examples",
        "List Common Mistakes to help AI avoid pitfalls",
        "Add 'When Users Ask' for FAQ-style guidance",
    ]
    for i, takeaway in enumerate(takeaways, 1):
        console.print(f"  {i}. {takeaway}")

    console.print("\n[bold green]Example completed successfully![/bold green]")


if __name__ == "__main__":
    main()
