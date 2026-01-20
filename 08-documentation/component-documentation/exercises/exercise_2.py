"""Exercise 2: Document an API with Multiple Endpoints

You're documenting a Task Management API. Create complete API documentation
for the endpoints listed below.

API Details:
- Base URL: https://api.taskmanager.io/v1
- Authentication: Bearer token
- Format: JSON

Endpoints to Document:
1. GET /tasks - List all tasks
2. POST /tasks - Create a task
3. GET /tasks/{id} - Get task by ID
4. PUT /tasks/{id} - Update a task
5. DELETE /tasks/{id} - Delete a task

Requirements:
1. Document all parameters for each endpoint
2. Include request body examples for POST/PUT
3. Document success responses with examples
4. Document error responses (400, 401, 404)
5. Include authentication instructions

Target:
- API documentation score: 80+
- All 5 endpoints documented
- Error responses for each endpoint
"""

from component_documentation.api_docs import document_endpoint, generate_api_docs
from component_documentation.models import ApiDocumentation


def exercise() -> list:
    """Create the API endpoints documentation.

    Returns:
        List of ApiEndpoint objects.
    """
    endpoints = []

    # TODO: Document the List Tasks endpoint
    # list_tasks = document_endpoint(
    #     method="GET",
    #     path="/tasks",
    #     summary="List all tasks",
    #     ...
    # )
    # endpoints.append(list_tasks)

    # TODO: Document the Create Task endpoint

    # TODO: Document the Get Task endpoint

    # TODO: Document the Update Task endpoint

    # TODO: Document the Delete Task endpoint

    return endpoints


def validate_solution() -> None:
    """Validate your API documentation."""
    from component_documentation.api_docs import validate_api_docs
    from rich.console import Console

    console = Console()
    endpoints = exercise()

    console.print("\n[bold]Exercise 2: Task Management API Documentation[/bold]\n")

    # Create docs object for validation
    docs = ApiDocumentation(
        title="Task Management API",
        description="API for managing tasks",
        base_url="https://api.taskmanager.io/v1",
        version="1.0.0",
        endpoints=endpoints,
        authentication="Bearer token required",
    )

    score = validate_api_docs(docs)

    console.print(f"Score: [{('green' if score.is_passing else 'red')}]{score.score}/100[/]")

    # Check requirements
    required_methods = ["GET", "POST", "PUT", "DELETE"]
    found_methods = [e.method.value for e in endpoints]

    console.print("\n[bold]Endpoint Coverage:[/bold]")
    for method in required_methods:
        if method in found_methods:
            console.print(f"  [green]PASS[/green] - {method} endpoint documented")
        else:
            console.print(f"  [red]FAIL[/red] - {method} endpoint missing")

    console.print(f"\n[bold]Endpoints documented:[/bold] {len(endpoints)}/5")

    if score.issues:
        console.print("\n[red]Issues:[/red]")
        for issue in score.issues[:5]:
            console.print(f"  - {issue}")

    if score.suggestions:
        console.print("\n[yellow]Suggestions:[/yellow]")
        for suggestion in score.suggestions[:3]:
            console.print(f"  - {suggestion}")

    if len(endpoints) >= 5 and score.is_passing:
        console.print("\n[bold green]All requirements met![/bold green]")

        # Generate and show the docs
        api_docs = generate_api_docs(
            title="Task Management API",
            description="API for managing tasks and projects",
            base_url="https://api.taskmanager.io/v1",
            version="1.0.0",
            endpoints=endpoints,
        )
        console.print("\n[dim]Generated documentation preview:[/dim]")
        console.print(api_docs[:1500] + "\n...")
    else:
        console.print("\n[yellow]Keep working on it![/yellow]")


if __name__ == "__main__":
    validate_solution()
