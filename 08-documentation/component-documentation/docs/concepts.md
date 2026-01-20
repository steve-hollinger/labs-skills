# Core Concepts

## Overview

Component documentation helps users, maintainers, and integrators understand how to work with your software. This guide covers the essential concepts for documenting components effectively.

## Concept 1: The Documentation Pyramid

### What It Is

Documentation exists at multiple levels, each serving different needs:

1. **README** (Entry Point) - First thing users see
2. **Guides & Tutorials** - How to accomplish specific tasks
3. **API Reference** - Complete technical details
4. **Inline Documentation** - Code-level explanations

### Why It Matters

Different audiences need different levels of detail:
- New users need quick starts and examples
- Experienced users need detailed API reference
- Maintainers need inline documentation

### How It Works

```
Level 4: API Reference (Generated)
├── Every function, class, parameter documented
├── Generated from code + docstrings
└── Searchable, comprehensive

Level 3: Guides & Tutorials
├── Task-oriented (how to achieve X)
├── Step-by-step instructions
└── Real-world scenarios

Level 2: README
├── What it is and why to use it
├── Installation instructions
├── Quick start example
└── Links to deeper documentation

Level 1: Inline Documentation
├── Docstrings on functions/classes
├── Comments on complex logic
└── Type hints for contracts
```

## Concept 2: README Structure

### What It Is

A README is the entry point to your project. It should quickly answer:
- What is this?
- Why would I use it?
- How do I get started?

### Why It Matters

Most users decide whether to use your software based on the README. A good README reduces support burden and increases adoption.

### How It Works

```markdown
# Project Name

One-line description of what it does.

## Features

- Key feature 1
- Key feature 2
- Key feature 3

## Installation

```bash
pip install project-name
```

## Quick Start

```python
from project import main_function

result = main_function(input_data)
print(result)
```

## Usage

### Basic Usage
[More detailed examples]

### Advanced Usage
[Complex scenarios]

## Configuration

| Option | Description | Default |
|--------|-------------|---------|
| timeout | Request timeout in seconds | 30 |

## API Reference

[Link to full API docs or summary of main functions]

## Contributing

[How to contribute]

## License

[License type]
```

## Concept 3: API Documentation

### What It Is

API documentation describes how to interact with your software programmatically, including:
- Functions and methods
- Parameters and return values
- Error conditions
- Usage examples

### Why It Matters

Good API docs enable developers to:
- Understand what's possible
- Implement integrations correctly
- Debug issues quickly
- Avoid common mistakes

### How It Works

**For functions:**
```python
def send_notification(
    user_id: str,
    message: str,
    channel: str = "email",
    priority: int = 1,
) -> NotificationResult:
    """Send a notification to a user.

    Args:
        user_id: The unique identifier of the user.
        message: The notification message content.
        channel: Delivery channel ("email", "sms", "push").
        priority: Message priority (1=low, 5=high).

    Returns:
        NotificationResult containing delivery status and ID.

    Raises:
        UserNotFoundError: If user_id doesn't exist.
        InvalidChannelError: If channel is not supported.
        RateLimitError: If user has too many recent notifications.

    Example:
        >>> result = send_notification("user123", "Hello!", channel="sms")
        >>> print(result.notification_id)
        "notif_abc123"
    """
```

**For REST APIs:**
```markdown
## POST /notifications

Send a notification to a user.

### Request

```json
{
    "user_id": "user123",
    "message": "Hello!",
    "channel": "email",
    "priority": 1
}
```

### Response

**Success (200)**
```json
{
    "notification_id": "notif_abc123",
    "status": "queued",
    "estimated_delivery": "2024-01-15T10:30:00Z"
}
```

**Errors**
| Code | Description |
|------|-------------|
| 404 | User not found |
| 400 | Invalid channel |
| 429 | Rate limit exceeded |
```

## Concept 4: Code Documentation

### What It Is

Code documentation includes:
- **Docstrings**: Function/class descriptions
- **Type hints**: Parameter and return types
- **Comments**: Explanations of complex logic
- **Module docstrings**: File-level documentation

### Why It Matters

Code documentation helps:
- New team members understand the codebase
- Maintainers make safe modifications
- IDE tools provide better assistance
- Generated documentation be more useful

### How It Works

**Module docstring:**
```python
"""User authentication module.

This module handles user authentication including:
- Password verification
- JWT token generation and validation
- Session management

Security considerations:
- All passwords are hashed with bcrypt
- Tokens expire after 24 hours
- Failed attempts are rate-limited

Example:
    >>> from auth import authenticate_user
    >>> token = authenticate_user("user@example.com", "password")
"""
```

**Class docstring:**
```python
class UserRepository:
    """Repository for user data access.

    This class provides an abstraction over the database layer
    for user-related operations. All methods handle their own
    database sessions.

    Attributes:
        db_url: Connection string for the database.
        pool_size: Number of connections to maintain.

    Example:
        >>> repo = UserRepository("postgresql://localhost/mydb")
        >>> user = await repo.get_by_email("user@example.com")
    """
```

**Inline comments:**
```python
def calculate_discount(order: Order) -> Decimal:
    # Base discount tiers (configured by business team)
    tiers = [(100, 0.05), (500, 0.10), (1000, 0.15)]

    total = order.subtotal

    # Find the highest applicable tier
    # NOTE: Tiers must be sorted ascending by threshold
    discount_rate = Decimal(0)
    for threshold, rate in tiers:
        if total >= threshold:
            discount_rate = Decimal(str(rate))

    # Apply loyalty bonus if eligible
    # (Customers with 10+ orders get extra 2%)
    if order.customer.order_count >= 10:
        discount_rate += Decimal("0.02")

    return total * discount_rate
```

## Concept 5: Documentation Maintenance

### What It Is

Documentation maintenance ensures docs stay accurate as code evolves.

### Why It Matters

Outdated documentation is often worse than no documentation because it:
- Misleads users
- Wastes debugging time
- Erodes trust in all documentation

### How It Works

**Include docs in PR checklist:**
```markdown
## PR Checklist
- [ ] Code changes are tested
- [ ] Documentation is updated
- [ ] README reflects any new features
- [ ] Docstrings added for new functions
```

**Use CI to catch missing docs:**
```python
# In CI pipeline
def check_docstrings():
    """Verify all public functions have docstrings."""
    for func in get_public_functions():
        if not func.__doc__:
            fail(f"Missing docstring: {func.__name__}")
```

**Document when you code:**
```python
# README-driven development
# 1. Write README describing the feature
# 2. Write function signature with docstring
# 3. Implement the function
# 4. README is already done!
```

## Summary

Key takeaways:
1. **Document at multiple levels** - README, guides, API reference, inline
2. **Structure READMEs consistently** - What, why, install, quick start, examples
3. **Write complete API docs** - Parameters, returns, errors, examples
4. **Document as you code** - It's easier and more accurate
5. **Maintain documentation** - Treat it as part of the codebase
