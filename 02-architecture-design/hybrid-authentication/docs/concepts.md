# Core Concepts

## Overview

This document covers the fundamental concepts for implementing hybrid authentication systems that combine multiple authentication strategies.

## Concept 1: JWT (JSON Web Tokens)

### What It Is

JWT is a compact, URL-safe token format that contains a set of claims encoded as JSON. It consists of three parts: header, payload, and signature.

```
eyJhbGciOiJIUzI1NiJ9.eyJzdWIiOiIxMjM0NTYiLCJyb2xlcyI6WyJ1c2VyIl19.signature
│──────────────────────┘ │─────────────────────────────────────────────┘ │─────────┘
        Header                              Payload                       Signature
```

### Why It Matters

JWTs enable:
- **Stateless authentication**: Server doesn't need to store sessions
- **Distributed systems**: Any service can validate tokens independently
- **Rich claims**: Tokens carry user information, roles, permissions
- **Short-lived credentials**: Supports expiration for security

### How It Works

```go
// Token Claims
type Claims struct {
    jwt.RegisteredClaims
    Roles       []string `json:"roles"`
    Permissions []string `json:"permissions,omitempty"`
}

// Generate Token
func GenerateToken(userID string, roles []string, secret []byte, expiry time.Duration) (string, error) {
    claims := Claims{
        RegisteredClaims: jwt.RegisteredClaims{
            Subject:   userID,
            IssuedAt:  jwt.NewNumericDate(time.Now()),
            ExpiresAt: jwt.NewNumericDate(time.Now().Add(expiry)),
            Issuer:    "auth-service",
        },
        Roles: roles,
    }

    token := jwt.NewWithClaims(jwt.SigningMethodHS256, claims)
    return token.SignedString(secret)
}

// Validate Token
func ValidateToken(tokenString string, secret []byte) (*Claims, error) {
    token, err := jwt.ParseWithClaims(tokenString, &Claims{}, func(t *jwt.Token) (interface{}, error) {
        // Verify signing method
        if _, ok := t.Method.(*jwt.SigningMethodHMAC); !ok {
            return nil, fmt.Errorf("unexpected signing method: %v", t.Header["alg"])
        }
        return secret, nil
    })

    if err != nil {
        return nil, err
    }

    if claims, ok := token.Claims.(*Claims); ok && token.Valid {
        return claims, nil
    }

    return nil, ErrInvalidToken
}
```

## Concept 2: API Key Authentication

### What It Is

API keys are simple string credentials used to identify and authenticate applications or services. They're typically long, random strings.

### Why It Matters

API keys are useful for:
- **Service-to-service communication**: Simpler than JWT for backend services
- **Rate limiting**: Track usage per key
- **Access control**: Assign permissions per key
- **Long-lived credentials**: Don't expire frequently like JWTs

### How It Works

```go
// API Key structure
type APIKey struct {
    ID          string
    Key         string    // Only stored as hash
    KeyHash     []byte    // bcrypt or argon2 hash
    ServiceName string
    Permissions []string
    CreatedAt   time.Time
    ExpiresAt   time.Time
    LastUsedAt  time.Time
}

// Generate API Key
func GenerateAPIKey() (string, error) {
    bytes := make([]byte, 32)
    if _, err := rand.Read(bytes); err != nil {
        return "", err
    }
    return base64.URLEncoding.EncodeToString(bytes), nil
}

// Hash API Key for storage
func HashAPIKey(key string) ([]byte, error) {
    return bcrypt.GenerateFromPassword([]byte(key), bcrypt.DefaultCost)
}

// Validate API Key (timing-safe)
func ValidateAPIKey(provided string, storedHash []byte) bool {
    err := bcrypt.CompareHashAndPassword(storedHash, []byte(provided))
    return err == nil
}
```

## Concept 3: Principal (Authenticated Identity)

### What It Is

A Principal represents an authenticated entity - either a user or a service. It's the unified representation of "who is making this request."

### Why It Matters

A unified Principal abstraction:
- **Normalizes different auth methods**: JWT and API key both produce a Principal
- **Simplifies authorization**: Check permissions against Principal, not auth method
- **Enables context propagation**: Pass identity through request handlers

### How It Works

