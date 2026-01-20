package tests

import (
	"context"
	"net/http"
	"net/http/httptest"
	"testing"
	"time"

	"github.com/labs-skills/hybrid-authentication/pkg/auth"
	"github.com/labs-skills/hybrid-authentication/pkg/middleware"
	"github.com/stretchr/testify/assert"
	"github.com/stretchr/testify/require"
)

func TestJWTService_GenerateAndValidate(t *testing.T) {
	config := auth.JWTConfig{
		Secret:       []byte("test-secret"),
		Issuer:       "test-issuer",
		AccessExpiry: 15 * time.Minute,
	}
	svc := auth.NewJWTService(config)

	// Generate token
	token, err := svc.GenerateToken("user-123", []string{"admin", "user"}, 15*time.Minute)
	require.NoError(t, err)
	assert.NotEmpty(t, token)

	// Validate token
	claims, err := svc.ValidateToken(token)
	require.NoError(t, err)
	assert.Equal(t, "user-123", claims.Subject)
	assert.Equal(t, []string{"admin", "user"}, claims.Roles)
	assert.Equal(t, "test-issuer", claims.Issuer)
}

func TestJWTService_ExpiredToken(t *testing.T) {
	config := auth.JWTConfig{
		Secret: []byte("test-secret"),
		Issuer: "test-issuer",
	}
	svc := auth.NewJWTService(config)

	// Generate expired token
	token, err := svc.GenerateToken("user-123", []string{"user"}, -1*time.Hour)
	require.NoError(t, err)

	// Validation should fail
	_, err = svc.ValidateToken(token)
	assert.ErrorIs(t, err, auth.ErrTokenExpired)
}

func TestJWTService_InvalidToken(t *testing.T) {
	config := auth.JWTConfig{
		Secret: []byte("test-secret"),
	}
	svc := auth.NewJWTService(config)

	tests := []struct {
		name  string
		token string
	}{
		{"empty token", ""},
		{"garbage token", "not-a-valid-token"},
		{"malformed jwt", "abc.def.ghi"},
	}

	for _, tt := range tests {
		t.Run(tt.name, func(t *testing.T) {
			_, err := svc.ValidateToken(tt.token)
			assert.Error(t, err)
		})
	}
}

func TestJWTService_WrongSecret(t *testing.T) {
	config1 := auth.JWTConfig{Secret: []byte("secret-1")}
	config2 := auth.JWTConfig{Secret: []byte("secret-2")}

	svc1 := auth.NewJWTService(config1)
	svc2 := auth.NewJWTService(config2)

	// Generate with secret-1
	token, err := svc1.GenerateToken("user-123", nil, 15*time.Minute)
	require.NoError(t, err)

	// Validate with secret-2 should fail
	_, err = svc2.ValidateToken(token)
	assert.Error(t, err)
}

func TestPrincipal_HasRole(t *testing.T) {
	principal := &auth.Principal{
		ID:    "user-1",
		Roles: []string{"admin", "user"},
	}

	assert.True(t, principal.HasRole("admin"))
	assert.True(t, principal.HasRole("user"))
	assert.False(t, principal.HasRole("superuser"))
}

func TestPrincipal_HasAnyRole(t *testing.T) {
	principal := &auth.Principal{
		ID:    "user-1",
		Roles: []string{"editor"},
	}

	assert.True(t, principal.HasAnyRole("admin", "editor", "viewer"))
	assert.False(t, principal.HasAnyRole("admin", "superuser"))
}

func TestPrincipal_HasPermission(t *testing.T) {
	principal := &auth.Principal{
		ID:          "user-1",
		Permissions: []string{"read", "write", "*"},
	}

	assert.True(t, principal.HasPermission("read"))
	assert.True(t, principal.HasPermission("write"))
	assert.True(t, principal.HasPermission("delete")) // * grants all
	assert.True(t, principal.HasPermission("anything"))
}

func TestContextPropagation(t *testing.T) {
	principal := &auth.Principal{
		ID:    "user-123",
		Type:  auth.PrincipalTypeUser,
		Roles: []string{"user"},
	}

	// Add to context
	ctx := auth.WithPrincipal(context.Background(), principal)

	// Retrieve from context
	retrieved, ok := auth.GetPrincipal(ctx)
	assert.True(t, ok)
	assert.Equal(t, principal.ID, retrieved.ID)
	assert.Equal(t, principal.Type, retrieved.Type)
}

func TestContextPropagation_NotPresent(t *testing.T) {
	ctx := context.Background()

	retrieved, ok := auth.GetPrincipal(ctx)
	assert.False(t, ok)
	assert.Nil(t, retrieved)
}

func TestAPIKeyGeneration(t *testing.T) {
	key1, err := auth.GenerateAPIKey()
	require.NoError(t, err)
	assert.NotEmpty(t, key1)

	key2, err := auth.GenerateAPIKey()
	require.NoError(t, err)
	assert.NotEmpty(t, key2)

	// Keys should be unique
	assert.NotEqual(t, key1, key2)
}

