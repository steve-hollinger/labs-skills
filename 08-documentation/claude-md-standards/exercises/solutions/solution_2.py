"""Solution for Exercise 2: Improve a Poorly-Written CLAUDE.md

This is the reference solution showing how to transform vague,
unhelpful CLAUDE.md content into specific, actionable guidance.
"""


def solution() -> str:
    """Reference solution for Exercise 2.

    Returns:
        The improved CLAUDE.md content.
    """
    return '''# CLAUDE.md - Payment Processing Service

A microservice handling payment transactions, refunds, and payment method management using Stripe as the payment provider.

## Overview

This service provides:
- Credit card payment processing via Stripe
- Refund handling (full and partial)
- Payment method storage (tokenized, PCI-compliant)
- Webhook handling for async payment events
- Transaction history and reporting

**Important:** This service handles financial data. All changes require code review and must pass all tests.

## Key Commands

```bash
# Setup
make setup              # Install dependencies
cp .env.example .env    # Create local env file
make db-start           # Start PostgreSQL
make db-migrate         # Run migrations

# Development
make dev                # Start server on port 8080
make dev-stripe         # Start with Stripe CLI for webhooks

# Testing
make test               # All tests (uses Stripe test mode)
make test-unit          # Unit tests only (no Stripe calls)
make test-integration   # Integration tests (requires Stripe)

# Code Quality
make lint               # Ruff + mypy strict mode
make format             # Auto-format code
make security-scan      # Run bandit security checks
```

## Project Structure

```
payment_service/
├── src/
│   ├── api/
│   │   ├── routes/          # FastAPI route handlers
│   │   └── schemas/         # Pydantic request/response models
│   ├── core/
│   │   ├── config.py        # Settings from environment
│   │   └── security.py      # API key validation
│   ├── domain/
│   │   ├── models/          # SQLAlchemy models
│   │   └── services/        # Business logic
│   └── integrations/
│       └── stripe_client.py # Stripe API wrapper
└── tests/
    ├── unit/                # No external calls
    ├── integration/         # Stripe test mode
    └── fixtures/            # Test data factories
```

## Architecture

### Service Layer Pattern
All business logic in `domain/services/`. Routes are thin wrappers.

```python
# Good - route calls service
@router.post("/payments")
async def create_payment(request: PaymentRequest):
    return await PaymentService.process_payment(request)

# Bad - business logic in route
@router.post("/payments")
async def create_payment(request: PaymentRequest):
    # Don't put Stripe calls here
    stripe.PaymentIntent.create(...)
```

### Stripe Integration
All Stripe calls go through `stripe_client.py`. Never call Stripe directly from routes or services.

```python
from src.integrations.stripe_client import StripeClient

# Good
result = await StripeClient.create_payment_intent(amount, currency)

# Bad - direct Stripe call
import stripe
stripe.PaymentIntent.create(amount=amount)
```

### Error Handling
```python
from src.core.exceptions import PaymentError, PaymentDeclinedError

# Specific exceptions with context
raise PaymentDeclinedError(
    message="Card declined",
    decline_code="insufficient_funds",
    payment_intent_id=pi_id
)

# Never expose raw Stripe errors to API consumers
try:
    result = await StripeClient.charge(...)
except stripe.CardError as e:
    raise PaymentDeclinedError.from_stripe_error(e)
```

## Code Style

### Naming Conventions
- Functions: `snake_case` (e.g., `process_refund`)
- Classes: `PascalCase` (e.g., `PaymentService`)
- Constants: `UPPER_SNAKE_CASE` (e.g., `MAX_REFUND_AMOUNT`)
- Files: `snake_case.py`

### Type Hints
Required on all functions. Use strict mypy.
```python
async def process_payment(
    amount: Decimal,
    currency: str,
    customer_id: str,
) -> PaymentResult:
    ...
```

### Amounts
Always use `Decimal` for money. Never `float`.
```python
from decimal import Decimal

# Good
amount = Decimal("19.99")

# Bad - floating point errors
amount = 19.99
```

## Common Mistakes

1. **Using float for money**
   - Why: Floating point precision errors
   - Fix: Use `Decimal` from the `decimal` module
   - Example: `Decimal("10.00")` not `10.00`

2. **Not validating webhook signatures**
   - Why: Security vulnerability, fake webhooks
   - Fix: Always use `stripe.Webhook.construct_event()`
   - Location: `src/api/routes/webhooks.py`

3. **Logging sensitive data**
   - Why: PCI compliance violation
   - Fix: Never log card numbers, CVV, or full tokens
   - Use: `mask_card_number()` from `src/core/security.py`

4. **Missing idempotency keys**
   - Why: Duplicate charges on retries
   - Fix: Always pass `idempotency_key` to Stripe calls
   ```python
   stripe.PaymentIntent.create(
       amount=amount,
       idempotency_key=f"payment-{order_id}"
   )
   ```

5. **Hardcoding Stripe keys**
   - Why: Security risk, breaks environments
   - Fix: Use environment variables via `src/core/config.py`

## Troubleshooting

### "Stripe API key is invalid"
```bash
# Check your .env file
cat .env | grep STRIPE

# Should have:
# STRIPE_SECRET_KEY=sk_test_...
# STRIPE_WEBHOOK_SECRET=whsec_...

# For local webhook testing:
stripe listen --forward-to localhost:8080/webhooks
```

### "Database connection refused"
```bash
# Start PostgreSQL
make db-start

# Check it's running
docker ps | grep postgres

# View logs if issues
docker logs payment-postgres
```

### "Tests failing with 'rate limit exceeded'"
Stripe test mode has rate limits. Solutions:
```bash
# Run with delays between tests
pytest --stripe-delay=1

# Or mock Stripe calls for unit tests
pytest tests/unit/  # No real Stripe calls
```

### "Webhook events not received locally"
```bash
# Install Stripe CLI
brew install stripe/stripe-cli/stripe

# Forward webhooks to local server
stripe listen --forward-to localhost:8080/webhooks

# Copy the webhook secret it shows to your .env
```

## Testing Notes

- **Unit tests**: Mock all external calls (Stripe, database)
- **Integration tests**: Use Stripe test mode, real database
- **Test cards**: Use Stripe's test card numbers
  - Success: `4242424242424242`
  - Decline: `4000000000000002`
  - Requires auth: `4000002500003155`

```python
# Example test with Stripe test mode
async def test_successful_payment(stripe_test_client):
    result = await PaymentService.process_payment(
        amount=Decimal("10.00"),
        card_number="4242424242424242",  # Test card
    )
    assert result.status == "succeeded"
```

## Security Requirements

- All PRs require security review for payment-related changes
- Never log full card numbers (use `mask_card_number()`)
- PCI DSS compliance required - no card data in our database
- Use Stripe tokens, not raw card data
- Webhook endpoints must validate signatures

## Dependencies

Key packages:
- stripe: Stripe API client
- fastapi: Web framework
- sqlalchemy: Database ORM
- pydantic: Data validation
- python-decimal: Precise money handling
'''


if __name__ == "__main__":
    from claude_md_standards.validator import validate_claude_md
    from rich.console import Console

    console = Console()

    # Show comparison
    from exercises.exercise_2 import BAD_CLAUDE_MD

    console.print("[bold]Original (Bad) Score:[/bold]")
    bad_result = validate_claude_md(BAD_CLAUDE_MD)
    console.print(f"  Score: [red]{bad_result.score}/100[/red]")

    console.print("\n[bold]Solution Score:[/bold]")
    good_result = validate_claude_md(solution())
    console.print(f"  Score: [green]{good_result.score}/100[/green]")

    improvement = good_result.score - bad_result.score
    console.print(f"\n[bold green]Improvement: +{improvement} points[/bold green]")
