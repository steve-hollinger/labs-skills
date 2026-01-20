// Package auth provides core authentication types and interfaces.
package auth

import (
	"context"
	"crypto/rand"
	"encoding/base64"
	"errors"
	"net/http"
	"time"

	"github.com/golang-jwt/jwt/v5"
	"golang.org/x/crypto/bcrypt"
)

// Common errors
var (
	ErrNoCredentials      = errors.New("no credentials provided")
	ErrInvalidCredentials = errors.New("invalid credentials")
	ErrInvalidToken       = errors.New("invalid token")
	ErrTokenExpired       = errors.New("token expired")
	ErrInvalidAPIKey      = errors.New("invalid API key")
	ErrExpiredAPIKey      = errors.New("expired API key")
	ErrInsufficientScope  = errors.New("insufficient scope")
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
	for _, perm := range p.Permissions {
		if perm == permission || perm == "*" {
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

// Context key type
type contextKey string

const principalContextKey contextKey = "principal"

// WithPrincipal adds a principal to the context
func WithPrincipal(ctx context.Context, p *Principal) context.Context {
	return context.WithValue(ctx, principalContextKey, p)
}

// GetPrincipal retrieves the principal from context
func GetPrincipal(ctx context.Context) (*Principal, bool) {
	p, ok := ctx.Value(principalContextKey).(*Principal)
	return p, ok
}

// MustGetPrincipal retrieves principal or panics
func MustGetPrincipal(ctx context.Context) *Principal {
	p, ok := GetPrincipal(ctx)
	if !ok {
		panic("no principal in context")
	}
	return p
}

// Authenticator validates credentials and returns a Principal
type Authenticator interface {
	Authenticate(r *http.Request) (*Principal, error)
}

// JWTClaims contains JWT token claims
type JWTClaims struct {
	jwt.RegisteredClaims
	Roles       []string          `json:"roles,omitempty"`
	Permissions []string          `json:"permissions,omitempty"`
	Metadata    map[string]string `json:"metadata,omitempty"`
}

// JWTConfig holds JWT configuration
type JWTConfig struct {
	Secret        []byte
	Issuer        string
	AccessExpiry  time.Duration
	RefreshExpiry time.Duration
}

// JWTService handles JWT operations
type JWTService struct {
	config JWTConfig
}

// NewJWTService creates a new JWT service
func NewJWTService(config JWTConfig) *JWTService {
	return &JWTService{config: config}
}

// GenerateToken creates a new JWT token
func (s *JWTService) GenerateToken(userID string, roles []string, expiry time.Duration) (string, error) {
	now := time.Now()

	claims := JWTClaims{
		RegisteredClaims: jwt.RegisteredClaims{
			Subject:   userID,
			Issuer:    s.config.Issuer,
			IssuedAt:  jwt.NewNumericDate(now),
			ExpiresAt: jwt.NewNumericDate(now.Add(expiry)),
		},
		Roles: roles,
	}

	token := jwt.NewWithClaims(jwt.SigningMethodHS256, claims)
	return token.SignedString(s.config.Secret)
}

// ValidateToken validates a JWT token and returns claims
func (s *JWTService) ValidateToken(tokenString string) (*JWTClaims, error) {
	token, err := jwt.ParseWithClaims(tokenString, &JWTClaims{}, func(t *jwt.Token) (interface{}, error) {
		// Verify signing method
		if _, ok := t.Method.(*jwt.SigningMethodHMAC); !ok {
			return nil, ErrInvalidToken
		}
		return s.config.Secret, nil
	})

	if err != nil {
		if errors.Is(err, jwt.ErrTokenExpired) {
			return nil, ErrTokenExpired
		}
		return nil, ErrInvalidToken
	}

	claims, ok := token.Claims.(*JWTClaims)
	if !ok || !token.Valid {
		return nil, ErrInvalidToken
	}

	return claims, nil
}

// APIKey represents an API key
type APIKey struct {
	ID          string
	KeyHash     []byte
	ServiceName string
	Permissions []string
	CreatedAt   time.Time
	ExpiresAt   time.Time
	LastUsedAt  time.Time
}

// GenerateAPIKey creates a new random API key
func GenerateAPIKey() (string, error) {
	bytes := make([]byte, 32)
	if _, err := rand.Read(bytes); err != nil {
		return "", err
	}
	return base64.URLEncoding.EncodeToString(bytes), nil
}

// HashAPIKey hashes an API key for storage
func HashAPIKey(key string) ([]byte, error) {
	return bcrypt.GenerateFromPassword([]byte(key), bcrypt.DefaultCost)
}

// ValidateAPIKeyHash checks if a key matches a hash
func ValidateAPIKeyHash(key string, hash []byte) bool {
	err := bcrypt.CompareHashAndPassword(hash, []byte(key))
	return err == nil
}

// APIKeyStore interface for API key persistence
type APIKeyStore interface {
	Store(key *APIKey) error
	FindByKey(key string) (*APIKey, error)
	Delete(id string) error
	UpdateLastUsed(id string, t time.Time) error
}

// InMemoryAPIKeyStore is a simple in-memory implementation
type InMemoryAPIKeyStore struct {
	keys map[string]*APIKey // keyHash -> APIKey
}

// NewInMemoryAPIKeyStore creates a new in-memory store
func NewInMemoryAPIKeyStore() *InMemoryAPIKeyStore {
	return &InMemoryAPIKeyStore{
		keys: make(map[string]*APIKey),
	}
}

// Store saves an API key
func (s *InMemoryAPIKeyStore) Store(key *APIKey) error {
	s.keys[key.ID] = key
	return nil
}

// FindByKey looks up an API key and validates it
func (s *InMemoryAPIKeyStore) FindByKey(rawKey string) (*APIKey, error) {
	for _, apiKey := range s.keys {
		if ValidateAPIKeyHash(rawKey, apiKey.KeyHash) {
			return apiKey, nil
		}
	}
	return nil, ErrInvalidAPIKey
}

// Delete removes an API key
func (s *InMemoryAPIKeyStore) Delete(id string) error {
	delete(s.keys, id)
	return nil
}

// UpdateLastUsed updates the last used timestamp
func (s *InMemoryAPIKeyStore) UpdateLastUsed(id string, t time.Time) error {
	if key, ok := s.keys[id]; ok {
		key.LastUsedAt = t
	}
	return nil
}
