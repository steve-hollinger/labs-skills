# CLAUDE.md - AI Assistant Guidance

This repository contains 58 self-contained skills for modern software development. Each skill is designed to be learned independently with working examples, tests, and documentation.

## Repository Purpose

Labs-skills is a learning repository where developers can master individual technical skills through hands-on practice. Skills are organized by category and designed to build upon each other.

## Key Commands

```bash
# Repository-level
make infra-up          # Start shared infrastructure (Neo4j, Kafka, DynamoDB, Valkey)
make infra-down        # Stop shared infrastructure
make new-skill         # Create new skill from template

# Skill-level (run from within a skill directory)
make setup             # Install dependencies
make examples          # Run example code
make test              # Run tests
make lint              # Check code quality
```

## Architecture Decisions

### Skill Independence
Each skill is self-contained with its own dependencies. This allows:
- Learning skills in any order
- Running skills without affecting others
- Clear dependency boundaries

### Shared Infrastructure
Common services (Neo4j, Kafka, DynamoDB, Valkey) run via shared docker-compose to avoid duplication.

### Consistent Structure
All skills follow the same layout:
- `README.md` - Entry point with quick start
- `CLAUDE.md` - AI guidance specific to the skill
- `Makefile` - Standard commands
- `docs/` - Detailed documentation
- `src/` or `cmd/` - Working examples
- `exercises/` - Practice problems
- `tests/` - Test coverage

## Working With Skills

### When helping users learn a skill:
1. Start with the skill's README.md for context
2. Reference the skill's CLAUDE.md for specific guidance
3. Use the examples in `src/` or `cmd/` as starting points
4. Point users to `exercises/` for practice
5. Run tests to verify understanding

### When creating or modifying skills:
1. Use templates from `shared/templates/`
2. Follow the existing structure exactly
3. Ensure all Makefile targets work
4. Include at least 3 progressive examples
5. Write comprehensive tests
6. Document patterns in `docs/patterns.md`

## Category Overview

| ID | Category | Skills Count | Focus Area |
|----|----------|--------------|------------|
| 01 | language-frameworks | 14 | Python, Go, Frontend core skills |
| 02 | architecture-design | 7 | Design patterns and architecture |
| 03 | testing | 7 | Testing frameworks and strategies |
| 04 | devops-deployment | 6 | Docker, CI/CD, FSD |
| 05 | data-databases | 7 | Storage, streaming, caching |
| 06 | ai-ml | 5 | LLM integration, search, evaluation |
| 07 | security | 5 | Auth, secrets, validation |
| 08 | documentation | 3 | Standards and practices |
| 09 | code-quality | 4 | Linting, typing, commits |

## Code Style Preferences

### Python
- Use UV for package management
- Ruff for linting (replaces black, isort, flake8)
- MyPy for type checking with strict mode
- Pydantic v2 for data validation

### Go
- golangci-lint with standard config
- Structured logging with constants
- Table-driven tests
- testify for assertions

### Frontend
- Vite 7 for build tooling
- React 19 with TypeScript
- Tailwind CSS 4 for styling
- Vitest for testing

## Common Patterns

### Error Handling
- Python: Use custom exceptions with context
- Go: Wrap errors with `fmt.Errorf("context: %w", err)`

### Configuration
- Python: Dynaconf with environment-based settings
- Go: Viper or environment variables

### Testing
- Always include unit, integration, and example tests
- Use mocks for external services
- Test edge cases and error paths

## File Naming Conventions

- Python: `snake_case.py`
- Go: `snake_case.go`
- Frontend: `PascalCase.tsx` for components, `camelCase.ts` for utilities
- Documentation: `kebab-case.md`
- Directories: `kebab-case/`

## When Users Ask About...

### "How do I start learning?"
Point to the Learning Paths in README.md based on their background.

### "What order should I learn skills?"
Skills are independent but some build on others. Check skill README prerequisites.

### "How do I run examples?"
Navigate to the skill directory and run `make setup && make examples`.

### "How do I verify my understanding?"
Complete the exercises in `exercises/` and run `make test`.

## Infrastructure Details

### DynamoDB Local
- Port: 8000
- No authentication required
- Data persisted in Docker volume

### Neo4j
- Bolt: localhost:7687
- HTTP: localhost:7474
- Username: neo4j
- Password: password

### Kafka
- Bootstrap: localhost:9092
- UI available at localhost:8080

### Valkey (Redis-compatible)
- Port: 6379
- No authentication required

## Important Notes

- Each skill directory has its own CLAUDE.md with specific guidance
- Always read the skill's CLAUDE.md before helping with that skill
- Exercises have solutions in `exercises/solutions/`
- Tests should pass before considering a skill complete
