# CLAUDE.md - Pydantic v2

This skill teaches data validation, serialization, and settings management using Pydantic v2, the most widely-used data validation library for Python.

## Key Concepts

- **BaseModel**: The foundation class for all Pydantic models with automatic validation
- **Field Types**: Built-in types with constraints (str, int, EmailStr, HttpUrl, etc.)
- **Validators**: Custom validation logic with @field_validator and @model_validator
- **Serialization**: Converting models to dict/JSON with model_dump() and model_dump_json()
- **Computed Fields**: Derived fields using @computed_field decorator
- **Model Composition**: Nested models, inheritance, and generic models

## Common Commands

```bash
make setup      # Install dependencies with UV
make examples   # Run all examples
make example-1  # Run basic models example
make example-2  # Run validators example
make example-3  # Run serialization example
make example-4  # Run composition example
make test       # Run pytest
make lint       # Run ruff and mypy
make clean      # Remove build artifacts
```

## Project Structure

```
pydantic-v2/
├── src/pydantic_v2/
│   ├── __init__.py
│   └── examples/
│       ├── example_1_basic_models.py
│       ├── example_2_validators.py
│       ├── example_3_serialization.py
│       └── example_4_composition.py
├── exercises/
│   ├── exercise_1_user_profile.py
│   ├── exercise_2_product_catalog.py
│   ├── exercise_3_api_responses.py
│   └── solutions/
├── tests/
│   └── test_examples.py
└── docs/
    ├── concepts.md
    └── patterns.md
```

## Code Patterns

### Pattern 1: Basic Model with Constraints
```python
from pydantic import BaseModel, Field

class User(BaseModel):
    name: str = Field(min_length=1, max_length=100)
    age: int = Field(ge=0, le=150)
    email: str
```

### Pattern 2: Field Validator
```python
from pydantic import BaseModel, field_validator

class Product(BaseModel):
    price: float

    @field_validator('price')
    @classmethod
    def validate_price(cls, v: float) -> float:
        if v < 0:
            raise ValueError('Price cannot be negative')
        return round(v, 2)
```

### Pattern 3: Model Validator (cross-field validation)
```python
from pydantic import BaseModel, model_validator

class DateRange(BaseModel):
    start: datetime
    end: datetime

    @model_validator(mode='after')
    def validate_range(self) -> 'DateRange':
        if self.end <= self.start:
            raise ValueError('end must be after start')
        return self
```

### Pattern 4: Computed Fields
```python
from pydantic import BaseModel, computed_field

class Rectangle(BaseModel):
    width: float
    height: float

    @computed_field
    @property
    def area(self) -> float:
        return self.width * self.height
```

## Common Mistakes

1. **Using v1 syntax in v2**
   - v1 used `@validator`, v2 uses `@field_validator`
   - v1 used `.dict()`, v2 uses `.model_dump()`
   - v1 used class `Config`, v2 uses `model_config` dict

2. **Forgetting @classmethod on field_validator**
   - Field validators must be class methods
   - The first parameter after `cls` is the value being validated

3. **Not catching ValidationError**
   - Always wrap parsing of untrusted data in try/except
   - Use `e.errors()` to get structured error information

4. **Mutating model fields directly**
   - Models are immutable by default
   - Use `model_copy(update={...})` to create modified copies

## When Users Ask About...

### "How do I get started?"
Point them to `make setup && make examples` and the README.md. Start with example_1 for basics.

### "Why isn't my validator running?"
Check that:
1. The decorator is `@field_validator`, not `@validator`
2. The method has `@classmethod` decorator
3. The field name in the decorator matches exactly

### "How do I handle optional fields?"
Use `Optional[Type]` or `Type | None` with a default value:
```python
from typing import Optional
nickname: Optional[str] = None
# or
nickname: str | None = None
```

### "How do I validate across multiple fields?"
Use `@model_validator(mode='after')` for cross-field validation.

### "What's the difference between mode='before' and mode='after'?"
- `mode='before'`: Validator runs before Pydantic's built-in validation
- `mode='after'`: Validator runs after all fields are validated

## Testing Notes

- Tests use pytest with markers
- Run specific tests: `pytest -k "test_name"`
- Check coverage: `make coverage`
- Tests include both valid and invalid input cases

## Dependencies

Key dependencies in pyproject.toml:
- pydantic>=2.0.0: Core validation library
- email-validator: For EmailStr validation
- pytest: Testing framework
- pytest-cov: Coverage reporting
