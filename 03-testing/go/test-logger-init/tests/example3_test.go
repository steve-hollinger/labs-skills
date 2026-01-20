package tests

import (
	"bytes"
	"context"
	"encoding/json"
	"io"
	"log/slog"
	"strings"
	"testing"

	"github.com/stretchr/testify/assert"
	"github.com/stretchr/testify/require"
)

// ============================================================================
// Example 3: Logger Configuration
// ============================================================================

// ============================================================================
// Discard Logger - Silence logs in tests
// ============================================================================

func NewDiscardLogger() *slog.Logger {
	return slog.New(slog.NewTextHandler(io.Discard, nil))
}

func TestExample3_DiscardLogger(t *testing.T) {
	logger := NewDiscardLogger()

	// These logs go nowhere - no output
	logger.Info("this is silenced")
	logger.Error("this error is silenced too")
	logger.Debug("debug silenced")

	// Test passes - logs don't clutter output
	assert.NotNil(t, logger)
}

// ============================================================================
// Capture Logger - Capture logs for assertions
// ============================================================================

type CaptureLogger struct {
	buf    bytes.Buffer
	Logger *slog.Logger
}

func NewCaptureLogger() *CaptureLogger {
	cl := &CaptureLogger{}
	cl.Logger = slog.New(slog.NewJSONHandler(&cl.buf, &slog.HandlerOptions{
		Level: slog.LevelDebug,
	}))
	return cl
}

func (cl *CaptureLogger) String() string {
	return cl.buf.String()
}

func (cl *CaptureLogger) Contains(substr string) bool {
	return strings.Contains(cl.buf.String(), substr)
}

func (cl *CaptureLogger) Lines() []string {
	s := strings.TrimSpace(cl.buf.String())
	if s == "" {
		return nil
	}
	return strings.Split(s, "\n")
}

func (cl *CaptureLogger) Clear() {
	cl.buf.Reset()
}

func (cl *CaptureLogger) GetEntries() []map[string]interface{} {
	var entries []map[string]interface{}
	for _, line := range cl.Lines() {
		var entry map[string]interface{}
		if err := json.Unmarshal([]byte(line), &entry); err == nil {
			entries = append(entries, entry)
		}
	}
	return entries
}

func TestExample3_CaptureLogger(t *testing.T) {
	cl := NewCaptureLogger()

	cl.Logger.Info("test message", "key", "value")
	cl.Logger.Error("error occurred", "code", 500)

	assert.True(t, cl.Contains("test message"))
	assert.True(t, cl.Contains("error occurred"))
	assert.True(t, cl.Contains("key"))
	assert.True(t, cl.Contains("value"))
	assert.True(t, cl.Contains("500"))

	entries := cl.GetEntries()
	assert.Len(t, entries, 2)
}

func TestExample3_CaptureLoggerAssertions(t *testing.T) {
	cl := NewCaptureLogger()

	// Simulate service logging
	cl.Logger.Info("processing started", "user_id", 123)
	cl.Logger.Debug("cache miss", "key", "user:123")
	cl.Logger.Info("processing completed", "duration_ms", 45)

	// Assert specific logs were written
	entries := cl.GetEntries()
	require.Len(t, entries, 3)

	// Check first entry
	assert.Equal(t, "processing started", entries[0]["msg"])

	// Check that debug was captured
	assert.True(t, cl.Contains("cache miss"))

	// Check last entry
	assert.Equal(t, "processing completed", entries[2]["msg"])
}

// ============================================================================
// Test Logger - Logs to t.Log()
// ============================================================================

type testLogHandler struct {
	t     *testing.T
	level slog.Level
	attrs []slog.Attr
}

func NewTestLogger(t *testing.T) *slog.Logger {
	return slog.New(&testLogHandler{t: t, level: slog.LevelDebug})
}

func NewTestLoggerWithLevel(t *testing.T, level slog.Level) *slog.Logger {
	return slog.New(&testLogHandler{t: t, level: level})
}

func (h *testLogHandler) Enabled(ctx context.Context, level slog.Level) bool {
	return level >= h.level
}

func (h *testLogHandler) Handle(ctx context.Context, r slog.Record) error {
	var attrs []string
	r.Attrs(func(a slog.Attr) bool {
		attrs = append(attrs, a.String())
		return true
	})

	if len(attrs) > 0 {
		h.t.Logf("[%s] %s %s", r.Level, r.Message, strings.Join(attrs, " "))
	} else {
		h.t.Logf("[%s] %s", r.Level, r.Message)
	}
	return nil
}

func (h *testLogHandler) WithAttrs(attrs []slog.Attr) slog.Handler {
	newAttrs := make([]slog.Attr, len(h.attrs)+len(attrs))
	copy(newAttrs, h.attrs)
	copy(newAttrs[len(h.attrs):], attrs)
	return &testLogHandler{t: h.t, level: h.level, attrs: newAttrs}
}

func (h *testLogHandler) WithGroup(name string) slog.Handler {
	return h
}

func TestExample3_TestLogger(t *testing.T) {
	logger := NewTestLogger(t)

	// These logs appear in verbose test output (-v flag)
	logger.Info("starting test operation")
	logger.Debug("detailed debug info", "step", 1)
	logger.Info("operation completed", "result", "success")

	// Logs appear with test output when run with -v
}

func TestExample3_TestLoggerWithLevel(t *testing.T) {
	// Only show warnings and above
	logger := NewTestLoggerWithLevel(t, slog.LevelWarn)

	logger.Debug("this won't show") // Below threshold
	logger.Info("this won't show")  // Below threshold
	logger.Warn("this will show")   // At threshold
	logger.Error("this will show")  // Above threshold
}

