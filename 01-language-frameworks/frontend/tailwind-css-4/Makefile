# Tailwind CSS 4 - Skill Makefile

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
	@echo "=== Example 1: Layout Fundamentals ==="
	@echo "Flexbox and Grid layouts with Tailwind"
	@echo "Open http://localhost:3000/examples/01-layout-fundamentals"
	npm run dev

example-2:
	@echo "=== Example 2: Component Patterns ==="
	@echo "Cards, buttons, forms, and navigation"
	@echo "Open http://localhost:3000/examples/02-component-patterns"
	npm run dev

example-3:
	@echo "=== Example 3: Responsive Design ==="
	@echo "Mobile-first responsive layouts"
	@echo "Open http://localhost:3000/examples/03-responsive-design"
	npm run dev

example-4:
	@echo "=== Example 4: Dark Mode & Theming ==="
	@echo "Theme switching and custom color schemes"
	@echo "Open http://localhost:3000/examples/04-dark-mode-theming"
	npm run dev

# Run tests
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
	find . -type d -name ".cache" -exec rm -rf {} + 2>/dev/null || true

# Show Tailwind classes used
analyze:
	@echo "Analyzing Tailwind classes..."
	@grep -rhoE 'class="[^"]*"' src/ | sort | uniq -c | sort -rn | head -50

# Create component template
new-component:
	@read -p "Component name (PascalCase): " name; \
	mkdir -p src/components; \
	echo "Creating component: $$name"
