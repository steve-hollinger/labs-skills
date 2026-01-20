# Example 2: Docker Build and Push

This example demonstrates building and pushing Docker images to GitHub Container Registry.

## Features

- **Multi-tag support**: Branch names, PR numbers, semantic versions, SHA
- **Build caching**: GitHub Actions cache for faster builds
- **Security scanning**: Trivy vulnerability scanning
- **Metadata extraction**: Automatic labels and tags
- **Permissions**: Minimal required permissions

## Workflow Structure

```
build ──────► scan (only on push)
```

## Image Tags Generated

| Trigger | Tags Generated |
|---------|---------------|
| Push to main | `latest`, `main`, `<sha>` |
| Push tag v1.2.3 | `1.2.3`, `1.2`, `v1.2.3` |
| Pull request | `pr-123` (not pushed) |

## Key Patterns Demonstrated

1. **Docker Buildx** - Advanced build features
2. **Metadata action** - Automatic tag/label generation
3. **Build caching** - `cache-from/to: type=gha`
4. **Conditional push** - Don't push on PRs
5. **Security scanning** - Trivy with SARIF output
6. **Permissions** - Explicit minimal permissions

## Usage

1. Copy `docker.yml` to `.github/workflows/docker.yml`
2. Ensure you have a `Dockerfile` in your repository
3. Enable "Write packages" permission in repository settings

## Registry

By default pushes to `ghcr.io/<owner>/<repo>`. To use Docker Hub or ECR:

```yaml
env:
  REGISTRY: docker.io  # or AWS ECR URL
  IMAGE_NAME: myorg/myimage
```
