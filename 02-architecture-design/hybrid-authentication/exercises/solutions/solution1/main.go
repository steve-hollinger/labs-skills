// Solution for Exercise 1: JWT Refresh Tokens with Rotation
//
// This solution implements secure token refresh with rotation.

package main

import (
	"encoding/json"
	"fmt"
	"log"
	"net/http"
	"sync"
	"time"

	"github.com/golang-jwt/jwt/v5"
	"github.com/google/uuid"
)

// Configuration
var (
	accessSecret  = []byte("access-secret-change-in-production")
	refreshSecret = []byte("refresh-secret-change-in-production")
	issuer        = "refresh-token-example"
	accessExpiry  = 15 * time.Minute
	refreshExpiry = 7 * 24 * time.Hour
)

// TokenPair contains access and refresh tokens
type TokenPair struct {
	AccessToken  string `json:"access_token"`
	RefreshToken string `json:"refresh_token"`
	ExpiresIn    int64  `json:"expires_in"`
}

// AccessClaims for access tokens
type AccessClaims struct {
	jwt.RegisteredClaims
	Roles []string `json:"roles"`
}

// RefreshClaims for refresh tokens
type RefreshClaims struct {
	jwt.RegisteredClaims
	TokenID string   `json:"jti"`
	Roles   []string `json:"roles"` // Carry roles for convenience
}

// RefreshTokenStore manages refresh tokens
type RefreshTokenStore struct {
	mu     sync.RWMutex
	tokens map[string]string // tokenID -> userID
}

func NewRefreshTokenStore() *RefreshTokenStore {
	return &RefreshTokenStore{
		tokens: make(map[string]string),
	}
}

func (s *RefreshTokenStore) Store(tokenID, userID string) error {
	s.mu.Lock()
	defer s.mu.Unlock()
	s.tokens[tokenID] = userID
	return nil
}

func (s *RefreshTokenStore) Validate(tokenID string) (string, error) {
	s.mu.RLock()
	defer s.mu.RUnlock()
	userID, ok := s.tokens[tokenID]
	if !ok {
		return "", fmt.Errorf("token not found or revoked")
	}
	return userID, nil
}

func (s *RefreshTokenStore) Revoke(tokenID string) error {
	s.mu.Lock()
	defer s.mu.Unlock()
	delete(s.tokens, tokenID)
	return nil
}

func (s *RefreshTokenStore) RevokeAllForUser(userID string) error {
	s.mu.Lock()
	defer s.mu.Unlock()
	for tokenID, uid := range s.tokens {
		if uid == userID {
			delete(s.tokens, tokenID)
		}
	}
	return nil
}

// TokenService manages token operations
type TokenService struct {
	store *RefreshTokenStore
}

func NewTokenService(store *RefreshTokenStore) *TokenService {
	return &TokenService{store: store}
}

func (s *TokenService) generateAccessToken(userID string, roles []string) (string, error) {
	claims := AccessClaims{
		RegisteredClaims: jwt.RegisteredClaims{
			Subject:   userID,
			Issuer:    issuer,
			IssuedAt:  jwt.NewNumericDate(time.Now()),
			ExpiresAt: jwt.NewNumericDate(time.Now().Add(accessExpiry)),
		},
		Roles: roles,
	}
	token := jwt.NewWithClaims(jwt.SigningMethodHS256, claims)
	return token.SignedString(accessSecret)
}

func (s *TokenService) generateRefreshToken(tokenID, userID string, roles []string) (string, error) {
	claims := RefreshClaims{
		RegisteredClaims: jwt.RegisteredClaims{
			Subject:   userID,
			Issuer:    issuer,
			IssuedAt:  jwt.NewNumericDate(time.Now()),
			ExpiresAt: jwt.NewNumericDate(time.Now().Add(refreshExpiry)),
		},
		TokenID: tokenID,
		Roles:   roles,
	}
	token := jwt.NewWithClaims(jwt.SigningMethodHS256, claims)
	return token.SignedString(refreshSecret)
}

func (s *TokenService) GenerateTokenPair(userID string, roles []string) (*TokenPair, error) {
	// Generate access token
	accessToken, err := s.generateAccessToken(userID, roles)
	if err != nil {
		return nil, fmt.Errorf("failed to generate access token: %w", err)
	}

	// Generate refresh token with unique ID
	tokenID := uuid.New().String()
	refreshToken, err := s.generateRefreshToken(tokenID, userID, roles)
	if err != nil {
		return nil, fmt.Errorf("failed to generate refresh token: %w", err)
	}

	// Store refresh token ID
	if err := s.store.Store(tokenID, userID); err != nil {
		return nil, fmt.Errorf("failed to store refresh token: %w", err)
	}

	return &TokenPair{
		AccessToken:  accessToken,
		RefreshToken: refreshToken,
		ExpiresIn:    int64(accessExpiry.Seconds()),
	}, nil
}

