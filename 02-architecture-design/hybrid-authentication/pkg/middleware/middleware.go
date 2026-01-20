// Package middleware provides authentication middleware implementations.
package middleware

import (
	"encoding/json"
	"log"
	"net/http"
	"strings"

	"github.com/labs-skills/hybrid-authentication/pkg/auth"
)

// JWTAuthenticator authenticates using JWT tokens
type JWTAuthenticator struct {
	jwtService *auth.JWTService
	headerName string
}

// NewJWTAuthenticator creates a new JWT authenticator
func NewJWTAuthenticator(jwtService *auth.JWTService) *JWTAuthenticator {
	return &JWTAuthenticator{
		jwtService: jwtService,
		headerName: "Authorization",
	}
}

// Authenticate extracts and validates JWT from request
func (a *JWTAuthenticator) Authenticate(r *http.Request) (*auth.Principal, error) {
	// Extract token from Authorization header
	header := r.Header.Get(a.headerName)
	if header == "" {
		return nil, auth.ErrNoCredentials
	}

	// Remove "Bearer " prefix
	if !strings.HasPrefix(header, "Bearer ") {
		return nil, auth.ErrInvalidCredentials
	}
	tokenString := strings.TrimPrefix(header, "Bearer ")

	// Validate token
	claims, err := a.jwtService.ValidateToken(tokenString)
	if err != nil {
		return nil, err
	}

	return &auth.Principal{
		ID:          claims.Subject,
		Type:        auth.PrincipalTypeUser,
		Roles:       claims.Roles,
		Permissions: claims.Permissions,
		Metadata:    claims.Metadata,
	}, nil
}

// APIKeyAuthenticator authenticates using API keys
type APIKeyAuthenticator struct {
	store      auth.APIKeyStore
	headerName string
	queryParam string
}

// NewAPIKeyAuthenticator creates a new API key authenticator
func NewAPIKeyAuthenticator(store auth.APIKeyStore) *APIKeyAuthenticator {
	return &APIKeyAuthenticator{
		store:      store,
		headerName: "X-API-Key",
		queryParam: "api_key",
	}
}

// WithHeaderName sets a custom header name
func (a *APIKeyAuthenticator) WithHeaderName(name string) *APIKeyAuthenticator {
	a.headerName = name
	return a
}

// WithQueryParam sets a custom query parameter name
func (a *APIKeyAuthenticator) WithQueryParam(name string) *APIKeyAuthenticator {
	a.queryParam = name
	return a
}

// Authenticate extracts and validates API key from request
func (a *APIKeyAuthenticator) Authenticate(r *http.Request) (*auth.Principal, error) {
	// Try header first
	key := r.Header.Get(a.headerName)
	if key == "" {
		// Try query parameter
		key = r.URL.Query().Get(a.queryParam)
	}

	if key == "" {
		return nil, auth.ErrNoCredentials
	}

	// Look up API key
	apiKey, err := a.store.FindByKey(key)
	if err != nil {
		return nil, auth.ErrInvalidAPIKey
	}

	// Check expiration
	if !apiKey.ExpiresAt.IsZero() && apiKey.ExpiresAt.Before(r.Context().Value("now").(interface{ Now() interface{} }) != nil) {
		return nil, auth.ErrExpiredAPIKey
	}

	return &auth.Principal{
		ID:          apiKey.ID,
		Type:        auth.PrincipalTypeService,
		Roles:       []string{"service"},
		Permissions: apiKey.Permissions,
		Metadata: map[string]string{
			"service_name": apiKey.ServiceName,
		},
	}, nil
}

// ChainAuthenticator tries multiple authenticators in order
type ChainAuthenticator struct {
	authenticators []auth.Authenticator
}

// NewChainAuthenticator creates a new chain authenticator
func NewChainAuthenticator(authenticators ...auth.Authenticator) *ChainAuthenticator {
	return &ChainAuthenticator{
		authenticators: authenticators,
	}
}

// Authenticate tries each authenticator in order
func (c *ChainAuthenticator) Authenticate(r *http.Request) (*auth.Principal, error) {
	var lastErr error

	for _, authenticator := range c.authenticators {
		principal, err := authenticator.Authenticate(r)
		if err == nil {
			return principal, nil
		}
		if err != auth.ErrNoCredentials {
			lastErr = err
		}
	}

	if lastErr != nil {
		return nil, lastErr
	}
	return nil, auth.ErrNoCredentials
}

