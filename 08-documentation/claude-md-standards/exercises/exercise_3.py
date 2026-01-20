"""Exercise 3: Create a CLAUDE.md Hierarchy for a Monorepo

You're working on a monorepo with multiple services and shared libraries.
Create a hierarchy of CLAUDE.md files that provide appropriate context
at each level.

Monorepo Structure:
ecommerce-platform/
├── CLAUDE.md                    # Root - you'll write this
├── services/
│   ├── CLAUDE.md                # Services shared context
│   ├── user-service/
│   │   └── CLAUDE.md            # User service specific
│   ├── product-service/
│   │   └── CLAUDE.md            # Product service specific
│   └── order-service/
│       └── CLAUDE.md            # Order service specific
├── shared/
│   ├── CLAUDE.md                # Shared libraries context
│   ├── common-utils/
│   └── api-client/
└── infrastructure/
    └── CLAUDE.md                # Infrastructure/DevOps

Project Context:
- Languages: Python (services), TypeScript (some shared libs)
- Services communicate via gRPC
- Shared PostgreSQL database per service
- Deployed on Kubernetes
- CI/CD via GitHub Actions

Instructions:
1. Write ROOT_CLAUDE_MD - general monorepo guidance
2. Write SERVICES_CLAUDE_MD - shared patterns for all services
3. Write USER_SERVICE_CLAUDE_MD - specific to user service

Each should:
- Reference parent context appropriately
- Not duplicate information from parent
- Add context-specific guidance

Expected Output:
- Three CLAUDE.md files with proper hierarchy
- No duplication between levels
- Each file scores 75+ individually
- Total combined score 240+ (80 average)
"""


def root_claude_md() -> str:
    """Write the root-level CLAUDE.md for the monorepo.

    This should cover:
    - Overall project structure
    - How to navigate the monorepo
    - Shared infrastructure setup
    - CI/CD overview
    """
    # TODO: Implement the root CLAUDE.md
    return """# CLAUDE.md - E-commerce Platform

TODO: Write root-level CLAUDE.md

## Overview

TODO: Describe the monorepo

## Navigation

TODO: How to find things

## Shared Infrastructure

TODO: How to start databases, etc.

"""


def services_claude_md() -> str:
    """Write the services-level CLAUDE.md.

    This should cover:
    - Patterns shared across all services
    - gRPC communication patterns
    - Common testing approaches
    - Service-level conventions
    """
    # TODO: Implement the services CLAUDE.md
    return """# CLAUDE.md - Services

TODO: Write services-level CLAUDE.md

**Parent context:** See root CLAUDE.md for monorepo overview.

## Service Architecture

TODO: Shared service patterns

"""


def user_service_claude_md() -> str:
    """Write the user-service-specific CLAUDE.md.

    This should cover:
    - What user-service does specifically
    - User-specific data models
    - Authentication/authorization patterns
    - User-specific testing
    """
    # TODO: Implement the user-service CLAUDE.md
    return """# CLAUDE.md - User Service

TODO: Write user-service CLAUDE.md

**Parent context:** See services/CLAUDE.md for shared patterns.

## Overview

TODO: What user-service does

"""


def validate_solution() -> None:
    """Validate all three CLAUDE.md files."""
    from claude_md_standards.validator import validate_claude_md
    from rich.console import Console
    from rich.table import Table

    console = Console()

    files = [
        ("Root", root_claude_md()),
        ("Services", services_claude_md()),
        ("User Service", user_service_claude_md()),
    ]

    console.print("[bold]CLAUDE.md Hierarchy Validation:[/bold]\n")

    table = Table(show_header=True, header_style="bold")
    table.add_column("Level")
    table.add_column("Score", justify="right")
    table.add_column("Valid")
    table.add_column("Issues")

    total_score = 0

    for name, content in files:
        result = validate_claude_md(content)
        total_score += result.score

        valid_str = "[green]Yes[/green]" if result.is_valid else "[red]No[/red]"
        score_color = "green" if result.score >= 75 else "yellow" if result.score >= 50 else "red"

        table.add_row(
            name,
            f"[{score_color}]{result.score}[/{score_color}]",
            valid_str,
            str(len(result.issues)),
        )

    console.print(table)
    console.print(f"\n[bold]Total Score:[/bold] {total_score}/300")
    console.print(f"[bold]Average Score:[/bold] {total_score // 3}/100")

    if total_score >= 240:
        console.print("\n[green]Excellent! Your hierarchy is well-structured.[/green]")
    elif total_score >= 180:
        console.print("\n[yellow]Good progress! Some improvements needed.[/yellow]")
    else:
        console.print("\n[red]Keep working on it. See the issues for each file.[/red]")

    # Show issues for each file
    for name, content in files:
        result = validate_claude_md(content)
        if result.issues:
            console.print(f"\n[bold]{name} Issues:[/bold]")
            for issue in result.issues[:3]:  # Show top 3
                console.print(f"  - {issue}")


def check_for_duplication() -> None:
    """Check if content is duplicated across levels."""
    from rich.console import Console

    console = Console()
    console.print("\n[bold]Duplication Check:[/bold]\n")

    root = root_claude_md().lower()
    services = services_claude_md().lower()
    user = user_service_claude_md().lower()

    # Check for command duplication (common issue)
    commands_to_check = ["make setup", "make test", "docker-compose"]

    for cmd in commands_to_check:
        in_root = cmd in root
        in_services = cmd in services
        in_user = cmd in user

        if sum([in_root, in_services, in_user]) > 1:
            console.print(f"[yellow]Warning:[/yellow] '{cmd}' appears in multiple files")
            console.print("  Consider: Commands should be specific to each level")

    console.print("\n[bold]Tip:[/bold] Each level should add new information, not repeat parent content.")


if __name__ == "__main__":
    validate_solution()
    check_for_duplication()
