package tests

import (
	"bytes"
	"encoding/json"
	"net/http"
	"net/http/httptest"
	"testing"

	"github.com/labs-skills/http-services/pkg/handlers"
	"github.com/labs-skills/http-services/pkg/middleware"
	"github.com/stretchr/testify/assert"
	"github.com/stretchr/testify/require"
)

func TestWriteJSON(t *testing.T) {
	tests := []struct {
		name       string
		status     int
		data       interface{}
		wantStatus int
		wantBody   string
	}{
		{
			name:       "success response",
			status:     http.StatusOK,
			data:       map[string]string{"message": "hello"},
			wantStatus: http.StatusOK,
			wantBody:   `{"message":"hello"}`,
		},
		{
			name:       "created response",
			status:     http.StatusCreated,
			data:       map[string]int{"id": 123},
			wantStatus: http.StatusCreated,
			wantBody:   `{"id":123}`,
		},
	}

	for _, tt := range tests {
		t.Run(tt.name, func(t *testing.T) {
			w := httptest.NewRecorder()
			err := handlers.WriteJSON(w, tt.status, tt.data)
			require.NoError(t, err)

			assert.Equal(t, tt.wantStatus, w.Code)
			assert.Equal(t, "application/json", w.Header().Get("Content-Type"))
			assert.JSONEq(t, tt.wantBody, w.Body.String())
		})
	}
}

func TestWriteError(t *testing.T) {
	w := httptest.NewRecorder()
	handlers.WriteError(w, http.StatusBadRequest, "invalid input")

	assert.Equal(t, http.StatusBadRequest, w.Code)
	assert.Equal(t, "application/json", w.Header().Get("Content-Type"))

	var resp handlers.ErrorResponse
	err := json.Unmarshal(w.Body.Bytes(), &resp)
	require.NoError(t, err)
	assert.Equal(t, "invalid input", resp.Error)
}

func TestDecodeJSON(t *testing.T) {
	type testRequest struct {
		Name  string `json:"name"`
		Value int    `json:"value"`
	}

	tests := []struct {
		name    string
		body    string
		wantErr bool
		want    testRequest
	}{
		{
			name:    "valid JSON",
			body:    `{"name":"test","value":42}`,
			wantErr: false,
			want:    testRequest{Name: "test", Value: 42},
		},
		{
			name:    "invalid JSON",
			body:    `{"name": invalid}`,
			wantErr: true,
		},
		{
			name:    "unknown field",
			body:    `{"name":"test","unknown":"field"}`,
			wantErr: true, // DisallowUnknownFields is set
		},
	}

	for _, tt := range tests {
		t.Run(tt.name, func(t *testing.T) {
			req := httptest.NewRequest(http.MethodPost, "/", bytes.NewBufferString(tt.body))
			var got testRequest
			err := handlers.DecodeJSON(req, &got)

			if tt.wantErr {
				assert.Error(t, err)
			} else {
				require.NoError(t, err)
				assert.Equal(t, tt.want, got)
			}
		})
	}
}

func TestMethodHandler(t *testing.T) {
	handler := &handlers.MethodHandler{
		Get: func(w http.ResponseWriter, r *http.Request) {
			w.WriteHeader(http.StatusOK)
			w.Write([]byte("GET"))
		},
		Post: func(w http.ResponseWriter, r *http.Request) {
			w.WriteHeader(http.StatusCreated)
			w.Write([]byte("POST"))
		},
	}

	tests := []struct {
		method     string
		wantStatus int
		wantBody   string
	}{
		{http.MethodGet, http.StatusOK, "GET"},
		{http.MethodPost, http.StatusCreated, "POST"},
		{http.MethodPut, http.StatusMethodNotAllowed, ""},
		{http.MethodDelete, http.StatusMethodNotAllowed, ""},
	}

	for _, tt := range tests {
		t.Run(tt.method, func(t *testing.T) {
			req := httptest.NewRequest(tt.method, "/", nil)
			w := httptest.NewRecorder()

			handler.ServeHTTP(w, req)

			assert.Equal(t, tt.wantStatus, w.Code)
			if tt.wantBody != "" {
				assert.Equal(t, tt.wantBody, w.Body.String())
			}
		})
	}
}

func TestLoggingMiddleware(t *testing.T) {
	handler := http.HandlerFunc(func(w http.ResponseWriter, r *http.Request) {
		w.WriteHeader(http.StatusOK)
		w.Write([]byte("OK"))
	})

	wrapped := middleware.Logging(handler)

	req := httptest.NewRequest(http.MethodGet, "/test", nil)
	w := httptest.NewRecorder()

	wrapped.ServeHTTP(w, req)

	assert.Equal(t, http.StatusOK, w.Code)
	assert.Equal(t, "OK", w.Body.String())
}

func TestRecoveryMiddleware(t *testing.T) {
	// Handler that panics
	handler := http.HandlerFunc(func(w http.ResponseWriter, r *http.Request) {
		panic("test panic")
	})

	wrapped := middleware.Recovery(handler)

	req := httptest.NewRequest(http.MethodGet, "/test", nil)
	w := httptest.NewRecorder()

	// Should not panic
	wrapped.ServeHTTP(w, req)

	assert.Equal(t, http.StatusInternalServerError, w.Code)
}

