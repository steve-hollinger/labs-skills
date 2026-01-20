"""Example 2: API Documentation

This example demonstrates how to document REST API endpoints effectively,
including parameters, responses, errors, and authentication.
"""

from rich.console import Console
from rich.panel import Panel
from rich.markdown import Markdown

from component_documentation.api_docs import (
    document_endpoint,
    generate_api_docs,
    validate_api_docs,
    generate_error_reference,
    generate_authentication_docs,
)
from component_documentation.models import ApiDocumentation, HttpMethod


def main() -> None:
    """Run the API documentation example."""
    console = Console()

    console.print(Panel.fit(
        "[bold blue]Example 2: API Documentation[/bold blue]\n"
        "Learn how to document REST API endpoints effectively.",
        title="Component Documentation"
    ))

    # Create sample endpoints
    console.print("\n[bold]Documenting API Endpoints:[/bold]\n")

    # Endpoint 1: List users
    list_users = document_endpoint(
        method="GET",
        path="/users",
        summary="List all users",
        description="Retrieve a paginated list of users. Results can be filtered by status and role.",
        parameters=[
            {"name": "limit", "type": "integer", "required": False,
             "description": "Maximum number of results (default: 20, max: 100)"},
            {"name": "offset", "type": "integer", "required": False,
             "description": "Pagination offset"},
            {"name": "status", "type": "string", "required": False,
             "description": "Filter by status (active, inactive, pending)"},
            {"name": "role", "type": "string", "required": False,
             "description": "Filter by role (admin, user, guest)"},
        ],
        responses=[
            {
                "status_code": 200,
                "description": "Successful response",
                "example": {
                    "data": [
                        {"id": "user_123", "name": "Alice", "email": "alice@example.com", "role": "admin"},
                        {"id": "user_456", "name": "Bob", "email": "bob@example.com", "role": "user"},
                    ],
                    "meta": {"total": 42, "limit": 20, "offset": 0},
                },
            },
            {
                "status_code": 401,
                "description": "Unauthorized - Invalid or missing API key",
                "example": {"error": {"code": "UNAUTHORIZED", "message": "Invalid API key"}},
            },
        ],
        tags=["Users"],
    )

    # Endpoint 2: Create user
    create_user = document_endpoint(
        method="POST",
        path="/users",
        summary="Create a new user",
        description="Create a new user account. An email verification will be sent.",
        request_body={
            "name": "Alice Smith",
            "email": "alice@example.com",
            "role": "user",
            "password": "secure_password_123",
        },
        responses=[
            {
                "status_code": 201,
                "description": "User created successfully",
                "example": {
                    "id": "user_789",
                    "name": "Alice Smith",
                    "email": "alice@example.com",
                    "role": "user",
                    "status": "pending",
                    "created_at": "2024-01-15T10:30:00Z",
                },
            },
            {
                "status_code": 400,
                "description": "Validation error",
                "example": {
                    "error": {
                        "code": "VALIDATION_ERROR",
                        "message": "Request validation failed",
                        "details": {"email": "Invalid email format"},
                    }
                },
            },
            {
                "status_code": 409,
                "description": "Email already exists",
                "example": {
                    "error": {
                        "code": "DUPLICATE_EMAIL",
                        "message": "A user with this email already exists",
                    }
                },
            },
        ],
        tags=["Users"],
    )

    # Endpoint 3: Get user by ID
    get_user = document_endpoint(
        method="GET",
        path="/users/{id}",
        summary="Get user by ID",
        description="Retrieve a single user by their unique identifier.",
        parameters=[
            {"name": "id", "type": "string", "required": True,
             "description": "The unique user identifier"},
        ],
        responses=[
            {
                "status_code": 200,
                "description": "Successful response",
                "example": {
                    "id": "user_123",
                    "name": "Alice",
                    "email": "alice@example.com",
                    "role": "admin",
                    "status": "active",
                    "created_at": "2024-01-01T00:00:00Z",
                },
            },
            {
                "status_code": 404,
                "description": "User not found",
                "example": {
                    "error": {
                        "code": "USER_NOT_FOUND",
                        "message": "No user found with the specified ID",
                    }
                },
            },
        ],
        tags=["Users"],
    )

    # Endpoint 4: Delete user
    delete_user = document_endpoint(
        method="DELETE",
        path="/users/{id}",
        summary="Delete a user",
        description="Permanently delete a user account. This action cannot be undone.",
        parameters=[
            {"name": "id", "type": "string", "required": True,
             "description": "The unique user identifier"},
        ],
        responses=[
            {
                "status_code": 204,
                "description": "User deleted successfully (no content)",
            },
            {
                "status_code": 404,
                "description": "User not found",
            },
            {
                "status_code": 403,
                "description": "Cannot delete admin users",
            },
        ],
        tags=["Users"],
    )

    # Generate complete API documentation
    api_docs = generate_api_docs(
        title="User Management API",
        description="""The User Management API allows you to create, retrieve, update, and delete user accounts.
All endpoints require authentication via API key.""",
        base_url="https://api.example.com/v1",
        version="1.0.0",
        endpoints=[list_users, create_user, get_user, delete_user],
        authentication=generate_authentication_docs(
            auth_type="API Key",
            header_name="Authorization",
            token_format="Bearer {token}",
            example_token="your-api-key-here",
        ),
    )

    # Show the generated documentation
    console.print(Panel(
        Markdown(api_docs[:3000] + "\n\n*... (truncated) ...*"),
        title="Generated API Documentation",
        border_style="green",
    ))

    # Validate the API docs
    console.print("\n" + "=" * 60)
    console.print("\n[bold]API Documentation Validation:[/bold]\n")

    docs_obj = ApiDocumentation(
        title="User Management API",
        description="API for user management",
        base_url="https://api.example.com/v1",
        version="1.0.0",
        endpoints=[list_users, create_user, get_user, delete_user],
        authentication="API Key required",
    )

    score = validate_api_docs(docs_obj)

    console.print(f"Score: [{('green' if score.is_passing else 'red')}]{score.score}/100[/]")

    if score.issues:
        console.print("\n[red]Issues:[/red]")
        for issue in score.issues:
            console.print(f"  - {issue}")

    if score.suggestions:
        console.print("\n[yellow]Suggestions:[/yellow]")
        for suggestion in score.suggestions:
            console.print(f"  - {suggestion}")

    # Show error reference generation
    console.print("\n" + "=" * 60)
    console.print("\n[bold]Error Reference Section:[/bold]\n")

    error_ref = generate_error_reference([
        ("INVALID_REQUEST", 400, "Request validation failed"),
        ("UNAUTHORIZED", 401, "Invalid or missing API key"),
        ("FORBIDDEN", 403, "Insufficient permissions"),
        ("NOT_FOUND", 404, "Resource not found"),
        ("CONFLICT", 409, "Resource already exists"),
        ("RATE_LIMITED", 429, "Too many requests"),
        ("INTERNAL_ERROR", 500, "Internal server error"),
    ])

    console.print(Markdown(error_ref))

    # Key takeaways
    console.print("\n" + "=" * 60)
    console.print("\n[bold]Key Takeaways:[/bold]\n")

    takeaways = [
        "Document every endpoint with method, path, and description",
        "Include all parameters with types and whether they're required",
        "Show request body examples for POST/PUT endpoints",
        "Document both success AND error responses",
        "Include realistic example payloads",
        "Create an error code reference for consistency",
        "Always document authentication requirements",
    ]

    for takeaway in takeaways:
        console.print(f"  - {takeaway}")

    console.print("\n[bold green]Example completed successfully![/bold green]")


if __name__ == "__main__":
    main()
