# Vite 7 - Frontend Build Tooling Skill Makefile

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
	@echo "=== Example 1: Basic Vite Setup ==="
	@echo "Demonstrates fundamental Vite project configuration"
	npx tsx src/examples/01-basic-setup/main.ts

example-2:
	@echo "=== Example 2: Development Server Configuration ==="
	@echo "Shows proxy, CORS, and server customization"
	npx tsx src/examples/02-dev-server-config/main.ts

example-3:
	@echo "=== Example 3: Build Optimization ==="
	@echo "Advanced production build configuration"
	npx tsx src/examples/03-build-optimization/main.ts

example-4:
	@echo "=== Example 4: Custom Plugins ==="
	@echo "Creating and using Vite plugins"
	npx tsx src/examples/04-custom-plugins/main.ts

# Run tests with Vitest
test:
	npm run test

# Run tests in watch mode
test-watch:
	npm run test:watch

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

# Analyze bundle size
analyze:
	npx vite-bundle-visualizer

# Create new example
new-example:
	@read -p "Example name (e.g., 05-new-feature): " name; \
	mkdir -p src/examples/$$name; \
	echo "// Example: $$name" > src/examples/$$name/main.ts; \
	echo "Created src/examples/$$name/"

# Validate configuration
validate-config:
	npx tsc --noEmit vite.config.ts
	@echo "Configuration is valid!"
