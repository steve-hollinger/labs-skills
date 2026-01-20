# Solution 1: Optimized Dockerfile

## Key Optimizations Applied

### 1. Base Image (Biggest Impact)
- **Before**: `python:3.12` (~1GB)
- **After**: `python:3.12-slim-bookworm` (~150MB)
- **Savings**: ~850MB

### 2. Removed Unnecessary Packages
- **Removed**: gcc, g++, make, curl, wget, vim
- **Removed**: numpy, pandas (not used by the app)
- These were installing ~300MB+ of unused packages

### 3. Layer Optimization
- Combined multiple `RUN apt-get` into none (not needed)
- Moved `COPY requirements.txt` before `pip install` for caching

### 4. Security Improvements
- Added non-root user
- Added health check
- Using gunicorn for production

### 5. Python Optimizations
- `PYTHONDONTWRITEBYTECODE=1` - Don't write .pyc files
- `PIP_NO_CACHE_DIR=1` - Don't cache pip downloads

## Size Comparison

| Image | Size |
|-------|------|
| Original | ~1.2GB |
| Optimized | ~150MB |
| Reduction | 87% |

## Commands to Verify

```bash
# Build original
docker build -f ../Dockerfile -t ex1-original ..

# Build optimized
docker build -f Dockerfile.optimized -t ex1-optimized ..

# Compare sizes
docker images | grep ex1

# Test functionality
docker run --rm -p 5000:5000 ex1-optimized
curl http://localhost:5000/health
```
