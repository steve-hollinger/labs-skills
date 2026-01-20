// Example 3: Hybrid Auth System
//
// This example demonstrates combining JWT and API key authentication:
// - Chain authenticator trying multiple strategies
// - Unified principal abstraction
// - Role-based access control
// - Protected resources with mixed auth
package main

import (
	"context"
	"crypto/rand"
	"encoding/base64"
	"encoding/json"
	"fmt"
	"log"
	"net/http"
	"strings"
	"sync"
	"time"

	"github.com/golang-jwt/jwt/v5"
	"golang.org/x/crypto/bcrypt"
)

// Configuration
var (
	jwtSecret   = []byte("jwt-secret-key-change-in-production")
	jwtIssuer   = "hybrid-auth-example"
	tokenExpiry = 15 * time.Minute
)

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

// HasRole checks if principal has a role
func (p *Principal) HasRole(role string) bool {
	for _, r := range p.Roles {
		if r == role {
			return true
		}
	}
	return false
}

// HasPermission checks if principal has a permission
func (p *Principal) HasPermission(permission string) bool {
	for _, perm := range p.Permissions {
		if perm == permission || perm == "*" {
			return true
		}
	}
	return false
}

// Context key
type contextKey string

const principalKey contextKey = "principal"

// WithPrincipal adds principal to context
func WithPrincipal(ctx context.Context, p *Principal) context.Context {
	return context.WithValue(ctx, principalKey, p)
}

// GetPrincipal retrieves principal from context
func GetPrincipal(ctx context.Context) (*Principal, bool) {
	p, ok := ctx.Value(principalKey).(*Principal)
	return p, ok
}

// --- JWT Authentication ---

type JWTClaims struct {
	jwt.RegisteredClaims
	Roles       []string `json:"roles"`
	Permissions []string `json:"permissions,omitempty"`
}

func generateJWT(userID string, roles, permissions []string) (string, error) {
	claims := JWTClaims{
		RegisteredClaims: jwt.RegisteredClaims{
			Subject:   userID,
			Issuer:    jwtIssuer,
			IssuedAt:  jwt.NewNumericDate(time.Now()),
			ExpiresAt: jwt.NewNumericDate(time.Now().Add(tokenExpiry)),
		},
		Roles:       roles,
		Permissions: permissions,
	}
	token := jwt.NewWithClaims(jwt.SigningMethodHS256, claims)
	return token.SignedString(jwtSecret)
}

func validateJWT(tokenString string) (*JWTClaims, error) {
	token, err := jwt.ParseWithClaims(tokenString, &JWTClaims{}, func(t *jwt.Token) (interface{}, error) {
		if _, ok := t.Method.(*jwt.SigningMethodHMAC); !ok {
			return nil, fmt.Errorf("unexpected signing method")
		}
		return jwtSecret, nil
	})
	if err != nil {
		return nil, err
	}
	if claims, ok := token.Claims.(*JWTClaims); ok && token.Valid {
		return claims, nil
	}
	return nil, fmt.Errorf("invalid token")
}

// --- API Key Store ---

type APIKey struct {
	ID          string
	KeyHash     []byte
	ServiceName string
	Permissions []string
}

type APIKeyStore struct {
	mu   sync.RWMutex
	keys map[string]*APIKey
}

func NewAPIKeyStore() *APIKeyStore {
	return &APIKeyStore{keys: make(map[string]*APIKey)}
}

func (s *APIKeyStore) CreateKey(serviceName string, permissions []string) (string, error) {
	bytes := make([]byte, 32)
	rand.Read(bytes)
	rawKey := base64.URLEncoding.EncodeToString(bytes)
	hash, _ := bcrypt.GenerateFromPassword([]byte(rawKey), bcrypt.DefaultCost)

	key := &APIKey{
		ID:          fmt.Sprintf("svc_%d", time.Now().UnixNano()),
		KeyHash:     hash,
		ServiceName: serviceName,
		Permissions: permissions,
	}

	s.mu.Lock()
	s.keys[key.ID] = key
	s.mu.Unlock()

	return rawKey, nil
}

func (s *APIKeyStore) Validate(rawKey string) (*APIKey, error) {
	s.mu.RLock()
	defer s.mu.RUnlock()

	for _, key := range s.keys {
		if bcrypt.CompareHashAndPassword(key.KeyHash, []byte(rawKey)) == nil {
			return key, nil
		}
	}
	return nil, fmt.Errorf("invalid API key")
}

// Global store
var apiKeyStore = NewAPIKeyStore()

