"""Solution for Exercise 3: Create a CLAUDE.md Hierarchy for a Monorepo

This is the reference solution showing properly structured CLAUDE.md
files at multiple levels of a monorepo.
"""


def root_claude_md() -> str:
    """Root-level CLAUDE.md for the monorepo."""
    return '''# CLAUDE.md - E-commerce Platform

A microservices-based e-commerce platform handling users, products, and orders.

## Overview

This monorepo contains:
- **3 services**: user-service, product-service, order-service
- **2 shared libraries**: common-utils, api-client
- **Infrastructure as code**: Kubernetes manifests, Terraform

Services communicate via gRPC. Each service has its own PostgreSQL database.

## Repository Navigation

```
ecommerce-platform/
├── services/           # Microservices (Python)
│   ├── user-service/   # Authentication, user profiles
│   ├── product-service/# Product catalog, inventory
│   └── order-service/  # Order processing, fulfillment
├── shared/             # Shared libraries
│   ├── common-utils/   # Logging, config, exceptions (Python)
│   └── api-client/     # Generated gRPC clients (TypeScript)
└── infrastructure/     # DevOps & deployment
    ├── k8s/            # Kubernetes manifests
    └── terraform/      # Cloud infrastructure
```

**Finding code:** Each directory has its own CLAUDE.md with specific guidance.

## Quick Start

```bash
# Start all infrastructure (databases, message queue)
make infra-up

# Start all services in development mode
make dev-all

# Or start a specific service
make dev-users
make dev-products
make dev-orders

# Run all tests across the monorepo
make test-all

# Stop everything
make infra-down
```

## Shared Infrastructure

All services depend on shared infrastructure started via Docker Compose:

```bash
make infra-up    # Starts: PostgreSQL (3 instances), Redis, Kafka
make infra-down  # Stops all
make infra-logs  # View logs
```

**Ports:**
- PostgreSQL (users): 5432
- PostgreSQL (products): 5433
- PostgreSQL (orders): 5434
- Redis: 6379
- Kafka: 9092

## Cross-Service Conventions

### gRPC Communication
Services communicate via gRPC, not REST. Proto files in `shared/proto/`.

```bash
# Regenerate gRPC clients after proto changes
make proto-gen
```

### Shared Configuration
Environment variables follow pattern: `{SERVICE}_{SETTING}`
- `USERS_DB_URL` - User service database
- `PRODUCTS_DB_URL` - Product service database

### Logging
All services use structured logging via `common-utils`:
```python
from common_utils.logging import get_logger
logger = get_logger(__name__)
logger.info("event", user_id=user_id, action="login")
```

### Error Handling
Use shared exceptions from `common-utils`:
```python
from common_utils.exceptions import NotFoundError, ValidationError
raise NotFoundError("User", user_id=user_id)
```

## CI/CD Overview

GitHub Actions runs on all PRs:
1. Lint all changed services
2. Test all changed services
3. Build Docker images
4. Deploy to staging (on merge to main)

**Workflow files:** `.github/workflows/`

## Getting Help

- Service-specific: Check `services/{name}/CLAUDE.md`
- Infrastructure: Check `infrastructure/CLAUDE.md`
- Architecture decisions: See `docs/adr/`
'''