```go
// PrincipalType identifies the type of authenticated entity
type PrincipalType string

const (
    PrincipalTypeUser    PrincipalType = "user"
    PrincipalTypeService PrincipalType = "service"
)

// Principal represents an authenticated entity
type Principal struct {
    ID          string
    Type        PrincipalType
    Roles       []string
    Permissions []string
    Metadata    map[string]string
}

// HasRole checks if principal has a specific role
func (p *Principal) HasRole(role string) bool {
    for _, r := range p.Roles {
        if r == role {
            return true
        }
    }
    return false
}

// HasPermission checks if principal has a specific permission
func (p *Principal) HasPermission(permission string) bool {
    // Check direct permissions
    for _, perm := range p.Permissions {
        if perm == permission {
            return true
        }
    }
    return false
}

// HasAnyRole checks if principal has any of the specified roles
func (p *Principal) HasAnyRole(roles ...string) bool {
    for _, role := range roles {
        if p.HasRole(role) {
            return true
        }
    }
    return false
}
```

## Concept 4: Authentication Middleware

### What It Is

Middleware that intercepts requests, extracts credentials, validates them, and attaches the authenticated Principal to the request context.

### Why It Matters

Auth middleware:
- **Centralizes authentication logic**: Don't repeat in every handler
- **Composes with other middleware**: Logging, rate limiting, etc.
- **Provides clean context propagation**: Handlers receive authenticated context

### How It Works

```go
// Authenticator validates credentials and returns a Principal
type Authenticator interface {
    Authenticate(r *http.Request) (*Principal, error)
}

// AuthMiddleware creates authentication middleware
func AuthMiddleware(auth Authenticator) func(http.Handler) http.Handler {
    return func(next http.Handler) http.Handler {
        return http.HandlerFunc(func(w http.ResponseWriter, r *http.Request) {
            principal, err := auth.Authenticate(r)
            if err != nil {
                // Log the actual error
                log.Printf("Authentication failed: %v", err)
                // Return generic error to client
                http.Error(w, "Unauthorized", http.StatusUnauthorized)
                return
            }

            // Add principal to context
            ctx := WithPrincipal(r.Context(), principal)
            next.ServeHTTP(w, r.WithContext(ctx))
        })
    }
}

// RequireRole middleware checks for required role
func RequireRole(role string) func(http.Handler) http.Handler {
    return func(next http.Handler) http.Handler {
        return http.HandlerFunc(func(w http.ResponseWriter, r *http.Request) {
            principal, ok := GetPrincipal(r.Context())
            if !ok || !principal.HasRole(role) {
                http.Error(w, "Forbidden", http.StatusForbidden)
                return
            }
            next.ServeHTTP(w, r)
        })
    }
}
```

## Concept 5: Context Propagation

### What It Is

Passing authentication information through the request context so that any handler or downstream service can access the authenticated principal.

### Why It Matters

Context propagation enables:
- **Access to identity anywhere**: Handlers, services, repositories
- **Audit logging**: Record who performed actions
- **Authorization checks**: Verify permissions at any layer
- **Service-to-service forwarding**: Pass identity to downstream services

### How It Works

```go
type contextKey string

const (
    principalContextKey contextKey = "principal"
    requestIDContextKey contextKey = "requestID"
)

// WithPrincipal adds a principal to the context
func WithPrincipal(ctx context.Context, p *Principal) context.Context {
    return context.WithValue(ctx, principalContextKey, p)
}

// GetPrincipal retrieves the principal from context
func GetPrincipal(ctx context.Context) (*Principal, bool) {
    p, ok := ctx.Value(principalContextKey).(*Principal)
    return p, ok
}

// MustGetPrincipal retrieves principal or panics (use after auth middleware)
func MustGetPrincipal(ctx context.Context) *Principal {
    p, ok := GetPrincipal(ctx)
    if !ok {
        panic("no principal in context - auth middleware not applied")
    }
    return p
}

// Usage in handler
func handleCreateResource(w http.ResponseWriter, r *http.Request) {
    principal := MustGetPrincipal(r.Context())

    // Use principal for authorization
    if !principal.HasPermission("resource:create") {
        http.Error(w, "Forbidden", http.StatusForbidden)
        return
    }

    // Use principal for audit
    log.Printf("User %s creating resource", principal.ID)

    // Continue with handler logic...
}
```

## Summary

Key takeaways:

1. **JWT**: Stateless, self-contained tokens ideal for user authentication
2. **API Keys**: Simple credentials ideal for service-to-service communication
3. **Principal**: Unified identity abstraction across auth methods
4. **Middleware**: Centralized auth logic that composes with other concerns
5. **Context Propagation**: Clean way to pass identity through the request lifecycle

The hybrid approach lets you use the right authentication method for each use case while maintaining consistent authorization logic.