// AuthMiddleware creates authentication middleware
func AuthMiddleware(authenticator auth.Authenticator) func(http.Handler) http.Handler {
	return func(next http.Handler) http.Handler {
		return http.HandlerFunc(func(w http.ResponseWriter, r *http.Request) {
			principal, err := authenticator.Authenticate(r)
			if err != nil {
				log.Printf("Authentication failed: %v", err)
				writeAuthError(w, err)
				return
			}

			ctx := auth.WithPrincipal(r.Context(), principal)
			next.ServeHTTP(w, r.WithContext(ctx))
		})
	}
}

// OptionalAuthMiddleware adds principal if present but doesn't require it
func OptionalAuthMiddleware(authenticator auth.Authenticator) func(http.Handler) http.Handler {
	return func(next http.Handler) http.Handler {
		return http.HandlerFunc(func(w http.ResponseWriter, r *http.Request) {
			principal, err := authenticator.Authenticate(r)
			if err == nil {
				ctx := auth.WithPrincipal(r.Context(), principal)
				r = r.WithContext(ctx)
			}
			next.ServeHTTP(w, r)
		})
	}
}

// RequireRole middleware checks for required role
func RequireRole(role string) func(http.Handler) http.Handler {
	return func(next http.Handler) http.Handler {
		return http.HandlerFunc(func(w http.ResponseWriter, r *http.Request) {
			principal, ok := auth.GetPrincipal(r.Context())
			if !ok {
				writeError(w, http.StatusUnauthorized, "Unauthorized", "UNAUTHORIZED")
				return
			}

			if !principal.HasRole(role) {
				writeError(w, http.StatusForbidden, "Forbidden", "FORBIDDEN")
				return
			}

			next.ServeHTTP(w, r)
		})
	}
}

// RequireAnyRole middleware checks for any of the required roles
func RequireAnyRole(roles ...string) func(http.Handler) http.Handler {
	return func(next http.Handler) http.Handler {
		return http.HandlerFunc(func(w http.ResponseWriter, r *http.Request) {
			principal, ok := auth.GetPrincipal(r.Context())
			if !ok {
				writeError(w, http.StatusUnauthorized, "Unauthorized", "UNAUTHORIZED")
				return
			}

			if !principal.HasAnyRole(roles...) {
				writeError(w, http.StatusForbidden, "Forbidden", "FORBIDDEN")
				return
			}

			next.ServeHTTP(w, r)
		})
	}
}

// RequirePermission middleware checks for required permission
func RequirePermission(permission string) func(http.Handler) http.Handler {
	return func(next http.Handler) http.Handler {
		return http.HandlerFunc(func(w http.ResponseWriter, r *http.Request) {
			principal, ok := auth.GetPrincipal(r.Context())
			if !ok {
				writeError(w, http.StatusUnauthorized, "Unauthorized", "UNAUTHORIZED")
				return
			}

			if !principal.HasPermission(permission) {
				writeError(w, http.StatusForbidden, "Insufficient permissions", "FORBIDDEN")
				return
			}

			next.ServeHTTP(w, r)
		})
	}
}

// Helper functions

func writeAuthError(w http.ResponseWriter, err error) {
	status := http.StatusUnauthorized
	message := "Authentication failed"
	code := "AUTH_ERROR"

	switch err {
	case auth.ErrTokenExpired:
		message = "Token has expired"
		code = "TOKEN_EXPIRED"
	case auth.ErrInvalidToken:
		message = "Invalid token"
		code = "INVALID_TOKEN"
	case auth.ErrInvalidAPIKey:
		message = "Invalid API key"
		code = "INVALID_API_KEY"
	case auth.ErrExpiredAPIKey:
		message = "API key has expired"
		code = "API_KEY_EXPIRED"
	case auth.ErrNoCredentials:
		message = "No credentials provided"
		code = "NO_CREDENTIALS"
	}

	writeError(w, status, message, code)
}

func writeError(w http.ResponseWriter, status int, message, code string) {
	w.Header().Set("Content-Type", "application/json")
	w.WriteHeader(status)
	json.NewEncoder(w).Encode(map[string]string{
		"error": message,
		"code":  code,
	})
}
