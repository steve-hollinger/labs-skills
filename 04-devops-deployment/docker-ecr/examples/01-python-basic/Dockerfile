# Example 1: Basic Python Application
# Demonstrates fundamental Dockerfile best practices

# Use specific version with slim variant
FROM python:3.12-slim-bookworm

# Set labels for image metadata
LABEL maintainer="labs-skills" \
      version="1.0.0" \
      description="Basic Python application example"

# Prevent Python from writing bytecode and buffering output
ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1 \
    PIP_NO_CACHE_DIR=1 \
    PIP_DISABLE_PIP_VERSION_CHECK=1

# Create non-root user for security
RUN groupadd -r appgroup && \
    useradd -r -g appgroup -d /app -s /sbin/nologin appuser

# Set working directory
WORKDIR /app

# Copy dependency file first (better layer caching)
COPY requirements.txt .

# Install dependencies
RUN pip install --no-cache-dir -r requirements.txt

# Copy application code with proper ownership
COPY --chown=appuser:appgroup . .

# Switch to non-root user
USER appuser

# Document the port (doesn't actually expose it)
EXPOSE 8000

# Health check
HEALTHCHECK --interval=30s --timeout=3s --start-period=5s --retries=3 \
    CMD python -c "import urllib.request; urllib.request.urlopen('http://localhost:8000/health')" || exit 1

# Use exec form for proper signal handling
CMD ["python", "-m", "uvicorn", "main:app", "--host", "0.0.0.0", "--port", "8000"]
