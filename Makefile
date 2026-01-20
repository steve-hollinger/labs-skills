# Labs Skills - Root Makefile
# Provides repository-wide commands

.PHONY: help infra-up infra-down new-skill test-all lint-all clean-all

# Default target
help:
	@echo "Labs Skills Repository"
	@echo ""
	@echo "Infrastructure:"
	@echo "  make infra-up      Start shared infrastructure (Neo4j, Kafka, DynamoDB, Valkey)"
	@echo "  make infra-down    Stop shared infrastructure"
	@echo "  make infra-logs    View infrastructure logs"
	@echo ""
	@echo "Skill Management:"
	@echo "  make new-skill TYPE=python NAME=skill-name CATEGORY=path"
	@echo "                     Create new skill from template"
	@echo "                     TYPE: python, go, or frontend"
	@echo "                     CATEGORY: e.g., 01-language-frameworks/python"
	@echo ""
	@echo "Repository-wide:"
	@echo "  make test-all      Run tests for all skills"
	@echo "  make lint-all      Run linting for all skills"
	@echo "  make clean-all     Clean all build artifacts"
	@echo ""
	@echo "Examples:"
	@echo "  make new-skill TYPE=python NAME=my-skill CATEGORY=01-language-frameworks/python"
	@echo "  make new-skill TYPE=go NAME=my-skill CATEGORY=01-language-frameworks/go"

# Infrastructure commands
infra-up:
	@echo "Starting shared infrastructure..."
	docker compose -f shared/docker/docker-compose.base.yml up -d
	@echo ""
	@echo "Services started:"
	@echo "  Neo4j:          bolt://localhost:7687 (user: neo4j, pass: password)"
	@echo "  Neo4j Browser:  http://localhost:7474"
	@echo "  Kafka:          localhost:9092"
	@echo "  Kafka UI:       http://localhost:8080"
	@echo "  DynamoDB:       http://localhost:8000"
	@echo "  Valkey:         localhost:6379"

infra-down:
	@echo "Stopping shared infrastructure..."
	docker compose -f shared/docker/docker-compose.base.yml down

infra-logs:
	docker compose -f shared/docker/docker-compose.base.yml logs -f

# Create new skill from template
new-skill:
ifndef TYPE
	$(error TYPE is required. Use TYPE=python, TYPE=go, or TYPE=frontend)
endif
ifndef NAME
	$(error NAME is required. Example: NAME=my-new-skill)
endif
ifndef CATEGORY
	$(error CATEGORY is required. Example: CATEGORY=01-language-frameworks/python)
endif
	@echo "Creating new $(TYPE) skill: $(NAME) in $(CATEGORY)"
	@./shared/scripts/create-skill.sh $(TYPE) $(NAME) $(CATEGORY)
	@echo "Skill created at $(CATEGORY)/$(NAME)"
	@echo "Next steps:"
	@echo "  1. cd $(CATEGORY)/$(NAME)"
	@echo "  2. Edit README.md and CLAUDE.md"
	@echo "  3. Add examples to src/ or cmd/"
	@echo "  4. Add exercises to exercises/"
	@echo "  5. Write tests in tests/"

# Run tests for all skills
test-all:
	@echo "Running tests for all skills..."
	@find . -name "Makefile" -not -path "./Makefile" -not -path "./shared/*" | while read f; do \
		dir=$$(dirname "$$f"); \
		echo "Testing: $$dir"; \
		(cd "$$dir" && make test 2>/dev/null || echo "  No tests or test failed"); \
	done

# Run linting for all skills
lint-all:
	@echo "Running linting for all skills..."
	@find . -name "Makefile" -not -path "./Makefile" -not -path "./shared/*" | while read f; do \
		dir=$$(dirname "$$f"); \
		echo "Linting: $$dir"; \
		(cd "$$dir" && make lint 2>/dev/null || echo "  No lint target or lint failed"); \
	done

# Clean all build artifacts
clean-all:
	@echo "Cleaning all build artifacts..."
	@find . -name "Makefile" -not -path "./Makefile" -not -path "./shared/*" | while read f; do \
		dir=$$(dirname "$$f"); \
		(cd "$$dir" && make clean 2>/dev/null || true); \
	done
	@find . -type d -name "__pycache__" -exec rm -rf {} + 2>/dev/null || true
	@find . -type d -name ".pytest_cache" -exec rm -rf {} + 2>/dev/null || true
	@find . -type d -name ".mypy_cache" -exec rm -rf {} + 2>/dev/null || true
	@find . -type d -name ".ruff_cache" -exec rm -rf {} + 2>/dev/null || true
	@find . -type d -name "node_modules" -exec rm -rf {} + 2>/dev/null || true
	@find . -type d -name "dist" -exec rm -rf {} + 2>/dev/null || true
	@echo "Clean complete"
