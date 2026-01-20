# Core Concepts

## Overview

Pydantic v2 is a data validation library that uses Python type hints to validate data at runtime. It provides a declarative way to define data structures with automatic validation, serialization, and documentation.

## Concept 1: BaseModel

### What It Is

`BaseModel` is the foundation class for all Pydantic models. When you inherit from it, you create a data class with automatic validation, serialization, and type coercion.

### Why It Matters

- Catches data errors at runtime with clear error messages
- Provides automatic type coercion (e.g., "42" -> 42 for int fields)
- Generates JSON Schema automatically
- Enables IDE autocompletion and type checking

### How It Works

When you instantiate a model, Pydantic:
1. Validates all input data against the field types
2. Coerces compatible types (configurable)
3. Raises `ValidationError` with details if validation fails
4. Returns an immutable model instance

```python
from pydantic import BaseModel

class User(BaseModel):
    name: str
    age: int
    active: bool = True  # Default value

# Successful creation
user = User(name="Alice", age=30)
print(user.name)  # "Alice"
print(user.age)   # 30

# Type coercion
user2 = User(name="Bob", age="25")  # String "25" coerced to int 25

# Validation error
try:
    User(name="Charlie", age="not a number")
except ValidationError as e:
    print(e.errors())
```

## Concept 2: Field Constraints

### What It Is

The `Field` function allows you to add metadata and constraints to model fields, such as minimum/maximum values, string patterns, and descriptions.

### Why It Matters

- Enforces business rules at the data layer
- Self-documents your data requirements
- Generates accurate API documentation
- Catches invalid data early

### How It Works

`Field()` accepts various parameters depending on the field type:

```python
from pydantic import BaseModel, Field

class Product(BaseModel):
    # Numeric constraints
    price: float = Field(gt=0, description="Product price in USD")
    quantity: int = Field(ge=0, le=1000, default=0)

    # String constraints
    name: str = Field(min_length=1, max_length=100)
    sku: str = Field(pattern=r'^[A-Z]{3}-\d{4}$')  # e.g., "ABC-1234"

    # General constraints
    tags: list[str] = Field(default_factory=list, max_length=10)

# Common Field parameters:
# - gt, ge, lt, le: numeric comparisons
# - min_length, max_length: string/list length
# - pattern: regex pattern for strings
# - default, default_factory: default values
# - description: field documentation
# - examples: example values for docs
```

## Concept 3: Validators

### What It Is

Validators are methods decorated with `@field_validator` or `@model_validator` that run custom validation logic beyond built-in constraints.

### Why It Matters

- Implement complex business rules
- Transform data during validation
- Validate relationships between fields
- Provide custom error messages

### How It Works

**Field Validators** validate a single field:

```python
from pydantic import BaseModel, field_validator

class User(BaseModel):
    username: str
    password: str

    @field_validator('username')
    @classmethod
    def username_alphanumeric(cls, v: str) -> str:
        if not v.isalnum():
            raise ValueError('must be alphanumeric')
        return v.lower()  # Transform to lowercase

    @field_validator('password')
    @classmethod
    def password_strength(cls, v: str) -> str:
        if len(v) < 8:
            raise ValueError('must be at least 8 characters')
        if not any(c.isupper() for c in v):
            raise ValueError('must contain uppercase letter')
        return v
```

**Model Validators** validate the entire model (cross-field validation):

```python
from pydantic import BaseModel, model_validator

class DateRange(BaseModel):
    start_date: date
    end_date: date

    @model_validator(mode='after')
    def validate_date_range(self) -> 'DateRange':
        if self.end_date <= self.start_date:
            raise ValueError('end_date must be after start_date')
        return self
```

## Concept 4: Serialization

### What It Is

Serialization converts Pydantic models to dictionaries, JSON strings, or other formats. Pydantic v2 provides fine-grained control over what and how data is serialized.

### Why It Matters

- API responses often need JSON output
- Database storage may need dict conversion
- Different contexts may need different field subsets
- Sensitive fields may need exclusion

### How It Works

```python
from pydantic import BaseModel, Field, field_serializer
from datetime import datetime

class User(BaseModel):
    name: str
    email: str
    password: str = Field(exclude=True)  # Never serialize
    created_at: datetime

    @field_serializer('created_at')
    def serialize_datetime(self, dt: datetime) -> str:
        return dt.isoformat()

user = User(
    name="Alice",
    email="alice@example.com",
    password="secret123",
    created_at=datetime.now()
)

# Convert to dict
data = user.model_dump()
# {'name': 'Alice', 'email': 'alice@example.com', 'created_at': '2024-...'}

# Convert to JSON
json_str = user.model_dump_json()

# Selective serialization
user.model_dump(include={'name', 'email'})
user.model_dump(exclude={'email'})
user.model_dump(exclude_unset=True)  # Only explicitly set fields
```

## Concept 5: Computed Fields

### What It Is

Computed fields are derived values calculated from other fields. They appear in serialization but aren't stored or validated as inputs.

### Why It Matters

- Avoid data duplication
- Ensure derived values are always consistent
- Simplify API responses with calculated values

### How It Works

```python
from pydantic import BaseModel, computed_field

class Rectangle(BaseModel):
    width: float
    height: float

    @computed_field
    @property
    def area(self) -> float:
        return self.width * self.height

    @computed_field
    @property
    def perimeter(self) -> float:
        return 2 * (self.width + self.height)

rect = Rectangle(width=10, height=5)
print(rect.area)       # 50.0
print(rect.perimeter)  # 30.0
print(rect.model_dump())
# {'width': 10.0, 'height': 5.0, 'area': 50.0, 'perimeter': 30.0}
```

## Summary

Key takeaways from these concepts:

1. **BaseModel** is your foundation - inherit from it for all data structures
2. **Field()** adds constraints and metadata without custom code
3. **Validators** handle complex business logic that constraints can't express
4. **Serialization** is built-in and highly configurable
5. **Computed fields** keep derived data consistent and DRY

Together, these concepts enable you to build robust, self-validating data layers that catch errors early and provide clear feedback.
