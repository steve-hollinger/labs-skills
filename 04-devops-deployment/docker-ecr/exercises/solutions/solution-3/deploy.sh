#!/bin/bash
# SOLUTION 3: Complete ECR deployment script
#
# Required environment variables:
#   AWS_REGION - AWS region (e.g., us-east-1)
#   REPO_NAME  - ECR repository name
#   VERSION    - Image version tag
#
# Optional:
#   AWS_ENDPOINT - Custom AWS endpoint (for LocalStack)
#   DOCKERFILE   - Path to Dockerfile (default: Dockerfile)

# Strict error handling
set -euo pipefail

# Color output helpers
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

log_info() {
    echo -e "${GREEN}[INFO]${NC} $1"
}

log_warn() {
    echo -e "${YELLOW}[WARN]${NC} $1"
}

log_error() {
    echo -e "${RED}[ERROR]${NC} $1"
}

log_step() {
    echo -e "${BLUE}[STEP]${NC} $1"
}

# ==============================================================================
# SECTION 1 - Validate Prerequisites
# ==============================================================================
validate_prerequisites() {
    log_step "Validating prerequisites..."

    # Check for required tools
    local required_tools=("docker" "aws" "git")
    for tool in "${required_tools[@]}"; do
        if ! command -v "$tool" &> /dev/null; then
            log_error "$tool is required but not installed"
            exit 1
        fi
    done
    log_info "All required tools are installed"

    # Check Docker daemon is running
    if ! docker info &> /dev/null; then
        log_error "Docker daemon is not running"
        exit 1
    fi
    log_info "Docker daemon is running"

    # Check for required environment variables
    local required_vars=("AWS_REGION" "REPO_NAME" "VERSION")
    for var in "${required_vars[@]}"; do
        if [[ -z "${!var:-}" ]]; then
            log_error "Required environment variable $var is not set"
            exit 1
        fi
    done
    log_info "All required environment variables are set"

    # Verify AWS credentials
    if ! aws sts get-caller-identity &> /dev/null; then
        log_error "AWS credentials are not configured or invalid"
        exit 1
    fi
    log_info "AWS credentials are valid"
}

# ==============================================================================
# SECTION 2 - Get AWS Account Info
# ==============================================================================
get_aws_info() {
    log_step "Getting AWS account information..."

    ACCOUNT_ID=$(aws sts get-caller-identity --query Account --output text)
    ECR_REGISTRY="${ACCOUNT_ID}.dkr.ecr.${AWS_REGION}.amazonaws.com"

    log_info "Account ID: ${ACCOUNT_ID}"
    log_info "ECR Registry: ${ECR_REGISTRY}"
}

# ==============================================================================
# SECTION 3 - Create ECR Repository (if needed)
# ==============================================================================
create_repository() {
    log_step "Checking ECR repository..."

    # Check if repository exists
    if aws ecr describe-repositories \
        --repository-names "${REPO_NAME}" \
        --region "${AWS_REGION}" &> /dev/null; then
        log_info "Repository '${REPO_NAME}' already exists"
    else
        log_info "Creating repository '${REPO_NAME}'..."

        aws ecr create-repository \
            --repository-name "${REPO_NAME}" \
            --region "${AWS_REGION}" \
            --image-scanning-configuration scanOnPush=true \
            --encryption-configuration encryptionType=AES256 \
            --image-tag-mutability MUTABLE

        log_info "Repository created with scanning enabled"

        # Set lifecycle policy to clean up old images
        log_info "Setting lifecycle policy..."
        aws ecr put-lifecycle-policy \
            --repository-name "${REPO_NAME}" \
            --region "${AWS_REGION}" \
            --lifecycle-policy-text '{
                "rules": [
                    {
                        "rulePriority": 1,
                        "description": "Keep last 10 images",
                        "selection": {
                            "tagStatus": "any",
                            "countType": "imageCountMoreThan",
                            "countNumber": 10
                        },
                        "action": {
                            "type": "expire"
                        }
                    }
                ]
            }'
        log_info "Lifecycle policy set"
    fi
}

# ==============================================================================
# SECTION 4 - Authenticate to ECR
# ==============================================================================
authenticate_ecr() {
    log_step "Authenticating to ECR..."

    aws ecr get-login-password --region "${AWS_REGION}" | \
        docker login --username AWS --password-stdin "${ECR_REGISTRY}"

    log_info "Successfully authenticated to ECR"
}

# ==============================================================================
# SECTION 5 - Build and Push Image
# ==============================================================================
build_and_push() {
    log_step "Building and pushing image..."

    # Get git commit SHA (short)
    local git_sha
    git_sha=$(git rev-parse --short HEAD 2>/dev/null || echo "unknown")

    # Dockerfile path (default to Dockerfile)
    local dockerfile="${DOCKERFILE:-Dockerfile}"

    # Full image URI
    local image_uri="${ECR_REGISTRY}/${REPO_NAME}"

    # Build image
    log_info "Building image..."
    docker build \
        --build-arg VERSION="${VERSION}" \
        --build-arg GIT_SHA="${git_sha}" \
        --build-arg BUILD_DATE="$(date -u +%Y-%m-%dT%H:%M:%SZ)" \
        -t "${REPO_NAME}:${VERSION}" \
        -t "${REPO_NAME}:${git_sha}" \
        -t "${REPO_NAME}:latest" \
        -f "${dockerfile}" \
        .

    log_info "Build complete"

    # Tag for ECR
    log_info "Tagging images for ECR..."
    docker tag "${REPO_NAME}:${VERSION}" "${image_uri}:${VERSION}"
    docker tag "${REPO_NAME}:${git_sha}" "${image_uri}:${git_sha}"
    docker tag "${REPO_NAME}:latest" "${image_uri}:latest"

    # Push all tags
    log_info "Pushing images to ECR..."
    docker push "${image_uri}:${VERSION}"
    docker push "${image_uri}:${git_sha}"
    docker push "${image_uri}:latest"

    log_info "Push complete"

    # Print summary
    echo ""
    log_info "=== Deployment Summary ==="
    log_info "Repository: ${REPO_NAME}"
    log_info "Version: ${VERSION}"
    log_info "Git SHA: ${git_sha}"
    log_info "Image URIs:"
    echo "  - ${image_uri}:${VERSION}"
    echo "  - ${image_uri}:${git_sha}"
    echo "  - ${image_uri}:latest"
}

# ==============================================================================
# Main execution
# ==============================================================================
main() {
    echo ""
    log_info "=========================================="
    log_info "   ECR Deployment Script"
    log_info "=========================================="
    echo ""

    validate_prerequisites
    get_aws_info
    create_repository
    authenticate_ecr
    build_and_push

    echo ""
    log_info "=========================================="
    log_info "   Deployment Complete!"
    log_info "=========================================="
    echo ""
}

# Run main function
main "$@"