func TestAPIKeyHash(t *testing.T) {
	key := "test-api-key-12345"

	// Hash the key
	hash, err := auth.HashAPIKey(key)
	require.NoError(t, err)
	assert.NotEmpty(t, hash)

	// Validate correct key
	assert.True(t, auth.ValidateAPIKeyHash(key, hash))

	// Validate incorrect key
	assert.False(t, auth.ValidateAPIKeyHash("wrong-key", hash))
}

func TestInMemoryAPIKeyStore(t *testing.T) {
	store := auth.NewInMemoryAPIKeyStore()

	// Generate and store a key
	rawKey, _ := auth.GenerateAPIKey()
	hash, _ := auth.HashAPIKey(rawKey)

	apiKey := &auth.APIKey{
		ID:          "key-1",
		KeyHash:     hash,
		ServiceName: "test-service",
		Permissions: []string{"read", "write"},
		CreatedAt:   time.Now(),
	}

	err := store.Store(apiKey)
	require.NoError(t, err)

	// Find by key
	found, err := store.FindByKey(rawKey)
	require.NoError(t, err)
	assert.Equal(t, "test-service", found.ServiceName)
	assert.Equal(t, []string{"read", "write"}, found.Permissions)

	// Not found for wrong key
	_, err = store.FindByKey("wrong-key")
	assert.Error(t, err)

	// Delete
	err = store.Delete("key-1")
	require.NoError(t, err)

	// Should not be found after delete
	_, err = store.FindByKey(rawKey)
	assert.Error(t, err)
}

func TestJWTAuthenticator(t *testing.T) {
	config := auth.JWTConfig{
		Secret:       []byte("test-secret"),
		Issuer:       "test",
		AccessExpiry: 15 * time.Minute,
	}
	jwtSvc := auth.NewJWTService(config)
	authenticator := middleware.NewJWTAuthenticator(jwtSvc)

	// Generate token
	token, _ := jwtSvc.GenerateToken("user-123", []string{"admin"}, 15*time.Minute)

	t.Run("valid token", func(t *testing.T) {
		req := httptest.NewRequest(http.MethodGet, "/", nil)
		req.Header.Set("Authorization", "Bearer "+token)

		principal, err := authenticator.Authenticate(req)
		require.NoError(t, err)
		assert.Equal(t, "user-123", principal.ID)
		assert.Equal(t, auth.PrincipalTypeUser, principal.Type)
		assert.Equal(t, []string{"admin"}, principal.Roles)
	})

	t.Run("missing header", func(t *testing.T) {
		req := httptest.NewRequest(http.MethodGet, "/", nil)

		_, err := authenticator.Authenticate(req)
		assert.ErrorIs(t, err, auth.ErrNoCredentials)
	})

	t.Run("invalid format", func(t *testing.T) {
		req := httptest.NewRequest(http.MethodGet, "/", nil)
		req.Header.Set("Authorization", "Basic abc123")

		_, err := authenticator.Authenticate(req)
		assert.Error(t, err)
	})

	t.Run("invalid token", func(t *testing.T) {
		req := httptest.NewRequest(http.MethodGet, "/", nil)
		req.Header.Set("Authorization", "Bearer invalid-token")

		_, err := authenticator.Authenticate(req)
		assert.Error(t, err)
	})
}

func TestChainAuthenticator(t *testing.T) {
	// Setup JWT authenticator
	jwtConfig := auth.JWTConfig{Secret: []byte("jwt-secret")}
	jwtSvc := auth.NewJWTService(jwtConfig)
	jwtAuth := middleware.NewJWTAuthenticator(jwtSvc)

	// Setup API key authenticator
	apiStore := auth.NewInMemoryAPIKeyStore()
	rawKey, _ := auth.GenerateAPIKey()
	hash, _ := auth.HashAPIKey(rawKey)
	apiStore.Store(&auth.APIKey{
		ID:          "api-1",
		KeyHash:     hash,
		ServiceName: "test-svc",
		Permissions: []string{"read"},
	})
	apiAuth := middleware.NewAPIKeyAuthenticator(apiStore)

	// Create chain
	chain := middleware.NewChainAuthenticator(jwtAuth, apiAuth)

	t.Run("jwt auth succeeds", func(t *testing.T) {
		token, _ := jwtSvc.GenerateToken("user-1", []string{"user"}, 15*time.Minute)
		req := httptest.NewRequest(http.MethodGet, "/", nil)
		req.Header.Set("Authorization", "Bearer "+token)

		principal, err := chain.Authenticate(req)
		require.NoError(t, err)
		assert.Equal(t, "user-1", principal.ID)
		assert.Equal(t, auth.PrincipalTypeUser, principal.Type)
	})

	t.Run("api key auth succeeds when jwt fails", func(t *testing.T) {
		req := httptest.NewRequest(http.MethodGet, "/", nil)
		req.Header.Set("X-API-Key", rawKey)

		principal, err := chain.Authenticate(req)
		require.NoError(t, err)
		assert.Equal(t, "api-1", principal.ID)
		assert.Equal(t, auth.PrincipalTypeService, principal.Type)
	})

	t.Run("both fail", func(t *testing.T) {
		req := httptest.NewRequest(http.MethodGet, "/", nil)

		_, err := chain.Authenticate(req)
		assert.Error(t, err)
	})
}

