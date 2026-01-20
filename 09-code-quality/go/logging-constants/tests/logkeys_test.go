package tests

import (
	"regexp"
	"testing"

	"github.com/stretchr/testify/assert"
	"github.com/stretchr/testify/require"

	"github.com/labs-skills/logging-constants/pkg/logkeys"
)

// TestKeyNamingConvention verifies all keys follow snake_case convention
func TestKeyNamingConvention(t *testing.T) {
	snakeCaseRegex := regexp.MustCompile(`^[a-z][a-z0-9]*(_[a-z0-9]+)*$`)

	keys := []struct {
		name  string
		value string
	}{
		{"UserID", logkeys.UserID},
		{"TenantID", logkeys.TenantID},
		{"SessionID", logkeys.SessionID},
		{"RequestID", logkeys.RequestID},
		{"TraceID", logkeys.TraceID},
		{"HTTPMethod", logkeys.HTTPMethod},
		{"HTTPPath", logkeys.HTTPPath},
		{"HTTPStatus", logkeys.HTTPStatus},
		{"DurationMS", logkeys.DurationMS},
		{"Error", logkeys.Error},
		{"ErrorCode", logkeys.ErrorCode},
		{"Component", logkeys.Component},
		{"Operation", logkeys.Operation},
	}

	for _, k := range keys {
		t.Run(k.name, func(t *testing.T) {
			assert.True(t, snakeCaseRegex.MatchString(k.value),
				"Key %s with value '%s' should be snake_case", k.name, k.value)
		})
	}
}

// TestKeyUniqueness verifies no duplicate key values
func TestKeyUniqueness(t *testing.T) {
	keys := []string{
		logkeys.UserID,
		logkeys.TenantID,
		logkeys.SessionID,
		logkeys.RequestID,
		logkeys.TraceID,
		logkeys.HTTPMethod,
		logkeys.HTTPPath,
		logkeys.HTTPStatus,
		logkeys.DurationMS,
		logkeys.Error,
		logkeys.ErrorCode,
		logkeys.Component,
		logkeys.Operation,
		logkeys.ResourceType,
		logkeys.ResourceID,
	}

	seen := make(map[string]bool)
	for _, key := range keys {
		require.False(t, seen[key], "Duplicate key value found: %s", key)
		seen[key] = true
	}
}

// TestIdentityKeys verifies identity-related keys exist
func TestIdentityKeys(t *testing.T) {
	assert.Equal(t, "user_id", logkeys.UserID)
	assert.Equal(t, "tenant_id", logkeys.TenantID)
	assert.Equal(t, "session_id", logkeys.SessionID)
	assert.Equal(t, "actor_type", logkeys.ActorType)
}

// TestRequestKeys verifies request tracking keys exist
func TestRequestKeys(t *testing.T) {
	assert.Equal(t, "request_id", logkeys.RequestID)
	assert.Equal(t, "trace_id", logkeys.TraceID)
	assert.Equal(t, "span_id", logkeys.SpanID)
	assert.Equal(t, "correlation_id", logkeys.CorrelationID)
}

// TestHTTPKeys verifies HTTP-specific keys exist
func TestHTTPKeys(t *testing.T) {
	assert.Equal(t, "http_method", logkeys.HTTPMethod)
	assert.Equal(t, "http_path", logkeys.HTTPPath)
	assert.Equal(t, "http_status", logkeys.HTTPStatus)
	assert.Equal(t, "client_ip", logkeys.ClientIP)
}

// TestTimingKeys verifies timing keys exist
func TestTimingKeys(t *testing.T) {
	assert.Equal(t, "duration_ms", logkeys.DurationMS)
	assert.Equal(t, "start_time", logkeys.StartTime)
	assert.Equal(t, "end_time", logkeys.EndTime)
}

// TestErrorKeys verifies error-related keys exist
func TestErrorKeys(t *testing.T) {
	assert.Equal(t, "error", logkeys.Error)
	assert.Equal(t, "error_code", logkeys.ErrorCode)
	assert.Equal(t, "error_type", logkeys.ErrorType)
	assert.Equal(t, "stack_trace", logkeys.StackTrace)
}

// TestOperationKeys verifies operation keys exist
func TestOperationKeys(t *testing.T) {
	assert.Equal(t, "operation", logkeys.Operation)
	assert.Equal(t, "component", logkeys.Component)
	assert.Equal(t, "layer", logkeys.Layer)
}

// TestResourceKeys verifies resource keys exist
func TestResourceKeys(t *testing.T) {
	assert.Equal(t, "resource_type", logkeys.ResourceType)
	assert.Equal(t, "resource_id", logkeys.ResourceID)
	assert.Equal(t, "count", logkeys.Count)
}

// TestMessageConstants verifies message constants exist
func TestMessageConstants(t *testing.T) {
	// Request lifecycle
	assert.Equal(t, "request started", logkeys.MsgRequestStarted)
	assert.Equal(t, "request completed", logkeys.MsgRequestCompleted)
	assert.Equal(t, "request failed", logkeys.MsgRequestFailed)

	// User operations
	assert.Equal(t, "user created", logkeys.MsgUserCreated)
	assert.Equal(t, "user updated", logkeys.MsgUserUpdated)
	assert.Equal(t, "user deleted", logkeys.MsgUserDeleted)
	assert.Equal(t, "user logged in", logkeys.MsgUserLoggedIn)
	assert.Equal(t, "user logged out", logkeys.MsgUserLoggedOut)

	// Service lifecycle
	assert.Equal(t, "service starting", logkeys.MsgServiceStarting)
	assert.Equal(t, "service started", logkeys.MsgServiceStarted)
	assert.Equal(t, "service stopping", logkeys.MsgServiceStopping)
}

// TestMessageNamingConvention verifies messages are lowercase
func TestMessageNamingConvention(t *testing.T) {
	messages := []string{
		logkeys.MsgRequestStarted,
		logkeys.MsgRequestCompleted,
		logkeys.MsgUserCreated,
		logkeys.MsgServiceStarted,
	}

	lowercaseRegex := regexp.MustCompile(`^[a-z][a-z0-9 ]*$`)

	for _, msg := range messages {
		assert.True(t, lowercaseRegex.MatchString(msg),
			"Message '%s' should be lowercase", msg)
	}
}

// TestDatabaseKeys verifies database-related keys
func TestDatabaseKeys(t *testing.T) {
	assert.Equal(t, "db_operation", logkeys.DBOperation)
	assert.Equal(t, "db_table", logkeys.DBTable)
	assert.Equal(t, "rows_affected", logkeys.RowsAffected)
}

// TestCacheKeys verifies cache-related keys
func TestCacheKeys(t *testing.T) {
	assert.Equal(t, "cache_key", logkeys.CacheKey)
	assert.Equal(t, "cache_hit", logkeys.CacheHit)
	assert.Equal(t, "cache_ttl_seconds", logkeys.CacheTTL)
}

// TestQueueKeys verifies queue-related keys
func TestQueueKeys(t *testing.T) {
	assert.Equal(t, "queue_name", logkeys.QueueName)
	assert.Equal(t, "message_id", logkeys.MessageID)
	assert.Equal(t, "message_type", logkeys.MessageType)
}
