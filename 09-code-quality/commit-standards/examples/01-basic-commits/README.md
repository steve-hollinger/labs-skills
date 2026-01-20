# Example 1: Basic Commit Messages

This example covers the fundamental commit types and how to write simple, effective commit messages.

## Learning Goals

- Understand the basic commit message format
- Learn when to use each commit type
- Write clear, concise descriptions

## The Basic Format

```
<type>: <description>
```

That's it! Start simple.

## Commit Types Reference

| Type | When to Use | Example |
|------|-------------|---------|
| `feat` | Adding new functionality | `feat: add user login form` |
| `fix` | Fixing a bug | `fix: resolve null pointer on empty list` |
| `docs` | Documentation changes only | `docs: add API usage examples` |
| `style` | Formatting, no logic change | `style: format with prettier` |
| `refactor` | Restructuring code | `refactor: extract helper function` |
| `test` | Adding or fixing tests | `test: add unit tests for auth` |
| `chore` | Maintenance tasks | `chore: update .gitignore` |

## Examples in This Directory

### Scenario: Building a Todo App

Imagine you're building a todo list application. Here are realistic commits:

```
feat: add todo item creation

feat: add todo item deletion

feat: add todo item completion toggle

fix: prevent empty todo items from being created

docs: add readme with setup instructions

style: format code with eslint --fix

test: add unit tests for todo operations

chore: add .env.example file
```

## Demo Script

Run the demo to see these examples validated:

```bash
npm run example:1
# or
make example-1
```

## Practice

Try writing commit messages for these scenarios:

1. You added a search feature to the todo app
2. You fixed a bug where completed todos weren't saving
3. You updated the README with new features
4. You reformatted the CSS files
5. You added tests for the search feature

<details>
<summary>Click to see suggested answers</summary>

1. `feat: add todo search functionality`
2. `fix: persist completed todo state to storage`
3. `docs: update readme with search feature`
4. `style: format css files with prettier`
5. `test: add unit tests for todo search`

</details>

## Common Mistakes

### Mistake 1: Capitalizing the Description

```
# Wrong
feat: Add new feature

# Correct
feat: add new feature
```

### Mistake 2: Adding a Period

```
# Wrong
fix: resolve bug.

# Correct
fix: resolve bug
```

### Mistake 3: Using Past Tense

```
# Wrong
feat: added user login

# Correct
feat: add user login
```

### Mistake 4: Being Too Vague

```
# Wrong
fix: fix bug

# Correct
fix: resolve null pointer when list is empty
```

## Key Takeaways

1. **Keep it simple**: `<type>: <description>` is all you need to start
2. **Be specific**: Describe what changed, not just "fix" or "update"
3. **Use present tense**: "add" not "added"
4. **Stay lowercase**: No capitals in the description
5. **Skip the period**: No punctuation at the end

## Next Steps

Continue to [Example 2: Scoped Commits](../02-scoped-commits/) to learn about adding context with scopes.
