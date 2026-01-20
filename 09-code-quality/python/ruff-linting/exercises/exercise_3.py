"""Exercise 3: Set Up Pre-commit Hooks with Ruff

Goal: Configure pre-commit hooks that run Ruff on every commit.

Instructions:
1. Create a .pre-commit-config.yaml file
2. Configure Ruff linting and formatting hooks
3. Install the hooks
4. Test with a commit

Requirements:
- Use the official Ruff pre-commit hooks
- Enable auto-fix for linting
- Run formatting after linting
- Include MyPy as an additional hook

Expected Files:
    my-project/
    ├── .pre-commit-config.yaml
    ├── pyproject.toml
    └── src/
        └── main.py

Commands to Run:
    pre-commit install         # Install hooks
    pre-commit run --all-files # Test on all files
    git add . && git commit    # Test on commit

Hints:
- Official Ruff hooks: https://github.com/astral-sh/ruff-pre-commit
- Use 'args: [--fix]' for auto-fixing
- Hook IDs: 'ruff' for linting, 'ruff-format' for formatting
- Order matters: ruff before ruff-format
"""

# Pre-commit configuration template
PRECOMMIT_CONFIG = '''
# .pre-commit-config.yaml
repos:
  # Ruff - Fast Python linter and formatter
  - repo: https://github.com/astral-sh/ruff-pre-commit
    rev: v0.3.0
    hooks:
      # Run Ruff linting with auto-fix
      - id: ruff
        args: [--fix]

      # Run Ruff formatting
      - id: ruff-format

  # MyPy - Static type checking
  - repo: https://github.com/pre-commit/mirrors-mypy
    rev: v1.8.0
    hooks:
      - id: mypy
        additional_dependencies:
          - types-requests
        args: [--strict]

  # General pre-commit hooks
  - repo: https://github.com/pre-commit/pre-commit-hooks
    rev: v4.5.0
    hooks:
      - id: trailing-whitespace
      - id: end-of-file-fixer
      - id: check-yaml
      - id: check-added-large-files
'''

# Alternative: Local hooks with UV
LOCAL_HOOKS_CONFIG = '''
# .pre-commit-config.yaml - Using local hooks with UV
repos:
  - repo: local
    hooks:
      - id: ruff-lint
        name: Ruff Lint
        entry: uv run ruff check --fix
        language: system
        types: [python]
        require_serial: true

      - id: ruff-format
        name: Ruff Format
        entry: uv run ruff format
        language: system
        types: [python]
        require_serial: true

      - id: mypy
        name: MyPy Type Check
        entry: uv run mypy
        language: system
        types: [python]
        require_serial: true
        args: [--strict]

  - repo: https://github.com/pre-commit/pre-commit-hooks
    rev: v4.5.0
    hooks:
      - id: trailing-whitespace
      - id: end-of-file-fixer
'''

SETUP_COMMANDS = """
Setup Commands:

# Install pre-commit (if not already installed)
pip install pre-commit
# or
uv add --dev pre-commit

# Install the hooks in your repository
pre-commit install

# Run hooks on all files (initial check)
pre-commit run --all-files

# Run specific hook
pre-commit run ruff --all-files
pre-commit run ruff-format --all-files

# Update hook versions
pre-commit autoupdate

# Skip hooks for a commit (use sparingly!)
git commit --no-verify -m "message"
"""


def verify_exercise() -> bool:
    """Verify the exercise was completed correctly."""
    import subprocess
    from pathlib import Path

    project = Path("my-project")
    precommit = project / ".pre-commit-config.yaml"

    checks = [
        ("Project directory exists", project.exists()),
        (".pre-commit-config.yaml exists", precommit.exists()),
    ]

    if precommit.exists():
        content = precommit.read_text()
        checks.append(("ruff hook configured", "id: ruff" in content))
        checks.append(("ruff-format hook configured", "ruff-format" in content))
        checks.append(("--fix flag for ruff", "--fix" in content))

    # Check if pre-commit is installed
    result = subprocess.run(
        ["pre-commit", "--version"],
        capture_output=True,
        text=True,
    )
    checks.append(("pre-commit installed", result.returncode == 0))

    # Check if hooks are installed
    git_hooks = project / ".git" / "hooks" / "pre-commit"
    checks.append(("hooks installed in git", git_hooks.exists()))

    print("\nExercise Verification:")
    print("-" * 40)

    all_passed = True
    for name, passed in checks:
        status = "PASS" if passed else "FAIL"
        print(f"  {status}: {name}")
        if not passed:
            all_passed = False

    # Try running pre-commit
    if project.exists() and precommit.exists():
        result = subprocess.run(
            ["pre-commit", "run", "--all-files"],
            cwd=project,
            capture_output=True,
            text=True,
        )
        if result.returncode == 0:
            print("  PASS: pre-commit runs successfully")
        else:
            print(f"  INFO: pre-commit found issues (expected for test files)")

    print("-" * 40)
    if all_passed:
        print("Exercise 3 completed successfully!")
    else:
        print("Exercise 3 not yet complete. See instructions above.")

    return all_passed


if __name__ == "__main__":
    print(__doc__)
    print("\nOfficial Ruff pre-commit configuration:")
    print(PRECOMMIT_CONFIG)
    print("\nAlternative: Local hooks with UV:")
    print(LOCAL_HOOKS_CONFIG)
    print(SETUP_COMMANDS)
