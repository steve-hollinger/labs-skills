// Example 2: API Key Authentication
//
// This example demonstrates implementing API key authentication:
// - API key generation and storage
// - Key validation with timing-safe comparison
// - Scoped permissions
// - Rate limiting per key
package main

import (
	"crypto/rand"
	"encoding/base64"
	"encoding/json"
	"fmt"
	"log"
	"net/http"
	"sync"
	"time"

	"golang.org/x/crypto/bcrypt"
)

// APIKey represents a stored API key
type APIKey struct {
	ID          string
	KeyHash     []byte
	ServiceName string
	Permissions []string
	RateLimit   int // requests per minute
	CreatedAt   time.Time
	ExpiresAt   time.Time
	LastUsedAt  time.Time
}

// Principal represents an authenticated service
type Principal struct {
	ID          string
	ServiceName string
	Permissions []string
}

// APIKeyStore manages API keys
type APIKeyStore struct {
	mu   sync.RWMutex
	keys map[string]*APIKey
}

func NewAPIKeyStore() *APIKeyStore {
	return &APIKeyStore{
		keys: make(map[string]*APIKey),
	}
}

// CreateKey generates and stores a new API key
func (s *APIKeyStore) CreateKey(serviceName string, permissions []string, rateLimit int, expiresIn time.Duration) (string, error) {
	// Generate random key
	bytes := make([]byte, 32)
	if _, err := rand.Read(bytes); err != nil {
		return "", err
	}
	rawKey := base64.URLEncoding.EncodeToString(bytes)

	// Hash the key for storage
	hash, err := bcrypt.GenerateFromPassword([]byte(rawKey), bcrypt.DefaultCost)
	if err != nil {
		return "", err
	}

	key := &APIKey{
		ID:          fmt.Sprintf("key_%d", time.Now().UnixNano()),
		KeyHash:     hash,
		ServiceName: serviceName,
		Permissions: permissions,
		RateLimit:   rateLimit,
		CreatedAt:   time.Now(),
	}

	if expiresIn > 0 {
		key.ExpiresAt = time.Now().Add(expiresIn)
	}

	s.mu.Lock()
	s.keys[key.ID] = key
	s.mu.Unlock()

	return rawKey, nil
}

// ValidateKey validates an API key and returns the principal
func (s *APIKeyStore) ValidateKey(rawKey string) (*Principal, *APIKey, error) {
	s.mu.RLock()
	defer s.mu.RUnlock()

	for _, apiKey := range s.keys {
		// Timing-safe comparison via bcrypt
		if err := bcrypt.CompareHashAndPassword(apiKey.KeyHash, []byte(rawKey)); err == nil {
			// Check expiration
			if !apiKey.ExpiresAt.IsZero() && apiKey.ExpiresAt.Before(time.Now()) {
				return nil, nil, fmt.Errorf("API key expired")
			}

			return &Principal{
				ID:          apiKey.ID,
				ServiceName: apiKey.ServiceName,
				Permissions: apiKey.Permissions,
			}, apiKey, nil
		}
	}

	return nil, nil, fmt.Errorf("invalid API key")
}

// RateLimiter tracks request rates per key
type RateLimiter struct {
	mu       sync.Mutex
	requests map[string][]time.Time
}

func NewRateLimiter() *RateLimiter {
	return &RateLimiter{
		requests: make(map[string][]time.Time),
	}
}

// Allow checks if a request is allowed for the given key
func (r *RateLimiter) Allow(keyID string, limit int) bool {
	r.mu.Lock()
	defer r.mu.Unlock()

	now := time.Now()
	windowStart := now.Add(-1 * time.Minute)

	// Clean old requests
	var recent []time.Time
	for _, t := range r.requests[keyID] {
		if t.After(windowStart) {
			recent = append(recent, t)
		}
	}

	if len(recent) >= limit {
		r.requests[keyID] = recent
		return false
	}

	r.requests[keyID] = append(recent, now)
	return true
}

// Global store and rate limiter
var (
	keyStore    = NewAPIKeyStore()
	rateLimiter = NewRateLimiter()
)

// Context key for principal
type contextKey string

const principalKey contextKey = "principal"

// APIKeyMiddleware validates API keys
func APIKeyMiddleware(next http.Handler) http.Handler {
	return http.HandlerFunc(func(w http.ResponseWriter, r *http.Request) {
		// Extract API key from header or query param
		apiKey := r.Header.Get("X-API-Key")
		if apiKey == "" {
			apiKey = r.URL.Query().Get("api_key")
		}

		if apiKey == "" {
			http.Error(w, `{"error":"API key required"}`, http.StatusUnauthorized)
			return
		}

		// Validate key
		principal, keyInfo, err := keyStore.ValidateKey(apiKey)
		if err != nil {
			log.Printf("API key validation failed: %v", err)
			http.Error(w, `{"error":"Invalid API key"}`, http.StatusUnauthorized)
			return
		}

		// Check rate limit
		if !rateLimiter.Allow(principal.ID, keyInfo.RateLimit) {
			w.Header().Set("Retry-After", "60")
			http.Error(w, `{"error":"Rate limit exceeded"}`, http.StatusTooManyRequests)
			return
		}

		// Add principal to context
		ctx := r.Context()
		ctx = context.WithValue(ctx, principalKey, principal)
		next.ServeHTTP(w, r.WithContext(ctx))
	})
}

