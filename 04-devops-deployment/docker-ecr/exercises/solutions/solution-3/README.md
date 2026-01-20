# Solution 3: ECR Deployment Script

## Key Features Implemented

### 1. Strict Error Handling
```bash
set -euo pipefail
```
- `-e`: Exit on any error
- `-u`: Error on undefined variables
- `-o pipefail`: Catch errors in pipelines

### 2. Prerequisites Validation
- Checks for required tools (docker, aws, git)
- Verifies Docker daemon is running
- Validates required environment variables
- Confirms AWS credentials are valid

### 3. ECR Repository Management
- Creates repository if it doesn't exist
- Enables image scanning on push
- Sets lifecycle policy for cleanup

### 4. Proper Tagging Strategy
Tags each image with:
- Version number (e.g., `1.0.0`)
- Git commit SHA (e.g., `abc123f`)
- `latest` for convenience

### 5. Error Handling
- Meaningful error messages with colors
- Proper exit codes
- Clear progress indicators

## Usage

```bash
# Required variables
export AWS_REGION=us-east-1
export REPO_NAME=my-application
export VERSION=1.0.0

# Optional
export DOCKERFILE=Dockerfile.production

# Run deployment
./deploy.sh
```

## Testing with LocalStack

```bash
# Start LocalStack
docker run -d -p 4566:4566 localstack/localstack

# Configure AWS CLI for LocalStack
export AWS_ENDPOINT_URL=http://localhost:4566
export AWS_ACCESS_KEY_ID=test
export AWS_SECRET_ACCESS_KEY=test
export AWS_REGION=us-east-1

# Run the script
./deploy.sh
```

## Script Structure

```
deploy.sh
├── validate_prerequisites()  # Check tools and config
├── get_aws_info()           # Get account ID and registry URL
├── create_repository()      # Create ECR repo if needed
├── authenticate_ecr()       # Docker login to ECR
├── build_and_push()         # Build, tag, and push image
└── main()                   # Orchestrate all steps
```

## Best Practices Demonstrated

1. **Idempotent**: Safe to run multiple times
2. **Verbose**: Clear logging of each step
3. **Configurable**: Environment variables for customization
4. **Secure**: No hardcoded credentials
5. **Maintainable**: Well-organized functions
