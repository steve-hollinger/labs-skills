.PHONY: setup examples test lint clean help example-1 example-2 example-3

# Default target
help:
	@echo "Conventional Commits Skill"
	@echo ""
	@echo "Usage: make [target]"
	@echo ""
	@echo "Targets:"
	@echo "  setup      Install commitlint, husky, and dependencies"
	@echo "  examples   Run all example demonstrations"
	@echo "  example-1  Run basic commits example"
	@echo "  example-2  Run scoped commits example"
	@echo "  example-3  Run breaking changes example"
	@echo "  test       Test commitlint configuration"
	@echo "  lint       Validate commit message format"
	@echo "  clean      Remove node_modules and build artifacts"
	@echo "  help       Show this help message"

# Install all dependencies
setup:
	@echo "Installing dependencies..."
	npm install
	@echo ""
	@echo "Initializing Husky git hooks..."
	npx husky init 2>/dev/null || true
	@echo ""
	@echo "Setup complete! Commitlint and Husky are ready."
	@echo ""
	@echo "To test your setup, run: make test"

# Run all examples
examples: example-1 example-2 example-3

# Run Example 1: Basic Commits
example-1:
	@echo "=========================================="
	@echo "Example 1: Basic Commit Messages"
	@echo "=========================================="
	@npm run example:1

# Run Example 2: Scoped Commits
example-2:
	@echo "=========================================="
	@echo "Example 2: Scoped Commit Messages"
	@echo "=========================================="
	@npm run example:2

# Run Example 3: Breaking Changes
example-3:
	@echo "=========================================="
	@echo "Example 3: Breaking Changes"
	@echo "=========================================="
	@npm run example:3

# Test commitlint configuration
test:
	@echo "Testing commitlint configuration..."
	@npm run test

# Validate a commit message (can pass MSG="your message")
lint:
	@if [ -z "$(MSG)" ]; then \
		echo "Usage: make lint MSG=\"feat: your commit message\""; \
		echo ""; \
		echo "Testing with default valid message..."; \
		echo "feat: add new feature" | npx commitlint; \
	else \
		echo "$(MSG)" | npx commitlint; \
	fi

# Validate commit message interactively
lint-last:
	@echo "Validating last commit message..."
	npx commitlint --from HEAD~1 --to HEAD --verbose

# Clean build artifacts
clean:
	@echo "Cleaning build artifacts..."
	rm -rf node_modules
	rm -rf .husky/_
	rm -f package-lock.json
	@echo "Clean complete."

# Install git hooks manually (if husky init fails)
install-hooks:
	@echo "Installing git hooks manually..."
	mkdir -p .husky
	echo '#!/usr/bin/env sh' > .husky/commit-msg
	echo 'npx --no -- commitlint --edit $$1' >> .husky/commit-msg
	chmod +x .husky/commit-msg
	@echo "Git hooks installed."

# Show commitlint rules
show-rules:
	@echo "Current commitlint rules:"
	@echo ""
	@cat commitlint.config.js | grep -A 100 "rules:"

# Validate multiple messages from a file
validate-file:
	@if [ -z "$(FILE)" ]; then \
		echo "Usage: make validate-file FILE=messages.txt"; \
	else \
		while IFS= read -r line; do \
			echo "Testing: $$line"; \
			echo "$$line" | npx commitlint && echo "  PASS" || echo "  FAIL"; \
			echo ""; \
		done < $(FILE); \
	fi
