# Labs Skills Repository

A comprehensive collection of 58 self-contained **Agent Skills** for modern software development. Each skill follows [Anthropic's Agent Skills format](https://docs.anthropic.com/en/docs/claude-code/agent-skills) with a `SKILL.md` file that enables AI assistants to apply the skill effectively.

Each skill is independent with working examples, tests, and reference documentation.

## Quick Start

```bash
# Clone the repository
git clone <repository-url>
cd labs-skills

# Navigate to a skill
cd 01-language-frameworks/python/fastapi-basics

# View the skill definition
cat SKILL.md
```

## Repository Structure

```
labs-skills/
├── shared/templates/                # Skill scaffolding templates
├── 01-language-frameworks/          # Python, Go, Frontend
├── 02-architecture-design/          # Design patterns
├── 03-testing/                      # Testing frameworks
├── 04-devops-deployment/            # Infrastructure and deployment
├── 05-data-databases/               # Storage and streaming
├── 06-ai-ml/                        # AI/ML integration
├── 07-security/                     # Security practices
├── 08-documentation/                # Documentation standards
└── 09-code-quality/                 # Linting and standards
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

## Skill Structure

Every skill follows [Anthropic's Agent Skills format](https://docs.anthropic.com/en/docs/claude-code/agent-skills):

```
skill-name/
├── SKILL.md            # Agent skill definition (YAML frontmatter + guidance)
├── docs/
│   ├── concepts.md     # Core concepts
│   └── patterns.md     # Code patterns and examples
└── README.md           # Overview
```

### SKILL.md Format

```yaml
---
name: building-fastapi-services
description: Build REST APIs with FastAPI. Use when creating Python web services.
---

# FastAPI Basics

## Quick Start
(concise example code)

## Key Points
(2-3 bullet points)

## Common Mistakes
(pitfalls to avoid)
```

The `name` uses gerund form (verb-ing) and `description` includes a "Use when..." trigger phrase.

## Contributing

See [CONTRIBUTING.md](./CONTRIBUTING.md) for guidelines on adding new skills.

## Skill Index

See [SKILL_INDEX.md](./SKILL_INDEX.md) for a complete alphabetical index of all skills.

## License

MIT License - See [LICENSE](./LICENSE) for details.
