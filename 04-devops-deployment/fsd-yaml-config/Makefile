# FSD YAML Config - Makefile

.PHONY: validate-all validate exercises check-solutions lint clean help

# Default YAML file for single validation
YAML ?= examples/01-basic-ecs-service.yml

# Validate all example YAML files
validate-all:
	@echo "Validating all FSD YAML examples..."
	@for file in examples/*.yml; do \
		echo "Validating $$file..."; \
		yamllint -c .yamllint.yml $$file || exit 1; \
		echo "  $$file: OK"; \
	done
	@echo "All validations passed!"

# Validate a specific YAML file
validate:
	@echo "Validating $(YAML)..."
	@yamllint -c .yamllint.yml $(YAML)
	@echo "$(YAML): Valid YAML syntax"
	@echo "Checking required fields..."
	@yq eval '.name' $(YAML) > /dev/null || (echo "Error: missing 'name' field" && exit 1)
	@yq eval '.platform' $(YAML) > /dev/null || (echo "Error: missing 'platform' field" && exit 1)
	@yq eval '.compute' $(YAML) > /dev/null || (echo "Error: missing 'compute' field" && exit 1)
	@echo "$(YAML): All required fields present"

# List available exercises
exercises:
	@echo "Available FSD YAML Exercises:"
	@echo ""
	@echo "  1. exercise-1-docker-to-fsd.md   - Convert Docker Compose to FSD"
	@echo "  2. exercise-2-eks-microservice.md - Write an EKS deployment"
	@echo "  3. exercise-3-lambda-triggers.md  - Lambda with multiple triggers"
	@echo "  4. exercise-4-batch-pipeline.md   - Batch processing pipeline"
	@echo ""
	@echo "Read exercise files in exercises/ directory"
	@echo "Submit solutions to exercises/solutions/"

# Validate exercise solutions
check-solutions:
	@echo "Validating exercise solutions..."
	@for file in exercises/solutions/*.yml; do \
		echo "Checking $$file..."; \
		yamllint -c .yamllint.yml $$file || exit 1; \
		yq eval '.name' $$file > /dev/null || (echo "Error: missing 'name' in $$file" && exit 1); \
		yq eval '.platform' $$file > /dev/null || (echo "Error: missing 'platform' in $$file" && exit 1); \
		echo "  $$file: OK"; \
	done
	@echo "All solutions validated!"

# Run YAML linting
lint:
	@echo "Linting all YAML files..."
	@yamllint -c .yamllint.yml examples/ exercises/solutions/

# Show example for a platform
show-ecs-example:
	@cat examples/01-basic-ecs-service.yml

show-eks-example:
	@cat examples/02-eks-worker-service.yml

show-lambda-example:
	@cat examples/03-lambda-event-handler.yml

show-batch-example:
	@cat examples/04-batch-data-processor.yml

# Setup (install required tools)
setup:
	@echo "Installing required tools..."
	@which yamllint > /dev/null || pip install yamllint
	@which yq > /dev/null || brew install yq
	@echo "Setup complete!"

# Clean temporary files
clean:
	@rm -f *.tmp
	@rm -rf __pycache__
	@echo "Cleaned!"

# Help
help:
	@echo "FSD YAML Config - Available Commands"
	@echo ""
	@echo "  make setup           - Install required tools (yamllint, yq)"
	@echo "  make validate-all    - Validate all example YAML files"
	@echo "  make validate YAML=f - Validate a specific YAML file"
	@echo "  make exercises       - List available exercises"
	@echo "  make check-solutions - Validate exercise solutions"
	@echo "  make lint           - Run YAML linting"
	@echo "  make clean          - Remove temporary files"
	@echo ""
	@echo "  make show-ecs-example    - Display ECS example"
	@echo "  make show-eks-example    - Display EKS example"
	@echo "  make show-lambda-example - Display Lambda example"
	@echo "  make show-batch-example  - Display Batch example"
