# CLAUDE.md - Docker/ECR

This skill teaches Docker containerization best practices and AWS ECR workflows for production deployments.

## Key Concepts

- **Dockerfile Optimization**: Layer ordering, caching, minimal base images
- **Multi-Stage Builds**: Separate build and runtime stages for smaller images
- **ECR Workflow**: Authentication, pushing, pulling, and lifecycle policies
- **Security Scanning**: Trivy and ECR native scanning for vulnerabilities
- **Image Tagging**: Semantic versioning and immutable tags

## Common Commands

```bash
make setup      # Verify Docker is installed
make examples   # Build all example images
make example-1  # Build basic Python example
make example-2  # Build multi-stage Go example
make example-3  # Build secure Node.js example
make lint       # Lint Dockerfiles with hadolint
make scan       # Run security scan with trivy
make clean      # Remove built images
```

## Project Structure

```
docker-ecr/
├── README.md
├── CLAUDE.md
├── Makefile
├── examples/
│   ├── 01-python-basic/
│   │   ├── Dockerfile
│   │   ├── main.py
│   │   └── requirements.txt
│   ├── 02-go-multistage/
│   │   ├── Dockerfile
│   │   ├── main.go
│   │   └── go.mod
│   └── 03-node-secure/
│       ├── Dockerfile
│       ├── server.js
│       └── package.json
├── exercises/
│   ├── exercise-1/
│   ├── exercise-2/
│   ├── exercise-3/
│   └── solutions/
└── docs/
    ├── concepts.md
    └── patterns.md
```

## Code Patterns

### Pattern 1: Minimal Python Image
```dockerfile
FROM python:3.12-slim-bookworm
WORKDIR /app
RUN useradd -r -s /bin/false appuser
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt
COPY --chown=appuser:appuser . .
USER appuser
EXPOSE 8000
CMD ["python", "-m", "uvicorn", "main:app", "--host", "0.0.0.0"]
```

### Pattern 2: Multi-Stage Go Build
```dockerfile
FROM golang:1.22-alpine AS builder
WORKDIR /build
COPY go.* ./
RUN go mod download
COPY . .
RUN CGO_ENABLED=0 GOOS=linux GOARCH=amd64 go build -ldflags="-s -w" -o app

FROM scratch
COPY --from=builder /build/app /app
ENTRYPOINT ["/app"]
```

### Pattern 3: ECR Push Script
```bash
#!/bin/bash
REGION="us-east-1"
ACCOUNT_ID=$(aws sts get-caller-identity --query Account --output text)
REPO_URI="${ACCOUNT_ID}.dkr.ecr.${REGION}.amazonaws.com/my-app"

aws ecr get-login-password --region $REGION | \
  docker login --username AWS --password-stdin $REPO_URI

docker build -t my-app:$VERSION .
docker tag my-app:$VERSION $REPO_URI:$VERSION
docker push $REPO_URI:$VERSION
```

## Common Mistakes

1. **Using `ADD` instead of `COPY`**
   - `ADD` has extra features (URL download, tar extraction) that are rarely needed
   - Use `COPY` for simple file copying; it's more explicit

2. **Not using `.dockerignore`**
   - Sending unnecessary files to build context slows builds
   - Always exclude: `.git`, `node_modules`, `__pycache__`, `*.pyc`, `.env`

3. **Installing packages in multiple RUN statements**
   - Creates unnecessary layers
   - Combine with `&&` and clean up in same layer

4. **Not pinning dependency versions**
   - Leads to non-reproducible builds
   - Pin exact versions in requirements.txt/go.mod/package-lock.json

## When Users Ask About...

### "How do I reduce my image size?"
1. Use slim/alpine base images
2. Implement multi-stage builds
3. Remove build dependencies in same layer
4. Use `--no-cache-dir` for pip
5. Review with `docker history` to find large layers

### "How do I debug a build?"
```bash
# Build up to a specific stage
docker build --target builder -t debug .

# Run intermediate container
docker run -it debug sh

# View layer history
docker history my-image:latest
```

### "How do I push to ECR?"
1. Authenticate: `aws ecr get-login-password | docker login`
2. Tag image: `docker tag local:tag repo:tag`
3. Push: `docker push repo:tag`

### "How do I scan for vulnerabilities?"
Use Trivy locally or enable ECR scanning on push. Always scan before deploying to production.

## Testing Notes

- Build examples with `make examples`
- Verify image sizes meet expectations
- Run containers to verify they start correctly
- Use hadolint for Dockerfile linting

## Dependencies

Key tools used:
- docker: Container runtime
- hadolint: Dockerfile linter
- trivy: Security scanner
- aws-cli: ECR interaction
