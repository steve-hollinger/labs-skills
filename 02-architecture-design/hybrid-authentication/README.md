# Hybrid Authentication

Learn to implement flexible multi-strategy authentication systems in Go. This skill covers combining JWT tokens with API keys, building authentication middleware, and propagating auth context through applications.

## Learning Objectives

After completing this skill, you will be able to:
- Implement JWT-based authentication with token generation and validation
- Create API key authentication for service-to-service communication
- Build flexible middleware that supports multiple auth strategies
- Propagate authentication context through request handling
- Design role-based access control (RBAC) systems
- Handle authentication errors securely

## Prerequisites

- Go 1.22+
- [Go HTTP Services](../../01-language-frameworks/go/http-services/) skill
- Understanding of JWT concepts (tokens, claims, signing)
- Basic cryptography concepts (hashing, HMAC)

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

### JWT Authentication

JSON Web Tokens (JWT) provide stateless authentication:

```go
// Generate a JWT token
func GenerateToken(userID string, roles []string, secret []byte) (string, error) {
    claims := jwt.MapClaims{
        "sub":   userID,
        "roles": roles,
        "iat":   time.Now().Unix(),
        "exp":   time.Now().Add(24 * time.Hour).Unix(),
    }

    token := jwt.NewWithClaims(jwt.SigningMethodHS256, claims)
    return token.SignedString(secret)
}
```

### API Key Authentication

API keys enable service-to-service auth:

```go
// Validate API key
func ValidateAPIKey(key string, store APIKeyStore) (*Principal, error) {
    apiKey, err := store.GetByKey(key)
    if err != nil {
        return nil, ErrInvalidAPIKey
    }

    if apiKey.ExpiresAt.Before(time.Now()) {
        return nil, ErrExpiredAPIKey
    }

    return &Principal{
        ID:          apiKey.ServiceID,
        Type:        PrincipalTypeService,
        Permissions: apiKey.Permissions,
    }, nil
}
```

### Auth Middleware

Middleware extracts and validates authentication:

```go
func AuthMiddleware(authenticator Authenticator) func(http.Handler) http.Handler {
    return func(next http.Handler) http.Handler {
        return http.HandlerFunc(func(w http.ResponseWriter, r *http.Request) {
            principal, err := authenticator.Authenticate(r)
            if err != nil {
                http.Error(w, "Unauthorized", http.StatusUnauthorized)
                return
            }

            ctx := WithPrincipal(r.Context(), principal)
            next.ServeHTTP(w, r.WithContext(ctx))
        })
    }
}
```

## Examples

### Example 1: JWT Authentication

Implementing JWT token generation, validation, and middleware.

```bash
make example-1
```

### Example 2: API Key Authentication

Building API key management and validation.

```bash
make example-2
```

### Example 3: Hybrid Auth System

Combining JWT and API keys with role-based access control.

```bash
make example-3
```

## Exercises

See the [exercises](./exercises/) directory for practice problems:

1. **Exercise 1**: Implement JWT refresh tokens with rotation
2. **Exercise 2**: Build an API key management system with rate limiting
3. **Exercise 3**: Create a complete auth system with RBAC and audit logging

Solutions are available in [exercises/solutions/](./exercises/solutions/).

## Common Mistakes

### Exposing Secrets in Errors

Never include sensitive information in error messages:

```go
// Bad - exposes internal details
if err != nil {
    http.Error(w, fmt.Sprintf("JWT validation failed: %v", err), 401)
}

// Good - generic error message
if err != nil {
    log.Printf("JWT validation failed: %v", err) // Log internally
    http.Error(w, "Invalid or expired token", 401)
}
```

### Not Validating Token Claims

Always validate all relevant claims:

```go
// Bad - only checks signature
token, err := jwt.Parse(tokenString, keyFunc)

// Good - validates claims too
token, err := jwt.ParseWithClaims(tokenString, &Claims{}, keyFunc)
if err != nil {
    return nil, err
}

claims := token.Claims.(*Claims)
if claims.ExpiresAt < time.Now().Unix() {
    return nil, ErrTokenExpired
}
```

### Storing Secrets in Code

Never hardcode secrets:

```go
// Bad - secret in code
var jwtSecret = []byte("my-super-secret-key")

// Good - from environment
var jwtSecret = []byte(os.Getenv("JWT_SECRET"))
```

## Further Reading

- [JWT.io](https://jwt.io/) - JWT debugger and library list
- [OWASP Authentication Cheat Sheet](https://cheatsheetseries.owasp.org/cheatsheets/Authentication_Cheat_Sheet.html)
- Related skills in this repository:
  - [Go HTTP Services](../../01-language-frameworks/go/http-services/)
  - [Secrets Manager](../../07-security/secrets-manager/)
