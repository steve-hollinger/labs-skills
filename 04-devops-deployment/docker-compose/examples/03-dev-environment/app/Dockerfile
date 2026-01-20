# Multi-stage Dockerfile for development and production

# ==============================================================================
# Base stage with common dependencies
# ==============================================================================
FROM python:3.12-slim-bookworm AS base

WORKDIR /app

# Install system dependencies
RUN apt-get update && \
    apt-get install -y --no-install-recommends curl && \
    rm -rf /var/lib/apt/lists/*

# Create virtual environment
RUN python -m venv /app/.venv
ENV PATH="/app/.venv/bin:$PATH"

# ==============================================================================
# Development stage
# ==============================================================================
FROM base AS development

# Install development dependencies
RUN pip install --no-cache-dir \
    uvicorn[standard] \
    debugpy \
    pytest \
    pytest-asyncio \
    httpx

# Copy requirements and install
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copy source (will be overridden by volume mount)
COPY . .

# Install package in development mode
RUN pip install -e .

EXPOSE 8000 5678

# Development command with hot reload
CMD ["uvicorn", "src.main:app", "--host", "0.0.0.0", "--port", "8000", "--reload"]

# ==============================================================================
# Production stage
# ==============================================================================
FROM base AS production

# Create non-root user
RUN useradd -r -s /bin/false appuser

# Copy requirements and install
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copy source
COPY . .

# Install package
RUN pip install --no-cache-dir .

# Switch to non-root user
USER appuser

EXPOSE 8000

CMD ["uvicorn", "src.main:app", "--host", "0.0.0.0", "--port", "8000"]
