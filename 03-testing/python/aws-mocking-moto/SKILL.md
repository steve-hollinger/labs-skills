---
name: mocking-aws-with-moto
description: This skill teaches AWS service mocking using the moto library for testing code that interacts with AWS services. Use when writing or improving tests.
---

# Aws Mocking Moto

## Quick Start
```python
from moto import mock_aws

@mock_aws
def test_s3_operations():
    s3 = boto3.client("s3", region_name="us-east-1")
    s3.create_bucket(Bucket="test-bucket")
    # All operations are mocked
```

## Commands
```bash
make setup      # Install dependencies with UV
make examples   # Run all examples
make example-1  # Run specific example
make test       # Run pytest
make lint       # Run ruff and mypy
make clean      # Remove build artifacts
```

## Key Points
- mock_aws Decorator
- Context Manager
- Service-specific Mocks

## Common Mistakes
1. **Missing AWS credentials** - Set AWS_ACCESS_KEY_ID and AWS_SECRET_ACCESS_KEY in fixtures
2. **Creating clients outside mock context** - Create boto3 clients inside the mock_aws context
3. **Forgetting region_name** - Always specify region_name="us-east-1"

## More Detail
- [docs/concepts.md](docs/concepts.md) - Core concepts and theory
- [docs/patterns.md](docs/patterns.md) - Full code patterns and examples