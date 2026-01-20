# Exercise 2: Implement Multi-Stage Build

## Objective

Convert a single-stage Dockerfile for a Go application into a multi-stage build that produces a minimal runtime image.

## Starting Point

The `Dockerfile` in this directory uses a single stage and includes the entire Go toolchain in the final image (~800MB). Your goal is to use multi-stage builds to create a final image under 15MB.

## Requirements

1. The final image must:
   - Be less than 15MB
   - Contain only the compiled binary
   - Include CA certificates for HTTPS
   - Run successfully

2. Your multi-stage build should:
   - Use appropriate base images for each stage
   - Download dependencies in a separate step for caching
   - Use build flags to create a small, static binary

## Current Dockerfile (single-stage)

```dockerfile
FROM golang:1.22

WORKDIR /app

COPY go.mod go.sum ./
RUN go mod download

COPY . .
RUN go build -o server ./cmd/server

EXPOSE 8080
CMD ["./server"]
```

## Files

- `Dockerfile` - Single-stage Dockerfile to convert
- `cmd/server/main.go` - Go HTTP server
- `go.mod` - Go module file

## Steps

1. Build the original image and note its size:
   ```bash
   docker build -t exercise2-original .
   docker images exercise2-original
   ```

2. Create `Dockerfile.multistage` with:
   - A builder stage for compilation
   - A minimal runtime stage (alpine or scratch)

3. Build and compare:
   ```bash
   docker build -f Dockerfile.multistage -t exercise2-optimized .
   docker images | grep exercise2
   ```

4. Verify the optimized image works:
   ```bash
   docker run --rm -p 8080:8080 exercise2-optimized
   curl http://localhost:8080/health
   ```

## Hints

- For the smallest image, consider `FROM scratch` or `FROM alpine:3.19`
- Use build flags: `CGO_ENABLED=0 GOOS=linux`
- Use ldflags to strip debug symbols: `-ldflags="-s -w"`
- If using scratch, you need to copy CA certificates from the builder

## Success Criteria

- [ ] Final image is less than 15MB
- [ ] Application starts and responds to health check
- [ ] Multi-stage build has clear separation between build and runtime
- [ ] Build stage caches dependencies effectively
