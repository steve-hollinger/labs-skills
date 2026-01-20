---
name: implementing-hybrid-auth
description: Implementing multi-strategy authentication systems that combine JWT tokens with API keys. Use when implementing authentication or verifying tokens.
---

# Hybrid Authentication

## Quick Start
```go
type Principal interface {
    GetID() string
    GetType() PrincipalType
    HasPermission(permission string) bool
    GetRoles() []string
}

type PrincipalType string

const (
    PrincipalTypeUser    PrincipalType = "user"
    PrincipalTypeService PrincipalType = "service"
)
```


## Key Points
- JWT Authentication
- API Key Authentication
- Principal

## Common Mistakes
1. **Not checking token expiration** - Always validate exp claim before trusting token
2. **Using weak secrets** - Use cryptographically random secrets (32+ bytes)
3. **Exposing internal errors** - Log detailed errors internally, return generic messages

## More Detail
- [docs/concepts.md](docs/concepts.md) - Core concepts and theory
- [docs/patterns.md](docs/patterns.md) - Full code patterns and examples