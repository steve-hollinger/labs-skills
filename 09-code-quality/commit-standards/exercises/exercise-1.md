# Exercise 1: Categorize and Write Commit Messages

## Objective

Practice identifying the correct commit type and writing well-formatted conventional commit messages.

## Scenario

You're working on an e-commerce application. Below are descriptions of changes that have been made. For each change, write an appropriate conventional commit message.

---

## Part A: Basic Commits

Write commit messages for the following changes:

### Change 1
You added a new feature that lets users filter products by price range.

```
Your commit message:

```

### Change 2
You fixed a bug where the shopping cart total was calculated incorrectly when applying discount codes.

```
Your commit message:

```

### Change 3
You updated the README file to include information about the new price filter feature.

```
Your commit message:

```

### Change 4
You ran prettier on all JavaScript files to fix formatting inconsistencies.

```
Your commit message:

```

### Change 5
You added unit tests for the discount code calculation function.

```
Your commit message:

```

---

## Part B: Scoped Commits

Write commit messages with appropriate scopes for these changes:

### Change 6
You improved the performance of the product search by adding database indexes.

```
Your commit message:

```

### Change 7
You refactored the user authentication code to use async/await instead of callbacks.

```
Your commit message:

```

### Change 8
You added a new API endpoint for retrieving order history.

```
Your commit message:

```

---

## Part C: Commits with Bodies

Write full commit messages (with bodies) for these complex changes:

### Change 9
You fixed a critical bug where user sessions were being terminated unexpectedly. The root cause was that the session timeout was being calculated from the session creation time instead of the last activity time.

```
Your commit message:




```

### Change 10
You added a new notification system that sends emails when orders are shipped. The feature includes email templates, a background job processor, and integration with SendGrid.

```
Your commit message:




```

---

## Validation

After completing your answers, validate them using commitlint:

```bash
# Validate a single message
echo "your commit message" | npx commitlint

# Or use the make command
make lint MSG="your commit message"
```

## Checklist

Before submitting, verify each commit message:

- [ ] Has a valid type (feat, fix, docs, etc.)
- [ ] Uses lowercase in the description
- [ ] Has no period at the end
- [ ] Is 72 characters or less for the header
- [ ] Uses imperative mood ("add" not "added")
- [ ] Has a blank line before the body (if body present)

---

When you're ready, check your answers in [solutions/exercise-1-solution.md](./solutions/exercise-1-solution.md).
