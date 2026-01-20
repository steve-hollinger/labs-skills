# Docker/ECR Skill Makefile

.PHONY: setup examples example-1 example-2 example-3 lint scan clean help

# Default target
help:
	@echo "Docker/ECR Skill"
	@echo ""
	@echo "Examples:"
	@echo "  make examples    Build all example images"
	@echo "  make example-1   Build basic Python example"
	@echo "  make example-2   Build multi-stage Go example"
	@echo "  make example-3   Build secure Node.js example"
	@echo ""
	@echo "Quality:"
	@echo "  make lint        Lint Dockerfiles with hadolint"
	@echo "  make scan        Scan images for vulnerabilities"
	@echo ""
	@echo "Other:"
	@echo "  make setup       Verify Docker installation"
	@echo "  make clean       Remove built images"

# Verify Docker is available
setup:
	@echo "Checking Docker installation..."
	@docker --version || (echo "Docker not found. Please install Docker." && exit 1)
	@echo "Docker is available."
	@echo ""
	@echo "Optional tools:"
	@which hadolint > /dev/null 2>&1 && echo "  hadolint: installed" || echo "  hadolint: not installed (brew install hadolint)"
	@which trivy > /dev/null 2>&1 && echo "  trivy: installed" || echo "  trivy: not installed (brew install trivy)"

# Run all examples
examples: example-1 example-2 example-3
	@echo ""
	@echo "All examples built successfully!"
	@docker images | grep "labs-skills"

# Example 1: Basic Python
example-1:
	@echo "Building Example 1: Basic Python Application..."
	docker build -t labs-skills/python-basic:latest ./examples/01-python-basic/
	@echo "Image size:"
	@docker images labs-skills/python-basic:latest --format "{{.Size}}"

# Example 2: Multi-stage Go
example-2:
	@echo "Building Example 2: Multi-Stage Go Build..."
	docker build -t labs-skills/go-multistage:latest ./examples/02-go-multistage/
	@echo "Image size:"
	@docker images labs-skills/go-multistage:latest --format "{{.Size}}"

# Example 3: Secure Node.js
example-3:
	@echo "Building Example 3: Secure Node.js..."
	docker build -t labs-skills/node-secure:latest ./examples/03-node-secure/
	@echo "Image size:"
	@docker images labs-skills/node-secure:latest --format "{{.Size}}"

# Lint Dockerfiles
lint:
	@echo "Linting Dockerfiles..."
	@if which hadolint > /dev/null 2>&1; then \
		find . -name "Dockerfile" -exec hadolint {} \;; \
	else \
		echo "hadolint not installed. Install with: brew install hadolint"; \
		exit 1; \
	fi

# Scan images for vulnerabilities
scan:
	@echo "Scanning images for vulnerabilities..."
	@if which trivy > /dev/null 2>&1; then \
		trivy image --severity HIGH,CRITICAL labs-skills/python-basic:latest || true; \
		trivy image --severity HIGH,CRITICAL labs-skills/go-multistage:latest || true; \
		trivy image --severity HIGH,CRITICAL labs-skills/node-secure:latest || true; \
	else \
		echo "trivy not installed. Install with: brew install trivy"; \
		exit 1; \
	fi

# Run example containers
run-1:
	docker run --rm -p 8000:8000 labs-skills/python-basic:latest

run-2:
	docker run --rm -p 8080:8080 labs-skills/go-multistage:latest

run-3:
	docker run --rm -p 3000:3000 labs-skills/node-secure:latest

# Clean built images
clean:
	@echo "Removing built images..."
	-docker rmi labs-skills/python-basic:latest 2>/dev/null
	-docker rmi labs-skills/go-multistage:latest 2>/dev/null
	-docker rmi labs-skills/node-secure:latest 2>/dev/null
	@echo "Clean complete"

# ECR helpers (require AWS CLI)
ecr-login:
	@echo "Logging into ECR..."
	@if [ -z "$$AWS_REGION" ]; then echo "Set AWS_REGION environment variable"; exit 1; fi
	@if [ -z "$$ECR_REGISTRY" ]; then echo "Set ECR_REGISTRY environment variable"; exit 1; fi
	aws ecr get-login-password --region $$AWS_REGION | \
		docker login --username AWS --password-stdin $$ECR_REGISTRY

ecr-create-repo:
	@if [ -z "$$AWS_REGION" ]; then echo "Set AWS_REGION environment variable"; exit 1; fi
	@if [ -z "$$REPO_NAME" ]; then echo "Set REPO_NAME environment variable"; exit 1; fi
	aws ecr create-repository \
		--repository-name $$REPO_NAME \
		--image-scanning-configuration scanOnPush=true \
		--region $$AWS_REGION

ecr-push:
	@if [ -z "$$ECR_REGISTRY" ]; then echo "Set ECR_REGISTRY environment variable"; exit 1; fi
	@if [ -z "$$REPO_NAME" ]; then echo "Set REPO_NAME environment variable"; exit 1; fi
	@if [ -z "$$IMAGE_TAG" ]; then echo "Set IMAGE_TAG environment variable"; exit 1; fi
	docker tag $$REPO_NAME:$$IMAGE_TAG $$ECR_REGISTRY/$$REPO_NAME:$$IMAGE_TAG
	docker push $$ECR_REGISTRY/$$REPO_NAME:$$IMAGE_TAG