// --- Authenticators ---

type Authenticator interface {
	Authenticate(r *http.Request) (*Principal, error)
}

type JWTAuthenticator struct{}

func (a *JWTAuthenticator) Authenticate(r *http.Request) (*Principal, error) {
	authHeader := r.Header.Get("Authorization")
	if !strings.HasPrefix(authHeader, "Bearer ") {
		return nil, fmt.Errorf("no bearer token")
	}

	claims, err := validateJWT(authHeader[7:])
	if err != nil {
		return nil, err
	}

	return &Principal{
		ID:          claims.Subject,
		Type:        PrincipalTypeUser,
		Roles:       claims.Roles,
		Permissions: claims.Permissions,
	}, nil
}

type APIKeyAuthenticator struct {
	store *APIKeyStore
}

func (a *APIKeyAuthenticator) Authenticate(r *http.Request) (*Principal, error) {
	key := r.Header.Get("X-API-Key")
	if key == "" {
		return nil, fmt.Errorf("no API key")
	}

	apiKey, err := a.store.Validate(key)
	if err != nil {
		return nil, err
	}

	return &Principal{
		ID:          apiKey.ID,
		Type:        PrincipalTypeService,
		Roles:       []string{"service"},
		Permissions: apiKey.Permissions,
		Metadata:    map[string]string{"service_name": apiKey.ServiceName},
	}, nil
}

// ChainAuthenticator tries multiple authenticators
type ChainAuthenticator struct {
	authenticators []Authenticator
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
	return nil, lastErr
}

// --- Middleware ---

func AuthMiddleware(auth Authenticator) func(http.Handler) http.Handler {
	return func(next http.Handler) http.Handler {
		return http.HandlerFunc(func(w http.ResponseWriter, r *http.Request) {
			principal, err := auth.Authenticate(r)
			if err != nil {
				log.Printf("Auth failed: %v", err)
				writeError(w, http.StatusUnauthorized, "Unauthorized")
				return
			}
			ctx := WithPrincipal(r.Context(), principal)
			next.ServeHTTP(w, r.WithContext(ctx))
		})
	}
}

func RequireRole(role string) func(http.Handler) http.Handler {
	return func(next http.Handler) http.Handler {
		return http.HandlerFunc(func(w http.ResponseWriter, r *http.Request) {
			principal, ok := GetPrincipal(r.Context())
			if !ok || !principal.HasRole(role) {
				writeError(w, http.StatusForbidden, "Forbidden: requires "+role+" role")
				return
			}
			next.ServeHTTP(w, r)
		})
	}
}

func RequirePermission(permission string) func(http.Handler) http.Handler {
	return func(next http.Handler) http.Handler {
		return http.HandlerFunc(func(w http.ResponseWriter, r *http.Request) {
			principal, ok := GetPrincipal(r.Context())
			if !ok || !principal.HasPermission(permission) {
				writeError(w, http.StatusForbidden, "Forbidden: requires "+permission+" permission")
				return
			}
			next.ServeHTTP(w, r)
		})
	}
}

// --- Handlers ---

var users = map[string]struct {
	Password    string
	Roles       []string
	Permissions []string
}{
	"admin": {"admin123", []string{"admin", "user"}, []string{"*"}},
	"user":  {"user123", []string{"user"}, []string{"articles:read"}},
}

func loginHandler(w http.ResponseWriter, r *http.Request) {
	if r.Method != http.MethodPost {
		writeError(w, http.StatusMethodNotAllowed, "Method not allowed")
		return
	}

	var req struct {
		Username string `json:"username"`
		Password string `json:"password"`
	}
	json.NewDecoder(r.Body).Decode(&req)

	userData, ok := users[req.Username]
	if !ok || userData.Password != req.Password {
		writeError(w, http.StatusUnauthorized, "Invalid credentials")
		return
	}

	token, _ := generateJWT(req.Username, userData.Roles, userData.Permissions)

	writeJSON(w, map[string]interface{}{
		"token":      token,
		"expires_in": int(tokenExpiry.Seconds()),
	})
}

func createAPIKeyHandler(w http.ResponseWriter, r *http.Request) {
	if r.Method != http.MethodPost {
		writeError(w, http.StatusMethodNotAllowed, "Method not allowed")
		return
	}

	var req struct {
		ServiceName string   `json:"service_name"`
		Permissions []string `json:"permissions"`
	}
	json.NewDecoder(r.Body).Decode(&req)

	key, _ := apiKeyStore.CreateKey(req.ServiceName, req.Permissions)

	writeJSON(w, map[string]interface{}{
		"api_key":     key,
		"permissions": req.Permissions,
		"message":     "Store securely!",
	})
}

