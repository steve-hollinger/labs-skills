# ios-localization - iOS/Swift Skill Makefile

.PHONY: setup build examples example-1 example-2 example-3 test lint clean

# Resolve dependencies
setup:
	swift package resolve

# Build the package
build:
	swift build

# Run all examples
examples: example-1 example-2 example-3

# Individual examples
example-1:
	swift run Example1

example-2:
	swift run Example2

example-3:
	swift run Example3

# Run tests
test:
	swift test

# Run tests with verbose output
test-verbose:
	swift test --verbose

# Run linting (requires SwiftLint)
lint:
	@if command -v swiftlint >/dev/null 2>&1; then \
		swiftlint lint Sources/ Tests/; \
	else \
		echo "SwiftLint not installed. Install with: brew install swiftlint"; \
	fi

# Format code (requires swift-format)
format:
	@if command -v swift-format >/dev/null 2>&1; then \
		swift-format format -i -r Sources/ Tests/; \
	else \
		echo "swift-format not installed. Install with: brew install swift-format"; \
	fi

# Clean build artifacts
clean:
	swift package clean
	rm -rf .build
	rm -rf .swiftpm
