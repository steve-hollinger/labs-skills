# GitHub Actions Skill Makefile

.PHONY: lint examples validate test-local clean help

# Default target
help:
	@echo "GitHub Actions Skill"
	@echo ""
	@echo "Validation:"
	@echo "  make lint       Validate workflow YAML syntax"
	@echo "  make validate   Run actionlint (if installed)"
	@echo ""
	@echo "Examples:"
	@echo "  make examples   Show example workflows"
	@echo "  make example-1  Show basic CI example"
	@echo "  make example-2  Show Docker build example"
	@echo "  make example-3  Show reusable workflow example"
	@echo ""
	@echo "Testing:"
	@echo "  make test-local Run workflows locally with act"
	@echo ""
	@echo "Other:"
	@echo "  make setup      Check for required tools"
	@echo "  make clean      Clean any generated files"

# Check for tools
setup:
	@echo "Checking for required tools..."
	@echo ""
	@echo "Required:"
	@which gh > /dev/null 2>&1 && echo "  gh (GitHub CLI): installed" || echo "  gh (GitHub CLI): not installed (brew install gh)"
	@echo ""
	@echo "Optional:"
	@which act > /dev/null 2>&1 && echo "  act: installed" || echo "  act: not installed (brew install act)"
	@which actionlint > /dev/null 2>&1 && echo "  actionlint: installed" || echo "  actionlint: not installed (brew install actionlint)"
	@which yq > /dev/null 2>&1 && echo "  yq: installed" || echo "  yq: not installed (brew install yq)"

# Validate YAML syntax
lint:
	@echo "Validating workflow syntax..."
	@for f in examples/*/*.yml examples/*/*.yaml exercises/*/*.yml exercises/*/*.yaml 2>/dev/null; do \
		if [ -f "$$f" ]; then \
			echo "Checking: $$f"; \
			python3 -c "import yaml; yaml.safe_load(open('$$f'))" 2>&1 || echo "  INVALID YAML"; \
		fi \
	done
	@echo "Done."

# Run actionlint for deeper validation
validate:
	@echo "Running actionlint..."
	@if which actionlint > /dev/null 2>&1; then \
		actionlint examples/*/*.yml examples/*/*.yaml 2>/dev/null || true; \
	else \
		echo "actionlint not installed. Install with: brew install actionlint"; \
	fi

# Show all examples
examples: example-1 example-2 example-3

# Example 1: Basic CI
example-1:
	@echo "============================================"
	@echo "Example 1: Basic CI Pipeline"
	@echo "============================================"
	@echo ""
	@cat examples/01-basic-ci/ci.yml
	@echo ""

# Example 2: Docker Build
example-2:
	@echo "============================================"
	@echo "Example 2: Docker Build and Push"
	@echo "============================================"
	@echo ""
	@cat examples/02-docker-build/docker.yml
	@echo ""

# Example 3: Reusable Workflow
example-3:
	@echo "============================================"
	@echo "Example 3: Reusable Workflow"
	@echo "============================================"
	@echo ""
	@echo "--- Reusable Workflow Definition ---"
	@cat examples/03-reusable-workflow/reusable.yml
	@echo ""
	@echo "--- Caller Workflow ---"
	@cat examples/03-reusable-workflow/caller.yml
	@echo ""

# Test workflows locally with act
test-local:
	@echo "Testing workflows with act..."
	@if which act > /dev/null 2>&1; then \
		echo "Running act on example workflow..."; \
		cd examples/01-basic-ci && act -n; \
	else \
		echo "act not installed. Install with: brew install act"; \
		echo ""; \
		echo "act allows you to run GitHub Actions locally."; \
		echo "See: https://github.com/nektos/act"; \
	fi

# Clean generated files
clean:
	@echo "Cleaning generated files..."
	@rm -rf .act
	@echo "Done."
