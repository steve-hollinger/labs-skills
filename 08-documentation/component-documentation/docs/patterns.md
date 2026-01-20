# Common Patterns

## Overview

This document covers common patterns for documenting different types of software components.

## Pattern 1: The Library README

### When to Use

When documenting a reusable library or package.

### Implementation

```markdown
# library-name

Brief, compelling description of what the library does.

[![PyPI](https://img.shields.io/pypi/v/library-name)](https://pypi.org/project/library-name/)
[![Tests](https://github.com/org/library-name/actions/workflows/test.yml/badge.svg)](...)

## Features

- Feature 1 with brief explanation
- Feature 2 with brief explanation
- Feature 3 with brief explanation

## Installation

```bash
pip install library-name
```

## Quick Start

```python
from library_name import main_function

# Most common use case in 3-5 lines
result = main_function(input_data)
print(result)
```

## Documentation

- [Getting Started Guide](docs/getting-started.md)
- [API Reference](docs/api.md)
- [Examples](examples/)

## Basic Usage

### Use Case 1

```python
# Runnable example
```

### Use Case 2

```python
# Runnable example
```

## Advanced Features

### Feature A

Explanation and example.

### Feature B

Explanation and example.

## Configuration

| Option | Type | Default | Description |
|--------|------|---------|-------------|
| timeout | int | 30 | Request timeout |
| retries | int | 3 | Number of retries |

## Error Handling

```python
from library_name.exceptions import LibraryError

try:
    result = main_function(data)
except LibraryError as e:
    print(f"Operation failed: {e}")
```

## Contributing

See [CONTRIBUTING.md](CONTRIBUTING.md) for guidelines.

## License

MIT License - see [LICENSE](LICENSE)
```

### Pitfalls to Avoid

- Don't put every feature in the README
- Don't forget error handling examples
- Don't skip the quick start section

## Pattern 2: The API Service Documentation

### When to Use

When documenting a REST API or web service.

### Implementation

```markdown
# Service Name API

Brief description of what the API provides.

Base URL: `https://api.example.com/v1`

## Authentication

All requests require an API key in the header:

```bash
curl -H "Authorization: Bearer YOUR_API_KEY" https://api.example.com/v1/endpoint
```

## Rate Limits

- 100 requests per minute
- 10,000 requests per day

## Endpoints

### Resources

#### List Resources

```
GET /resources
```

**Parameters**
| Name | Type | Required | Description |
|------|------|----------|-------------|
| limit | integer | No | Max results (default 20) |
| offset | integer | No | Pagination offset |

**Response**
```json
{
    "data": [
        {"id": "1", "name": "Example"}
    ],
    "meta": {
        "total": 100,
        "limit": 20,
        "offset": 0
    }
}
```

#### Get Resource

```
GET /resources/{id}
```

**Response**
```json
{
    "id": "1",
    "name": "Example",
    "created_at": "2024-01-15T10:30:00Z"
}
```

**Errors**
| Code | Description |
|------|-------------|
| 404 | Resource not found |

#### Create Resource

```
POST /resources
```

**Request Body**
```json
{
    "name": "New Resource",
    "type": "example"
}
```

**Response** (201 Created)
```json
{
    "id": "2",
    "name": "New Resource",
    "type": "example"
}
```

## Error Handling

All errors follow this format:

```json
{
    "error": {
        "code": "RESOURCE_NOT_FOUND",
        "message": "The requested resource does not exist",
        "details": {"resource_id": "123"}
    }
}
```

### Error Codes

| Code | HTTP Status | Description |
|------|-------------|-------------|
| INVALID_REQUEST | 400 | Request validation failed |
| UNAUTHORIZED | 401 | Invalid or missing API key |
| RESOURCE_NOT_FOUND | 404 | Resource doesn't exist |
| RATE_LIMITED | 429 | Too many requests |

## SDKs

