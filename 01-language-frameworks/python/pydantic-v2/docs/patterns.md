# Common Patterns

## Overview

This document covers common patterns and best practices for Pydantic v2 data validation.

## Pattern 1: Request/Response Models

### When to Use

When building APIs that receive and send structured data. Separate models for input (create/update) vs output (response) provide better validation and security.

### Implementation

```python
from pydantic import BaseModel, Field, computed_field
from datetime import datetime
from typing import Optional

# Input model - what the client sends
class UserCreate(BaseModel):
    username: str = Field(min_length=3, max_length=50)
    email: str
    password: str = Field(min_length=8)

# Update model - partial updates with all optional
class UserUpdate(BaseModel):
    username: Optional[str] = Field(None, min_length=3, max_length=50)
    email: Optional[str] = None

# Output model - what the API returns
class UserResponse(BaseModel):
    id: int
    username: str
    email: str
    created_at: datetime

    model_config = {"from_attributes": True}  # Allow ORM objects
```

### Example

```python
# Create endpoint receives UserCreate
def create_user(data: UserCreate) -> UserResponse:
    # Password never exposed in response
    user = db.create(data)
    return UserResponse.model_validate(user)

# Update endpoint receives UserUpdate
def update_user(user_id: int, data: UserUpdate) -> UserResponse:
    updates = data.model_dump(exclude_unset=True)
    user = db.update(user_id, updates)
    return UserResponse.model_validate(user)
```

### Pitfalls to Avoid

- Don't include sensitive fields (passwords, tokens) in response models
- Don't use the same model for create and response
- Remember to set `from_attributes=True` for ORM integration

## Pattern 2: Nested Models with Validation

### When to Use

When data has hierarchical structure and each level needs validation.

### Implementation

```python
from pydantic import BaseModel, Field, model_validator
from typing import List

class Address(BaseModel):
    street: str
    city: str
    country: str = Field(min_length=2, max_length=2)  # ISO code
    postal_code: str

class OrderItem(BaseModel):
    product_id: int
    quantity: int = Field(gt=0)
    unit_price: float = Field(gt=0)

    @computed_field
    @property
    def total(self) -> float:
        return self.quantity * self.unit_price

class Order(BaseModel):
    customer_id: int
    shipping_address: Address
    billing_address: Address | None = None
    items: List[OrderItem] = Field(min_length=1)

    @computed_field
    @property
    def order_total(self) -> float:
        return sum(item.total for item in self.items)

    @model_validator(mode='after')
    def set_billing_address(self) -> 'Order':
        if self.billing_address is None:
            # Use shipping address if billing not provided
            self.billing_address = self.shipping_address
        return self
```

### Example

```python
order = Order(
    customer_id=123,
    shipping_address={
        "street": "123 Main St",
        "city": "Boston",
        "country": "US",
        "postal_code": "02101"
    },
    items=[
        {"product_id": 1, "quantity": 2, "unit_price": 29.99},
        {"product_id": 2, "quantity": 1, "unit_price": 49.99}
    ]
)
print(order.order_total)  # 109.97
```

### Pitfalls to Avoid

- Don't deeply nest beyond 3-4 levels (consider flattening)
- Don't forget that nested validation errors include the path

## Pattern 3: Discriminated Unions

### When to Use

When a field can be one of several types, and you need to distinguish them based on a discriminator field.

### Implementation

```python
from pydantic import BaseModel, Field
from typing import Literal, Union
from typing_extensions import Annotated

class CreditCardPayment(BaseModel):
    type: Literal["credit_card"] = "credit_card"
    card_number: str = Field(min_length=16, max_length=16)
    expiry: str
    cvv: str = Field(min_length=3, max_length=4)

class BankTransferPayment(BaseModel):
    type: Literal["bank_transfer"] = "bank_transfer"
    account_number: str
    routing_number: str

class PayPalPayment(BaseModel):
    type: Literal["paypal"] = "paypal"
    email: str

# Discriminated union - Pydantic uses 'type' field to determine which model
Payment = Annotated[
    Union[CreditCardPayment, BankTransferPayment, PayPalPayment],
    Field(discriminator="type")
]

class Checkout(BaseModel):
    order_id: int
    payment: Payment
```

### Example

```python
# Automatically parsed as CreditCardPayment
checkout1 = Checkout(
    order_id=1,
    payment={
        "type": "credit_card",
        "card_number": "4111111111111111",
        "expiry": "12/25",
        "cvv": "123"
    }
)

# Automatically parsed as PayPalPayment
checkout2 = Checkout(
    order_id=2,
    payment={"type": "paypal", "email": "user@example.com"}
)
```

