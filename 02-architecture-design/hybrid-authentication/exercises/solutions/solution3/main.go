// Solution for Exercise 3: Complete RBAC Auth System with Audit Logging
//
// Production-ready auth with RBAC, sessions, and audit logging.

package main

import (
	"context"
	"encoding/json"
	"fmt"
	"log"
	"net/http"
	"strings"
	"sync"
	"time"

	"github.com/google/uuid"
)

// RBAC System

type Role struct {
	Name        string
	Permissions []string
}

type RBAC struct {
	mu    sync.RWMutex
	roles map[string]*Role
}

func NewRBAC() *RBAC {
	rbac := &RBAC{roles: make(map[string]*Role)}

	// Default roles
	rbac.DefineRole("admin", "*")
	rbac.DefineRole("editor", "articles:read", "articles:write", "articles:delete")
	rbac.DefineRole("viewer", "articles:read")

	return rbac
}

func (r *RBAC) DefineRole(name string, permissions ...string) {
	r.mu.Lock()
	defer r.mu.Unlock()
	r.roles[name] = &Role{Name: name, Permissions: permissions}
}

func (r *RBAC) HasPermission(roles []string, permission string) bool {
	r.mu.RLock()
	defer r.mu.RUnlock()

	for _, roleName := range roles {
		role, ok := r.roles[roleName]
		if !ok {
			continue
		}
		for _, perm := range role.Permissions {
			if perm == "*" || perm == permission {
				return true
			}
			// Wildcard match: "articles:*" matches "articles:read"
			if strings.HasSuffix(perm, ":*") {
				prefix := strings.TrimSuffix(perm, "*")
				if strings.HasPrefix(permission, prefix) {
					return true
				}
			}
		}
	}
	return false
}

// Audit Logging

type AuditEvent struct {
	Timestamp time.Time         `json:"timestamp"`
	EventType string            `json:"event_type"`
	UserID    string            `json:"user_id"`
	Action    string            `json:"action"`
	Outcome   string            `json:"outcome"`
	IPAddress string            `json:"ip_address"`
	Details   map[string]string `json:"details,omitempty"`
}

type AuditLogger struct {
	mu      sync.RWMutex
	events  []AuditEvent
	eventCh chan AuditEvent
}

func NewAuditLogger() *AuditLogger {
	logger := &AuditLogger{
		events:  make([]AuditEvent, 0),
		eventCh: make(chan AuditEvent, 100),
	}

	// Background goroutine for async logging
	go func() {
		for event := range logger.eventCh {
			logger.mu.Lock()
			logger.events = append(logger.events, event)
			// Keep last 1000 events
			if len(logger.events) > 1000 {
				logger.events = logger.events[len(logger.events)-1000:]
			}
			logger.mu.Unlock()
			log.Printf("[AUDIT] %s: %s - %s (%s)",
				event.EventType, event.UserID, event.Action, event.Outcome)
		}
	}()

	return logger
}

func (l *AuditLogger) Log(event AuditEvent) {
	event.Timestamp = time.Now()
	select {
	case l.eventCh <- event:
	default:
		log.Printf("Audit log buffer full, dropping event")
	}
}

func (l *AuditLogger) GetEvents(limit int) []AuditEvent {
	l.mu.RLock()
	defer l.mu.RUnlock()

	if limit > len(l.events) {
		limit = len(l.events)
	}
	result := make([]AuditEvent, limit)
	copy(result, l.events[len(l.events)-limit:])
	return result
}

func (l *AuditLogger) GetEventsForUser(userID string, limit int) []AuditEvent {
	l.mu.RLock()
	defer l.mu.RUnlock()

	var result []AuditEvent
	for i := len(l.events) - 1; i >= 0 && len(result) < limit; i-- {
		if l.events[i].UserID == userID {
			result = append(result, l.events[i])
		}
	}
	return result
}

// Session Management

type Session struct {
	ID        string    `json:"id"`
	UserID    string    `json:"user_id"`
	CreatedAt time.Time `json:"created_at"`
	ExpiresAt time.Time `json:"expires_at"`
	IPAddress string    `json:"ip_address"`
	UserAgent string    `json:"user_agent"`
}