// RequirePermission checks for required permission
func RequirePermission(permission string) func(http.Handler) http.Handler {
	return func(next http.Handler) http.Handler {
		return http.HandlerFunc(func(w http.ResponseWriter, r *http.Request) {
			principal := r.Context().Value(principalKey).(*Principal)

			hasPermission := false
			for _, p := range principal.Permissions {
				if p == permission || p == "*" {
					hasPermission = true
					break
				}
			}

			if !hasPermission {
				http.Error(w, `{"error":"Insufficient permissions"}`, http.StatusForbidden)
				return
			}

			next.ServeHTTP(w, r)
		})
	}
}

// Handlers

func createKeyHandler(w http.ResponseWriter, r *http.Request) {
	if r.Method != http.MethodPost {
		http.Error(w, `{"error":"Method not allowed"}`, http.StatusMethodNotAllowed)
		return
	}

	var req struct {
		ServiceName string   `json:"service_name"`
		Permissions []string `json:"permissions"`
		RateLimit   int      `json:"rate_limit"`
		ExpiresIn   int      `json:"expires_in_hours"`
	}

	if err := json.NewDecoder(r.Body).Decode(&req); err != nil {
		http.Error(w, `{"error":"Invalid JSON"}`, http.StatusBadRequest)
		return
	}

	if req.ServiceName == "" {
		http.Error(w, `{"error":"service_name required"}`, http.StatusBadRequest)
		return
	}

	if req.RateLimit == 0 {
		req.RateLimit = 60 // default
	}

	expiresIn := time.Duration(req.ExpiresIn) * time.Hour

	rawKey, err := keyStore.CreateKey(req.ServiceName, req.Permissions, req.RateLimit, expiresIn)
	if err != nil {
		log.Printf("Failed to create API key: %v", err)
		http.Error(w, `{"error":"Internal error"}`, http.StatusInternalServerError)
		return
	}

	w.Header().Set("Content-Type", "application/json")
	json.NewEncoder(w).Encode(map[string]interface{}{
		"api_key":      rawKey,
		"service_name": req.ServiceName,
		"permissions":  req.Permissions,
		"rate_limit":   req.RateLimit,
		"message":      "Store this key securely - it cannot be retrieved again!",
	})
}

func whoamiHandler(w http.ResponseWriter, r *http.Request) {
	principal := r.Context().Value(principalKey).(*Principal)

	w.Header().Set("Content-Type", "application/json")
	json.NewEncoder(w).Encode(map[string]interface{}{
		"key_id":       principal.ID,
		"service_name": principal.ServiceName,
		"permissions":  principal.Permissions,
	})
}

func readDataHandler(w http.ResponseWriter, r *http.Request) {
	principal := r.Context().Value(principalKey).(*Principal)

	w.Header().Set("Content-Type", "application/json")
	json.NewEncoder(w).Encode(map[string]interface{}{
		"data":        []string{"item1", "item2", "item3"},
		"accessed_by": principal.ServiceName,
	})
}

func writeDataHandler(w http.ResponseWriter, r *http.Request) {
	principal := r.Context().Value(principalKey).(*Principal)

	w.Header().Set("Content-Type", "application/json")
	json.NewEncoder(w).Encode(map[string]interface{}{
		"message":    "Data written successfully",
		"written_by": principal.ServiceName,
	})
}

import "context"

func main() {
	mux := http.NewServeMux()

	// Management endpoint (would be protected in production)
	mux.HandleFunc("/keys/create", createKeyHandler)

	// API endpoints
	mux.Handle("/whoami", APIKeyMiddleware(http.HandlerFunc(whoamiHandler)))
	mux.Handle("/data/read", APIKeyMiddleware(RequirePermission("data:read")(http.HandlerFunc(readDataHandler))))
	mux.Handle("/data/write", APIKeyMiddleware(RequirePermission("data:write")(http.HandlerFunc(writeDataHandler))))

	fmt.Println("Example 2: API Key Authentication")
	fmt.Println("==================================")
	fmt.Println()
	fmt.Println("Starting server on http://localhost:8080")
	fmt.Println()
	fmt.Println("Available endpoints:")
	fmt.Println("  POST /keys/create - Create a new API key")
	fmt.Println("  GET  /whoami      - Get current service info")
	fmt.Println("  GET  /data/read   - Read data (requires data:read)")
	fmt.Println("  POST /data/write  - Write data (requires data:write)")
	fmt.Println()
	fmt.Println("Test commands:")
	fmt.Println("  # Create an API key with read permission")
	fmt.Println(`  API_KEY=$(curl -s -X POST http://localhost:8080/keys/create -d '{"service_name":"reader-service","permissions":["data:read"],"rate_limit":10}' | jq -r .api_key)`)
	fmt.Println()
	fmt.Println("  # Use the API key")
	fmt.Println(`  curl -H "X-API-Key: $API_KEY" http://localhost:8080/whoami`)
	fmt.Println(`  curl -H "X-API-Key: $API_KEY" http://localhost:8080/data/read`)
	fmt.Println()
	fmt.Println("  # Try to write (should fail - no data:write permission)")
	fmt.Println(`  curl -H "X-API-Key: $API_KEY" http://localhost:8080/data/write`)
	fmt.Println()
	fmt.Println("  # Test rate limiting (run 11+ times quickly)")
	fmt.Println(`  for i in {1..12}; do curl -s -H "X-API-Key: $API_KEY" http://localhost:8080/whoami; done`)
	fmt.Println()

	log.Fatal(http.ListenAndServe(":8080", mux))
}
