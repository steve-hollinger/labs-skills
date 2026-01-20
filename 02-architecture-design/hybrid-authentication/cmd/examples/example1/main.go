// Example 1: JWT Authentication
//
// This example demonstrates implementing JWT-based authentication:
// - Token generation with claims
// - Token validation
// - Authentication middleware
// - Protected endpoints
package main

import (
	"encoding/json"
	"fmt"
	"log"
	"net/http"
	"time"

	"github.com/golang-jwt/jwt/v5"
)

// Config
var (
	jwtSecret     = []byte("super-secret-key-change-in-production")
	jwtIssuer     = "auth-example"
	tokenExpiry   = 15 * time.Minute
)

// Claims represents JWT claims
type Claims struct {
	jwt.RegisteredClaims
	Roles []string `json:"roles"`
}

// User represents a user in our system
type User struct {
	ID       string   `json:"id"`
	Username string   `json:"username"`
	Roles    []string `json:"roles"`
}

// Mock user database
var users = map[string]struct {
	Password string
	User     User
}{
	"alice": {
		Password: "password123",
		User: User{
			ID:       "user-1",
			Username: "alice",
			Roles:    []string{"admin", "user"},
		},
	},
	"bob": {
		Password: "password456",
		User: User{
			ID:       "user-2",
			Username: "bob",
			Roles:    []string{"user"},
		},
	},
}

// generateToken creates a new JWT token for a user
func generateToken(user User) (string, error) {
	now := time.Now()

	claims := Claims{
		RegisteredClaims: jwt.RegisteredClaims{
			Subject:   user.ID,
			Issuer:    jwtIssuer,
			IssuedAt:  jwt.NewNumericDate(now),
			ExpiresAt: jwt.NewNumericDate(now.Add(tokenExpiry)),
		},
		Roles: user.Roles,
	}

	token := jwt.NewWithClaims(jwt.SigningMethodHS256, claims)
	return token.SignedString(jwtSecret)
}

// validateToken parses and validates a JWT token
func validateToken(tokenString string) (*Claims, error) {
	token, err := jwt.ParseWithClaims(tokenString, &Claims{}, func(t *jwt.Token) (interface{}, error) {
		// Verify signing method
		if _, ok := t.Method.(*jwt.SigningMethodHMAC); !ok {
			return nil, fmt.Errorf("unexpected signing method: %v", t.Header["alg"])
		}
		return jwtSecret, nil
	})

	if err != nil {
		return nil, err
	}

	claims, ok := token.Claims.(*Claims)
	if !ok || !token.Valid {
		return nil, fmt.Errorf("invalid token")
	}

	return claims, nil
}

// Context key for principal
type contextKey string

const principalKey contextKey = "principal"

// AuthMiddleware validates JWT and adds principal to context
func AuthMiddleware(next http.Handler) http.Handler {
	return http.HandlerFunc(func(w http.ResponseWriter, r *http.Request) {
		// Extract token from Authorization header
		authHeader := r.Header.Get("Authorization")
		if authHeader == "" {
			http.Error(w, `{"error":"No authorization header"}`, http.StatusUnauthorized)
			return
		}

		// Check for Bearer prefix
		if len(authHeader) < 7 || authHeader[:7] != "Bearer " {
			http.Error(w, `{"error":"Invalid authorization format"}`, http.StatusUnauthorized)
			return
		}

		tokenString := authHeader[7:]

		// Validate token
		claims, err := validateToken(tokenString)
		if err != nil {
			log.Printf("Token validation failed: %v", err)
			http.Error(w, `{"error":"Invalid or expired token"}`, http.StatusUnauthorized)
			return
		}

		// Add claims to context
		ctx := r.Context()
		ctx = context.WithValue(ctx, principalKey, claims)
		next.ServeHTTP(w, r.WithContext(ctx))
	})
}

// RequireRole middleware checks for required role
func RequireRole(role string) func(http.Handler) http.Handler {
	return func(next http.Handler) http.Handler {
		return http.HandlerFunc(func(w http.ResponseWriter, r *http.Request) {
			claims := r.Context().Value(principalKey).(*Claims)

			hasRole := false
			for _, r := range claims.Roles {
				if r == role {
					hasRole = true
					break
				}
			}

			if !hasRole {
				http.Error(w, `{"error":"Forbidden: insufficient role"}`, http.StatusForbidden)
				return
			}

			next.ServeHTTP(w, r)
		})
	}
}

