# Example Dockerfile for the Docker build workflow

FROM python:3.12-slim-bookworm

# Build args from workflow
ARG VERSION=dev
ARG COMMIT_SHA=unknown

# Labels from metadata action
LABEL org.opencontainers.image.source="https://github.com/OWNER/REPO"
LABEL org.opencontainers.image.version="${VERSION}"
LABEL org.opencontainers.image.revision="${COMMIT_SHA}"

WORKDIR /app

# Create non-root user
RUN useradd -r -s /bin/false appuser

# Install dependencies
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copy application
COPY . .

# Set environment variables
ENV VERSION=${VERSION}
ENV COMMIT_SHA=${COMMIT_SHA}

# Switch to non-root user
USER appuser

EXPOSE 8000

CMD ["python", "-m", "uvicorn", "main:app", "--host", "0.0.0.0", "--port", "8000"]