func whoamiHandler(w http.ResponseWriter, r *http.Request) {
	principal, _ := GetPrincipal(r.Context())

	writeJSON(w, map[string]interface{}{
		"id":          principal.ID,
		"type":        principal.Type,
		"roles":       principal.Roles,
		"permissions": principal.Permissions,
		"metadata":    principal.Metadata,
	})
}

func articlesHandler(w http.ResponseWriter, r *http.Request) {
	principal, _ := GetPrincipal(r.Context())

	writeJSON(w, map[string]interface{}{
		"articles":   []string{"Article 1", "Article 2", "Article 3"},
		"accessed_by": principal.ID,
		"auth_type":   principal.Type,
	})
}

func adminHandler(w http.ResponseWriter, r *http.Request) {
	principal, _ := GetPrincipal(r.Context())

	writeJSON(w, map[string]interface{}{
		"message":     "Welcome to admin area!",
		"accessed_by": principal.ID,
	})
}

func writeJSON(w http.ResponseWriter, data interface{}) {
	w.Header().Set("Content-Type", "application/json")
	json.NewEncoder(w).Encode(data)
}

func writeError(w http.ResponseWriter, status int, message string) {
	w.Header().Set("Content-Type", "application/json")
	w.WriteHeader(status)
	json.NewEncoder(w).Encode(map[string]string{"error": message})
}

func main() {
	// Create chain authenticator (JWT first, then API key)
	chainAuth := &ChainAuthenticator{
		authenticators: []Authenticator{
			&JWTAuthenticator{},
			&APIKeyAuthenticator{store: apiKeyStore},
		},
	}

	mux := http.NewServeMux()

	// Auth endpoints
	mux.HandleFunc("/login", loginHandler)
	mux.HandleFunc("/api-keys/create", createAPIKeyHandler)

	// Protected endpoints - accept both JWT and API key
	mux.Handle("/whoami", AuthMiddleware(chainAuth)(http.HandlerFunc(whoamiHandler)))
	mux.Handle("/articles", AuthMiddleware(chainAuth)(RequirePermission("articles:read")(http.HandlerFunc(articlesHandler))))
	mux.Handle("/admin", AuthMiddleware(chainAuth)(RequireRole("admin")(http.HandlerFunc(adminHandler))))

	fmt.Println("Example 3: Hybrid Auth System")
	fmt.Println("=============================")
	fmt.Println()
	fmt.Println("Starting server on http://localhost:8080")
	fmt.Println()
	fmt.Println("This server accepts both JWT tokens and API keys!")
	fmt.Println()
	fmt.Println("Test users: admin:admin123, user:user123")
	fmt.Println()
	fmt.Println("Test commands:")
	fmt.Println()
	fmt.Println("  # Login as user (JWT)")
	fmt.Println(`  JWT=$(curl -s -X POST http://localhost:8080/login -d '{"username":"user","password":"user123"}' | jq -r .token)`)
	fmt.Println()
	fmt.Println("  # Create API key for a service")
	fmt.Println(`  API_KEY=$(curl -s -X POST http://localhost:8080/api-keys/create -d '{"service_name":"reader-svc","permissions":["articles:read"]}' | jq -r .api_key)`)
	fmt.Println()
	fmt.Println("  # Access with JWT")
	fmt.Println(`  curl -H "Authorization: Bearer $JWT" http://localhost:8080/whoami`)
	fmt.Println()
	fmt.Println("  # Access with API key")
	fmt.Println(`  curl -H "X-API-Key: $API_KEY" http://localhost:8080/whoami`)
	fmt.Println()
	fmt.Println("  # Both can read articles")
	fmt.Println(`  curl -H "Authorization: Bearer $JWT" http://localhost:8080/articles`)
	fmt.Println(`  curl -H "X-API-Key: $API_KEY" http://localhost:8080/articles`)
	fmt.Println()
	fmt.Println("  # Only admin users can access /admin")
	fmt.Println(`  ADMIN_JWT=$(curl -s -X POST http://localhost:8080/login -d '{"username":"admin","password":"admin123"}' | jq -r .token)`)
	fmt.Println(`  curl -H "Authorization: Bearer $ADMIN_JWT" http://localhost:8080/admin`)
	fmt.Println()

	log.Fatal(http.ListenAndServe(":8080", mux))
}
