# Common Patterns

## Overview

This document covers common patterns and best practices for implementing hybrid authentication systems.

## Pattern 1: Chain Authenticator

### When to Use

Use a chain authenticator when your API needs to support multiple authentication methods (JWT, API key, etc.) and you want to try them in order.

### Implementation

```go
// ChainAuthenticator tries multiple authenticators in order
type ChainAuthenticator struct {
    authenticators []Authenticator
}

func NewChainAuthenticator(authenticators ...Authenticator) *ChainAuthenticator {
    return &ChainAuthenticator{
        authenticators: authenticators,
    }
}

func (c *ChainAuthenticator) Authenticate(r *http.Request) (*Principal, error) {
    var lastErr error

    for _, auth := range c.authenticators {
        principal, err := auth.Authenticate(r)
        if err == nil {
            return principal, nil
        }
        lastErr = err
    }

    if lastErr != nil {
        return nil, lastErr
    }
    return nil, ErrNoCredentials
}
```

### Example Usage

```go
// Create individual authenticators
jwtAuth := NewJWTAuthenticator(jwtSecret)
apiKeyAuth := NewAPIKeyAuthenticator(apiKeyStore)

// Chain them - JWT first, then API key
auth := NewChainAuthenticator(jwtAuth, apiKeyAuth)

// Use in middleware
handler := AuthMiddleware(auth)(myHandler)
```

### Pitfalls to Avoid

- Don't expose which authentication method failed
- Return generic "Unauthorized" to prevent enumeration
- Log detailed errors server-side for debugging

## Pattern 2: Token Refresh with Rotation

### When to Use

Use refresh token rotation for long-lived sessions where you want to minimize the impact of token theft.

### Implementation

```go
// TokenPair contains access and refresh tokens
type TokenPair struct {
    AccessToken  string
    RefreshToken string
    ExpiresIn    int64
}

// RefreshTokenStore manages refresh tokens
type RefreshTokenStore interface {
    Store(tokenID, userID string, expiresAt time.Time) error
    Validate(tokenID string) (userID string, err error)
    Revoke(tokenID string) error
    RevokeAllForUser(userID string) error
}

// TokenService manages token generation and refresh
type TokenService struct {
    accessSecret  []byte
    refreshSecret []byte
    store         RefreshTokenStore
    accessTTL     time.Duration
    refreshTTL    time.Duration
}

// GenerateTokenPair creates new access and refresh tokens
func (s *TokenService) GenerateTokenPair(userID string, roles []string) (*TokenPair, error) {
    // Generate access token (short-lived)
    accessToken, err := s.generateAccessToken(userID, roles)
    if err != nil {
        return nil, err
    }

    // Generate refresh token (longer-lived)
    refreshTokenID := uuid.New().String()
    refreshToken, err := s.generateRefreshToken(refreshTokenID, userID)
    if err != nil {
        return nil, err
    }

    // Store refresh token ID
    if err := s.store.Store(refreshTokenID, userID, time.Now().Add(s.refreshTTL)); err != nil {
        return nil, err
    }

    return &TokenPair{
        AccessToken:  accessToken,
        RefreshToken: refreshToken,
        ExpiresIn:    int64(s.accessTTL.Seconds()),
    }, nil
}

// RefreshTokens validates refresh token and issues new pair (rotation)
func (s *TokenService) RefreshTokens(refreshToken string) (*TokenPair, error) {
    // Parse and validate refresh token
    claims, err := s.validateRefreshToken(refreshToken)
    if err != nil {
        return nil, ErrInvalidRefreshToken
    }

    // Verify token is in store (not revoked)
    userID, err := s.store.Validate(claims.TokenID)
    if err != nil {
        return nil, ErrInvalidRefreshToken
    }

    // Revoke old refresh token (rotation)
    if err := s.store.Revoke(claims.TokenID); err != nil {
        log.Printf("Failed to revoke old refresh token: %v", err)
    }

    // Generate new token pair
    // Note: In production, fetch fresh roles from database
    return s.GenerateTokenPair(userID, claims.Roles)
}
```

## Pattern 3: Role-Based Access Control (RBAC)

### When to Use

Use RBAC when you need to control access based on user roles rather than individual permissions.

### Implementation

```go
// Role defines a set of permissions
type Role struct {
    Name        string
    Permissions []string
}

// RBAC manages role-based access control
type RBAC struct {
    roles map[string]*Role
}

func NewRBAC() *RBAC {
    return &RBAC{
        roles: make(map[string]*Role),
    }
}

func (r *RBAC) DefineRole(name string, permissions ...string) {
    r.roles[name] = &Role{
        Name:        name,
        Permissions: permissions,
    }
}

func (r *RBAC) GetPermissions(roles []string) []string {
    permSet := make(map[string]bool)
    for _, roleName := range roles {
        if role, ok := r.roles[roleName]; ok {
            for _, perm := range role.Permissions {
                permSet[perm] = true
            }
        }
    }

    permissions := make([]string, 0, len(permSet))
    for perm := range permSet {
        permissions = append(permissions, perm)
    }
    return permissions
}

func (r *RBAC) HasPermission(roles []string, permission string) bool {
    for _, roleName := range roles {
        if role, ok := r.roles[roleName]; ok {
            for _, perm := range role.Permissions {
                if perm == permission || perm == "*" {
                    return true
                }
                // Check wildcard patterns
                if strings.HasSuffix(perm, ":*") {
                    prefix := strings.TrimSuffix(perm, "*")
                    if strings.HasPrefix(permission, prefix) {
                        return true
                    }
                }
            }
        }
    }
    return false
}

// RequirePermission middleware
func RequirePermission(rbac *RBAC, permission string) func(http.Handler) http.Handler {
    return func(next http.Handler) http.Handler {
        return http.HandlerFunc(func(w http.ResponseWriter, r *http.Request) {
            principal, ok := GetPrincipal(r.Context())
            if !ok {
                http.Error(w, "Unauthorized", http.StatusUnauthorized)
                return
            }

            if !rbac.HasPermission(principal.Roles, permission) {
                http.Error(w, "Forbidden", http.StatusForbidden)
                return
            }

            next.ServeHTTP(w, r)
        })
    }
}
```

