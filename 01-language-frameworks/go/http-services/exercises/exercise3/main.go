// Exercise 3: Rate Limiting Middleware
//
// Implement a rate limiting middleware using the token bucket algorithm.
// This middleware should limit requests per IP address.
//
// Requirements:
// 1. Create a RateLimiter middleware that:
//    - Allows N requests per minute per IP address
//    - Returns 429 Too Many Requests when limit exceeded
//    - Includes "Retry-After" header with seconds until reset
//
// 2. Configuration:
//    - requests_per_minute: configurable (default: 60)
//    - burst: allow small bursts above limit (default: 10)
//
// 3. Response when rate limited:
//    {
//      "error": "Rate limit exceeded",
//      "retry_after": 30
//    }
//
// 4. Track rate limits per IP using:
//    - sync.Map for thread-safe IP tracking
//    - Token bucket or sliding window algorithm
//
// Bonus:
// - Add X-RateLimit-Remaining header
// - Add X-RateLimit-Reset header
// - Clean up old entries periodically
//
// Hints:
// - Get client IP from r.RemoteAddr (strip port with net.SplitHostPort)
// - Use time.Now().Unix() for tracking windows
// - Consider using sync/atomic for counters

package main

import (
	"fmt"
	"net/http"
)

// RateLimiterConfig holds rate limiter settings
type RateLimiterConfig struct {
	RequestsPerMinute int
	BurstSize         int
}

// DefaultConfig returns sensible defaults
func DefaultConfig() RateLimiterConfig {
	return RateLimiterConfig{
		RequestsPerMinute: 60,
		BurstSize:         10,
	}
}

// RateLimiter tracks request counts per IP
type RateLimiter struct {
	config RateLimiterConfig
	// TODO: Add fields for tracking requests per IP
	// Hint: Use sync.Map with IP as key
}

// NewRateLimiter creates a new rate limiter
func NewRateLimiter(config RateLimiterConfig) *RateLimiter {
	// TODO: Initialize the rate limiter
	return &RateLimiter{
		config: config,
	}
}

// Allow checks if a request from the given IP is allowed
func (rl *RateLimiter) Allow(ip string) (bool, int) {
	// TODO: Implement rate limiting logic
	// Returns: (allowed bool, retryAfterSeconds int)
	// 1. Get or create bucket for IP
	// 2. Check if request is allowed
	// 3. Return retry-after time if not allowed
	return true, 0
}

// Middleware returns the rate limiting middleware
func (rl *RateLimiter) Middleware(next http.Handler) http.Handler {
	return http.HandlerFunc(func(w http.ResponseWriter, r *http.Request) {
		// TODO: Implement middleware
		// 1. Extract client IP from r.RemoteAddr
		// 2. Call rl.Allow(ip)
		// 3. If not allowed, return 429 with JSON error
		// 4. If allowed, call next.ServeHTTP(w, r)

		next.ServeHTTP(w, r)
	})
}

// Example handler to test the middleware
func helloHandler(w http.ResponseWriter, r *http.Request) {
	w.Header().Set("Content-Type", "application/json")
	w.Write([]byte(`{"message": "Hello, World!"}`))
}

func main() {
	limiter := NewRateLimiter(RateLimiterConfig{
		RequestsPerMinute: 10, // Low limit for testing
		BurstSize:         2,
	})

	handler := limiter.Middleware(http.HandlerFunc(helloHandler))

	http.Handle("/", handler)

	fmt.Println("Exercise 3: Rate Limiting Middleware")
	fmt.Println("Starting server on http://localhost:8080")
	fmt.Println()
	fmt.Println("Rate limit: 10 requests per minute")
	fmt.Println()
	fmt.Println("Test with rapid requests:")
	fmt.Println("  for i in {1..15}; do curl -w '\\n' http://localhost:8080/; done")
	fmt.Println()
	fmt.Println("You should see 429 errors after the limit is exceeded")

	http.ListenAndServe(":8080", nil)
}
