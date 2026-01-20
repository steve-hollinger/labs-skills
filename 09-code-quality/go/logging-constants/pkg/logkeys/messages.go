// Package logkeys provides standardized logging message constants.
package logkeys

// Request lifecycle messages
const (
	// MsgRequestStarted indicates a request has begun processing
	MsgRequestStarted = "request started"

	// MsgRequestCompleted indicates a request completed successfully
	MsgRequestCompleted = "request completed"

	// MsgRequestFailed indicates a request failed
	MsgRequestFailed = "request failed"

	// MsgRequestTimeout indicates a request timed out
	MsgRequestTimeout = "request timeout"
)

// User operation messages
const (
	// MsgUserCreated indicates a user was created
	MsgUserCreated = "user created"

	// MsgUserUpdated indicates a user was updated
	MsgUserUpdated = "user updated"

	// MsgUserDeleted indicates a user was deleted
	MsgUserDeleted = "user deleted"

	// MsgUserLoggedIn indicates a user logged in
	MsgUserLoggedIn = "user logged in"

	// MsgUserLoggedOut indicates a user logged out
	MsgUserLoggedOut = "user logged out"

	// MsgUserNotFound indicates a user was not found
	MsgUserNotFound = "user not found"

	// MsgAuthenticationFailed indicates authentication failed
	MsgAuthenticationFailed = "authentication failed"

	// MsgAuthorizationFailed indicates authorization failed
	MsgAuthorizationFailed = "authorization failed"
)

// Generic CRUD messages
const (
	// MsgRecordCreated indicates a record was created
	MsgRecordCreated = "record created"

	// MsgRecordUpdated indicates a record was updated
	MsgRecordUpdated = "record updated"

	// MsgRecordDeleted indicates a record was deleted
	MsgRecordDeleted = "record deleted"

	// MsgRecordFetched indicates a record was fetched
	MsgRecordFetched = "record fetched"

	// MsgRecordNotFound indicates a record was not found
	MsgRecordNotFound = "record not found"

	// MsgRecordAlreadyExists indicates a duplicate record
	MsgRecordAlreadyExists = "record already exists"
)

// Service lifecycle messages
const (
	// MsgServiceStarting indicates a service is starting
	MsgServiceStarting = "service starting"

	// MsgServiceStarted indicates a service started successfully
	MsgServiceStarted = "service started"

	// MsgServiceStopping indicates a service is stopping
	MsgServiceStopping = "service stopping"

	// MsgServiceStopped indicates a service stopped
	MsgServiceStopped = "service stopped"

	// MsgServiceHealthy indicates a service is healthy
	MsgServiceHealthy = "service healthy"

	// MsgServiceUnhealthy indicates a service is unhealthy
	MsgServiceUnhealthy = "service unhealthy"
)

// Configuration messages
const (
	// MsgConfigLoaded indicates configuration was loaded
	MsgConfigLoaded = "configuration loaded"

	// MsgConfigReloaded indicates configuration was reloaded
	MsgConfigReloaded = "configuration reloaded"

	// MsgConfigInvalid indicates invalid configuration
	MsgConfigInvalid = "invalid configuration"
)

// Database messages
const (
	// MsgDatabaseConnected indicates database connection succeeded
	MsgDatabaseConnected = "database connected"

	// MsgDatabaseDisconnected indicates database disconnection
	MsgDatabaseDisconnected = "database disconnected"

	// MsgDatabaseQueryFailed indicates a query failed
	MsgDatabaseQueryFailed = "database query failed"

	// MsgDatabaseMigrationRun indicates a migration was run
	MsgDatabaseMigrationRun = "database migration run"
)

// Cache messages
const (
	// MsgCacheHit indicates a cache hit
	MsgCacheHit = "cache hit"

	// MsgCacheMiss indicates a cache miss
	MsgCacheMiss = "cache miss"

	// MsgCacheSet indicates a value was cached
	MsgCacheSet = "cache set"

	// MsgCacheInvalidated indicates cache was invalidated
	MsgCacheInvalidated = "cache invalidated"
)

// Queue messages
const (
	// MsgMessagePublished indicates a message was published
	MsgMessagePublished = "message published"

	// MsgMessageReceived indicates a message was received
	MsgMessageReceived = "message received"

	// MsgMessageProcessed indicates a message was processed
	MsgMessageProcessed = "message processed"

	// MsgMessageFailed indicates message processing failed
	MsgMessageFailed = "message processing failed"
)

// External service messages
const (
	// MsgExternalCallStarted indicates an external call started
	MsgExternalCallStarted = "external call started"

	// MsgExternalCallCompleted indicates an external call completed
	MsgExternalCallCompleted = "external call completed"

	// MsgExternalCallFailed indicates an external call failed
	MsgExternalCallFailed = "external call failed"

	// MsgExternalCallRetrying indicates retrying an external call
	MsgExternalCallRetrying = "retrying external call"
)

// Batch processing messages
const (
	// MsgBatchStarted indicates batch processing started
	MsgBatchStarted = "batch processing started"

	// MsgBatchCompleted indicates batch processing completed
	MsgBatchCompleted = "batch processing completed"

	// MsgBatchItemProcessed indicates a batch item was processed
	MsgBatchItemProcessed = "batch item processed"

	// MsgBatchItemFailed indicates a batch item failed
	MsgBatchItemFailed = "batch item failed"
)

// Validation messages
const (
	// MsgValidationFailed indicates validation failed
	MsgValidationFailed = "validation failed"

	// MsgInputInvalid indicates invalid input
	MsgInputInvalid = "invalid input"

	// MsgFieldRequired indicates a required field is missing
	MsgFieldRequired = "required field missing"
)