type SessionManager struct {
	mu                 sync.RWMutex
	sessions           map[string]*Session
	userSessions       map[string][]string
	maxSessionsPerUser int
	sessionTTL         time.Duration
}

func NewSessionManager(maxSessions int) *SessionManager {
	return &SessionManager{
		sessions:           make(map[string]*Session),
		userSessions:       make(map[string][]string),
		maxSessionsPerUser: maxSessions,
		sessionTTL:         24 * time.Hour,
	}
}

func (m *SessionManager) Create(userID, ip, userAgent string) (*Session, error) {
	m.mu.Lock()
	defer m.mu.Unlock()

	// Check session limit
	userSessions := m.userSessions[userID]
	if len(userSessions) >= m.maxSessionsPerUser {
		// Revoke oldest session
		oldestID := userSessions[0]
		delete(m.sessions, oldestID)
		m.userSessions[userID] = userSessions[1:]
	}

	session := &Session{
		ID:        uuid.New().String(),
		UserID:    userID,
		CreatedAt: time.Now(),
		ExpiresAt: time.Now().Add(m.sessionTTL),
		IPAddress: ip,
		UserAgent: userAgent,
	}

	m.sessions[session.ID] = session
	m.userSessions[userID] = append(m.userSessions[userID], session.ID)

	return session, nil
}

func (m *SessionManager) Validate(sessionID string) (*Session, error) {
	m.mu.RLock()
	defer m.mu.RUnlock()

	session, ok := m.sessions[sessionID]
	if !ok {
		return nil, fmt.Errorf("session not found")
	}

	if session.ExpiresAt.Before(time.Now()) {
		return nil, fmt.Errorf("session expired")
	}

	return session, nil
}

func (m *SessionManager) Revoke(sessionID string) error {
	m.mu.Lock()
	defer m.mu.Unlock()

	session, ok := m.sessions[sessionID]
	if !ok {
		return fmt.Errorf("session not found")
	}

	delete(m.sessions, sessionID)

	// Remove from user sessions
	userSessions := m.userSessions[session.UserID]
	for i, id := range userSessions {
		if id == sessionID {
			m.userSessions[session.UserID] = append(userSessions[:i], userSessions[i+1:]...)
			break
		}
	}

	return nil
}

func (m *SessionManager) RevokeAllForUser(userID string) error {
	m.mu.Lock()
	defer m.mu.Unlock()

	for _, sessionID := range m.userSessions[userID] {
		delete(m.sessions, sessionID)
	}
	delete(m.userSessions, userID)

	return nil
}

func (m *SessionManager) GetUserSessions(userID string) []*Session {
	m.mu.RLock()
	defer m.mu.RUnlock()

	var sessions []*Session
	for _, sessionID := range m.userSessions[userID] {
		if session, ok := m.sessions[sessionID]; ok {
			sessions = append(sessions, session)
		}
	}
	return sessions
}

// Login Attempt Tracker

type LoginAttemptTracker struct {
	mu              sync.Mutex
	attempts        map[string][]time.Time
	maxAttempts     int
	lockoutDuration time.Duration
}

func NewLoginAttemptTracker(maxAttempts int, lockoutDuration time.Duration) *LoginAttemptTracker {
	return &LoginAttemptTracker{
		attempts:        make(map[string][]time.Time),
		maxAttempts:     maxAttempts,
		lockoutDuration: lockoutDuration,
	}
}

func (t *LoginAttemptTracker) RecordFailure(userID string) {
	t.mu.Lock()
	defer t.mu.Unlock()
	t.attempts[userID] = append(t.attempts[userID], time.Now())
}

func (t *LoginAttemptTracker) RecordSuccess(userID string) {
	t.mu.Lock()
	defer t.mu.Unlock()
	delete(t.attempts, userID)
}

