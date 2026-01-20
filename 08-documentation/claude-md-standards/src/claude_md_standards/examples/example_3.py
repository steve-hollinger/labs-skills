"""Example 3: Project-Type Templates

This example demonstrates how to generate CLAUDE.md templates for different
project types: web APIs, CLI tools, libraries, and more. Each template is
customized with appropriate sections and guidance for that project type.
"""

from rich.console import Console
from rich.panel import Panel
from rich.markdown import Markdown

from claude_md_standards.generator import (
    generate_claude_md,
    generate_web_api_template,
    generate_cli_template,
    generate_library_template,
    ProjectConfig,
    ProjectType,
)


def main() -> None:
    """Run the project templates example."""
    console = Console()

    console.print(Panel.fit(
        "[bold blue]Example 3: Project-Type Templates[/bold blue]\n"
        "Generate CLAUDE.md templates for different project types.",
        title="CLAUDE.md Standards"
    ))

    # Example 1: Web API
    console.print("\n[bold cyan]1. Web API Template (Python/FastAPI)[/bold cyan]\n")

    web_api_md = generate_web_api_template(
        name="Order Service",
        description="Microservice handling order creation, updates, and fulfillment tracking.",
        language="python",
        framework="FastAPI",
    )

    console.print(Panel(
        Markdown(web_api_md[:2000] + "\n\n*... (truncated for display) ...*"),
        title="Order Service CLAUDE.md",
        border_style="cyan",
    ))

    # Example 2: CLI Tool
    console.print("\n[bold green]2. CLI Tool Template (Python)[/bold green]\n")

    cli_md = generate_cli_template(
        name="Data Migrator",
        description="Command-line tool for migrating data between database schemas.",
        language="python",
    )

    console.print(Panel(
        Markdown(cli_md[:2000] + "\n\n*... (truncated for display) ...*"),
        title="Data Migrator CLAUDE.md",
        border_style="green",
    ))

    # Example 3: Library
    console.print("\n[bold yellow]3. Library Template (Python)[/bold yellow]\n")

    lib_md = generate_library_template(
        name="validation-utils",
        description="Reusable validation utilities for Pydantic models and API requests.",
        language="python",
    )

    console.print(Panel(
        Markdown(lib_md[:2000] + "\n\n*... (truncated for display) ...*"),
        title="validation-utils CLAUDE.md",
        border_style="yellow",
    ))

    # Example 4: Go Web API
    console.print("\n[bold magenta]4. Web API Template (Go)[/bold magenta]\n")

    go_api_md = generate_web_api_template(
        name="Notification Gateway",
        description="High-performance notification delivery service supporting email, SMS, and push.",
        language="go",
        framework="Gin",
    )

    console.print(Panel(
        Markdown(go_api_md[:2000] + "\n\n*... (truncated for display) ...*"),
        title="Notification Gateway CLAUDE.md",
        border_style="magenta",
    ))

    # Example 5: Custom configuration with additional sections
    console.print("\n[bold red]5. Custom Template with Additional Sections[/bold red]\n")

    custom_config = ProjectConfig(
        name="ML Pipeline",
        project_type=ProjectType.DATA_PIPELINE,
        description="Machine learning pipeline for fraud detection model training and inference.",
        language="python",
        framework="Apache Airflow",
        additional_sections={
            "ML-Specific Guidelines": """
### Model Versioning
- All models stored in MLflow: `mlflow.company.com`
- Version format: `fraud-model-v{major}.{minor}.{patch}`
- Never delete model versions; mark as archived instead

### Data Requirements
- Training data in S3: `s3://ml-data/fraud/training/`
- Feature store: `feature-store.company.com`
- Data must be at least 30 days old (regulatory requirement)

### Experiment Tracking
```python
import mlflow

with mlflow.start_run():
    mlflow.log_param("learning_rate", lr)
    mlflow.log_metric("auc", auc_score)
    mlflow.sklearn.log_model(model, "model")
```
""",
            "Compliance Notes": """
- All model predictions must be logged for audit
- PII must be masked in feature data
- Model decisions require explainability output
- Retraining requires approval from ML governance team
""",
        },
    )

    custom_md = generate_claude_md(custom_config)

    console.print(Panel(
        Markdown(custom_md[:2500] + "\n\n*... (truncated for display) ...*"),
        title="ML Pipeline CLAUDE.md",
        border_style="red",
    ))

    # Summary: When to use each template
    console.print("\n" + "=" * 60)
    console.print("\n[bold]Template Selection Guide:[/bold]\n")

    from rich.table import Table

    table = Table(show_header=True, header_style="bold")
    table.add_column("Project Type", style="cyan")
    table.add_column("Use When", width=40)
    table.add_column("Key Sections")

    table.add_row(
        "Web API",
        "Building HTTP services, REST APIs, GraphQL endpoints",
        "Endpoints, Auth, Error Handling",
    )
    table.add_row(
        "CLI Tool",
        "Command-line utilities, scripts, automation tools",
        "Arguments, Subcommands, Output Formats",
    )
    table.add_row(
        "Library",
        "Reusable packages, SDKs, utility modules",
        "Public API, Usage Examples, Versioning",
    )
    table.add_row(
        "Frontend",
        "Web apps, SPAs, component libraries",
        "Components, State, Styling, Build",
    )
    table.add_row(
        "Data Pipeline",
        "ETL jobs, ML pipelines, data processing",
        "Data Sources, Scheduling, Monitoring",
    )
    table.add_row(
        "Monorepo",
        "Multi-project repositories with shared code",
        "Navigation, Shared Deps, Per-Service Docs",
    )

    console.print(table)

    # Interactive usage hint
    console.print("\n[bold]Interactive Usage:[/bold]\n")
    console.print("To generate a template interactively, use:")
    console.print("[cyan]  from claude_md_standards.generator import generate_from_prompts[/cyan]")
    console.print("[cyan]  config = generate_from_prompts()[/cyan]")
    console.print("[cyan]  print(generate_claude_md(config))[/cyan]")

    console.print("\n[bold green]Example completed successfully![/bold green]")


if __name__ == "__main__":
    main()
