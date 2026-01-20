# Labs Skills

A collection of **68 Agent Skills** for modern software development, following [Anthropic's Agent Skills format](https://docs.anthropic.com/en/docs/claude-code/skills).

## Categories

| ID | Category | Skills | Focus Area |
|----|----------|--------|------------|
| 01 | language-frameworks | 13 | Python, Go, Frontend |
| 02 | architecture-design | 7 | Design patterns and architecture |
| 03 | testing | 7 | Testing frameworks and strategies |
| 04 | devops-deployment | 6 | Docker, CI/CD, FSD |
| 05 | data-databases | 7 | Storage, streaming, caching |
| 06 | ai-ml | 5 | LLM integration, search, evaluation |
| 07 | security | 5 | Auth, secrets, validation |
| 08 | documentation | 4 | Standards and practices |
| 09 | code-quality | 6 | Linting, typing, commits |
| 10 | mobile-dev | 8 | iOS/Swift, SwiftUI |

## Skill Index

<details>
<summary><strong>01 - Language Frameworks (13 skills)</strong></summary>

| Skill | Name | Description |
|-------|------|-------------|
| frontend/react-19-typescript | building-react-typescript-apps | Modern React development with TypeScript |
| frontend/tailwind-css-4 | styling-with-tailwind | Utility-first CSS with Tailwind CSS 4 |
| frontend/vite-7 | building-with-vite | Modern frontend build tooling with Vite 7 |
| go/concurrency | managing-go-concurrency | Go concurrency primitives and patterns |
| go/http-services | building-http-services | HTTP APIs using Go's net/http |
| go/kafka-franz-go | streaming-with-franz-go | High-performance Kafka with franz-go |
| go/mcp-server | building-mcp-servers | MCP servers in Go |
| go/neo4j-driver | using-neo4j-go-driver | Go and Neo4j integration |
| python/dynaconf-config | configuring-with-dynaconf | Configuration management with Dynaconf |
| python/fastapi-basics | building-fastapi-services | Web APIs with FastAPI |
| python/langchain-langgraph | building-langchain-agents | LLM orchestration with LangChain |
| python/pydantic-v2 | validating-with-pydantic | Data validation with Pydantic |
| python/uv-package-manager | managing-python-packages | Fast Python package management with UV |

</details>

<details>
<summary><strong>02 - Architecture Design (7 skills)</strong></summary>

| Skill | Name | Description |
|-------|------|-------------|
| component-system | building-component-systems | Modular component architecture patterns |
| dual-mode-streaming | implementing-dual-mode-streaming | Sync and async API patterns |
| episode-based-history | managing-episode-history | Conversation history management |
| factory-pattern | implementing-factory-patterns | Factory pattern for object creation |
| four-layer-prompts | structuring-four-layer-prompts | Structured prompt organization |
| hybrid-authentication | implementing-hybrid-auth | Multi-strategy authentication |
| tool-registry | building-tool-registries | Dynamic tool management patterns |

</details>

<details>
<summary><strong>03 - Testing (7 skills)</strong></summary>

| Skill | Name | Description |
|-------|------|-------------|
| go/race-detector | detecting-go-race-conditions | Race condition detection in Go |
| go/test-logger-init | initializing-test-loggers | Test initialization patterns |
| go/testcontainers | testing-with-containers | Integration testing with Testcontainers |
| go/testify-framework | testing-with-testify | Go testing with Testify |
| python/aws-mocking-moto | mocking-aws-with-moto | AWS mocking with moto |
| python/pytest-asyncio | testing-async-python | Async testing with pytest-asyncio |
| python/pytest-markers | organizing-pytest-markers | Pytest markers for organization |

</details>

<details>
<summary><strong>04 - DevOps & Deployment (6 skills)</strong></summary>

| Skill | Name | Description |
|-------|------|-------------|
| docker-compose | composing-docker-services | Multi-container orchestration |
| docker-ecr | building-docker-images | Docker and AWS ECR workflows |
| fsd-dependencies | defining-fsd-dependencies | FSD dependency configuration |
| fsd-iam-policies | creating-iam-policies | IAM policies for FSD services |
| fsd-yaml-config | configuring-fsd-services | FSD YAML configuration |
| github-actions | automating-with-github-actions | CI/CD with GitHub Actions |

</details>

<details>
<summary><strong>05 - Data & Databases (7 skills)</strong></summary>

| Skill | Name | Description |
|-------|------|-------------|
| dynamodb-schema | designing-dynamodb-schemas | DynamoDB schema design |
| dynamodb-streams-cdc | streaming-dynamodb-changes | Change data capture with DynamoDB |
| kafka-event-streaming | streaming-kafka-events | Event-driven architecture with Kafka |
| neo4j-cypher | querying-with-cypher | Cypher query language |
| neo4j-date-datetime | handling-neo4j-dates | Temporal data in Neo4j |
| s3-content-addressed | storing-content-addressed-s3 | Content-addressed storage with S3 |
| valkey-redis | caching-with-valkey | Caching with Valkey/Redis |

</details>

<details>
<summary><strong>06 - AI/ML (5 skills)</strong></summary>

| Skill | Name | Description |
|-------|------|-------------|
| hybrid-search | implementing-hybrid-search | Vector + keyword search |
| mcp-tool-schemas | designing-mcp-tool-schemas | MCP tool schema design |
| openai-responses-api | using-openai-responses-api | OpenAI API integration |
| opik-evaluation | evaluating-with-opik | LLM evaluation with Opik |
| sse-streaming | streaming-server-sent-events | SSE for LLM streaming |

</details>

<details>
<summary><strong>07 - Security (5 skills)</strong></summary>

| Skill | Name | Description |
|-------|------|-------------|
| api-key-auth | implementing-api-key-auth | API key authentication |
| jwt-validation | validating-jwt-tokens | JWT token validation |
| oauth-21-oidc | implementing-oauth-oidc | OAuth 2.1 and OIDC |
| secrets-manager | managing-aws-secrets | AWS Secrets Manager |
| token-masking | masking-sensitive-tokens | Sensitive data masking |

</details>

<details>
<summary><strong>08 - Documentation (4 skills)</strong></summary>

| Skill | Name | Description |
|-------|------|-------------|
| claude-md-standards | writing-claude-md-files | Writing CLAUDE.md files |
| component-documentation | documenting-components | Component documentation |
| skill-writing | writing-agent-skills | Creating Agent Skills |
| system-prompts | crafting-system-prompts | System prompt engineering |

</details>

<details>
<summary><strong>09 - Code Quality (6 skills)</strong></summary>

| Skill | Name | Description |
|-------|------|-------------|
| commit-standards | writing-commit-messages | Conventional commit messages |
| go/golangci-lint | linting-go-code | Go linting with golangci-lint |
| go/logging-constants | defining-logging-constants | Structured logging in Go |
| python/bandit-security | scanning-python-security | Security scanning with Bandit |
| python/mypy-type-checking | type-checking-with-mypy | Type checking with MyPy |
| python/ruff-linting | linting-with-ruff | Fast Python linting with Ruff |

</details>

<details>
<summary><strong>10 - Mobile Development (8 skills)</strong></summary>

| Skill | Name | Description |
|-------|------|-------------|
| ios/ios-analytics | implementing-ios-analytics | iOS analytics and tracking |
| ios/ios-chat-history | building-chat-history | Chat history management |
| ios/ios-localization | localizing-ios-apps | iOS localization |
| ios/ios-networking | networking-with-async-await | iOS networking with async/await |
| ios/swift-6-concurrency | migrating-to-swift-6 | Swift 6 concurrency migration |
| ios/swiftui-animations | animating-swiftui-views | SwiftUI animations |
| ios/swiftui-architecture | structuring-swiftui-apps | SwiftUI app architecture |
| ios/swiftui-state-management | managing-swiftui-state | SwiftUI state management |

</details>

## Skill Structure

Each skill follows the minimal Agent Skills layout:

```
skill-name/
├── SKILL.md            # YAML frontmatter + guidance
└── docs/
    ├── concepts.md     # Core concepts
    └── patterns.md     # Code patterns
```

## Using with Claude Code

### Option 1: Clone as Project Skills

```bash
git clone https://github.com/steve-hollinger/labs-skills.git
cd labs-skills
claude  # Skills are discovered from nested directories
```

### Option 2: Copy Skills Manually

```bash
# Copy specific skills to your global skills directory
cp -r 01-language-frameworks/python/fastapi-basics ~/.claude/skills/

# Or to a project's local skills
cp -r 07-security/jwt-validation ./your-project/.claude/skills/
```

### Option 3: Symlink for Development

```bash
# Symlink entire categories
ln -s /path/to/labs-skills/01-language-frameworks ~/.claude/skills/language-frameworks
```

## SKILL.md Format

Skills use YAML frontmatter with a gerund-form name and trigger description:

```yaml
---
name: building-fastapi-services
description: Build REST APIs with FastAPI. Use when creating Python web services.
---

# FastAPI Basics

## Quick Start
(concise example code)

## Key Points
- Point 1
- Point 2

## Common Mistakes
1. **Mistake name** - Brief explanation

## More Detail
- docs/concepts.md
- docs/patterns.md
```

## License

MIT
