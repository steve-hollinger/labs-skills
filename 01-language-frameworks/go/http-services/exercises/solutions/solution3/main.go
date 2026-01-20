// Solution for Exercise 3: Rate Limiting Middleware
//
// This solution implements a token bucket rate limiter with
// per-IP tracking and proper HTTP status codes.

package main

import (
	"encoding/json"
	"fmt"
	"net"
	"net/http"
	"sync"
	"time"
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

// bucket tracks requests for a single IP
type bucket struct {
	tokens     float64
	lastUpdate time.Time
	mu         sync.Mutex
}

// RateLimiter tracks request counts per IP using token bucket algorithm
type RateLimiter struct {
	config  RateLimiterConfig
	buckets sync.Map // map[string]*bucket
	rate    float64  // tokens per second
}

// NewRateLimiter creates a new rate limiter
func NewRateLimiter(config RateLimiterConfig) *RateLimiter {
	return &RateLimiter{
		config: config,
		rate:   float64(config.RequestsPerMinute) / 60.0, // tokens per second
	}
}

// getBucket gets or creates a bucket for the given IP
func (rl *RateLimiter) getBucket(ip string) *bucket {
	if b, ok := rl.buckets.Load(ip); ok {
		return b.(*bucket)
	}

	// Create new bucket with full tokens
	newBucket := &bucket{
		tokens:     float64(rl.config.BurstSize),
		lastUpdate: time.Now(),
	}

	// Use LoadOrStore to handle race condition
	actual, _ := rl.buckets.LoadOrStore(ip, newBucket)
	return actual.(*bucket)
}

// Allow checks if a request from the given IP is allowed
func (rl *RateLimiter) Allow(ip string) (allowed bool, remaining int, retryAfter int) {
	b := rl.getBucket(ip)
	b.mu.Lock()
	defer b.mu.Unlock()

	now := time.Now()
	elapsed := now.Sub(b.lastUpdate).Seconds()
	b.lastUpdate = now

	// Add tokens based on elapsed time
	b.tokens += elapsed * rl.rate
	if b.tokens > float64(rl.config.BurstSize) {
		b.tokens = float64(rl.config.BurstSize)
	}

	// Check if we have tokens available
	if b.tokens >= 1 {
		b.tokens--
		return true, int(b.tokens), 0
	}

	// Calculate retry after (time until 1 token is available)
	tokensNeeded := 1 - b.tokens
	secondsUntilToken := tokensNeeded / rl.rate

	return false, 0, int(secondsUntilToken) + 1
}

// Middleware returns the rate limiting middleware
func (rl *RateLimiter) Middleware(next http.Handler) http.Handler {
	return http.HandlerFunc(func(w http.ResponseWriter, r *http.Request) {
		// Extract client IP
		ip := getClientIP(r)

		allowed, remaining, retryAfter := rl.Allow(ip)

		// Add rate limit headers
		w.Header().Set("X-RateLimit-Limit", fmt.Sprintf("%d", rl.config.RequestsPerMinute))
		w.Header().Set("X-RateLimit-Remaining", fmt.Sprintf("%d", remaining))

		if !allowed {
			w.Header().Set("Retry-After", fmt.Sprintf("%d", retryAfter))
			w.Header().Set("Content-Type", "application/json")
			w.WriteHeader(http.StatusTooManyRequests)
			json.NewEncoder(w).Encode(map[string]interface{}{
				"error":       "Rate limit exceeded",
				"retry_after": retryAfter,
			})
			return
		}

		next.ServeHTTP(w, r)
	})
}

// getClientIP extracts the client IP from the request
func getClientIP(r *http.Request) string {
	// Check X-Forwarded-For header first (for proxied requests)
	if xff := r.Header.Get("X-Forwarded-For"); xff != "" {
		// Take the first IP in the chain
		if idx := len(xff); idx > 0 {
			return xff
		}
	}

	// Check X-Real-IP header
	if xri := r.Header.Get("X-Real-IP"); xri != "" {
		return xri
	}

	// Fall back to RemoteAddr
	ip, _, err := net.SplitHostPort(r.RemoteAddr)
	if err != nil {
		return r.RemoteAddr
	}
	return ip
}

// StartCleanup periodically removes old buckets to prevent memory leaks
func (rl *RateLimiter) StartCleanup(interval time.Duration) {
	go func() {
		ticker := time.NewTicker(interval)
		defer ticker.Stop()

		for range ticker.C {
			rl.cleanup()
		}
	}()
}

func (rl *RateLimiter) cleanup() {
	threshold := time.Now().Add(-5 * time.Minute)

	rl.buckets.Range(func(key, value interface{}) bool {
		b := value.(*bucket)
		b.mu.Lock()
		if b.lastUpdate.Before(threshold) {
			rl.buckets.Delete(key)
		}
		b.mu.Unlock()
		return true
	})
}

// Example handler to test the middleware
func helloHandler(w http.ResponseWriter, r *http.Request) {
	w.Header().Set("Content-Type", "application/json")
	json.NewEncoder(w).Encode(map[string]string{
		"message": "Hello, World!",
	})
}

func main() {
	limiter := NewRateLimiter(RateLimiterConfig{
		RequestsPerMinute: 10, // Low limit for testing
		BurstSize:         3,  // Allow small bursts
	})

	// Start cleanup goroutine
	limiter.StartCleanup(5 * time.Minute)

	handler := limiter.Middleware(http.HandlerFunc(helloHandler))

	http.Handle("/", handler)

	fmt.Println("Solution 3: Rate Limiting Middleware")
	fmt.Println("Starting server on http://localhost:8080")
	fmt.Println()
	fmt.Println("Rate limit: 10 requests per minute, burst: 3")
	fmt.Println()
	fmt.Println("Test with rapid requests:")
	fmt.Println("  for i in {1..15}; do")
	fmt.Println("    echo \"Request $i:\"")
	fmt.Println("    curl -s -w ' HTTP %{http_code}\\n' http://localhost:8080/")
	fmt.Println("    sleep 0.1")
	fmt.Println("  done")
	fmt.Println()
	fmt.Println("Check the X-RateLimit-* headers:")
	fmt.Println("  curl -i http://localhost:8080/")
	fmt.Println()

	if err := http.ListenAndServe(":8080", nil); err != nil {
		fmt.Printf("Server error: %v\n", err)
	}
}
