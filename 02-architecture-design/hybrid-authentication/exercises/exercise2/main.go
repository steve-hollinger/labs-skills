// Exercise 2: API Key Management System
//
// Build a complete API key management system with:
// - Key generation with scopes
// - Key listing (for the owner)
// - Key revocation
// - Rate limiting per key
// - Usage tracking
//
// Requirements:
// 1. Create an API key with:
//    - Unique ID
//    - Service name
//    - Scopes/permissions
//    - Rate limit (requests per minute)
//    - Optional expiration
// 2. List all keys for a service (hashed, not raw)
// 3. Revoke a key by ID
// 4. Track usage (request count, last used)
// 5. Enforce rate limits per key
//
// API Design:
//   POST /keys          - Create new key
//   GET  /keys          - List keys (requires auth)
//   DELETE /keys/{id}   - Revoke key
//   GET  /keys/{id}/stats - Usage statistics
//
// Hints:
// - Store key hash, not raw key
// - Return raw key only on creation (one time!)
// - Use separate struct for API response (hide hash)

package main

import (
	"fmt"
	"net/http"
	"time"
)

// APIKey represents a stored API key
type APIKey struct {
	ID          string
	KeyPrefix   string // First 8 chars for identification
	KeyHash     []byte
	ServiceName string
	Scopes      []string
	RateLimit   int
	CreatedAt   time.Time
	ExpiresAt   time.Time
	LastUsedAt  time.Time
	RequestCount int64
}

// APIKeyResponse is the public representation (no hash)
type APIKeyResponse struct {
	ID          string    `json:"id"`
	KeyPrefix   string    `json:"key_prefix"`
	ServiceName string    `json:"service_name"`
	Scopes      []string  `json:"scopes"`
	RateLimit   int       `json:"rate_limit"`
	CreatedAt   time.Time `json:"created_at"`
	ExpiresAt   time.Time `json:"expires_at,omitempty"`
}

// CreateKeyRequest is the request to create a new key
type CreateKeyRequest struct {
	ServiceName  string   `json:"service_name"`
	Scopes       []string `json:"scopes"`
	RateLimit    int      `json:"rate_limit"`
	ExpiresInDays int     `json:"expires_in_days,omitempty"`
}

// CreateKeyResponse includes the raw key (only time it's returned)
type CreateKeyResponse struct {
	APIKey  string   `json:"api_key"` // Raw key - save it!
	ID      string   `json:"id"`
	Scopes  []string `json:"scopes"`
	Message string   `json:"message"`
}

// UsageStats shows key usage statistics
type UsageStats struct {
	KeyID        string    `json:"key_id"`
	RequestCount int64     `json:"request_count"`
	LastUsedAt   time.Time `json:"last_used_at"`
	RateLimit    int       `json:"rate_limit"`
	CurrentRate  int       `json:"current_rate"` // requests in current minute
}

// APIKeyStore manages API keys
type APIKeyStore struct {
	// TODO: Add fields
	// keys map[id]*APIKey
}

func NewAPIKeyStore() *APIKeyStore {
	// TODO: Initialize
	return &APIKeyStore{}
}

// Create generates and stores a new API key
func (s *APIKeyStore) Create(req CreateKeyRequest) (*CreateKeyResponse, error) {
	// TODO: Implement
	// 1. Generate random 32-byte key
	// 2. Hash the key for storage
	// 3. Store key prefix for identification
	// 4. Return raw key (one time only!)
	return nil, fmt.Errorf("not implemented")
}

// List returns all keys for display (without hashes)
func (s *APIKeyStore) List() []APIKeyResponse {
	// TODO: Implement
	return nil
}

// Get retrieves a key by ID
func (s *APIKeyStore) Get(id string) (*APIKey, error) {
	// TODO: Implement
	return nil, fmt.Errorf("not implemented")
}

// Validate checks a raw key and returns the key info
func (s *APIKeyStore) Validate(rawKey string) (*APIKey, error) {
	// TODO: Implement (timing-safe comparison)
	return nil, fmt.Errorf("not implemented")
}

// Revoke deletes a key
func (s *APIKeyStore) Revoke(id string) error {
	// TODO: Implement
	return fmt.Errorf("not implemented")
}

// RecordUsage updates usage statistics
func (s *APIKeyStore) RecordUsage(id string) error {
	// TODO: Implement
	return fmt.Errorf("not implemented")
}

// GetStats returns usage statistics for a key
func (s *APIKeyStore) GetStats(id string) (*UsageStats, error) {
	// TODO: Implement
	return nil, fmt.Errorf("not implemented")
}

// RateLimiter tracks request rates per key
type RateLimiter struct {
	// TODO: Add fields for tracking requests per minute
}

func NewRateLimiter() *RateLimiter {
	// TODO: Initialize
	return &RateLimiter{}
}

// Allow checks if a request is allowed
func (r *RateLimiter) Allow(keyID string, limit int) bool {
	// TODO: Implement
	// Track requests per key per minute window
	return false
}

// Handlers

func createKeyHandler(w http.ResponseWriter, r *http.Request) {
	// TODO: Implement key creation
	http.Error(w, "Not implemented", http.StatusNotImplemented)
}

func listKeysHandler(w http.ResponseWriter, r *http.Request) {
	// TODO: Implement key listing
	http.Error(w, "Not implemented", http.StatusNotImplemented)
}

func revokeKeyHandler(w http.ResponseWriter, r *http.Request) {
	// TODO: Implement key revocation
	http.Error(w, "Not implemented", http.StatusNotImplemented)
}

func keyStatsHandler(w http.ResponseWriter, r *http.Request) {
	// TODO: Implement stats endpoint
	http.Error(w, "Not implemented", http.StatusNotImplemented)
}

func protectedHandler(w http.ResponseWriter, r *http.Request) {
	// TODO: Implement protected endpoint using API key auth
	http.Error(w, "Not implemented", http.StatusNotImplemented)
}

func main() {
	fmt.Println("Exercise 2: API Key Management System")
	fmt.Println("======================================")
	fmt.Println()
	fmt.Println("Implement a complete API key management system:")
	fmt.Println("  - Key generation with scopes")
	fmt.Println("  - Key listing and revocation")
	fmt.Println("  - Rate limiting per key")
	fmt.Println("  - Usage tracking")
	fmt.Println()
	fmt.Println("Endpoints to implement:")
	fmt.Println("  POST   /keys           - Create new key")
	fmt.Println("  GET    /keys           - List all keys")
	fmt.Println("  DELETE /keys/{id}      - Revoke key")
	fmt.Println("  GET    /keys/{id}/stats - Usage statistics")
	fmt.Println("  GET    /protected      - Test protected endpoint")
	fmt.Println()

	http.HandleFunc("/keys", func(w http.ResponseWriter, r *http.Request) {
		switch r.Method {
		case http.MethodPost:
			createKeyHandler(w, r)
		case http.MethodGet:
			listKeysHandler(w, r)
		default:
			http.Error(w, "Method not allowed", http.StatusMethodNotAllowed)
		}
	})
	http.HandleFunc("/keys/", revokeKeyHandler)
	http.HandleFunc("/protected", protectedHandler)

	fmt.Println("Starting server on http://localhost:8080")
	http.ListenAndServe(":8080", nil)
}
