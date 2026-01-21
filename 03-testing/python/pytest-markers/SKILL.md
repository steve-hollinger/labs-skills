---
name: organizing-pytest-markers
description: Pytest markers for test organization, categorization, and selective execution. Use when writing or improving tests.
---

# Pytest Markers

## Quick Start
```python
import pytest
import sys

@pytest.mark.skipif(
    sys.platform == "win32",
    reason="Unix-only feature"
)
def test_unix_specific():
    pass
```


## Key Points
- Built-in Markers
- Custom Markers
- Marker Expressions

## Common Mistakes
1. **Unregistered markers cause warnings** - Add markers to pyproject.toml [tool.pytest.ini_options] markers list
2. **Using skipif when xfail is appropriate** - Use xfail for known bugs to track when they get fixed
3. **Parametrize without ids** - Always provide meaningful ids for parametrize

## More Detail
- [docs/concepts.md](docs/concepts.md) - Core concepts and theory
- [docs/patterns.md](docs/patterns.md) - Full code patterns and examples