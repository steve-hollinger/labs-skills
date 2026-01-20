# Docker Compose Skill Makefile

.PHONY: setup examples example-1 example-2 example-3 up down logs ps clean help

# Default target
help:
	@echo "Docker Compose Skill"
	@echo ""
	@echo "Examples:"
	@echo "  make examples    Run all examples"
	@echo "  make example-1   Run basic web stack"
	@echo "  make example-2   Run microservices example"
	@echo "  make example-3   Run dev environment"
	@echo ""
	@echo "Operations:"
	@echo "  make up          Start example services"
	@echo "  make down        Stop example services"
	@echo "  make logs        View service logs"
	@echo "  make ps          List running services"
	@echo ""
	@echo "Other:"
	@echo "  make setup       Verify Docker Compose installation"
	@echo "  make clean       Remove all containers, volumes, and images"

# Verify Docker Compose is available
setup:
	@echo "Checking Docker Compose installation..."
	@docker compose version || (echo "Docker Compose not found. Please install Docker." && exit 1)
	@echo ""
	@echo "Docker Compose is available."
	@docker compose version

# Run all examples
examples: example-1-stop example-1 example-2-stop example-2 example-3-stop example-3
	@echo ""
	@echo "All examples completed!"

# Example 1: Basic Web Stack
example-1:
	@echo "============================================"
	@echo "Example 1: Basic Web Stack"
	@echo "============================================"
	cd examples/01-web-stack && docker compose up -d
	@echo ""
	@echo "Services started. Waiting for health..."
	@sleep 5
	cd examples/01-web-stack && docker compose ps
	@echo ""
	@echo "Test the API:"
	@echo "  curl http://localhost:8001/health"
	@echo ""
	@echo "Stop with: make example-1-stop"

example-1-stop:
	@cd examples/01-web-stack && docker compose down -v 2>/dev/null || true

# Example 2: Microservices
example-2:
	@echo "============================================"
	@echo "Example 2: Microservices Architecture"
	@echo "============================================"
	cd examples/02-microservices && docker compose up -d
	@echo ""
	@echo "Services started. Waiting for health..."
	@sleep 10
	cd examples/02-microservices && docker compose ps
	@echo ""
	@echo "Test the gateway:"
	@echo "  curl http://localhost:8002/health"
	@echo ""
	@echo "Stop with: make example-2-stop"

example-2-stop:
	@cd examples/02-microservices && docker compose down -v 2>/dev/null || true

# Example 3: Dev Environment
example-3:
	@echo "============================================"
	@echo "Example 3: Development Environment"
	@echo "============================================"
	cd examples/03-dev-environment && docker compose up -d
	@echo ""
	@echo "Services started."
	cd examples/03-dev-environment && docker compose ps
	@echo ""
	@echo "Development server running at:"
	@echo "  http://localhost:8003"
	@echo ""
	@echo "Stop with: make example-3-stop"

example-3-stop:
	@cd examples/03-dev-environment && docker compose down -v 2>/dev/null || true

# Generic up/down for current directory or specified example
EXAMPLE ?= 01-web-stack

up:
	cd examples/$(EXAMPLE) && docker compose up -d
	cd examples/$(EXAMPLE) && docker compose ps

down:
	cd examples/$(EXAMPLE) && docker compose down

logs:
	cd examples/$(EXAMPLE) && docker compose logs -f

ps:
	cd examples/$(EXAMPLE) && docker compose ps

# Clean everything
clean:
	@echo "Stopping all example services..."
	-cd examples/01-web-stack && docker compose down -v 2>/dev/null
	-cd examples/02-microservices && docker compose down -v 2>/dev/null
	-cd examples/03-dev-environment && docker compose down -v 2>/dev/null
	@echo ""
	@echo "Removing unused Docker resources..."
	docker system prune -f
	@echo ""
	@echo "Clean complete"