func (t *LoginAttemptTracker) IsLocked(userID string) bool {
	t.mu.Lock()
	defer t.mu.Unlock()

	attempts := t.attempts[userID]
	if len(attempts) < t.maxAttempts {
		return false
	}

	// Check if within lockout window
	windowStart := time.Now().Add(-t.lockoutDuration)
	recentAttempts := 0
	for _, attempt := range attempts {
		if attempt.After(windowStart) {
			recentAttempts++
		}
	}

	return recentAttempts >= t.maxAttempts
}

// Global instances
var (
	rbac           = NewRBAC()
	auditLogger    = NewAuditLogger()
	sessionManager = NewSessionManager(5)
	loginTracker   = NewLoginAttemptTracker(3, 15*time.Minute)
)

// Mock users
var users = map[string]struct {
	Password string
	Roles    []string
}{
	"admin":  {"admin123", []string{"admin"}},
	"editor": {"editor123", []string{"editor"}},
	"viewer": {"viewer123", []string{"viewer"}},
}

// Context keys
type contextKey string

const sessionKey contextKey = "session"

// Middleware

func SessionMiddleware(next http.Handler) http.Handler {
	return http.HandlerFunc(func(w http.ResponseWriter, r *http.Request) {
		sessionID := r.Header.Get("X-Session-ID")
		if sessionID == "" {
			writeError(w, http.StatusUnauthorized, "Session required")
			return
		}

		session, err := sessionManager.Validate(sessionID)
		if err != nil {
			auditLogger.Log(AuditEvent{
				EventType: "auth_failure",
				UserID:    "unknown",
				Action:    r.URL.Path,
				Outcome:   "invalid_session",
				IPAddress: r.RemoteAddr,
			})
			writeError(w, http.StatusUnauthorized, "Invalid session")
			return
		}

		ctx := context.WithValue(r.Context(), sessionKey, session)
		next.ServeHTTP(w, r.WithContext(ctx))
	})
}

func RequirePermission(permission string) func(http.Handler) http.Handler {
	return func(next http.Handler) http.Handler {
		return http.HandlerFunc(func(w http.ResponseWriter, r *http.Request) {
			session := r.Context().Value(sessionKey).(*Session)
			user := users[session.UserID]

			if !rbac.HasPermission(user.Roles, permission) {
				auditLogger.Log(AuditEvent{
					EventType: "authz_failure",
					UserID:    session.UserID,
					Action:    r.URL.Path,
					Outcome:   "insufficient_permission",
					IPAddress: r.RemoteAddr,
					Details:   map[string]string{"required": permission},
				})
				writeError(w, http.StatusForbidden, "Insufficient permissions")
				return
			}

			next.ServeHTTP(w, r)
		})
	}
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
	json.NewDecoder(r.Body).Decode(&req)

	// Check lockout
	if loginTracker.IsLocked(req.Username) {
		auditLogger.Log(AuditEvent{
			EventType: "auth_failure",
			UserID:    req.Username,
			Action:    "login",
			Outcome:   "account_locked",
			IPAddress: r.RemoteAddr,
		})
		writeError(w, http.StatusTooManyRequests, "Account temporarily locked")
		return
	}

	// Validate credentials
	user, ok := users[req.Username]
	if !ok || user.Password != req.Password {
		loginTracker.RecordFailure(req.Username)
		auditLogger.Log(AuditEvent{
			EventType: "auth_failure",
			UserID:    req.Username,
			Action:    "login",
			Outcome:   "invalid_credentials",
			IPAddress: r.RemoteAddr,
		})
		writeError(w, http.StatusUnauthorized, "Invalid credentials")
		return
	}

	loginTracker.RecordSuccess(req.Username)

	// Create session
	session, _ := sessionManager.Create(req.Username, r.RemoteAddr, r.UserAgent())

	auditLogger.Log(AuditEvent{
		EventType: "auth_success",
		UserID:    req.Username,
		Action:    "login",
		Outcome:   "success",
		IPAddress: r.RemoteAddr,
	})

	writeJSON(w, map[string]interface{}{
		"session_id": session.ID,
		"expires_at": session.ExpiresAt,
		"roles":      user.Roles,
	})
}

