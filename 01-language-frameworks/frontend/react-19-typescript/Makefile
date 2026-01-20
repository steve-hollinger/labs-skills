# React 19 + TypeScript - Skill Makefile

.PHONY: setup dev build preview examples example-1 example-2 example-3 example-4 test lint format clean

# Install dependencies
setup:
	npm install

# Start development server with HMR
dev:
	npm run dev

# Build for production
build:
	npm run build

# Preview production build
preview:
	npm run preview

# Run all examples
examples: example-1 example-2 example-3 example-4

# Individual examples
example-1:
	@echo "=== Example 1: Component Basics ==="
	@echo "Demonstrates typed components, props, and basic patterns"
	npx tsx src/examples/01-component-basics/main.tsx

example-2:
	@echo "=== Example 2: Hooks Deep Dive ==="
	@echo "Shows useState, useEffect, useReducer, and custom hooks"
	npx tsx src/examples/02-hooks-deep-dive/main.tsx

example-3:
	@echo "=== Example 3: React 19 Features ==="
	@echo "Explores use(), Actions, and new capabilities"
	npx tsx src/examples/03-react-19-features/main.tsx

example-4:
	@echo "=== Example 4: Advanced Patterns ==="
	@echo "Context, composition, and performance patterns"
	npx tsx src/examples/04-advanced-patterns/main.tsx

# Run tests with Vitest
test:
	npm run test

# Run tests in watch mode
test-watch:
	npm run test:watch

# Run tests with coverage
test-coverage:
	npm run test:coverage

# Run linting
lint:
	npm run lint

# Format code
format:
	npm run format

# Clean build artifacts
clean:
	rm -rf dist node_modules .vite
	rm -rf coverage
	find . -type d -name ".cache" -exec rm -rf {} + 2>/dev/null || true

# Type check without emitting
typecheck:
	npx tsc --noEmit

# Create new component
new-component:
	@read -p "Component name (PascalCase): " name; \
	mkdir -p src/components/$$name; \
	echo "export { default } from './$$name'" > src/components/$$name/index.ts; \
	echo "Created src/components/$$name/"
