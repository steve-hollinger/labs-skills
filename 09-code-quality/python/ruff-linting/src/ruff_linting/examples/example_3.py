"""Example 3: Editor and CI Integration

This example demonstrates integrating Ruff with editors, CI/CD
pipelines, and pre-commit hooks.
"""


def demonstrate_vscode_integration() -> None:
    """Show VS Code configuration for Ruff."""
    print("\n" + "=" * 60)
    print("STEP 1: VS Code Integration")
    print("=" * 60)

    settings = '''
Install the Ruff VS Code extension:
    1. Open Extensions (Cmd+Shift+X)
    2. Search "Ruff"
    3. Install "Ruff" by Astral

Configure settings.json:

{
    // Use Ruff as the formatter
    "[python]": {
        "editor.defaultFormatter": "charliermarsh.ruff",
        "editor.formatOnSave": true,
        "editor.codeActionsOnSave": {
            "source.fixAll.ruff": "explicit",
            "source.organizeImports.ruff": "explicit"
        }
    },

    // Ruff extension settings
    "ruff.lint.run": "onSave",
    "ruff.format.args": [],
    "ruff.importStrategy": "fromEnvironment",

    // Disable conflicting formatters
    "python.formatting.provider": "none"
}
'''
    print(settings)

    workspace = '''
Or in .vscode/settings.json for project-specific settings:

{
    "ruff.lint.args": [
        "--config=pyproject.toml"
    ],
    "ruff.path": [".venv/bin/ruff"]
}
'''
    print(workspace)


def demonstrate_pycharm_integration() -> None:
    """Show PyCharm configuration for Ruff."""
    print("\n" + "=" * 60)
    print("STEP 2: PyCharm Integration")
    print("=" * 60)

    print("""
Option 1: Ruff Plugin
    1. Settings > Plugins > Marketplace
    2. Search "Ruff"
    3. Install and restart

Option 2: External Tool
    1. Settings > Tools > External Tools
    2. Add new tool:
        Name: Ruff Check
        Program: $PyInterpreterDirectory$/ruff
        Arguments: check --fix $FilePath$
        Working directory: $ProjectFileDir$

Option 3: File Watcher
    1. Settings > Tools > File Watchers
    2. Add new watcher:
        File type: Python
        Scope: Project Files
        Program: ruff
        Arguments: check --fix $FilePath$
        Output paths: $FilePath$

PyCharm also supports Ruff as an external formatter:
    Settings > Editor > Code Style > Python > Formatter: Ruff
""")


def demonstrate_neovim_integration() -> None:
    """Show Neovim/NvChad configuration for Ruff."""
    print("\n" + "=" * 60)
    print("STEP 3: Neovim Integration")
    print("=" * 60)

    lua_config = '''
Using nvim-lspconfig with ruff-lsp:

-- In your LSP configuration
local lspconfig = require('lspconfig')

lspconfig.ruff_lsp.setup({
    on_attach = function(client, bufnr)
        -- Disable hover (use pyright instead)
        client.server_capabilities.hoverProvider = false
    end,
    init_options = {
        settings = {
            args = {},
        }
    }
})

-- Use with pyright for best experience
lspconfig.pyright.setup({})

Using conform.nvim for formatting:

require("conform").setup({
    formatters_by_ft = {
        python = { "ruff_format" },
    },
})

Using none-ls (null-ls):

local null_ls = require("null-ls")
null_ls.setup({
    sources = {
        null_ls.builtins.formatting.ruff,
        null_ls.builtins.diagnostics.ruff,
    },
})
'''
    print(lua_config)


def demonstrate_github_actions() -> None:
    """Show GitHub Actions configuration for Ruff."""
    print("\n" + "=" * 60)
    print("STEP 4: GitHub Actions Integration")
    print("=" * 60)

    basic_workflow = '''
Basic lint workflow (.github/workflows/lint.yml):

name: Lint

on:
  push:
    branches: [main]
  pull_request:

jobs:
  lint:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v4

      - name: Install UV
        uses: astral-sh/setup-uv@v4

      - name: Install dependencies
        run: uv sync --all-extras

      - name: Ruff check
        run: uv run ruff check --output-format=github .

      - name: Ruff format check
        run: uv run ruff format --check .
'''
    print("Basic workflow:")
    print(basic_workflow)

    advanced_workflow = '''
Advanced workflow with caching:

name: Code Quality

on: [push, pull_request]

jobs:
  lint:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v4

      - uses: astral-sh/setup-uv@v4

      - uses: actions/cache@v4
        with:
          path: |
            ~/.cache/uv
            .venv
          key: lint-${{ hashFiles('uv.lock') }}

      - run: uv sync --all-extras

      - name: Ruff check
        run: uv run ruff check --output-format=github .

      - name: Ruff format
        run: uv run ruff format --check --diff .

      - name: MyPy
        run: uv run mypy src/
'''
    print("\nAdvanced workflow:")
    print(advanced_workflow)


