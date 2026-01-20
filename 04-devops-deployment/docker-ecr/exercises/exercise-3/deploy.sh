#!/bin/bash
# EXERCISE 3: Complete this ECR deployment script
#
# Required environment variables:
#   AWS_REGION - AWS region (e.g., us-east-1)
#   REPO_NAME  - ECR repository name
#   VERSION    - Image version tag
#
# Optional:
#   AWS_ENDPOINT - Custom AWS endpoint (for LocalStack)

# TODO: Add strict error handling
# set -???

# Color output helpers (optional but nice)
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
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

# ==============================================================================
# TODO: SECTION 1 - Validate Prerequisites
# ==============================================================================
# Check for required tools: docker, aws
# Check for required environment variables: AWS_REGION, REPO_NAME, VERSION
# Example:
#   if ! command -v docker &> /dev/null; then
#       log_error "docker is required but not installed"
#       exit 1
#   fi

validate_prerequisites() {
    log_info "Validating prerequisites..."

    # TODO: Implement prerequisite checks
    echo "TODO: Implement validate_prerequisites"
}

# ==============================================================================
# TODO: SECTION 2 - Get AWS Account Info
# ==============================================================================
# Get the AWS account ID and construct the ECR registry URL
# Example: 123456789.dkr.ecr.us-east-1.amazonaws.com

get_aws_info() {
    log_info "Getting AWS account information..."

    # TODO: Get account ID using aws sts get-caller-identity
    # TODO: Construct ECR_REGISTRY URL

    echo "TODO: Implement get_aws_info"

    # These should be set:
    # ACCOUNT_ID="..."
    # ECR_REGISTRY="..."
}

# ==============================================================================
# TODO: SECTION 3 - Create ECR Repository (if needed)
# ==============================================================================
# Create the repository if it doesn't exist
# Enable image scanning on push

create_repository() {
    log_info "Checking ECR repository..."

    # TODO: Check if repository exists with aws ecr describe-repositories
    # TODO: If not, create with aws ecr create-repository
    # TODO: Enable scanning: --image-scanning-configuration scanOnPush=true

    echo "TODO: Implement create_repository"
}

# ==============================================================================
# TODO: SECTION 4 - Authenticate to ECR
# ==============================================================================
# Get login password and authenticate Docker to ECR

authenticate_ecr() {
    log_info "Authenticating to ECR..."

    # TODO: Use aws ecr get-login-password | docker login ...

    echo "TODO: Implement authenticate_ecr"
}

# ==============================================================================
# TODO: SECTION 5 - Build and Push Image
# ==============================================================================
# Build the Docker image
# Tag with version and git SHA
# Push all tags to ECR

build_and_push() {
    log_info "Building and pushing image..."

    # TODO: Get git commit SHA (short)
    # TODO: Build image with docker build
    # TODO: Tag with version, SHA, and latest
    # TODO: Push all tags

    echo "TODO: Implement build_and_push"
}

# ==============================================================================
# Main execution
# ==============================================================================

main() {
    log_info "Starting ECR deployment..."

    validate_prerequisites
    get_aws_info
    create_repository
    authenticate_ecr
    build_and_push

    log_info "Deployment complete!"
    # TODO: Print the final image URI
}

# Run main function
main "$@"
