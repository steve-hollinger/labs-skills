"""API documentation utilities."""

from typing import Any, Optional

from component_documentation.models import (
    ApiEndpoint,
    ApiParameter,
    ApiResponse,
    ApiDocumentation,
    HttpMethod,
    DocumentationScore,
)


def document_endpoint(
    method: str,
    path: str,
    summary: str,
    description: str = "",
    parameters: Optional[list[dict[str, Any]]] = None,
    request_body: Optional[dict[str, Any]] = None,
    responses: Optional[list[dict[str, Any]]] = None,
    tags: Optional[list[str]] = None,
) -> ApiEndpoint:
    """Create an API endpoint documentation object.

    Args:
        method: HTTP method (GET, POST, PUT, DELETE, PATCH).
        path: URL path for the endpoint.
        summary: Brief summary of what the endpoint does.
        description: Detailed description (optional).
        parameters: List of parameter definitions.
        request_body: Request body example/schema.
        responses: List of response definitions.
        tags: Tags for categorization.

    Returns:
        ApiEndpoint object ready for rendering.

    Example:
        >>> endpoint = document_endpoint(
        ...     method="POST",
        ...     path="/users",
        ...     summary="Create a new user",
        ...     parameters=[
        ...         {"name": "email", "type": "string", "required": True, "description": "User email"}
        ...     ],
        ...     responses=[
        ...         {"status_code": 201, "description": "User created", "example": {"id": "123"}}
        ...     ]
        ... )
    """
    # Parse parameters
    parsed_params = []
    if parameters:
        for param in parameters:
            parsed_params.append(
                ApiParameter(
                    name=param["name"],
                    param_type=param.get("type", "string"),
                    required=param.get("required", False),
                    description=param.get("description", ""),
                    default=param.get("default"),
                    example=param.get("example"),
                )
            )

    # Parse responses
    parsed_responses = []
    if responses:
        for resp in responses:
            parsed_responses.append(
                ApiResponse(
                    status_code=resp["status_code"],
                    description=resp.get("description", ""),
                    example=resp.get("example"),
                    schema=resp.get("schema"),
                )
            )

    return ApiEndpoint(
        method=HttpMethod(method.upper()),
        path=path,
        summary=summary,
        description=description,
        parameters=parsed_params,
        request_body=request_body,
        responses=parsed_responses,
        tags=tags or [],
    )


def generate_api_docs(
    title: str,
    description: str,
    base_url: str,
    version: str,
    endpoints: list[ApiEndpoint],
    authentication: Optional[str] = None,
) -> str:
    """Generate complete API documentation as markdown.

    Args:
        title: API title.
        description: API description.
        base_url: Base URL for the API.
        version: API version.
        endpoints: List of endpoint definitions.
        authentication: Authentication instructions.

    Returns:
        Complete API documentation as markdown string.
    """
    docs = ApiDocumentation(
        title=title,
        description=description,
        base_url=base_url,
        version=version,
        endpoints=endpoints,
        authentication=authentication,
    )

    return docs.render_markdown()


def validate_api_docs(docs: ApiDocumentation) -> DocumentationScore:
    """Validate API documentation for completeness.

    Args:
        docs: API documentation to validate.

    Returns:
        DocumentationScore with issues and suggestions.
    """
    score = DocumentationScore(score=100)

    # Check basic info
    if not docs.title:
        score.add_issue("Missing API title", penalty=15)

    if not docs.description:
        score.add_issue("Missing API description", penalty=10)

    if not docs.base_url:
        score.add_issue("Missing base URL", penalty=10)

    if not docs.authentication:
        score.add_suggestion("Consider adding authentication instructions")

    if not docs.endpoints:
        score.add_issue("No endpoints documented", penalty=30)
        return score

    # Check endpoints
    for endpoint in docs.endpoints:
        endpoint_name = f"{endpoint.method.value} {endpoint.path}"

        if not endpoint.summary:
            score.add_issue(f"Missing summary for {endpoint_name}", penalty=5)

        if not endpoint.responses:
            score.add_issue(f"No responses documented for {endpoint_name}", penalty=5)

        # Check for success and error responses
        status_codes = [r.status_code for r in endpoint.responses]
        has_success = any(200 <= code < 300 for code in status_codes)
        has_error = any(400 <= code < 600 for code in status_codes)

        if not has_success:
            score.add_issue(f"No success response for {endpoint_name}", penalty=5)

        if not has_error:
            score.add_suggestion(f"Consider documenting error responses for {endpoint_name}")

        # Check parameters
        for param in endpoint.parameters:
            if not param.description:
                score.add_issue(
                    f"Missing description for parameter '{param.name}' in {endpoint_name}",
                    penalty=3,
                )

    return score


def generate_error_reference(
    errors: list[tuple[str, int, str]],
) -> str:
    """Generate an error code reference section.

    Args:
        errors: List of (code, status, description) tuples.

    Returns:
        Markdown table of error codes.

    Example:
        >>> errors = [
        ...     ("INVALID_REQUEST", 400, "Request validation failed"),
        ...     ("UNAUTHORIZED", 401, "Missing or invalid credentials"),
        ...     ("NOT_FOUND", 404, "Resource not found"),
        ... ]
        >>> print(generate_error_reference(errors))
    """
    lines = [
        "## Error Codes",
        "",
        "| Code | HTTP Status | Description |",
        "|------|-------------|-------------|",
    ]

    for code, status, description in errors:
        lines.append(f"| `{code}` | {status} | {description} |")

    lines.append("")
    lines.append("All errors follow this format:")
    lines.append("")
    lines.append("```json")
    lines.append("""{
    "error": {
        "code": "ERROR_CODE",
        "message": "Human-readable description",
        "details": {}
    }
}""")
    lines.append("```")

    return "\n".join(lines)


def generate_authentication_docs(
    auth_type: str,
    header_name: str = "Authorization",
    token_format: str = "Bearer {token}",
    example_token: str = "your-api-key",
) -> str:
    """Generate authentication documentation.

    Args:
        auth_type: Type of authentication (API Key, Bearer Token, etc.).
        header_name: Name of the header for authentication.
        token_format: Format of the token value.
        example_token: Example token for documentation.

    Returns:
        Markdown authentication documentation.
    """
    formatted_token = token_format.format(token=example_token)

    return f"""## Authentication

This API uses {auth_type} for authentication.

Include your credentials in the `{header_name}` header:

```bash
curl -H "{header_name}: {formatted_token}" \\
    https://api.example.com/v1/endpoint
```

### Getting an API Key

1. Sign up at https://example.com/signup
2. Navigate to Settings > API Keys
3. Click "Create New Key"
4. Copy your key (it won't be shown again)

### Security Notes

- Never share your API key publicly
- Rotate keys periodically
- Use environment variables to store keys
"""