def services_claude_md() -> str:
    """Services-level CLAUDE.md with shared patterns."""
    return '''# CLAUDE.md - Services

Shared conventions for all microservices in `/services/`.

**Parent context:** See root CLAUDE.md for monorepo overview.

## Service Architecture

All services follow the same structure:
```
{service-name}/
├── src/
│   ├── api/          # gRPC service implementations
│   ├── domain/       # Business logic, models
│   ├── repository/   # Database access
│   └── main.py       # Entry point
├── tests/
├── pyproject.toml
└── CLAUDE.md         # Service-specific guidance
```

## Common Commands

All services support these Makefile targets:

```bash
# From service directory
make setup        # Install dependencies
make dev          # Run in development mode
make test         # Run tests
make lint         # Check code quality
make proto        # Regenerate gRPC stubs
```

## gRPC Patterns

### Service Definition
```python
from generated import service_pb2_grpc

class UserServicer(service_pb2_grpc.UserServiceServicer):
    async def GetUser(self, request, context):
        user = await self.repository.get(request.user_id)
        if not user:
            context.abort(grpc.StatusCode.NOT_FOUND, "User not found")
        return user.to_proto()
```

### Client Calls
```python
from common_utils.grpc import create_channel

async with create_channel("product-service:50051") as channel:
    stub = ProductServiceStub(channel)
    product = await stub.GetProduct(GetProductRequest(id=product_id))
```

### Error Handling in gRPC
```python
# Server-side: use context.abort()
context.abort(grpc.StatusCode.NOT_FOUND, f"User {user_id} not found")

# Client-side: catch grpc.RpcError
try:
    response = await stub.GetUser(request)
except grpc.RpcError as e:
    if e.code() == grpc.StatusCode.NOT_FOUND:
        # Handle not found
```

## Database Patterns

### Repository Pattern
All database access goes through repository classes:
```python
class UserRepository:
    def __init__(self, session: AsyncSession):
        self.session = session

    async def get_by_id(self, user_id: str) -> User | None:
        result = await self.session.execute(
            select(User).where(User.id == user_id)
        )
        return result.scalar_one_or_none()
```

### Migrations
Each service manages its own migrations:
```bash
# Create migration
alembic revision --autogenerate -m "description"

# Apply migrations
alembic upgrade head
```

## Testing Standards

### Unit Tests
- Mock external dependencies (database, other services)
- Fast execution, no infrastructure needed
- Location: `tests/unit/`

### Integration Tests
- Use real database (test instance)
- Mock other services with fake gRPC servers
- Location: `tests/integration/`

```python
@pytest.fixture
async def db_session():
    # Creates test database, runs migrations, yields session
    ...

async def test_create_user(db_session):
    repo = UserRepository(db_session)
    user = await repo.create(email="test@example.com")
    assert user.id is not None
```

## Common Mistakes

1. **Calling other services synchronously**
   - Always use `async/await` for gRPC calls
   - Don't block the event loop

2. **Sharing database connections**
   - Each service has its own database
   - Never access another service's database directly

3. **Hardcoding service addresses**
   - Use environment variables: `PRODUCT_SERVICE_URL`
   - In K8s, use service DNS names

## Health Checks

All services must implement:
```python
async def HealthCheck(self, request, context):
    # Check database connection
    # Check critical dependencies
    return HealthCheckResponse(status=ServingStatus.SERVING)
```
'''


