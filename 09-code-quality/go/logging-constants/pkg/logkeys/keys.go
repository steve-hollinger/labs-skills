// Package logkeys provides standardized logging key constants.
//
// Using constants for log keys ensures consistency across services,
// makes logs searchable, and enables IDE support for autocomplete.
package logkeys

// Identity keys - who is performing the action
const (
	// UserID identifies the user performing an action
	UserID = "user_id"

	// TenantID identifies the tenant/organization
	TenantID = "tenant_id"

	// SessionID identifies a user session
	SessionID = "session_id"

	// ActorType identifies the type of actor (user, system, service)
	ActorType = "actor_type"

	// ServiceName identifies which service generated the log
	ServiceName = "service"
)

// Request keys - tracking requests through the system
const (
	// RequestID is a unique identifier for a request
	RequestID = "request_id"

	// TraceID is for distributed tracing
	TraceID = "trace_id"

	// SpanID is for distributed tracing spans
	SpanID = "span_id"

	// ParentSpanID links to parent span in distributed trace
	ParentSpanID = "parent_span_id"

	// CorrelationID links related operations
	CorrelationID = "correlation_id"
)

// HTTP keys - HTTP-specific information
const (
	// HTTPMethod is the HTTP method (GET, POST, etc.)
	HTTPMethod = "http_method"

	// HTTPPath is the request path
	HTTPPath = "http_path"

	// HTTPStatus is the response status code
	HTTPStatus = "http_status"

	// HTTPUserAgent is the client's user agent
	HTTPUserAgent = "http_user_agent"

	// ClientIP is the client's IP address
	ClientIP = "client_ip"
)

// Operation keys - what is happening
const (
	// Operation is the name of the operation being performed
	Operation = "operation"

	// Action is a specific action within an operation
	Action = "action"

	// Status is the status of an operation (success, failure, etc.)
	Status = "status"

	// Component identifies the component within a service
	Component = "component"

	// Layer identifies the architectural layer (handler, service, repo)
	Layer = "layer"
)

// Timing keys - performance and timing information
const (
	// DurationMS is the duration in milliseconds
	DurationMS = "duration_ms"

	// StartTime is when an operation started
	StartTime = "start_time"

	// EndTime is when an operation ended
	EndTime = "end_time"

	// Timestamp is a generic timestamp field
	Timestamp = "timestamp"
)

// Error keys - error details
const (
	// Error is the error message
	Error = "error"

	// ErrorCode is a machine-readable error code
	ErrorCode = "error_code"

	// ErrorType categorizes the error (validation, database, etc.)
	ErrorType = "error_type"

	// StackTrace is the error stack trace
	StackTrace = "stack_trace"

	// RetryCount is the number of retries attempted
	RetryCount = "retry_count"
)

// Resource keys - what is being acted upon
const (
	// ResourceType identifies the type of resource
	ResourceType = "resource_type"

	// ResourceID identifies a specific resource
	ResourceID = "resource_id"

	// ResourceName is a human-readable resource name
	ResourceName = "resource_name"

	// Count is a quantity of items
	Count = "count"

	// BatchID identifies a batch of operations
	BatchID = "batch_id"

	// Version is a version identifier
	Version = "version"
)

// Database keys - database-specific information
const (
	// DBOperation is the database operation (select, insert, etc.)
	DBOperation = "db_operation"

	// DBTable is the database table name
	DBTable = "db_table"

	// DBQuery is the database query (be careful with sensitive data)
	DBQuery = "db_query"

	// RowsAffected is the number of rows affected
	RowsAffected = "rows_affected"
)

// Queue keys - message queue information
const (
	// QueueName is the name of the queue
	QueueName = "queue_name"

	// MessageID is the message identifier
	MessageID = "message_id"

	// MessageType is the type of message
	MessageType = "message_type"

	// ConsumerGroup is the consumer group name
	ConsumerGroup = "consumer_group"
)

// Cache keys - caching information
const (
	// CacheKey is the cache key
	CacheKey = "cache_key"

	// CacheHit indicates if there was a cache hit
	CacheHit = "cache_hit"

	// CacheTTL is the cache TTL in seconds
	CacheTTL = "cache_ttl_seconds"
)

// Feature flags and experiments
const (
	// FeatureFlag is the name of a feature flag
	FeatureFlag = "feature_flag"

	// FeatureEnabled indicates if feature is enabled
	FeatureEnabled = "feature_enabled"

	// ExperimentID identifies an experiment
	ExperimentID = "experiment_id"

	// ExperimentVariant is the experiment variant
	ExperimentVariant = "experiment_variant"
)
