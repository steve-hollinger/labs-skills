# {{SKILL_NAME}} - Frontend Skill Makefile

.PHONY: setup dev examples build test lint clean coverage

# Install dependencies
setup:
	npm install

# Start development server
dev:
	npm run dev

# Build and preview examples
examples:
	npm run build
	npm run preview

# Production build
build:
	npm run build

# Run tests
test:
	npm run test

# Run tests with coverage
coverage:
	npm run test:coverage

# Run linting
lint:
	npm run lint
	npm run typecheck

# Fix linting issues
lint-fix:
	npm run lint:fix

# Clean build artifacts
clean:
	rm -rf node_modules dist .vite