func (s *TokenService) RefreshTokens(refreshToken string) (*TokenPair, error) {
	// Parse refresh token
	token, err := jwt.ParseWithClaims(refreshToken, &RefreshClaims{}, func(t *jwt.Token) (interface{}, error) {
		if _, ok := t.Method.(*jwt.SigningMethodHMAC); !ok {
			return nil, fmt.Errorf("unexpected signing method")
		}
		return refreshSecret, nil
	})
	if err != nil {
		return nil, fmt.Errorf("invalid refresh token: %w", err)
	}

	claims, ok := token.Claims.(*RefreshClaims)
	if !ok || !token.Valid {
		return nil, fmt.Errorf("invalid refresh token claims")
	}

	// Verify token is in store (not revoked)
	userID, err := s.store.Validate(claims.TokenID)
	if err != nil {
		return nil, fmt.Errorf("refresh token revoked or invalid")
	}

	// Verify user matches
	if userID != claims.Subject {
		return nil, fmt.Errorf("token user mismatch")
	}

	// ROTATION: Revoke old refresh token
	if err := s.store.Revoke(claims.TokenID); err != nil {
		log.Printf("Warning: failed to revoke old refresh token: %v", err)
	}

	// Generate new token pair
	return s.GenerateTokenPair(userID, claims.Roles)
}

func (s *TokenService) Logout(userID string) error {
	return s.store.RevokeAllForUser(userID)
}

// Global instances
var (
	tokenStore   = NewRefreshTokenStore()
	tokenService = NewTokenService(tokenStore)
)

// Mock users
var users = map[string]struct {
	Password string
	Roles    []string
}{
	"alice": {"password123", []string{"admin", "user"}},
	"bob":   {"password456", []string{"user"}},
}

// Handlers

func loginHandler(w http.ResponseWriter, r *http.Request) {
	if r.Method != http.MethodPost {
		writeError(w, http.StatusMethodNotAllowed, "Method not allowed")
		return
	}

	var req struct {
		Username string `json:"username"`
		Password string `json:"password"`
	}
	if err := json.NewDecoder(r.Body).Decode(&req); err != nil {
		writeError(w, http.StatusBadRequest, "Invalid JSON")
		return
	}

	// Validate credentials
	user, ok := users[req.Username]
	if !ok || user.Password != req.Password {
		writeError(w, http.StatusUnauthorized, "Invalid credentials")
		return
	}

	// Generate token pair
	pair, err := tokenService.GenerateTokenPair(req.Username, user.Roles)
	if err != nil {
		log.Printf("Token generation failed: %v", err)
		writeError(w, http.StatusInternalServerError, "Internal error")
		return
	}

	writeJSON(w, pair)
}

func refreshHandler(w http.ResponseWriter, r *http.Request) {
	if r.Method != http.MethodPost {
		writeError(w, http.StatusMethodNotAllowed, "Method not allowed")
		return
	}

	var req struct {
		RefreshToken string `json:"refresh_token"`
	}
	if err := json.NewDecoder(r.Body).Decode(&req); err != nil {
		writeError(w, http.StatusBadRequest, "Invalid JSON")
		return
	}

	pair, err := tokenService.RefreshTokens(req.RefreshToken)
	if err != nil {
		log.Printf("Token refresh failed: %v", err)
		writeError(w, http.StatusUnauthorized, "Invalid or expired refresh token")
		return
	}

	writeJSON(w, pair)
}

func logoutHandler(w http.ResponseWriter, r *http.Request) {
	if r.Method != http.MethodPost {
		writeError(w, http.StatusMethodNotAllowed, "Method not allowed")
		return
	}

	var req struct {
		UserID string `json:"user_id"`
	}
	if err := json.NewDecoder(r.Body).Decode(&req); err != nil {
		writeError(w, http.StatusBadRequest, "Invalid JSON")
		return
	}

	if err := tokenService.Logout(req.UserID); err != nil {
		log.Printf("Logout failed: %v", err)
		writeError(w, http.StatusInternalServerError, "Internal error")
		return
	}

	writeJSON(w, map[string]string{"message": "Logged out successfully"})
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
	http.HandleFunc("/login", loginHandler)
	http.HandleFunc("/refresh", refreshHandler)
	http.HandleFunc("/logout", logoutHandler)

	fmt.Println("Solution 1: JWT Refresh Tokens with Rotation")
	fmt.Println("=============================================")
	fmt.Println()
	fmt.Println("Starting server on http://localhost:8080")
	fmt.Println()
	fmt.Println("Test commands:")
	fmt.Println()
	fmt.Println("  # Login to get token pair")
	fmt.Println(`  TOKENS=$(curl -s -X POST http://localhost:8080/login -d '{"username":"alice","password":"password123"}')`)
	fmt.Println(`  echo $TOKENS | jq`)
	fmt.Println()
	fmt.Println("  # Extract refresh token")
	fmt.Println(`  REFRESH=$(echo $TOKENS | jq -r .refresh_token)`)
	fmt.Println()
	fmt.Println("  # Refresh tokens (old refresh token is now invalid)")
	fmt.Println(`  NEW_TOKENS=$(curl -s -X POST http://localhost:8080/refresh -d "{\"refresh_token\":\"$REFRESH\"}")`)
	fmt.Println(`  echo $NEW_TOKENS | jq`)
	fmt.Println()
	fmt.Println("  # Try to use old refresh token again (should fail)")
	fmt.Println(`  curl -s -X POST http://localhost:8080/refresh -d "{\"refresh_token\":\"$REFRESH\"}"`)
	fmt.Println()
	fmt.Println("  # Logout (revokes all tokens)")
	fmt.Println(`  curl -X POST http://localhost:8080/logout -d '{"user_id":"alice"}'`)
	fmt.Println()

	log.Fatal(http.ListenAndServe(":8080", nil))
}