func TestRequestIDMiddleware(t *testing.T) {
	handler := http.HandlerFunc(func(w http.ResponseWriter, r *http.Request) {
		// Check that request ID is in context
		id := middleware.GetRequestID(r.Context())
		assert.NotEmpty(t, id)
		w.WriteHeader(http.StatusOK)
	})

	wrapped := middleware.RequestID(handler)

	req := httptest.NewRequest(http.MethodGet, "/test", nil)
	w := httptest.NewRecorder()

	wrapped.ServeHTTP(w, req)

	// Check that X-Request-ID header was set
	assert.NotEmpty(t, w.Header().Get("X-Request-ID"))
}

func TestCORSMiddleware(t *testing.T) {
	handler := http.HandlerFunc(func(w http.ResponseWriter, r *http.Request) {
		w.WriteHeader(http.StatusOK)
	})

	wrapped := middleware.CORS([]string{"http://example.com"})(handler)

	tests := []struct {
		name           string
		method         string
		origin         string
		wantCORSHeader bool
	}{
		{
			name:           "allowed origin",
			method:         http.MethodGet,
			origin:         "http://example.com",
			wantCORSHeader: true,
		},
		{
			name:           "disallowed origin",
			method:         http.MethodGet,
			origin:         "http://other.com",
			wantCORSHeader: false,
		},
		{
			name:           "preflight request",
			method:         http.MethodOptions,
			origin:         "http://example.com",
			wantCORSHeader: true,
		},
	}

	for _, tt := range tests {
		t.Run(tt.name, func(t *testing.T) {
			req := httptest.NewRequest(tt.method, "/test", nil)
			req.Header.Set("Origin", tt.origin)
			w := httptest.NewRecorder()

			wrapped.ServeHTTP(w, req)

			if tt.wantCORSHeader {
				assert.Equal(t, tt.origin, w.Header().Get("Access-Control-Allow-Origin"))
			} else {
				assert.Empty(t, w.Header().Get("Access-Control-Allow-Origin"))
			}
		})
	}
}

func TestMiddlewareChain(t *testing.T) {
	var order []string

	mw1 := func(next http.Handler) http.Handler {
		return http.HandlerFunc(func(w http.ResponseWriter, r *http.Request) {
			order = append(order, "mw1-before")
			next.ServeHTTP(w, r)
			order = append(order, "mw1-after")
		})
	}

	mw2 := func(next http.Handler) http.Handler {
		return http.HandlerFunc(func(w http.ResponseWriter, r *http.Request) {
			order = append(order, "mw2-before")
			next.ServeHTTP(w, r)
			order = append(order, "mw2-after")
		})
	}

	handler := http.HandlerFunc(func(w http.ResponseWriter, r *http.Request) {
		order = append(order, "handler")
	})

	wrapped := middleware.Chain(handler, mw1, mw2)

	req := httptest.NewRequest(http.MethodGet, "/", nil)
	w := httptest.NewRecorder()

	wrapped.ServeHTTP(w, req)

	// mw1 is first in the list, so it should execute first (outermost)
	expected := []string{"mw1-before", "mw2-before", "handler", "mw2-after", "mw1-after"}
	assert.Equal(t, expected, order)
}

func TestResponseWriter(t *testing.T) {
	t.Run("captures status code", func(t *testing.T) {
		w := httptest.NewRecorder()
		rw := middleware.NewResponseWriter(w)

		rw.WriteHeader(http.StatusCreated)
		assert.Equal(t, http.StatusCreated, rw.Status)
	})

	t.Run("default status is 200", func(t *testing.T) {
		w := httptest.NewRecorder()
		rw := middleware.NewResponseWriter(w)

		rw.Write([]byte("test"))
		assert.Equal(t, http.StatusOK, rw.Status)
	})

	t.Run("captures bytes written", func(t *testing.T) {
		w := httptest.NewRecorder()
		rw := middleware.NewResponseWriter(w)

		rw.Write([]byte("hello"))
		assert.Equal(t, 5, rw.BytesWrites)
	})
}

// Integration test example
func TestHealthEndpoint(t *testing.T) {
	mux := http.NewServeMux()
	mux.HandleFunc("/health", func(w http.ResponseWriter, r *http.Request) {
		if r.Method != http.MethodGet {
			handlers.WriteError(w, http.StatusMethodNotAllowed, "Method not allowed")
			return
		}
		handlers.WriteJSON(w, http.StatusOK, map[string]string{"status": "healthy"})
	})

	server := httptest.NewServer(mux)
	defer server.Close()

	t.Run("GET returns healthy", func(t *testing.T) {
		resp, err := http.Get(server.URL + "/health")
		require.NoError(t, err)
		defer resp.Body.Close()

		assert.Equal(t, http.StatusOK, resp.StatusCode)

		var body map[string]string
		err = json.NewDecoder(resp.Body).Decode(&body)
		require.NoError(t, err)
		assert.Equal(t, "healthy", body["status"])
	})

	t.Run("POST returns 405", func(t *testing.T) {
		resp, err := http.Post(server.URL+"/health", "application/json", nil)
		require.NoError(t, err)
		defer resp.Body.Close()

		assert.Equal(t, http.StatusMethodNotAllowed, resp.StatusCode)
	})
}