def demonstrate_precommit() -> None:
    """Show pre-commit configuration for Ruff."""
    print("\n" + "=" * 60)
    print("STEP 5: Pre-commit Hooks")
    print("=" * 60)

    precommit_config = '''
Using official Ruff pre-commit hooks:

# .pre-commit-config.yaml
repos:
  - repo: https://github.com/astral-sh/ruff-pre-commit
    rev: v0.3.0
    hooks:
      # Linting with auto-fix
      - id: ruff
        args: [--fix]

      # Formatting
      - id: ruff-format
'''
    print(precommit_config)

    local_hooks = '''
Or use local hooks (for UV projects):

# .pre-commit-config.yaml
repos:
  - repo: local
    hooks:
      - id: ruff-check
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
'''
    print("Using local hooks:")
    print(local_hooks)

    setup = '''
Setup commands:
    pip install pre-commit              # Install pre-commit
    pre-commit install                  # Install hooks
    pre-commit run --all-files          # Run on all files
    pre-commit autoupdate               # Update hook versions
'''
    print(setup)


def demonstrate_makefile_targets() -> None:
    """Show Makefile targets for Ruff."""
    print("\n" + "=" * 60)
    print("STEP 6: Makefile Targets")
    print("=" * 60)

    makefile = '''
Standard Makefile targets for Ruff:

.PHONY: lint format check

# Check for issues (CI-friendly)
lint:
\tuv run ruff check src/ tests/
\tuv run ruff format --check src/ tests/

# Auto-fix and format
format:
\tuv run ruff format src/ tests/
\tuv run ruff check --fix src/ tests/

# Full code quality check
check: lint
\tuv run mypy src/
\tuv run pytest

# Watch mode (requires entr or similar)
watch:
\tfind src tests -name "*.py" | entr -c uv run ruff check src/ tests/
'''
    print(makefile)


def demonstrate_ci_output_formats() -> None:
    """Show different output formats for CI."""
    print("\n" + "=" * 60)
    print("STEP 7: CI Output Formats")
    print("=" * 60)

    print("""
Ruff supports multiple output formats for different CI systems:

GitHub Actions (annotations in PR):
    ruff check --output-format=github .

JSON (machine-readable):
    ruff check --output-format=json .

GitLab CI (code quality report):
    ruff check --output-format=gitlab .

SARIF (GitHub security tab):
    ruff check --output-format=sarif .

Standard text (default):
    ruff check --output-format=text .

Grouped by file:
    ruff check --output-format=grouped .

Statistics (rule counts):
    ruff check --statistics .

Example GitHub output:
    ::warning file=src/main.py,line=10,col=5::F841 Local variable `x` is assigned but never used
""")


def main() -> None:
    """Run the editor and CI integration example."""
    print("Example 3: Editor and CI Integration")
    print("=" * 60)

    print("""
This example covers integrating Ruff with development tools:
- VS Code configuration
- PyCharm setup
- Neovim/NvChad configuration
- GitHub Actions workflows
- Pre-commit hooks
- Makefile targets
""")

    demonstrate_vscode_integration()
    demonstrate_pycharm_integration()
    demonstrate_neovim_integration()
    demonstrate_github_actions()
    demonstrate_precommit()
    demonstrate_makefile_targets()
    demonstrate_ci_output_formats()

    print("\n" + "=" * 60)
    print("Example completed successfully!")
    print("=" * 60)
    print("\nNext steps:")
    print("  1. Set up Ruff in your editor of choice")
    print("  2. Add Ruff to your project's CI workflow")
    print("  3. Complete Exercise 3 to set up pre-commit hooks")


if __name__ == "__main__":
    main()