def user_service_claude_md() -> str:
    """User-service-specific CLAUDE.md."""
    return '''# CLAUDE.md - User Service

Authentication and user profile management service.

**Parent context:** See `services/CLAUDE.md` for shared patterns.

## Overview

Handles:
- User registration and email verification
- Password authentication and password reset
- JWT token issuance and validation
- User profile CRUD operations

**Port:** 50051 (gRPC)

## Key Commands

```bash
make dev          # Start on port 50051
make test         # Run all tests
make test-auth    # Run only auth-related tests
make gen-keys     # Generate new JWT signing keys
```

## User Service Specifics

### JWT Token Handling
```python
from src.auth.jwt import create_access_token, verify_token

# Creating tokens
token = create_access_token(user_id=user.id, roles=user.roles)

# Verifying (in middleware or interceptor)
payload = verify_token(token)  # Raises InvalidTokenError
```

### Password Hashing
Always use the auth module, never hash directly:
```python
from src.auth.password import hash_password, verify_password

# Registration
user.password_hash = hash_password(plain_password)

# Login
if not verify_password(plain_password, user.password_hash):
    raise InvalidCredentialsError()
```

### Email Verification Flow
1. User registers -> `email_verification_token` created
2. Email sent with token link
3. User clicks link -> `/verify-email` endpoint
4. Token validated -> `email_verified = True`

```python
# Don't implement custom verification
from src.services.email_verification import send_verification_email
await send_verification_email(user)
```

## Data Models

### User Model
```python
class User(Base):
    id: UUID
    email: str              # Unique, indexed
    password_hash: str      # Bcrypt hash
    email_verified: bool    # Default False
    created_at: datetime
    updated_at: datetime

    # Profile fields
    display_name: str | None
    avatar_url: str | None
```

### User Proto
```protobuf
message User {
    string id = 1;
    string email = 2;
    string display_name = 3;
    bool email_verified = 4;
}
```

## API Endpoints (gRPC)

| Method | Request | Response | Auth Required |
|--------|---------|----------|---------------|
| Register | RegisterRequest | User | No |
| Login | LoginRequest | TokenResponse | No |
| GetUser | GetUserRequest | User | Yes |
| UpdateProfile | UpdateProfileRequest | User | Yes |
| ChangePassword | ChangePasswordRequest | Empty | Yes |

## Common Mistakes (User Service Specific)

1. **Returning password hash in responses**
   - Never include `password_hash` in User proto/response
   - The proto definition intentionally omits it

2. **Not rate limiting auth endpoints**
   - `/login` and `/register` have rate limits
   - Check `src/middleware/rate_limit.py`

3. **Storing plain-text passwords (even temporarily)**
   - Hash immediately on receipt
   - Never log passwords

4. **Not invalidating tokens on password change**
   - Password change must increment `token_version`
   - Old tokens become invalid

## Testing Auth Flows

```python
# Test fixtures provide authenticated context
@pytest.fixture
def auth_context():
    """Creates a gRPC context with valid auth token."""
    user = UserFactory()
    token = create_access_token(user.id)
    metadata = [("authorization", f"Bearer {token}")]
    return create_context_with_metadata(metadata)

async def test_get_user_requires_auth(user_service, auth_context):
    response = await user_service.GetUser(
        GetUserRequest(user_id="..."),
        auth_context
    )
    assert response.email == "..."
```

## Environment Variables

User service specific:
```bash
USERS_DB_URL=postgresql://...   # Database connection
JWT_SECRET_KEY=...              # Token signing key
JWT_EXPIRY_HOURS=24             # Token lifetime
EMAIL_VERIFICATION_URL=...      # Base URL for verify links
SMTP_HOST=...                   # Email sending
```

## Troubleshooting

### "Token validation failed"
- Check `JWT_SECRET_KEY` matches across environments
- Verify token hasn't expired
- Check `token_version` if password was changed

### "Email not sending"
- Verify SMTP credentials in environment
- Check email service logs: `docker logs user-service`
- In dev, emails print to console instead of sending
'''


if __name__ == "__main__":
    from claude_md_standards.validator import validate_claude_md
    from rich.console import Console
    from rich.table import Table

    console = Console()

    files = [
        ("Root", root_claude_md()),
        ("Services", services_claude_md()),
        ("User Service", user_service_claude_md()),
    ]

    console.print("[bold]Solution Validation:[/bold]\n")

    table = Table(show_header=True, header_style="bold")
    table.add_column("Level")
    table.add_column("Score", justify="right")
    table.add_column("Valid")
    table.add_column("Lines")
    table.add_column("Words")

    total_score = 0

    for name, content in files:
        result = validate_claude_md(content)
        total_score += result.score
        lines = len(content.splitlines())
        words = len(content.split())

        table.add_row(
            name,
            f"[green]{result.score}[/green]",
            "[green]Yes[/green]" if result.is_valid else "[red]No[/red]",
            str(lines),
            str(words),
        )

    console.print(table)
    console.print(f"\n[bold]Total Score:[/bold] [green]{total_score}/300[/green]")
    console.print(f"[bold]Average Score:[/bold] [green]{total_score // 3}/100[/green]")
