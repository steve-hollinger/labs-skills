# CLAUDE.md - Hybrid Authentication

This skill teaches implementing multi-strategy authentication systems that combine JWT tokens with API keys.

## Key Concepts

- **JWT Authentication**: Stateless tokens with claims for user identity
- **API Key Authentication**: Simple keys for service-to-service communication
- **Principal**: Unified representation of authenticated identity
- **Auth Context**: Propagating authentication through request handling
- **RBAC**: Role-based access control for authorization
- **Middleware Chain**: Composable authentication layers

## Common Commands

```bash
make setup      # Download dependencies
make examples   # Run all examples
make example-1  # Run JWT authentication example
make example-2  # Run API key authentication example
make example-3  # Run hybrid auth system example
make test       # Run go test
make test-race  # Run tests with race detector
make lint       # Run golangci-lint
make clean      # Remove build artifacts
```

## Project Structure

```
hybrid-authentication/
├── cmd/examples/
│   ├── example1/main.go     # JWT authentication
│   ├── example2/main.go     # API key authentication
│   └── example3/main.go     # Hybrid auth system
├── pkg/
│   ├── auth/                # Core auth types and interfaces
│   └── middleware/          # Auth middleware implementations
├── exercises/
│   ├── exercise1/           # JWT refresh tokens
│   ├── exercise2/           # API key management
│   ├── exercise3/           # Complete RBAC system
│   └── solutions/
├── tests/
│   └── *_test.go
└── docs/
    ├── concepts.md
    └── patterns.md
```

## Code Patterns

### Pattern 1: Principal Interface
```go
type Principal interface {
    GetID() string
    GetType() PrincipalType
    HasPermission(permission string) bool
    GetRoles() []string
}

type PrincipalType string

const (
    PrincipalTypeUser    PrincipalType = "user"
    PrincipalTypeService PrincipalType = "service"
)
```

### Pattern 2: Authenticator Interface
```go
type Authenticator interface {
    Authenticate(r *http.Request) (Principal, error)
}

type ChainAuthenticator struct {
    authenticators []Authenticator
}

func (c *ChainAuthenticator) Authenticate(r *http.Request) (Principal, error) {
    for _, auth := range c.authenticators {
        principal, err := auth.Authenticate(r)
        if err == nil {
            return principal, nil
        }
    }
    return nil, ErrNoValidCredentials
}
```

### Pattern 3: Context Propagation
```go
type contextKey string

const principalKey contextKey = "principal"

func WithPrincipal(ctx context.Context, p Principal) context.Context {
    return context.WithValue(ctx, principalKey, p)
}

func GetPrincipal(ctx context.Context) (Principal, bool) {
    p, ok := ctx.Value(principalKey).(Principal)
    return p, ok
}
```

## Common Mistakes

1. **Not checking token expiration**
   - Why it happens: Relying only on signature validation
   - How to fix: Always validate exp claim before trusting token

2. **Using weak secrets**
   - Why it happens: Using short or predictable secrets
   - How to fix: Use cryptographically random secrets (32+ bytes)

3. **Exposing internal errors**
   - Why it happens: Passing validation errors to clients
   - How to fix: Log detailed errors internally, return generic messages

4. **Not timing-safe comparison for API keys**
   - Why it happens: Using == for string comparison
   - How to fix: Use crypto/subtle.ConstantTimeCompare

## When Users Ask About...

### "How do I get started?"
Point them to `make setup && make example-1` for basic JWT auth.

### "Should I use JWT or API keys?"
- JWT for user authentication (short-lived, contains claims)
- API keys for service-to-service (long-lived, simpler)
- Hybrid approach combines both benefits

### "How do I handle token refresh?"
See Exercise 1 - implement refresh tokens with rotation to prevent replay attacks.

### "How do I implement RBAC?"
See Example 3 - use roles in JWT claims and check permissions in middleware.

### "How do I store API keys securely?"
Hash API keys before storage (like passwords). Only store the hash, compare using timing-safe comparison.

## Testing Notes

- Test both valid and invalid tokens
- Test expired tokens separately
- Test malformed tokens (bad signature, wrong algorithm)
- Use table-driven tests for permission checks
- Mock time for expiration tests

## Dependencies

Key dependencies in go.mod:
- github.com/golang-jwt/jwt/v5: JWT parsing and generation
- github.com/stretchr/testify: Testing assertions
- golang.org/x/crypto: Secure hashing and comparison
