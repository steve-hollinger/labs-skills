# FSD Dependencies - Makefile

.PHONY: validate-all validate exercises check-solutions lint clean help

# Default YAML file for single validation
YAML ?= examples/01-dynamodb-dependency.yml

# Validate all example YAML files
validate-all:
	@echo "Validating all FSD dependency examples..."
	@for file in examples/*.yml; do \
		echo "Validating $$file..."; \
		yamllint -c .yamllint.yml $$file || exit 1; \
		echo "  Checking dependencies block..."; \
		yq eval '.dependencies' $$file > /dev/null || (echo "Error: missing 'dependencies' in $$file" && exit 1); \
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
	@yq eval '.dependencies' $(YAML) > /dev/null || (echo "Error: missing 'dependencies' field" && exit 1)
	@echo "Checking dependency structure..."
	@yq eval '.dependencies[].type' $(YAML) > /dev/null || (echo "Error: dependencies missing 'type'" && exit 1)
	@yq eval '.dependencies[].name' $(YAML) > /dev/null || (echo "Error: dependencies missing 'name'" && exit 1)
	@echo "$(YAML): All required fields present"

# Validate dependency types
validate-types:
	@echo "Validating dependency types in $(YAML)..."
	@yq eval '.dependencies[].type' $(YAML) | while read type; do \
		case "$$type" in \
			aws_dynamodb_table|aws_s3_bucket|aws_sqs_queue|aws_sns_topic|aws_kinesis_stream|aws_rds_instance|aws_elasticache|kafka_topic|service) \
				echo "  $$type: valid" ;; \
			*) \
				echo "  $$type: INVALID" && exit 1 ;; \
		esac \
	done

# List available exercises
exercises:
	@echo "Available FSD Dependencies Exercises:"
	@echo ""
	@echo "  1. exercise-1-dynamodb-tables.md  - Add DynamoDB tables to a service"
	@echo "  2. exercise-2-s3-lifecycle.md     - Configure S3 with lifecycle policies"
	@echo "  3. exercise-3-kafka-setup.md      - Set up Kafka consumer/producer"
	@echo "  4. exercise-4-service-graph.md    - Design multi-service dependency graph"
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
		yq eval '.dependencies' $$file > /dev/null || (echo "Error: missing 'dependencies' in $$file" && exit 1); \
		echo "  $$file: OK"; \
	done
	@echo "All solutions validated!"

# Show example for a dependency type
show-dynamodb-example:
	@cat examples/01-dynamodb-dependency.yml

show-s3-example:
	@cat examples/02-s3-sqs-dependencies.yml

show-kafka-example:
	@cat examples/03-kafka-dependencies.yml

show-rds-example:
	@cat examples/04-rds-dependency.yml

show-service-example:
	@cat examples/05-cross-service-dependencies.yml

# List dependencies from a YAML file
list-deps:
	@echo "Dependencies in $(YAML):"
	@yq eval '.dependencies[] | "  - " + .type + ": " + .name + " (" + .mode + ")"' $(YAML)

# Run YAML linting
lint:
	@echo "Linting all YAML files..."
	@yamllint -c .yamllint.yml examples/ exercises/solutions/

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
	@echo "FSD Dependencies - Available Commands"
	@echo ""
	@echo "  make setup            - Install required tools (yamllint, yq)"
	@echo "  make validate-all     - Validate all example YAML files"
	@echo "  make validate YAML=f  - Validate a specific YAML file"
	@echo "  make validate-types   - Validate dependency types"
	@echo "  make list-deps YAML=f - List dependencies in a file"
	@echo "  make exercises        - List available exercises"
	@echo "  make check-solutions  - Validate exercise solutions"
	@echo "  make lint            - Run YAML linting"
	@echo "  make clean           - Remove temporary files"
	@echo ""
	@echo "  make show-dynamodb-example - Display DynamoDB example"
	@echo "  make show-s3-example       - Display S3/SQS example"
	@echo "  make show-kafka-example    - Display Kafka example"
	@echo "  make show-rds-example      - Display RDS example"
	@echo "  make show-service-example  - Display cross-service example"
