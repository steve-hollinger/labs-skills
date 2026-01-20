# Pydantic v2

Master data validation, serialization, and settings management with Pydantic v2 - the most widely-used data validation library for Python.

## Learning Objectives

After completing this skill, you will be able to:
- Define data models with automatic validation
- Use field types, constraints, and custom validators
- Serialize models to JSON/dict and parse from various sources
- Implement computed fields and model methods
- Use model inheritance and composition effectively
- Handle validation errors gracefully

## Prerequisites

- Python 3.11+
- UV package manager
- Basic understanding of Python type hints

## Quick Start

```bash
# Install dependencies
make setup

# Run examples
make examples

# Run tests
make test
```

## Concepts

### Models and Fields

Pydantic models are Python classes that inherit from `BaseModel`. Fields are defined using type annotations with automatic validation.

```python
from pydantic import BaseModel, Field

class User(BaseModel):
    name: str
    age: int = Field(ge=0, le=150)
    email: str = Field(pattern=r'^[\w\.-]+@[\w\.-]+\.\w+$')
```

### Validators

Custom validation logic using `@field_validator` and `@model_validator` decorators.

```python
from pydantic import BaseModel, field_validator

class Product(BaseModel):
    name: str
    price: float

    @field_validator('price')
    @classmethod
    def price_must_be_positive(cls, v: float) -> float:
        if v <= 0:
            raise ValueError('Price must be positive')
        return v
```

### Serialization

Control how models are converted to dicts/JSON with serialization options.

```python
user = User(name="Alice", age=30, email="alice@example.com")
user.model_dump()  # Convert to dict
user.model_dump_json()  # Convert to JSON string
```

## Examples

### Example 1: Basic Models

This example demonstrates defining models with various field types and constraints.

```bash
make example-1
```

### Example 2: Custom Validators

Building on the basics with field and model validators for complex validation logic.

```bash
make example-2
```

### Example 3: Serialization and Parsing

Advanced serialization options and parsing from various data sources.

```bash
make example-3
```

### Example 4: Model Composition

Using nested models, inheritance, and generic models.

```bash
make example-4
```

## Exercises

See the [exercises](./exercises/) directory for practice problems:

1. **Exercise 1**: Create a User Profile Model - Define a user model with proper validation
2. **Exercise 2**: Build a Product Catalog - Implement nested models with validators
3. **Exercise 3**: API Response Models - Create serializable response models with computed fields

Solutions are available in [exercises/solutions/](./exercises/solutions/).

## Common Mistakes

### Using v1 Syntax in v2

Pydantic v2 uses new decorator names and methods:
- `@validator` -> `@field_validator`
- `.dict()` -> `.model_dump()`
- `.json()` -> `.model_dump_json()`
- `Config` class -> `model_config` dict

### Forgetting @classmethod on Validators

Field validators must be class methods:

```python
# Correct
@field_validator('name')
@classmethod
def validate_name(cls, v):
    return v

# Incorrect - will not work
@field_validator('name')
def validate_name(self, v):
    return v
```

### Not Handling ValidationError

Always catch `ValidationError` when parsing untrusted data:

```python
from pydantic import ValidationError

try:
    user = User(**untrusted_data)
except ValidationError as e:
    print(e.errors())
```

## Further Reading

- [Official Pydantic Documentation](https://docs.pydantic.dev/)
- [Migration Guide v1 to v2](https://docs.pydantic.dev/latest/migration/)
- Related skills in this repository:
  - [FastAPI Basics](../fastapi-basics/) - Uses Pydantic for request/response models
  - [Dynaconf Config](../dynaconf-config/) - Alternative configuration approach