### Pitfalls to Avoid

- Ensure discriminator field has the same name in all union members
- Use `Literal` types for the discriminator values
- Remember the discriminator must be a required field

## Pattern 4: Custom Types with Annotated

### When to Use

When you need reusable validated types across multiple models.

### Implementation

```python
from pydantic import BaseModel, AfterValidator, BeforeValidator
from typing_extensions import Annotated
import re

# Custom validated types
def validate_phone(v: str) -> str:
    # Remove non-digits
    digits = re.sub(r'\D', '', v)
    if len(digits) != 10:
        raise ValueError('Phone number must be 10 digits')
    return f"({digits[:3]}) {digits[3:6]}-{digits[6:]}"

def validate_slug(v: str) -> str:
    v = v.lower().strip()
    if not re.match(r'^[a-z0-9]+(?:-[a-z0-9]+)*$', v):
        raise ValueError('Invalid slug format')
    return v

PhoneNumber = Annotated[str, AfterValidator(validate_phone)]
Slug = Annotated[str, AfterValidator(validate_slug)]

# Reuse across models
class Contact(BaseModel):
    name: str
    phone: PhoneNumber

class BlogPost(BaseModel):
    title: str
    slug: Slug
    author_phone: PhoneNumber
```

### Example

```python
contact = Contact(name="Alice", phone="555-123-4567")
print(contact.phone)  # "(555) 123-4567"

post = BlogPost(
    title="Hello World",
    slug="hello-world",
    author_phone="5551234567"
)
```

### Pitfalls to Avoid

- Use `AfterValidator` for validation after type coercion
- Use `BeforeValidator` for preprocessing before type coercion
- Keep custom validators simple and focused

## Pattern 5: Configuration with model_config

### When to Use

When you need to customize model behavior globally.

### Implementation

```python
from pydantic import BaseModel, ConfigDict

class StrictModel(BaseModel):
    """Base model with strict validation."""
    model_config = ConfigDict(
        strict=True,           # No type coercion
        frozen=True,           # Immutable
        extra="forbid",        # No extra fields allowed
        validate_assignment=True,  # Validate on attribute assignment
    )

class APIModel(BaseModel):
    """Base model for API responses."""
    model_config = ConfigDict(
        from_attributes=True,  # Allow ORM objects
        populate_by_name=True, # Allow alias or field name
        str_strip_whitespace=True,  # Strip whitespace from strings
    )

class User(APIModel):
    user_name: str = Field(alias="userName")
    email_address: str = Field(alias="emailAddress")

# Works with both snake_case and camelCase
user1 = User(userName="alice", emailAddress="alice@example.com")
user2 = User(user_name="bob", email_address="bob@example.com")
```

### Pitfalls to Avoid

- `strict=True` disables all type coercion (may break existing code)
- `frozen=True` makes models hashable but immutable
- `extra="forbid"` is safer for APIs but may break forward compatibility

## Anti-Patterns

### Anti-Pattern 1: Mutable Default Values

Don't use mutable defaults directly:

```python
# Bad - shared mutable default
class BadModel(BaseModel):
    tags: list[str] = []  # This will cause issues

# Good - use default_factory
class GoodModel(BaseModel):
    tags: list[str] = Field(default_factory=list)
```

### Better Approach

Always use `Field(default_factory=...)` for mutable defaults like lists, dicts, or sets.

### Anti-Pattern 2: Over-Validation in Models

Don't put business logic in validators:

```python
# Bad - business logic in model
class OrderBad(BaseModel):
    items: list[OrderItem]

    @model_validator(mode='after')
    def apply_discounts_and_calculate_tax(self) -> 'OrderBad':
        # Don't do complex business logic here
        pass

# Good - models validate data structure only
class OrderGood(BaseModel):
    items: list[OrderItem]

    @computed_field
    @property
    def subtotal(self) -> float:
        return sum(item.total for item in self.items)

# Business logic in service layer
def process_order(order: OrderGood) -> ProcessedOrder:
    discounts = calculate_discounts(order)
    tax = calculate_tax(order)
    return ProcessedOrder(...)
```

## Choosing the Right Pattern

| Scenario | Recommended Pattern |
|----------|-------------------|
| API input/output | Request/Response Models |
| Hierarchical data | Nested Models |
| Polymorphic types | Discriminated Unions |
| Reusable validation | Custom Types with Annotated |
| ORM integration | model_config with from_attributes |
| Immutable data | model_config with frozen=True |
