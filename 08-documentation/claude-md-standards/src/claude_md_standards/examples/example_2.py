"""Example 2: Good vs Bad AI Guidance

This example compares effective CLAUDE.md content with common anti-patterns.
Learn to identify vague, unhelpful guidance and transform it into actionable
instructions that help AI assistants work effectively.
"""

from rich.console import Console
from rich.panel import Panel
from rich.table import Table
from rich.syntax import Syntax

from claude_md_standards.validator import validate_claude_md


# Example of BAD CLAUDE.md content
BAD_CLAUDE_MD = """# CLAUDE.md

## About

This is our project. It does stuff.

## Setup

Install the dependencies and run the project.

## Code Style

Follow best practices and write clean code. Make sure everything
is properly formatted and use appropriate naming conventions.

## Testing

Write tests for your code. Make sure they pass.

## Common Issues

If something doesn't work, check the logs and fix it.

## Questions

Ask the team if you have questions.
"""

# The same content, but GOOD
GOOD_CLAUDE_MD = """# CLAUDE.md - Inventory Management API

A REST API for tracking warehouse inventory, built with FastAPI and PostgreSQL.

## Overview

This service handles:
- Product catalog management (CRUD operations)
- Inventory levels tracking per warehouse
- Low-stock alerts and reorder suggestions
- Integration with supplier APIs for automated ordering

## Setup

```bash
# 1. Install dependencies
make setup

# 2. Start database
docker-compose up -d postgres

# 3. Run migrations
make db-migrate

# 4. Start development server
make dev   # Runs on http://localhost:8000
```

## Code Style

### Naming Conventions
- Functions/variables: `snake_case` (e.g., `get_inventory_level`)
- Classes: `PascalCase` (e.g., `InventoryService`)
- Constants: `UPPER_SNAKE_CASE` (e.g., `MAX_BATCH_SIZE`)

### Formatting
- Line length: 100 characters max
- Use ruff for formatting: `make format`
- Imports sorted with isort (handled by ruff)

### Type Hints
Required on all function signatures:
```python
# Good
def update_stock(product_id: int, quantity: int) -> StockLevel:
    ...

# Bad - missing type hints
def update_stock(product_id, quantity):
    ...
```

## Testing

### Running Tests
```bash
make test              # All tests
make test-unit         # Unit tests only (fast)
make test-integration  # Integration tests (requires DB)
pytest -k "inventory"  # Tests matching pattern
```

### Test Requirements
- New features require tests (minimum 80% coverage)
- Unit tests for business logic in `tests/unit/`
- Integration tests for API endpoints in `tests/integration/`

### Test Data
```python
# Use factories for test data
from tests.factories import ProductFactory

def test_low_stock_alert():
    product = ProductFactory(stock_level=5, reorder_threshold=10)
    assert product.needs_reorder is True
```

## Common Issues

### "Connection refused to localhost:5432"
PostgreSQL is not running.
```bash
docker-compose up -d postgres
docker-compose logs postgres  # Check for errors
```

### "ModuleNotFoundError: No module named 'app'"
Dependencies not installed or venv not activated.
```bash
make setup
source .venv/bin/activate
```

### "Tests failing with 'relation does not exist'"
Migrations haven't been run on test database.
```bash
make db-migrate
```

## Getting Help

- API docs: http://localhost:8000/docs (when running)
- Architecture decisions: see `docs/adr/`
- Slack: #inventory-api-help
"""


# Comparison pairs showing transformation
COMPARISONS = [
    {
        "topic": "Project Description",
        "bad": "This is our project. It does stuff.",
        "good": "A REST API for tracking warehouse inventory, built with FastAPI and PostgreSQL.",
        "why": "Specific description tells AI what technology stack to expect and what the project does.",
    },
    {
        "topic": "Setup Instructions",
        "bad": "Install the dependencies and run the project.",
        "good": """```bash
make setup
docker-compose up -d postgres
make db-migrate
make dev
```""",
        "why": "Actual commands that AI can copy, paste, and execute. No ambiguity.",
    },
    {
        "topic": "Code Style",
        "bad": "Follow best practices and write clean code.",
        "good": """- Functions/variables: `snake_case`
- Classes: `PascalCase`
- Line length: 100 characters
- Use ruff for formatting: `make format`""",
        "why": "Concrete rules that can be followed. 'Best practices' means nothing specific.",
    },
    {
        "topic": "Testing Guidance",
        "bad": "Write tests for your code. Make sure they pass.",
        "good": """```bash
make test              # All tests
make test-unit         # Unit tests only
pytest -k "inventory"  # Pattern matching
```
- Minimum 80% coverage
- Unit tests in tests/unit/
- Integration tests in tests/integration/""",
        "why": "Shows exact commands, specifies coverage requirements, explains test organization.",
    },
    {
        "topic": "Troubleshooting",
        "bad": "If something doesn't work, check the logs and fix it.",
        "good": """### "Connection refused to localhost:5432"
PostgreSQL is not running.
```bash
docker-compose up -d postgres
```""",
        "why": "Specific error message with specific solution. AI can pattern-match errors to fixes.",
    },
]


