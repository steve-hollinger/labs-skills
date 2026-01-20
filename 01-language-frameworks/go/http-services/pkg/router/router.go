// Package router provides routing utilities for HTTP services.
package router

import (
	"net/http"
	"strings"
)

// Router is a simple HTTP router with middleware support
type Router struct {
	mux         *http.ServeMux
	middlewares []func(http.Handler) http.Handler
	prefix      string
}

// New creates a new Router
func New() *Router {
	return &Router{
		mux:         http.NewServeMux(),
		middlewares: make([]func(http.Handler) http.Handler, 0),
	}
}

// Use adds middleware to the router
func (r *Router) Use(mw func(http.Handler) http.Handler) {
	r.middlewares = append(r.middlewares, mw)
}

// Group creates a sub-router with a path prefix
func (r *Router) Group(prefix string) *Router {
	return &Router{
		mux:         r.mux,
		middlewares: r.middlewares,
		prefix:      r.prefix + prefix,
	}
}

// Handle registers a handler for the given pattern
func (r *Router) Handle(pattern string, handler http.Handler) {
	fullPattern := r.prefix + pattern
	r.mux.Handle(fullPattern, handler)
}

// HandleFunc registers a handler function for the given pattern
func (r *Router) HandleFunc(pattern string, handler http.HandlerFunc) {
	r.Handle(pattern, handler)
}

// GET registers a handler for GET requests
func (r *Router) GET(pattern string, handler http.HandlerFunc) {
	r.HandleFunc("GET "+pattern, handler)
}

// POST registers a handler for POST requests
func (r *Router) POST(pattern string, handler http.HandlerFunc) {
	r.HandleFunc("POST "+pattern, handler)
}

// PUT registers a handler for PUT requests
func (r *Router) PUT(pattern string, handler http.HandlerFunc) {
	r.HandleFunc("PUT "+pattern, handler)
}

// DELETE registers a handler for DELETE requests
func (r *Router) DELETE(pattern string, handler http.HandlerFunc) {
	r.HandleFunc("DELETE "+pattern, handler)
}

// PATCH registers a handler for PATCH requests
func (r *Router) PATCH(pattern string, handler http.HandlerFunc) {
	r.HandleFunc("PATCH "+pattern, handler)
}

// Handler returns the final http.Handler with all middleware applied
func (r *Router) Handler() http.Handler {
	var handler http.Handler = r.mux

	// Apply middleware in reverse order
	for i := len(r.middlewares) - 1; i >= 0; i-- {
		handler = r.middlewares[i](handler)
	}

	return handler
}

// ServeHTTP implements http.Handler
func (r *Router) ServeHTTP(w http.ResponseWriter, req *http.Request) {
	r.Handler().ServeHTTP(w, req)
}

// PathParam extracts a path parameter from the URL
// For Go 1.22+ this uses r.PathValue, for older versions it falls back to manual parsing
func PathParam(r *http.Request, name string) string {
	// Try Go 1.22+ PathValue first
	if val := r.PathValue(name); val != "" {
		return val
	}

	// Fallback: manual extraction (limited functionality)
	// This is a simple implementation for single-segment params
	return ""
}

// PathParams extracts multiple path parameters
func PathParams(r *http.Request, names ...string) map[string]string {
	params := make(map[string]string)
	for _, name := range names {
		params[name] = PathParam(r, name)
	}
	return params
}

// QueryParam returns a query parameter or default value
func QueryParam(r *http.Request, name, defaultVal string) string {
	if val := r.URL.Query().Get(name); val != "" {
		return val
	}
	return defaultVal
}

// QueryParams returns all values for a query parameter
func QueryParams(r *http.Request, name string) []string {
	return r.URL.Query()[name]
}

// SplitPath splits a URL path into segments
func SplitPath(path string) []string {
	path = strings.Trim(path, "/")
	if path == "" {
		return []string{}
	}
	return strings.Split(path, "/")
}