### Example Setup

```go
rbac := NewRBAC()

// Define roles
rbac.DefineRole("admin", "*")
rbac.DefineRole("editor", "articles:read", "articles:write", "articles:delete")
rbac.DefineRole("viewer", "articles:read")
rbac.DefineRole("api-service", "articles:read", "users:read")

// Use in routes
mux.Handle("/articles", RequirePermission(rbac, "articles:read")(listArticlesHandler))
mux.Handle("/articles/create", RequirePermission(rbac, "articles:write")(createArticleHandler))
```

## Pattern 4: API Key with Scopes

### When to Use

Use scoped API keys when different services need different levels of access.

### Implementation

```go
// ScopedAPIKey includes permission scopes
type ScopedAPIKey struct {
    ID          string
    KeyHash     []byte
    ServiceName string
    Scopes      []string
    RateLimit   int // requests per minute
    CreatedAt   time.Time
    ExpiresAt   time.Time
}

// APIKeyAuthenticator validates API keys and checks scopes
type APIKeyAuthenticator struct {
    store       APIKeyStore
    headerName  string
    queryParam  string
}

func (a *APIKeyAuthenticator) Authenticate(r *http.Request) (*Principal, error) {
    // Extract API key from header or query param
    key := r.Header.Get(a.headerName)
    if key == "" {
        key = r.URL.Query().Get(a.queryParam)
    }
    if key == "" {
        return nil, ErrNoAPIKey
    }

    // Look up and validate key
    apiKey, err := a.store.FindByKey(key)
    if err != nil {
        return nil, ErrInvalidAPIKey
    }

    // Check expiration
    if !apiKey.ExpiresAt.IsZero() && apiKey.ExpiresAt.Before(time.Now()) {
        return nil, ErrExpiredAPIKey
    }

    return &Principal{
        ID:          apiKey.ID,
        Type:        PrincipalTypeService,
        Roles:       []string{"service"},
        Permissions: apiKey.Scopes,
        Metadata: map[string]string{
            "service_name": apiKey.ServiceName,
        },
    }, nil
}

// RequireScope middleware for API key scope validation
func RequireScope(scope string) func(http.Handler) http.Handler {
    return func(next http.Handler) http.Handler {
        return http.HandlerFunc(func(w http.ResponseWriter, r *http.Request) {
            principal, ok := GetPrincipal(r.Context())
            if !ok || !principal.HasPermission(scope) {
                http.Error(w, "Forbidden: insufficient scope", http.StatusForbidden)
                return
            }
            next.ServeHTTP(w, r)
        })
    }
}
```

## Pattern 5: Secure Error Handling

### When to Use

Always use secure error handling for authentication to prevent information leakage.

### Implementation

```go
// AuthError wraps authentication errors with safe messages
type AuthError struct {
    internal error  // Detailed error for logging
    message  string // Safe message for client
    code     string // Error code for client
}

func (e *AuthError) Error() string {
    return e.internal.Error()
}

func (e *AuthError) SafeMessage() string {
    return e.message
}

// Common auth errors
var (
    ErrInvalidCredentials = &AuthError{
        internal: errors.New("invalid credentials"),
        message:  "Invalid credentials",
        code:     "INVALID_CREDENTIALS",
    }
    ErrTokenExpired = &AuthError{
        internal: errors.New("token expired"),
        message:  "Token has expired",
        code:     "TOKEN_EXPIRED",
    }
    ErrInsufficientPermissions = &AuthError{
        internal: errors.New("insufficient permissions"),
        message:  "Access denied",
        code:     "ACCESS_DENIED",
    }
)

// WriteAuthError writes a safe error response
func WriteAuthError(w http.ResponseWriter, err error, status int) {
    response := map[string]string{
        "error": "Authentication failed",
        "code":  "AUTH_ERROR",
    }

    if authErr, ok := err.(*AuthError); ok {
        response["error"] = authErr.SafeMessage()
        response["code"] = authErr.code
    }

    w.Header().Set("Content-Type", "application/json")
    w.WriteHeader(status)
    json.NewEncoder(w).Encode(response)
}
```

## Anti-Patterns

### Anti-Pattern 1: Timing Attacks on API Keys

```go
// Bad - vulnerable to timing attack
func validateKey(provided, stored string) bool {
    return provided == stored // Early return reveals length match
}
```

### Better Approach

```go
// Good - constant-time comparison
func validateKey(provided, storedHash []byte) bool {
    return subtle.ConstantTimeCompare(
        []byte(provided),
        storedHash,
    ) == 1
}

// Or use bcrypt which is inherently timing-safe
func validateKey(provided string, storedHash []byte) bool {
    err := bcrypt.CompareHashAndPassword(storedHash, []byte(provided))
    return err == nil
}
```

### Anti-Pattern 2: JWT Algorithm Confusion

```go
// Bad - accepts any algorithm
token, _ := jwt.Parse(tokenString, func(t *jwt.Token) (interface{}, error) {
    return secret, nil
})
```

### Better Approach

```go
// Good - explicitly check algorithm
token, err := jwt.Parse(tokenString, func(t *jwt.Token) (interface{}, error) {
    if _, ok := t.Method.(*jwt.SigningMethodHMAC); !ok {
        return nil, fmt.Errorf("unexpected signing method: %v", t.Header["alg"])
    }
    return secret, nil
})
```