- [Python SDK](https://github.com/org/sdk-python)
- [JavaScript SDK](https://github.com/org/sdk-js)

## Changelog

See [CHANGELOG.md](CHANGELOG.md) for version history.
```

### Pitfalls to Avoid

- Don't forget authentication details
- Don't skip error responses
- Don't omit rate limit information

## Pattern 3: The Function Docstring

### When to Use

When documenting any public function or method.

### Implementation (Google Style)

```python
def process_payment(
    amount: Decimal,
    currency: str,
    customer_id: str,
    idempotency_key: str | None = None,
) -> PaymentResult:
    """Process a payment transaction.

    Charges the customer's default payment method for the specified amount.
    The transaction is idempotent if an idempotency_key is provided.

    Args:
        amount: The payment amount. Must be positive.
        currency: ISO 4217 currency code (e.g., "USD", "EUR").
        customer_id: The unique identifier of the customer.
        idempotency_key: Optional key to prevent duplicate charges.
            If provided and a payment with this key exists, the
            existing payment is returned instead of creating a new one.

    Returns:
        PaymentResult containing the payment ID, status, and receipt URL.

    Raises:
        InvalidAmountError: If amount is zero or negative.
        CustomerNotFoundError: If customer_id doesn't exist.
        PaymentDeclinedError: If the payment method was declined.
            Contains decline_code and message for debugging.
        PaymentProcessingError: If an unexpected error occurs.

    Example:
        >>> from decimal import Decimal
        >>> result = process_payment(
        ...     amount=Decimal("19.99"),
        ...     currency="USD",
        ...     customer_id="cust_123",
        ...     idempotency_key="order_456"
        ... )
        >>> print(result.status)
        'succeeded'
        >>> print(result.receipt_url)
        'https://pay.example.com/receipts/pay_abc'

    Note:
        This function is synchronous. For high-throughput scenarios,
        consider using `process_payment_async` instead.
    """
```

### Implementation (NumPy Style)

```python
def calculate_statistics(
    data: np.ndarray,
    weights: np.ndarray | None = None,
) -> StatisticsResult:
    """Calculate weighted statistics for an array.

    Parameters
    ----------
    data : np.ndarray
        Input data array. Must be 1-dimensional.
    weights : np.ndarray, optional
        Weight for each data point. If None, uniform weights are used.
        Must have same shape as data.

    Returns
    -------
    StatisticsResult
        Named tuple containing:
        - mean : float
            Weighted mean of the data.
        - std : float
            Weighted standard deviation.
        - median : float
            Weighted median.

    Raises
    ------
    ValueError
        If data is empty or multi-dimensional.
    ShapeMismatchError
        If weights shape doesn't match data shape.

    Examples
    --------
    >>> data = np.array([1, 2, 3, 4, 5])
    >>> result = calculate_statistics(data)
    >>> result.mean
    3.0

    >>> weights = np.array([1, 1, 1, 2, 2])
    >>> result = calculate_statistics(data, weights)
    >>> result.mean
    3.57
    """
```

### Pitfalls to Avoid

- Don't skip the Raises section
- Don't write vague parameter descriptions
- Don't forget to include examples

## Pattern 4: The Class Documentation

### When to Use

When documenting a class, especially public API classes.

### Implementation

```python
class DataPipeline:
    """A configurable data processing pipeline.

    DataPipeline provides a fluent interface for building and executing
    data transformation workflows. Pipelines are immutable - each
    transformation method returns a new pipeline instance.

    The pipeline supports three types of operations:
    - **Transformations**: Map, filter, and modify data
    - **Aggregations**: Reduce data to summary statistics
    - **I/O Operations**: Read from and write to various sources

    Attributes:
        name: Human-readable name for the pipeline.
        stages: List of transformation stages (read-only).
        config: Pipeline configuration settings.

    Example:
        Basic usage with method chaining:

        >>> pipeline = (
        ...     DataPipeline("user-analysis")
        ...     .read_csv("users.csv")
        ...     .filter(lambda row: row["active"])
        ...     .transform(normalize_email)
        ...     .aggregate(count_by("country"))
        ...     .write_json("output.json")
        ... )
        >>> result = pipeline.execute()

        Using configuration:

        >>> config = PipelineConfig(parallel=True, workers=4)
        >>> pipeline = DataPipeline("fast-pipeline", config=config)

    Note:
        Pipelines are lazy - no processing occurs until execute() is called.
        This allows for optimization and validation before running.

    See Also:
        StreamingPipeline: For processing data that doesn't fit in memory.
        PipelineConfig: Configuration options for pipeline execution.
    """

    def __init__(
        self,
        name: str,
        config: PipelineConfig | None = None,
    ) -> None:
        """Initialize a new DataPipeline.

        Args:
            name: Human-readable name for identification and logging.
            config: Optional configuration. Uses defaults if not provided.
        """

    def transform(
        self,
        func: Callable[[Row], Row],
        name: str | None = None,
    ) -> "DataPipeline":
        """Apply a transformation function to each row.

        Args:
            func: Function that takes a row and returns a transformed row.
            name: Optional name for this stage (for debugging).

        Returns:
            A new DataPipeline with the transformation added.

        Example:
            >>> def uppercase_name(row):
            ...     row["name"] = row["name"].upper()
            ...     return row
            >>> pipeline = pipeline.transform(uppercase_name)
        """
```

### Pitfalls to Avoid

- Don't skip the class-level docstring
- Don't forget to document attributes
- Don't omit usage examples

## Anti-Patterns

### Anti-Pattern 1: The Empty Docstring

Docstrings that exist but provide no value.

```python
# Bad
def process(data):
    """Process the data."""
    ...

# Good
def process(data: list[dict]) -> ProcessResult:
    """Transform raw data records into normalized format.

    Args:
        data: List of raw data dictionaries from the API.

    Returns:
        ProcessResult containing normalized records and error count.
    """
```

### Anti-Pattern 2: The Outdated README

README that describes features differently than they work.

```markdown
# Bad - README says one thing, code does another

## Usage
```python
result = process(data, format="json")  # format param was removed!
```
```

### Anti-Pattern 3: The Comment That Repeats Code

Comments that describe what's obvious from the code.

```python
# Bad
x = x + 1  # Increment x by 1

# Good
x = x + 1  # Account for 0-based indexing in output
```

## Choosing the Right Pattern

| Component Type | Primary Pattern | Key Sections |
|---------------|-----------------|--------------|
| Library/Package | Library README | Features, Quick Start, API |
| REST API | API Docs | Endpoints, Auth, Errors |
| Function | Docstring | Args, Returns, Raises, Example |
| Class | Class Docs | Purpose, Attributes, Methods |
| Module | Module Docstring | Overview, Key Functions, Examples |