def main() -> None:
    """Run the good vs bad guidance comparison example."""
    console = Console()

    console.print(Panel.fit(
        "[bold blue]Example 2: Good vs Bad AI Guidance[/bold blue]\n"
        "Compare effective CLAUDE.md content with common anti-patterns.",
        title="CLAUDE.md Standards"
    ))

    # Show validation of bad CLAUDE.md
    console.print("\n[bold red]The BAD CLAUDE.md:[/bold red]\n")
    console.print(Syntax(BAD_CLAUDE_MD, "markdown", theme="monokai", line_numbers=True))

    console.print("\n[bold]Validation Results (Bad):[/bold]")
    bad_result = validate_claude_md(BAD_CLAUDE_MD)
    console.print(f"Score: [red]{bad_result.score}/100[/red]")
    console.print(f"Valid: [red]{bad_result.is_valid}[/red]")
    console.print("\n[yellow]Issues:[/yellow]")
    for issue in bad_result.issues[:5]:  # Show first 5
        console.print(f"  - {issue}")
    if len(bad_result.issues) > 5:
        console.print(f"  ... and {len(bad_result.issues) - 5} more issues")

    # Show validation of good CLAUDE.md
    console.print("\n" + "=" * 60)
    console.print("\n[bold green]The GOOD CLAUDE.md:[/bold green]\n")
    console.print(Syntax(GOOD_CLAUDE_MD[:1500] + "\n...(truncated)...", "markdown", theme="monokai", line_numbers=True))

    console.print("\n[bold]Validation Results (Good):[/bold]")
    good_result = validate_claude_md(GOOD_CLAUDE_MD)
    console.print(f"Score: [green]{good_result.score}/100[/green]")
    console.print(f"Valid: [green]{good_result.is_valid}[/green]")
    if good_result.issues:
        console.print("\n[yellow]Minor issues:[/yellow]")
        for issue in good_result.issues:
            console.print(f"  - {issue}")
    else:
        console.print("\n[green]No issues found![/green]")

    # Side-by-side comparisons
    console.print("\n" + "=" * 60)
    console.print("\n[bold]Side-by-Side Comparisons:[/bold]\n")

    for comp in COMPARISONS:
        table = Table(title=f"[bold]{comp['topic']}[/bold]", show_header=True, header_style="bold")
        table.add_column("Bad", style="red", width=35)
        table.add_column("Good", style="green", width=35)
        table.add_row(comp["bad"], comp["good"])
        console.print(table)
        console.print(f"[cyan]Why it matters:[/cyan] {comp['why']}\n")

    # Summary of anti-patterns
    console.print("=" * 60)
    console.print("\n[bold]Common Anti-Patterns to Avoid:[/bold]\n")

    anti_patterns = [
        ("Vague descriptions", "Be specific about what the project does and how"),
        ("Missing commands", "Include copy-paste-able commands"),
        ("Aspirational language", "'Best practices' and 'clean code' mean nothing concrete"),
        ("Assuming knowledge", "Explain project-specific terms and patterns"),
        ("Generic troubleshooting", "Match specific errors to specific solutions"),
        ("Missing 'why'", "Explain reasoning behind decisions, not just rules"),
    ]

    for pattern, fix in anti_patterns:
        console.print(f"  [red]X[/red] [bold]{pattern}[/bold]")
        console.print(f"      [green]Fix:[/green] {fix}\n")

    console.print("\n[bold green]Example completed successfully![/bold green]")


if __name__ == "__main__":
    main()
