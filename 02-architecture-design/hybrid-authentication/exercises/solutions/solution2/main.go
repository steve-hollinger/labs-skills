// Solution for Exercise 2: API Key Management System
//
// Complete implementation of API key management with rate limiting.

package main

import (
	"crypto/rand"
	"encoding/base64"
	"encoding/json"
	"fmt"
	"log"
	"net/http"
	"strings"
	"sync"
	"sync/atomic"
	"time"

	"golang.org/x/crypto/bcrypt"
)

// APIKey represents a stored API key
type APIKey struct {
	ID           string
	KeyPrefix    string
	KeyHash      []byte
	ServiceName  string
	Scopes       []string
	RateLimit    int
	CreatedAt    time.Time
	ExpiresAt    time.Time
	LastUsedAt   time.Time
	RequestCount atomic.Int64
}

// APIKeyResponse for listing (no hash)
type APIKeyResponse struct {
	ID          string    `json:"id"`
	KeyPrefix   string    `json:"key_prefix"`
	ServiceName string    `json:"service_name"`
	Scopes      []string  `json:"scopes"`
	RateLimit   int       `json:"rate_limit"`
	CreatedAt   time.Time `json:"created_at"`
	ExpiresAt   time.Time `json:"expires_at,omitempty"`
}

type CreateKeyRequest struct {
	ServiceName   string   `json:"service_name"`
	Scopes        []string `json:"scopes"`
	RateLimit     int      `json:"rate_limit"`
	ExpiresInDays int      `json:"expires_in_days,omitempty"`
}

type CreateKeyResponse struct {
	APIKey  string   `json:"api_key"`
	ID      string   `json:"id"`
	Scopes  []string `json:"scopes"`
	Message string   `json:"message"`
}

