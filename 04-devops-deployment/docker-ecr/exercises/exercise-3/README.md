# Exercise 3: ECR Deployment Workflow

## Objective

Create a complete ECR deployment workflow script that builds, tags, and pushes images to AWS ECR with proper error handling and best practices.

## Starting Point

The `deploy.sh` script in this directory is incomplete. You need to implement a robust deployment script that handles common scenarios.

## Requirements

Your script must:

1. **Validate Prerequisites**
   - Check for required tools (docker, aws)
   - Validate required environment variables
   - Verify AWS credentials are configured

2. **Create ECR Repository** (if needed)
   - Create repository if it doesn't exist
   - Enable image scanning on push
   - Set appropriate lifecycle policies

3. **Build and Push**
   - Build the Docker image with proper tagging
   - Tag with both version and commit SHA
   - Push all tags to ECR
   - Handle failures gracefully

4. **Output**
   - Display progress messages
   - Show final image URI
   - Exit with appropriate status codes

## Files

- `deploy.sh` - Incomplete deployment script to complete
- `Dockerfile` - Sample application Dockerfile
- `app.py` - Sample application

## Expected Usage

```bash
# Set required environment variables
export AWS_REGION=us-east-1
export REPO_NAME=my-app
export VERSION=1.0.0

# Run the deployment
./deploy.sh
```

## Steps

1. Review the incomplete `deploy.sh`

2. Implement the missing sections:
   - Prerequisites check
   - ECR repository creation
   - Authentication
   - Build and push logic
   - Error handling

3. Test the script locally (you can use LocalStack for ECR):
   ```bash
   # Start LocalStack (optional)
   docker run -d -p 4566:4566 localstack/localstack

   # Set AWS endpoint for LocalStack
   export AWS_ENDPOINT=http://localhost:4566

   # Run your script
   ./deploy.sh
   ```

## Hints

- Use `set -euo pipefail` for strict error handling
- Get AWS account ID with: `aws sts get-caller-identity --query Account --output text`
- ECR login: `aws ecr get-login-password | docker login --username AWS --password-stdin $REGISTRY`
- Check repository exists: `aws ecr describe-repositories --repository-names $REPO`

## Success Criteria

- [ ] Script validates all prerequisites
- [ ] Creates ECR repository with scanning enabled
- [ ] Authenticates to ECR successfully
- [ ] Builds image with proper tags (version + SHA)
- [ ] Pushes all tags to ECR
- [ ] Handles errors gracefully with clear messages
- [ ] Follows shell scripting best practices
