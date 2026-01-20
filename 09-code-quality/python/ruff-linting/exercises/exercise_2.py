"""Exercise 2: Migrate from flake8/black to Ruff

Goal: Convert a project using flake8 and black to use Ruff.

Instructions:
1. Review the legacy configuration below
2. Create equivalent Ruff configuration
3. Remove legacy tool configurations
4. Verify the new configuration catches the same issues

Legacy Configuration to Migrate:

setup.cfg:
```
[flake8]
max-line-length = 100
ignore = E501,W503,E203
per-file-ignores =
    tests/*:S101,S106
    __init__.py:F401
exclude =
    .git,
    .venv,
    migrations
```

pyproject.toml:
```
[tool.black]
line-length = 100
target-version = ["py311"]
exclude = '''
/(
    .git
    | .venv
    | migrations
)/
'''

[tool.isort]
profile = "black"
line_length = 100
known_first_party = ["mypackage"]
skip = [".git", ".venv", "migrations"]
```

Expected Output:
- Single [tool.ruff] configuration
- Same behavior as flake8+black+isort
- Cleaner pyproject.toml

Hints:
- Ruff uses different ignore codes for some rules
- W503 doesn't exist in Ruff (handled by formatter)
- E203 doesn't exist in Ruff (Black-compatible by default)
- isort settings go in [tool.ruff.lint.isort]
"""

# Legacy configuration to migrate
LEGACY_SETUP_CFG = '''
[flake8]
max-line-length = 100
ignore = E501,W503,E203
per-file-ignores =
    tests/*:S101,S106
    __init__.py:F401
exclude =
    .git,
    .venv,
    migrations
select = E,F,W,C90
'''

LEGACY_PYPROJECT = '''
[tool.black]
line-length = 100
target-version = ["py311"]
exclude = """
/(
    .git
    | .venv
    | migrations
)/
"""

[tool.isort]
profile = "black"
line_length = 100
known_first_party = ["mypackage"]
skip = [".git", ".venv", "migrations"]
'''

# Equivalent Ruff configuration
EXPECTED_RUFF_CONFIG = '''
[tool.ruff]
line-length = 100
target-version = "py311"
exclude = [
    ".git",
    ".venv",
    "migrations",
]

[tool.ruff.lint]
# E, F, W from flake8; C90 is mccabe complexity
select = ["E", "F", "W", "I", "C90"]

# E501 ignored (formatter handles it)
# W503 and E203 don't exist in Ruff
ignore = ["E501"]

[tool.ruff.lint.per-file-ignores]
"tests/*" = ["S101", "S106"]
"__init__.py" = ["F401"]

[tool.ruff.lint.isort]
known-first-party = ["mypackage"]

[tool.ruff.lint.mccabe]
max-complexity = 10

[tool.ruff.format]
quote-style = "double"
'''

MIGRATION_CHECKLIST = """
Migration Checklist:

1. [ ] Create [tool.ruff] section with line-length and target-version
2. [ ] Add exclude patterns
3. [ ] Map flake8 select/ignore to [tool.ruff.lint]
4. [ ] Convert per-file-ignores
5. [ ] Add [tool.ruff.lint.isort] for import sorting
6. [ ] Remove [tool.black] section
7. [ ] Remove [tool.isort] section
8. [ ] Delete setup.cfg or remove [flake8] section
9. [ ] Update CI to use 'ruff check' and 'ruff format'
10. [ ] Test: ruff check . && ruff format --check .
"""


def verify_exercise() -> bool:
    """Verify the migration was completed correctly."""
    from pathlib import Path

    project = Path("migrated-project")
    pyproject = project / "pyproject.toml"

    checks = []

    if pyproject.exists():
        content = pyproject.read_text()

        # Check Ruff configuration exists
        checks.append(("[tool.ruff] exists", "[tool.ruff]" in content))
        checks.append(("line-length configured", "line-length" in content))
        checks.append(("target-version configured", "target-version" in content))

        # Check legacy config removed
        checks.append(("[tool.black] removed", "[tool.black]" not in content))
        checks.append(("[tool.isort] removed", "[tool.isort]" not in content))

        # Check lint config
        checks.append(("[tool.ruff.lint] exists", "[tool.ruff.lint]" in content))
        checks.append(("per-file-ignores configured", "per-file-ignores" in content))

    else:
        checks.append(("pyproject.toml exists", False))

    # Check setup.cfg removed or flake8 removed
    setup_cfg = project / "setup.cfg"
    if setup_cfg.exists():
        content = setup_cfg.read_text()
        checks.append(("[flake8] removed from setup.cfg", "[flake8]" not in content))
    else:
        checks.append(("setup.cfg removed", True))

    print("\nMigration Verification:")
    print("-" * 40)

    all_passed = True
    for name, passed in checks:
        status = "PASS" if passed else "FAIL"
        print(f"  {status}: {name}")
        if not passed:
            all_passed = False

    print("-" * 40)
    if all_passed:
        print("Exercise 2 completed successfully!")
    else:
        print("Exercise 2 not yet complete. See instructions above.")

    return all_passed


if __name__ == "__main__":
    print(__doc__)
    print("\nLegacy setup.cfg to migrate:")
    print(LEGACY_SETUP_CFG)
    print("\nLegacy pyproject.toml to migrate:")
    print(LEGACY_PYPROJECT)
    print(MIGRATION_CHECKLIST)
    print("\nExpected Ruff configuration:")
    print(EXPECTED_RUFF_CONFIG)