// Handlers

func loginHandler(w http.ResponseWriter, r *http.Request) {
	if r.Method != http.MethodPost {
		http.Error(w, `{"error":"Method not allowed"}`, http.StatusMethodNotAllowed)
		return
	}

	var req struct {
		Username string `json:"username"`
		Password string `json:"password"`
	}

	if err := json.NewDecoder(r.Body).Decode(&req); err != nil {
		http.Error(w, `{"error":"Invalid JSON"}`, http.StatusBadRequest)
		return
	}

	// Validate credentials
	userData, ok := users[req.Username]
	if !ok || userData.Password != req.Password {
		// Don't reveal whether username exists
		http.Error(w, `{"error":"Invalid credentials"}`, http.StatusUnauthorized)
		return
	}

	// Generate token
	token, err := generateToken(userData.User)
	if err != nil {
		log.Printf("Failed to generate token: %v", err)
		http.Error(w, `{"error":"Internal error"}`, http.StatusInternalServerError)
		return
	}

	w.Header().Set("Content-Type", "application/json")
	json.NewEncoder(w).Encode(map[string]interface{}{
		"token":      token,
		"expires_in": int(tokenExpiry.Seconds()),
		"user": map[string]interface{}{
			"id":       userData.User.ID,
			"username": userData.User.Username,
			"roles":    userData.User.Roles,
		},
	})
}

func meHandler(w http.ResponseWriter, r *http.Request) {
	claims := r.Context().Value(principalKey).(*Claims)

	w.Header().Set("Content-Type", "application/json")
	json.NewEncoder(w).Encode(map[string]interface{}{
		"user_id": claims.Subject,
		"roles":   claims.Roles,
		"issuer":  claims.Issuer,
		"issued":  claims.IssuedAt.Time,
		"expires": claims.ExpiresAt.Time,
	})
}

func adminHandler(w http.ResponseWriter, r *http.Request) {
	claims := r.Context().Value(principalKey).(*Claims)

	w.Header().Set("Content-Type", "application/json")
	json.NewEncoder(w).Encode(map[string]interface{}{
		"message": "Welcome to the admin area!",
		"user_id": claims.Subject,
	})
}

func publicHandler(w http.ResponseWriter, r *http.Request) {
	w.Header().Set("Content-Type", "application/json")
	json.NewEncoder(w).Encode(map[string]string{
		"message": "This is a public endpoint",
	})
}

import "context"

func main() {
	mux := http.NewServeMux()

	// Public endpoints
	mux.HandleFunc("/public", publicHandler)
	mux.HandleFunc("/login", loginHandler)

	// Protected endpoints
	mux.Handle("/me", AuthMiddleware(http.HandlerFunc(meHandler)))
	mux.Handle("/admin", AuthMiddleware(RequireRole("admin")(http.HandlerFunc(adminHandler))))

	fmt.Println("Example 1: JWT Authentication")
	fmt.Println("=============================")
	fmt.Println()
	fmt.Println("Starting server on http://localhost:8080")
	fmt.Println()
	fmt.Println("Available endpoints:")
	fmt.Println("  POST /login  - Login and get JWT token")
	fmt.Println("  GET  /public - Public endpoint (no auth)")
	fmt.Println("  GET  /me     - Get current user (requires auth)")
	fmt.Println("  GET  /admin  - Admin only (requires admin role)")
	fmt.Println()
	fmt.Println("Test users:")
	fmt.Println("  alice:password123 (admin)")
	fmt.Println("  bob:password456 (user)")
	fmt.Println()
	fmt.Println("Test commands:")
	fmt.Println("  # Login as alice")
	fmt.Println(`  TOKEN=$(curl -s -X POST http://localhost:8080/login -d '{"username":"alice","password":"password123"}' | jq -r .token)`)
	fmt.Println()
	fmt.Println("  # Access protected endpoint")
	fmt.Println(`  curl -H "Authorization: Bearer $TOKEN" http://localhost:8080/me`)
	fmt.Println()
	fmt.Println("  # Access admin endpoint")
	fmt.Println(`  curl -H "Authorization: Bearer $TOKEN" http://localhost:8080/admin`)
	fmt.Println()

	log.Fatal(http.ListenAndServe(":8080", mux))
}
