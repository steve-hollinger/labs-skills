// Exercise 1: JWT Refresh Tokens with Rotation
//
// Implement a secure token refresh system with rotation.
// When a refresh token is used, it should be invalidated and a new pair issued.
//
// Requirements:
// 1. Create TokenPair struct with access and refresh tokens
// 2. Implement token generation:
//    - Access token: short-lived (15 min), contains user claims
//    - Refresh token: longer-lived (7 days), contains token ID
// 3. Store refresh token IDs (not the tokens themselves)
// 4. Implement refresh endpoint:
//    - Validate refresh token
//    - Check if token ID is in store (not revoked)
//    - Revoke old token (rotation)
//    - Issue new token pair
// 5. Implement logout that revokes all refresh tokens for user
//
// Security considerations:
// - Refresh token rotation prevents replay attacks
// - Storing token IDs (not full tokens) is more secure
// - Revoking all tokens on logout provides session management
//
// Hints:
// - Use uuid for refresh token IDs
// - Store: map[tokenID]userID for active refresh tokens
// - Include tokenID in refresh token claims

package main

import (
	"fmt"
	"net/http"
)

// TokenPair contains access and refresh tokens
type TokenPair struct {
	AccessToken  string `json:"access_token"`
	RefreshToken string `json:"refresh_token"`
	ExpiresIn    int64  `json:"expires_in"`
}

// RefreshTokenStore manages refresh tokens
// TODO: Implement with proper methods
type RefreshTokenStore struct {
	// tokens map[tokenID]userID
}

func NewRefreshTokenStore() *RefreshTokenStore {
	// TODO: Initialize store
	return &RefreshTokenStore{}
}

// Store saves a refresh token ID
func (s *RefreshTokenStore) Store(tokenID, userID string) error {
	// TODO: Implement
	return fmt.Errorf("not implemented")
}

// Validate checks if a token ID is valid
func (s *RefreshTokenStore) Validate(tokenID string) (userID string, err error) {
	// TODO: Implement
	return "", fmt.Errorf("not implemented")
}

// Revoke removes a refresh token
func (s *RefreshTokenStore) Revoke(tokenID string) error {
	// TODO: Implement
	return fmt.Errorf("not implemented")
}

// RevokeAllForUser removes all refresh tokens for a user
func (s *RefreshTokenStore) RevokeAllForUser(userID string) error {
	// TODO: Implement
	return fmt.Errorf("not implemented")
}

// TokenService manages token operations
type TokenService struct {
	store *RefreshTokenStore
	// TODO: Add secrets and configuration
}

func NewTokenService(store *RefreshTokenStore) *TokenService {
	return &TokenService{store: store}
}

// GenerateTokenPair creates new access and refresh tokens
func (s *TokenService) GenerateTokenPair(userID string, roles []string) (*TokenPair, error) {
	// TODO: Implement
	// 1. Generate access token with user claims
	// 2. Generate refresh token with tokenID
	// 3. Store tokenID -> userID mapping
	// 4. Return token pair
	return nil, fmt.Errorf("not implemented")
}

// RefreshTokens validates refresh token and issues new pair
func (s *TokenService) RefreshTokens(refreshToken string) (*TokenPair, error) {
	// TODO: Implement
	// 1. Parse and validate refresh token
	// 2. Check if tokenID is in store
	// 3. Revoke old tokenID (rotation!)
	// 4. Generate new token pair
	return nil, fmt.Errorf("not implemented")
}

// Logout revokes all tokens for user
func (s *TokenService) Logout(userID string) error {
	// TODO: Implement
	return s.store.RevokeAllForUser(userID)
}

// Handlers

func loginHandler(w http.ResponseWriter, r *http.Request) {
	// TODO: Implement login that returns TokenPair
	http.Error(w, "Not implemented", http.StatusNotImplemented)
}

func refreshHandler(w http.ResponseWriter, r *http.Request) {
	// TODO: Implement token refresh
	http.Error(w, "Not implemented", http.StatusNotImplemented)
}

func logoutHandler(w http.ResponseWriter, r *http.Request) {
	// TODO: Implement logout that revokes all tokens
	http.Error(w, "Not implemented", http.StatusNotImplemented)
}

func main() {
	fmt.Println("Exercise 1: JWT Refresh Tokens with Rotation")
	fmt.Println("=============================================")
	fmt.Println()
	fmt.Println("Implement a token refresh system with:")
	fmt.Println("  - Short-lived access tokens (15 min)")
	fmt.Println("  - Long-lived refresh tokens (7 days)")
	fmt.Println("  - Token rotation on refresh")
	fmt.Println("  - Logout that revokes all tokens")
	fmt.Println()
	fmt.Println("Endpoints to implement:")
	fmt.Println("  POST /login   - Returns token pair")
	fmt.Println("  POST /refresh - Refresh tokens (rotation)")
	fmt.Println("  POST /logout  - Revoke all tokens")
	fmt.Println()

	http.HandleFunc("/login", loginHandler)
	http.HandleFunc("/refresh", refreshHandler)
	http.HandleFunc("/logout", logoutHandler)

	fmt.Println("Starting server on http://localhost:8080")
	http.ListenAndServe(":8080", nil)
}
