// Package handlers provides reusable HTTP handler patterns.
package handlers

import (
	"encoding/json"
	"net/http"
)

// Response helpers

// WriteJSON writes a JSON response with the given status code
func WriteJSON(w http.ResponseWriter, status int, data interface{}) error {
	w.Header().Set("Content-Type", "application/json")
	w.WriteHeader(status)
	return json.NewEncoder(w).Encode(data)
}

// ErrorResponse represents a standard API error response
type ErrorResponse struct {
	Error   string            `json:"error"`
	Code    string            `json:"code,omitempty"`
	Details map[string]string `json:"details,omitempty"`
}

// WriteError writes a JSON error response
func WriteError(w http.ResponseWriter, status int, message string) {
	w.Header().Set("Content-Type", "application/json")
	w.WriteHeader(status)
	json.NewEncoder(w).Encode(ErrorResponse{Error: message})
}

// WriteErrorWithCode writes a JSON error response with an error code
func WriteErrorWithCode(w http.ResponseWriter, status int, message, code string) {
	w.Header().Set("Content-Type", "application/json")
	w.WriteHeader(status)
	json.NewEncoder(w).Encode(ErrorResponse{Error: message, Code: code})
}

// DecodeJSON decodes a JSON request body into the given value
func DecodeJSON(r *http.Request, v interface{}) error {
	decoder := json.NewDecoder(r.Body)
	decoder.DisallowUnknownFields()
	return decoder.Decode(v)
}

// MethodHandler routes requests to handlers based on HTTP method
type MethodHandler struct {
	Get    http.HandlerFunc
	Post   http.HandlerFunc
	Put    http.HandlerFunc
	Delete http.HandlerFunc
	Patch  http.HandlerFunc
}

// ServeHTTP implements http.Handler
func (m *MethodHandler) ServeHTTP(w http.ResponseWriter, r *http.Request) {
	var handler http.HandlerFunc

	switch r.Method {
	case http.MethodGet:
		handler = m.Get
	case http.MethodPost:
		handler = m.Post
	case http.MethodPut:
		handler = m.Put
	case http.MethodDelete:
		handler = m.Delete
	case http.MethodPatch:
		handler = m.Patch
	}

	if handler == nil {
		WriteError(w, http.StatusMethodNotAllowed, "Method not allowed")
		return
	}

	handler(w, r)
}
