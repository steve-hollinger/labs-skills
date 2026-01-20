# Labs Skills Repository

A comprehensive collection of 58 self-contained **Agent Skills** for modern software development. Each skill follows [Anthropic's Agent Skills format](https://docs.anthropic.com/en/docs/claude-code/agent-skills) with a `SKILL.md` file that enables AI assistants to apply the skill effectively.

Each skill is independent with working examples, tests, and reference documentation.

## Quick Start

```bash
# Clone the repository
git clone <repository-url>
cd labs-skills

# Start shared infrastructure (Neo4j, Kafka, DynamoDB-local, Valkey)
make infra-up

# Navigate to a skill
cd 01-language-frameworks/python/fastapi-basics

# Install dependencies and run examples
make setup
make examples
make test
```

## Repository Structure

```
labs-skills/
├── shared/                          # Shared infrastructure & templates
│   ├── docker/                      # Base docker-compose for services
│   ├── templates/                   # Skill scaffolding templates
│   └── scripts/                     # Automation scripts
├── 01-language-frameworks/          # Programming languages & frameworks
│   ├── python/                      # Python ecosystem
│   ├── go/                          # Go ecosystem
│   └── frontend/                    # Frontend technologies
├── 02-architecture-design/          # Design patterns & architecture
├── 03-testing/                      # Testing frameworks & strategies
│   ├── python/                      # Python testing
│   └── go/                          # Go testing
├── 04-devops-deployment/            # DevOps & deployment tools
├── 05-data-databases/               # Data storage & streaming
├── 06-ai-ml/                        # AI/ML & LLM integration
├── 07-security/                     # Security practices
├── 08-documentation/                # Documentation standards
└── 09-code-quality/                 # Code quality tools
    ├── python/                      # Python linting/typing
    ├── go/                          # Go linting
    └── commit-standards/            # Commit conventions
```

## Categories Overview

| Category | Skills | Description |
|----------|--------|-------------|
| [01-language-frameworks](./01-language-frameworks/) | 14 | Core language skills (Python, Go, Frontend) |
| [02-architecture-design](./02-architecture-design/) | 7 | Design patterns and architectural decisions |
| [03-testing](./03-testing/) | 7 | Testing frameworks and strategies |
| [04-devops-deployment](./04-devops-deployment/) | 6 | Infrastructure and deployment |
| [05-data-databases](./05-data-databases/) | 7 | Data storage, streaming, and caching |
| [06-ai-ml](./06-ai-ml/) | 5 | AI/ML integration and tooling |
| [07-security](./07-security/) | 5 | Security best practices |
| [08-documentation](./08-documentation/) | 3 | Documentation standards |
| [09-code-quality](./09-code-quality/) | 4 | Linting, typing, and standards |

## How Each Skill Works

Every skill follows a consistent structure using [Anthropic's Agent Skills format](https://docs.anthropic.com/en/docs/claude-code/agent-skills):

```
skill-name/
├── SKILL.md            # Agent skill definition (YAML frontmatter + guidance)
├── README.md           # Overview and quick start
├── pyproject.toml      # Dependencies (Python) or go.mod (Go)
├── Makefile            # Standard commands
├── docs/               # Reference documentation
│   ├── concepts.md     # Core concepts
│   └── patterns.md     # Common patterns
├── src/                # Working examples
└── tests/              # Test suite
```

### SKILL.md Format

Each skill includes a `SKILL.md` file with YAML frontmatter:

```yaml
---
name: building-fastapi-services
description: Build REST APIs with FastAPI. Use when creating Python web services.
---

# FastAPI Basics

## Quick Start
(concise example code)

## Commands
(make targets)

## Key Points
(2-3 bullet points)
```

The `name` uses gerund form (verb-ing) and `description` includes a "Use when..." trigger phrase.

### Standard Commands

Each skill supports these Makefile targets:

```bash
make setup      # Install dependencies
make examples   # Run example code
make test       # Run tests
make lint       # Check code quality
make clean      # Clean build artifacts
```

## Prerequisites

- Docker and Docker Compose
- Python 3.11+ with UV package manager
- Go 1.22+
- Node.js 20+ (for frontend skills)

## Shared Infrastructure

Start all shared services with:

```bash
make infra-up
```

This starts:
- **Neo4j** - Graph database (bolt://localhost:7687)
- **Kafka** - Event streaming (localhost:9092)
- **DynamoDB Local** - AWS DynamoDB emulator (localhost:8000)
- **Valkey** - Redis-compatible cache (localhost:6379)

Stop services:
```bash
make infra-down
```

## Contributing

See [CONTRIBUTING.md](./CONTRIBUTING.md) for guidelines on adding new skills.

## Skill Index

See [SKILL_INDEX.md](./SKILL_INDEX.md) for a complete alphabetical index of all skills.

## License

MIT License - See [LICENSE](./LICENSE) for details.
