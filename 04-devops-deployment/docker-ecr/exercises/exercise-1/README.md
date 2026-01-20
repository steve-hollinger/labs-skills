# Exercise 1: Optimize an Inefficient Dockerfile

## Objective

Take an inefficient Dockerfile and optimize it to reduce image size by at least 80%.

## Starting Point

The `Dockerfile` in this directory has several issues that result in a bloated image (~1.2GB).
Your goal is to optimize it to under 200MB while maintaining functionality.

## Requirements

1. The optimized image must:
   - Be less than 200MB
   - Run as a non-root user
   - Pass the health check
   - Successfully serve the application

2. You should apply these optimizations:
   - Use an appropriate slim base image
   - Order layers for optimal caching
   - Remove unnecessary build dependencies
   - Use multi-stage build if beneficial
   - Add proper .dockerignore

## Current Dockerfile (with issues)

```dockerfile
FROM python:3.12

RUN apt-get update
RUN apt-get install -y gcc g++ make
RUN apt-get install -y curl wget vim
RUN pip install flask gunicorn requests numpy pandas

COPY . /app
WORKDIR /app

RUN pip install -r requirements.txt

EXPOSE 5000
CMD python app.py
```

## Files

- `Dockerfile` - The inefficient Dockerfile to optimize
- `app.py` - Simple Flask application
- `requirements.txt` - Python dependencies

## Steps

1. Build the original image and note its size:
   ```bash
   docker build -t exercise1-original .
   docker images exercise1-original
   ```

2. Create an optimized `Dockerfile.optimized`

3. Build and compare:
   ```bash
   docker build -f Dockerfile.optimized -t exercise1-optimized .
   docker images | grep exercise1
   ```

4. Verify the optimized image works:
   ```bash
   docker run --rm -p 5000:5000 exercise1-optimized
   curl http://localhost:5000/health
   ```

## Hints

- Look at the base image choice
- Consider what packages are actually needed at runtime vs build time
- Check if all pip packages are really needed
- Think about layer ordering

## Success Criteria

- [ ] Image size reduced by 80%+ (from ~1.2GB to <200MB)
- [ ] Application starts and responds to health check
- [ ] Runs as non-root user
- [ ] Dockerfile follows best practices