func logoutHandler(w http.ResponseWriter, r *http.Request) {
	session := r.Context().Value(sessionKey).(*Session)

	sessionManager.Revoke(session.ID)

	auditLogger.Log(AuditEvent{
		EventType: "session_revoked",
		UserID:    session.UserID,
		Action:    "logout",
		Outcome:   "success",
		IPAddress: r.RemoteAddr,
	})

	writeJSON(w, map[string]string{"message": "Logged out"})
}

func logoutEverywhereHandler(w http.ResponseWriter, r *http.Request) {
	session := r.Context().Value(sessionKey).(*Session)

	sessionManager.RevokeAllForUser(session.UserID)

	auditLogger.Log(AuditEvent{
		EventType: "all_sessions_revoked",
		UserID:    session.UserID,
		Action:    "logout_everywhere",
		Outcome:   "success",
		IPAddress: r.RemoteAddr,
	})

	writeJSON(w, map[string]string{"message": "All sessions revoked"})
}

func sessionsHandler(w http.ResponseWriter, r *http.Request) {
	session := r.Context().Value(sessionKey).(*Session)
	sessions := sessionManager.GetUserSessions(session.UserID)

	writeJSON(w, map[string]interface{}{
		"sessions": sessions,
		"count":    len(sessions),
	})
}

func auditLogHandler(w http.ResponseWriter, r *http.Request) {
	events := auditLogger.GetEvents(50)
	writeJSON(w, map[string]interface{}{
		"events": events,
		"count":  len(events),
	})
}

func articlesHandler(w http.ResponseWriter, r *http.Request) {
	session := r.Context().Value(sessionKey).(*Session)

	writeJSON(w, map[string]interface{}{
		"articles":   []string{"Article 1", "Article 2", "Article 3"},
		"accessed_by": session.UserID,
	})
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
	mux := http.NewServeMux()

	mux.HandleFunc("/login", loginHandler)
	mux.Handle("/logout", SessionMiddleware(http.HandlerFunc(logoutHandler)))
	mux.Handle("/logout-everywhere", SessionMiddleware(http.HandlerFunc(logoutEverywhereHandler)))
	mux.Handle("/sessions", SessionMiddleware(http.HandlerFunc(sessionsHandler)))
	mux.Handle("/audit", SessionMiddleware(RequirePermission("*")(http.HandlerFunc(auditLogHandler))))
	mux.Handle("/articles", SessionMiddleware(RequirePermission("articles:read")(http.HandlerFunc(articlesHandler))))

	fmt.Println("Solution 3: Complete RBAC Auth System with Audit Logging")
	fmt.Println("=========================================================")
	fmt.Println()
	fmt.Println("Starting server on http://localhost:8080")
	fmt.Println()
	fmt.Println("Test users: admin:admin123, editor:editor123, viewer:viewer123")
	fmt.Println()
	fmt.Println("Test commands:")
	fmt.Println()
	fmt.Println("  # Login as viewer")
	fmt.Println(`  SESSION=$(curl -s -X POST http://localhost:8080/login -d '{"username":"viewer","password":"viewer123"}' | jq -r .session_id)`)
	fmt.Println()
	fmt.Println("  # Read articles (should work)")
	fmt.Println(`  curl -H "X-Session-ID: $SESSION" http://localhost:8080/articles`)
	fmt.Println()
	fmt.Println("  # Try audit log (should fail - admin only)")
	fmt.Println(`  curl -H "X-Session-ID: $SESSION" http://localhost:8080/audit`)
	fmt.Println()
	fmt.Println("  # Login as admin and view audit log")
	fmt.Println(`  ADMIN=$(curl -s -X POST http://localhost:8080/login -d '{"username":"admin","password":"admin123"}' | jq -r .session_id)`)
	fmt.Println(`  curl -H "X-Session-ID: $ADMIN" http://localhost:8080/audit | jq`)
	fmt.Println()
	fmt.Println("  # Test account lockout (3 failed attempts)")
	fmt.Println(`  for i in {1..4}; do curl -X POST http://localhost:8080/login -d '{"username":"viewer","password":"wrong"}'; done`)
	fmt.Println()

	log.Fatal(http.ListenAndServe(":8080", mux))
}
