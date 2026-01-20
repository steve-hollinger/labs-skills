# Example 2: Multi-Stage Go Build
# Demonstrates multi-stage builds for compiled languages

# ==============================================================================
# Build Stage
# ==============================================================================
FROM golang:1.22-alpine AS builder

# Install CA certificates for HTTPS calls and git for modules
RUN apk --no-cache add ca-certificates git

WORKDIR /build

# Copy dependency files first (better caching)
COPY go.mod go.sum ./
RUN go mod download

# Copy source code
COPY . .

# Build with optimizations
# CGO_ENABLED=0: Static binary, no C dependencies
# -ldflags="-s -w": Strip debug info for smaller binary
# -trimpath: Remove file paths from binary
RUN CGO_ENABLED=0 GOOS=linux GOARCH=amd64 \
    go build \
    -ldflags="-s -w -X main.version=1.0.0" \
    -trimpath \
    -o /app \
    ./cmd/server

# ==============================================================================
# Runtime Stage
# ==============================================================================
FROM alpine:3.19 AS runtime

# Add labels
LABEL maintainer="labs-skills" \
      version="1.0.0" \
      description="Multi-stage Go build example"

# Install CA certificates for HTTPS and create non-root user
RUN apk --no-cache add ca-certificates && \
    addgroup -g 1001 -S appgroup && \
    adduser -u 1001 -S appuser -G appgroup

# Copy binary from builder
COPY --from=builder /app /app

# Use non-root user
USER appuser

# Document port
EXPOSE 8080

# Health check
HEALTHCHECK --interval=30s --timeout=3s --start-period=5s --retries=3 \
    CMD wget --no-verbose --tries=1 --spider http://localhost:8080/health || exit 1

# Run the application
ENTRYPOINT ["/app"]

# ==============================================================================
# Alternative: Scratch image (even smaller, ~5MB)
# ==============================================================================
# Uncomment below and comment out the alpine runtime stage for minimal image
# FROM scratch AS runtime-scratch
# COPY --from=builder /etc/ssl/certs/ca-certificates.crt /etc/ssl/certs/
# COPY --from=builder /app /app
# ENTRYPOINT ["/app"]