type UsageStats struct {
	KeyID        string    `json:"key_id"`
	ServiceName  string    `json:"service_name"`
	RequestCount int64     `json:"request_count"`
	LastUsedAt   time.Time `json:"last_used_at"`
	RateLimit    int       `json:"rate_limit"`
	CurrentRate  int       `json:"current_rate"`
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

func (s *APIKeyStore) Create(req CreateKeyRequest) (*CreateKeyResponse, error) {
	// Generate random key
	bytes := make([]byte, 32)
	if _, err := rand.Read(bytes); err != nil {
		return nil, err
	}
	rawKey := base64.URLEncoding.EncodeToString(bytes)

	// Hash for storage
	hash, err := bcrypt.GenerateFromPassword([]byte(rawKey), bcrypt.DefaultCost)
	if err != nil {
		return nil, err
	}

	key := &APIKey{
		ID:          fmt.Sprintf("key_%d", time.Now().UnixNano()),
		KeyPrefix:   rawKey[:8],
		KeyHash:     hash,
		ServiceName: req.ServiceName,
		Scopes:      req.Scopes,
		RateLimit:   req.RateLimit,
		CreatedAt:   time.Now(),
	}

	if req.ExpiresInDays > 0 {
		key.ExpiresAt = time.Now().AddDate(0, 0, req.ExpiresInDays)
	}

	s.mu.Lock()
	s.keys[key.ID] = key
	s.mu.Unlock()

	return &CreateKeyResponse{
		APIKey:  rawKey,
		ID:      key.ID,
		Scopes:  key.Scopes,
		Message: "Store this key securely - it cannot be retrieved again!",
	}, nil
}

func (s *APIKeyStore) List() []APIKeyResponse {
	s.mu.RLock()
	defer s.mu.RUnlock()

	result := make([]APIKeyResponse, 0, len(s.keys))
	for _, key := range s.keys {
		result = append(result, APIKeyResponse{
			ID:          key.ID,
			KeyPrefix:   key.KeyPrefix,
			ServiceName: key.ServiceName,
			Scopes:      key.Scopes,
			RateLimit:   key.RateLimit,
			CreatedAt:   key.CreatedAt,
			ExpiresAt:   key.ExpiresAt,
		})
	}
	return result
}

func (s *APIKeyStore) Get(id string) (*APIKey, error) {
	s.mu.RLock()
	defer s.mu.RUnlock()

	key, ok := s.keys[id]
	if !ok {
		return nil, fmt.Errorf("key not found")
	}
	return key, nil
}

func (s *APIKeyStore) Validate(rawKey string) (*APIKey, error) {
	s.mu.RLock()
	defer s.mu.RUnlock()

	for _, key := range s.keys {
		if bcrypt.CompareHashAndPassword(key.KeyHash, []byte(rawKey)) == nil {
			// Check expiration
			if !key.ExpiresAt.IsZero() && key.ExpiresAt.Before(time.Now()) {
				return nil, fmt.Errorf("key expired")
			}
			return key, nil
		}
	}
	return nil, fmt.Errorf("invalid key")
}

func (s *APIKeyStore) Revoke(id string) error {
	s.mu.Lock()
	defer s.mu.Unlock()

	if _, ok := s.keys[id]; !ok {
		return fmt.Errorf("key not found")
	}
	delete(s.keys, id)
	return nil
}

func (s *APIKeyStore) RecordUsage(key *APIKey) {
	key.LastUsedAt = time.Now()
	key.RequestCount.Add(1)
}

func (s *APIKeyStore) GetStats(id string) (*UsageStats, error) {
	key, err := s.Get(id)
	if err != nil {
		return nil, err
	}

	return &UsageStats{
		KeyID:        key.ID,
		ServiceName:  key.ServiceName,
		RequestCount: key.RequestCount.Load(),
		LastUsedAt:   key.LastUsedAt,
		RateLimit:    key.RateLimit,
		CurrentRate:  rateLimiter.GetCurrentRate(key.ID),
	}, nil
}

// RateLimiter tracks requests per key
type RateLimiter struct {
	mu       sync.Mutex
	requests map[string][]time.Time
}

func NewRateLimiter() *RateLimiter {
	return &RateLimiter{
		requests: make(map[string][]time.Time),
	}
}

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

func (r *RateLimiter) GetCurrentRate(keyID string) int {
	r.mu.Lock()
	defer r.mu.Unlock()

	now := time.Now()
	windowStart := now.Add(-1 * time.Minute)

	count := 0
	for _, t := range r.requests[keyID] {
		if t.After(windowStart) {
			count++
		}
	}
	return count
}

// Global instances
var (
	keyStore    = NewAPIKeyStore()
	rateLimiter = NewRateLimiter()
)

// Context key
type contextKey string

const apiKeyContextKey contextKey = "apiKey"

// Middleware
func APIKeyMiddleware(next http.Handler) http.Handler {
	return http.HandlerFunc(func(w http.ResponseWriter, r *http.Request) {
		key := r.Header.Get("X-API-Key")
		if key == "" {
			key = r.URL.Query().Get("api_key")
		}
		if key == "" {
			writeError(w, http.StatusUnauthorized, "API key required")
			return
		}

		apiKey, err := keyStore.Validate(key)
		if err != nil {
			writeError(w, http.StatusUnauthorized, "Invalid API key")
			return
		}

		if !rateLimiter.Allow(apiKey.ID, apiKey.RateLimit) {
			w.Header().Set("Retry-After", "60")
			writeError(w, http.StatusTooManyRequests, "Rate limit exceeded")
			return
		}

		keyStore.RecordUsage(apiKey)

		ctx := r.Context()
		ctx = context.WithValue(ctx, apiKeyContextKey, apiKey)
		next.ServeHTTP(w, r.WithContext(ctx))
	})
}

func RequireScope(scope string) func(http.Handler) http.Handler {
	return func(next http.Handler) http.Handler {
		return http.HandlerFunc(func(w http.ResponseWriter, r *http.Request) {
			apiKey := r.Context().Value(apiKeyContextKey).(*APIKey)
			hasScope := false
			for _, s := range apiKey.Scopes {
				if s == scope || s == "*" {
					hasScope = true
					break
				}
			}
			if !hasScope {
				writeError(w, http.StatusForbidden, "Insufficient scope")
				return
			}
			next.ServeHTTP(w, r)
		})
	}
}

import "context"

// Handlers
func createKeyHandler(w http.ResponseWriter, r *http.Request) {
	var req CreateKeyRequest
	if err := json.NewDecoder(r.Body).Decode(&req); err != nil {
		writeError(w, http.StatusBadRequest, "Invalid JSON")
		return
	}

	if req.ServiceName == "" {
		writeError(w, http.StatusBadRequest, "service_name required")
		return
	}
	if req.RateLimit == 0 {
		req.RateLimit = 60
	}

	resp, err := keyStore.Create(req)
	if err != nil {
		writeError(w, http.StatusInternalServerError, "Failed to create key")
		return
	}

	w.WriteHeader(http.StatusCreated)
	writeJSON(w, resp)
}

func listKeysHandler(w http.ResponseWriter, r *http.Request) {
	keys := keyStore.List()
	writeJSON(w, map[string]interface{}{
		"keys":  keys,
		"count": len(keys),
	})
}

func revokeKeyHandler(w http.ResponseWriter, r *http.Request) {
	if r.Method != http.MethodDelete {
		writeError(w, http.StatusMethodNotAllowed, "Method not allowed")
		return
	}

	id := strings.TrimPrefix(r.URL.Path, "/keys/")
	if strings.Contains(id, "/") {
		// Handle /keys/{id}/stats
		parts := strings.Split(id, "/")
		if len(parts) == 2 && parts[1] == "stats" {
			keyStatsHandler(w, r, parts[0])
			return
		}
	}

	if err := keyStore.Revoke(id); err != nil {
		writeError(w, http.StatusNotFound, "Key not found")
		return
	}

	writeJSON(w, map[string]string{"message": "Key revoked"})
}

func keyStatsHandler(w http.ResponseWriter, r *http.Request, id string) {
	stats, err := keyStore.GetStats(id)
	if err != nil {
		writeError(w, http.StatusNotFound, "Key not found")
		return
	}
	writeJSON(w, stats)
}

func protectedHandler(w http.ResponseWriter, r *http.Request) {
	apiKey := r.Context().Value(apiKeyContextKey).(*APIKey)
	writeJSON(w, map[string]interface{}{
		"message":      "Access granted!",
		"service":      apiKey.ServiceName,
		"scopes":       apiKey.Scopes,
		"request_count": apiKey.RequestCount.Load(),
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
	mux := http.NewServeMux()

	mux.HandleFunc("/keys", func(w http.ResponseWriter, r *http.Request) {
		switch r.Method {
		case http.MethodPost:
			createKeyHandler(w, r)
		case http.MethodGet:
			listKeysHandler(w, r)
		default:
			writeError(w, http.StatusMethodNotAllowed, "Method not allowed")
		}
	})
	mux.HandleFunc("/keys/", revokeKeyHandler)
	mux.Handle("/protected", APIKeyMiddleware(http.HandlerFunc(protectedHandler)))

	fmt.Println("Solution 2: API Key Management System")
	fmt.Println("======================================")
	fmt.Println()
	fmt.Println("Starting server on http://localhost:8080")
	fmt.Println()
	fmt.Println("Test commands:")
	fmt.Println()
	fmt.Println("  # Create API key")
	fmt.Println(`  KEY=$(curl -s -X POST http://localhost:8080/keys -d '{"service_name":"test-svc","scopes":["read","write"],"rate_limit":5}' | jq -r .api_key)`)
	fmt.Println()
	fmt.Println("  # List keys")
	fmt.Println("  curl http://localhost:8080/keys | jq")
	fmt.Println()
	fmt.Println("  # Use protected endpoint")
	fmt.Println(`  curl -H "X-API-Key: $KEY" http://localhost:8080/protected`)
	fmt.Println()
	fmt.Println("  # Test rate limiting (run 6+ times)")
	fmt.Println(`  for i in {1..6}; do curl -s -H "X-API-Key: $KEY" http://localhost:8080/protected | jq -r '.message // .error'; done`)
	fmt.Println()

	log.Fatal(http.ListenAndServe(":8080", mux))
}
