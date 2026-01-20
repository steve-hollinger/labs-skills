# CLAUDE.md - AWS Mocking with moto

This skill teaches AWS service mocking using the moto library for testing code that interacts with AWS services.

## Key Concepts

- **mock_aws Decorator**: Decorates functions to mock all AWS services
- **Context Manager**: `with mock_aws():` for scoped mocking
- **Service-specific Mocks**: mock_dynamodb, mock_s3, mock_sqs for targeted mocking
- **Pytest Integration**: Fixtures that provide mocked AWS resources

## Common Commands

```bash
make setup      # Install dependencies with UV
make examples   # Run all examples
make example-1  # Run specific example
make test       # Run pytest
make lint       # Run ruff and mypy
make clean      # Remove build artifacts
```

## Project Structure

```
aws-mocking-moto/
├── src/aws_mocking_moto/
│   ├── __init__.py
│   └── examples/
│       ├── example_1_dynamodb.py
│       ├── example_2_s3.py
│       ├── example_3_sqs.py
│       └── example_4_fixtures.py
├── exercises/
│   ├── exercise_1.py
│   ├── exercise_2.py
│   ├── exercise_3.py
│   └── solutions/
├── tests/
│   ├── test_dynamodb.py
│   ├── test_s3.py
│   └── test_sqs.py
└── docs/
    ├── concepts.md
    └── patterns.md
```

## Code Patterns

### Pattern 1: Decorator Pattern
```python
from moto import mock_aws

@mock_aws
def test_s3_operations():
    s3 = boto3.client("s3", region_name="us-east-1")
    s3.create_bucket(Bucket="test-bucket")
    # All operations are mocked
```

### Pattern 2: Context Manager Pattern
```python
def test_with_context():
    with mock_aws():
        dynamodb = boto3.resource("dynamodb", region_name="us-east-1")
        # Operations are mocked within the context
```

### Pattern 3: Pytest Fixture Pattern
```python
@pytest.fixture
def dynamodb_table():
    with mock_aws():
        dynamodb = boto3.resource("dynamodb", region_name="us-east-1")
        table = dynamodb.create_table(...)
        yield table
```

### Pattern 4: Multiple Services
```python
@mock_aws
def test_multi_service():
    # Mock multiple services together
    s3 = boto3.client("s3", region_name="us-east-1")
    sqs = boto3.client("sqs", region_name="us-east-1")
    dynamodb = boto3.resource("dynamodb", region_name="us-east-1")
```

## Common Mistakes

1. **Missing AWS credentials**
   - Why: moto requires fake credentials to be set
   - Fix: Set AWS_ACCESS_KEY_ID and AWS_SECRET_ACCESS_KEY in fixtures

2. **Creating clients outside mock context**
   - Why: Client connects to real AWS before mock starts
   - Fix: Create boto3 clients inside the mock_aws context

3. **Forgetting region_name**
   - Why: Default region may not match expectations
   - Fix: Always specify region_name="us-east-1"

4. **Not creating resources before testing**
   - Why: Mocked AWS starts empty
   - Fix: Create tables, buckets, queues in setup

## When Users Ask About...

### "How do I get started?"
Point them to `make setup && make examples` and the README.md.

### "Why is my test hitting real AWS?"
Check that boto3 clients are created inside mock_aws context.

### "How do I mock multiple services?"
Use @mock_aws which mocks all services, or chain decorators.

### "How do I test async AWS operations?"
Use aioboto3 or aiobotocore with moto - mock_aws works with async too.

### "Why do I need to set credentials?"
moto validates credentials exist, even though they're fake.

## Testing Notes

- Tests use pytest with moto
- Always set fake AWS credentials in conftest.py
- Create resources (tables, buckets) in fixtures
- Run specific tests: `pytest -k "test_name"`

## Dependencies

Key dependencies in pyproject.toml:
- boto3>=1.34.0: AWS SDK
- moto[all]>=5.0.0: AWS mocking library
- pytest>=8.0.0: Testing framework
