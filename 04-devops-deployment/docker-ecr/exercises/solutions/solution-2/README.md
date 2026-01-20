# Solution 2: Multi-Stage Build

## Key Optimizations Applied

### 1. Multi-Stage Build
- **Builder stage**: Contains Go toolchain, compiles code
- **Runtime stage**: Contains only the binary
- Go toolchain (~500MB) is not in final image

### 2. Static Binary
```dockerfile
CGO_ENABLED=0 GOOS=linux GOARCH=amd64 go build ...
```
- Creates a static binary with no C dependencies
- Can run on minimal base images like alpine or scratch

### 3. Stripped Debug Symbols
```dockerfile
-ldflags="-s -w"
```
- `-s`: Strip symbol table
- `-w`: Strip DWARF debug information
- Reduces binary size by ~30%

### 4. Minimal Base Image
- Using `alpine:3.19` (~5MB) instead of `golang:1.22` (~800MB)
- Could use `scratch` for even smaller (~0MB base)

### 5. CA Certificates
- Copied from builder for HTTPS support
- Required if the application makes outbound HTTPS requests

## Size Comparison

| Image | Size |
|-------|------|
| Single-stage (golang:1.22) | ~800MB |
| Multi-stage (alpine:3.19) | ~10MB |
| Multi-stage (scratch) | ~5MB |
| Reduction | 98%+ |

## Commands to Verify

```bash
# Build original
cd ..
docker build -f Dockerfile -t ex2-original .

# Build optimized
docker build -f solutions/solution-2/Dockerfile.multistage -t ex2-optimized .

# Compare sizes
docker images | grep ex2

# Test functionality
docker run --rm -p 8080:8080 ex2-optimized
curl http://localhost:8080/health
```

## Why Multi-Stage?

1. **Security**: Fewer packages = smaller attack surface
2. **Speed**: Smaller images deploy faster
3. **Cost**: Less storage and bandwidth
4. **Clarity**: Clear separation of build and runtime