// ============================================================================
// Assertable Logger - Full log assertion capabilities
// ============================================================================

type AssertableLogger struct {
	entries []LogEntry
}

type LogEntry struct {
	Level   slog.Level
	Message string
	Attrs   map[string]interface{}
}

func NewAssertableLogger() (*AssertableLogger, *slog.Logger) {
	al := &AssertableLogger{
		entries: make([]LogEntry, 0),
	}
	logger := slog.New(&assertableHandler{al: al})
	return al, logger
}

type assertableHandler struct {
	al    *AssertableLogger
	attrs map[string]interface{}
}

func (h *assertableHandler) Enabled(ctx context.Context, level slog.Level) bool {
	return true
}

func (h *assertableHandler) Handle(ctx context.Context, r slog.Record) error {
	entry := LogEntry{
		Level:   r.Level,
		Message: r.Message,
		Attrs:   make(map[string]interface{}),
	}

	// Copy handler attrs
	for k, v := range h.attrs {
		entry.Attrs[k] = v
	}

	// Add record attrs
	r.Attrs(func(a slog.Attr) bool {
		entry.Attrs[a.Key] = a.Value.Any()
		return true
	})

	h.al.entries = append(h.al.entries, entry)
	return nil
}

func (h *assertableHandler) WithAttrs(attrs []slog.Attr) slog.Handler {
	newAttrs := make(map[string]interface{})
	for k, v := range h.attrs {
		newAttrs[k] = v
	}
	for _, a := range attrs {
		newAttrs[a.Key] = a.Value.Any()
	}
	return &assertableHandler{al: h.al, attrs: newAttrs}
}

func (h *assertableHandler) WithGroup(name string) slog.Handler {
	return h
}

func (al *AssertableLogger) AssertLogged(t *testing.T, level slog.Level, message string) {
	t.Helper()
	for _, entry := range al.entries {
		if entry.Level == level && strings.Contains(entry.Message, message) {
			return
		}
	}
	t.Errorf("expected log entry with level=%s message containing %q, entries: %+v",
		level, message, al.entries)
}

func (al *AssertableLogger) AssertNotLogged(t *testing.T, level slog.Level, message string) {
	t.Helper()
	for _, entry := range al.entries {
		if entry.Level == level && strings.Contains(entry.Message, message) {
			t.Errorf("unexpected log entry: %+v", entry)
			return
		}
	}
}

func (al *AssertableLogger) AssertAttrLogged(t *testing.T, key string, value interface{}) {
	t.Helper()
	for _, entry := range al.entries {
		if v, ok := entry.Attrs[key]; ok && v == value {
			return
		}
	}
	t.Errorf("expected log entry with attr %s=%v", key, value)
}

func (al *AssertableLogger) Count() int {
	return len(al.entries)
}

func (al *AssertableLogger) Clear() {
	al.entries = al.entries[:0]
}

func TestExample3_AssertableLogger(t *testing.T) {
	al, logger := NewAssertableLogger()

	// Simulate application logging
	logger.Info("user logged in", "user_id", int64(123))
	logger.Debug("session created", "session_id", "abc123")
	logger.Info("request completed", "status", 200)

	// Assert specific logs
	al.AssertLogged(t, slog.LevelInfo, "user logged in")
	al.AssertLogged(t, slog.LevelDebug, "session created")
	al.AssertAttrLogged(t, "user_id", int64(123))
	al.AssertAttrLogged(t, "status", 200)

	// Assert something wasn't logged
	al.AssertNotLogged(t, slog.LevelError, "")

	assert.Equal(t, 3, al.Count())
}

// ============================================================================
// Service with Injected Logger
// ============================================================================

type UserService struct {
	logger *slog.Logger
}

func NewUserService(logger *slog.Logger) *UserService {
	return &UserService{logger: logger}
}

func (s *UserService) GetUser(id int64) (*User, error) {
	s.logger.Info("getting user", "user_id", id)

	// Simulate user lookup
	user := &User{ID: id, Name: "Test User", Email: "test@example.com"}

	s.logger.Debug("user found", "user_id", id, "name", user.Name)
	return user, nil
}

func (s *UserService) DeleteUser(id int64) error {
	s.logger.Warn("deleting user", "user_id", id)
	return nil
}

func TestExample3_ServiceWithLogger(t *testing.T) {
	t.Run("with discard logger", func(t *testing.T) {
		// Silence logs
		service := NewUserService(NewDiscardLogger())
		user, err := service.GetUser(1)

		require.NoError(t, err)
		assert.Equal(t, int64(1), user.ID)
	})

	t.Run("with capture logger", func(t *testing.T) {
		cl := NewCaptureLogger()
		service := NewUserService(cl.Logger)

		_, _ = service.GetUser(42)

		assert.True(t, cl.Contains("getting user"))
		assert.True(t, cl.Contains("user_id"))
		assert.True(t, cl.Contains("42"))
	})

	t.Run("with assertable logger", func(t *testing.T) {
		al, logger := NewAssertableLogger()
		service := NewUserService(logger)

		_, _ = service.GetUser(99)
		_ = service.DeleteUser(99)

		al.AssertLogged(t, slog.LevelInfo, "getting user")
		al.AssertLogged(t, slog.LevelDebug, "user found")
		al.AssertLogged(t, slog.LevelWarn, "deleting user")
		al.AssertAttrLogged(t, "user_id", int64(99))
	})
}