func TestAuthMiddleware(t *testing.T) {
	jwtConfig := auth.JWTConfig{Secret: []byte("test-secret")}
	jwtSvc := auth.NewJWTService(jwtConfig)
	authenticator := middleware.NewJWTAuthenticator(jwtSvc)

	handler := http.HandlerFunc(func(w http.ResponseWriter, r *http.Request) {
		principal, ok := auth.GetPrincipal(r.Context())
		if !ok {
			w.WriteHeader(http.StatusInternalServerError)
			return
		}
		w.Write([]byte(principal.ID))
	})

	wrapped := middleware.AuthMiddleware(authenticator)(handler)

	t.Run("authenticated request", func(t *testing.T) {
		token, _ := jwtSvc.GenerateToken("user-123", nil, 15*time.Minute)
		req := httptest.NewRequest(http.MethodGet, "/", nil)
		req.Header.Set("Authorization", "Bearer "+token)
		w := httptest.NewRecorder()

		wrapped.ServeHTTP(w, req)

		assert.Equal(t, http.StatusOK, w.Code)
		assert.Equal(t, "user-123", w.Body.String())
	})

	t.Run("unauthenticated request", func(t *testing.T) {
		req := httptest.NewRequest(http.MethodGet, "/", nil)
		w := httptest.NewRecorder()

		wrapped.ServeHTTP(w, req)

		assert.Equal(t, http.StatusUnauthorized, w.Code)
	})
}

func TestRequireRole(t *testing.T) {
	handler := http.HandlerFunc(func(w http.ResponseWriter, r *http.Request) {
		w.Write([]byte("OK"))
	})

	wrapped := middleware.RequireRole("admin")(handler)

	t.Run("has required role", func(t *testing.T) {
		principal := &auth.Principal{ID: "user-1", Roles: []string{"admin", "user"}}
		ctx := auth.WithPrincipal(context.Background(), principal)
		req := httptest.NewRequest(http.MethodGet, "/", nil).WithContext(ctx)
		w := httptest.NewRecorder()

		wrapped.ServeHTTP(w, req)

		assert.Equal(t, http.StatusOK, w.Code)
	})

	t.Run("missing required role", func(t *testing.T) {
		principal := &auth.Principal{ID: "user-1", Roles: []string{"user"}}
		ctx := auth.WithPrincipal(context.Background(), principal)
		req := httptest.NewRequest(http.MethodGet, "/", nil).WithContext(ctx)
		w := httptest.NewRecorder()

		wrapped.ServeHTTP(w, req)

		assert.Equal(t, http.StatusForbidden, w.Code)
	})

	t.Run("no principal in context", func(t *testing.T) {
		req := httptest.NewRequest(http.MethodGet, "/", nil)
		w := httptest.NewRecorder()

		wrapped.ServeHTTP(w, req)

		assert.Equal(t, http.StatusUnauthorized, w.Code)
	})
}

func TestRequirePermission(t *testing.T) {
	handler := http.HandlerFunc(func(w http.ResponseWriter, r *http.Request) {
		w.Write([]byte("OK"))
	})

	wrapped := middleware.RequirePermission("articles:write")(handler)

	t.Run("has required permission", func(t *testing.T) {
		principal := &auth.Principal{ID: "user-1", Permissions: []string{"articles:write"}}
		ctx := auth.WithPrincipal(context.Background(), principal)
		req := httptest.NewRequest(http.MethodGet, "/", nil).WithContext(ctx)
		w := httptest.NewRecorder()

		wrapped.ServeHTTP(w, req)

		assert.Equal(t, http.StatusOK, w.Code)
	})

	t.Run("has wildcard permission", func(t *testing.T) {
		principal := &auth.Principal{ID: "admin-1", Permissions: []string{"*"}}
		ctx := auth.WithPrincipal(context.Background(), principal)
		req := httptest.NewRequest(http.MethodGet, "/", nil).WithContext(ctx)
		w := httptest.NewRecorder()

		wrapped.ServeHTTP(w, req)

		assert.Equal(t, http.StatusOK, w.Code)
	})

	t.Run("missing permission", func(t *testing.T) {
		principal := &auth.Principal{ID: "user-1", Permissions: []string{"articles:read"}}
		ctx := auth.WithPrincipal(context.Background(), principal)
		req := httptest.NewRequest(http.MethodGet, "/", nil).WithContext(ctx)
		w := httptest.NewRecorder()

		wrapped.ServeHTTP(w, req)

		assert.Equal(t, http.StatusForbidden, w.Code)
	})
}
