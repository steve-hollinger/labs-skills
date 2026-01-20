# Exercise 1: Solutions

## Part A: Basic Commits

### Change 1 - Price filter feature
```
feat: add product price range filter
```

Or with a scope:
```
feat(products): add price range filter
```

### Change 2 - Cart total bug
```
fix: correct cart total calculation with discount codes
```

Or with scope and more detail:
```
fix(cart): correct total calculation when discount codes applied
```

### Change 3 - README update
```
docs: add price filter documentation to readme
```

Or:
```
docs(readme): document price filter feature
```

### Change 4 - Prettier formatting
```
style: format javascript files with prettier
```

Note: Use `style` for formatting-only changes, not `chore`.

### Change 5 - Unit tests
```
test: add unit tests for discount code calculation
```

Or with scope:
```
test(cart): add unit tests for discount calculation
```

---

## Part B: Scoped Commits

### Change 6 - Database indexes for search
```
perf(db): add indexes to improve product search performance
```

Or:
```
perf(search): add database indexes for product queries
```

### Change 7 - Auth refactoring
```
refactor(auth): migrate from callbacks to async/await
```

### Change 8 - Order history endpoint
```
feat(api): add order history retrieval endpoint
```

Or with more detail:
```
feat(api): add GET /orders endpoint for order history
```

---

## Part C: Commits with Bodies

### Change 9 - Session timeout bug

```
fix(auth): use last activity time for session timeout

Sessions were being terminated based on creation time rather
than last activity time. This caused active users to be
unexpectedly logged out.

Changed session validation to use lastActivityAt timestamp
instead of createdAt.
```

### Change 10 - Notification system

```
feat(notifications): add order shipment email notifications

Implemented email notification system for shipped orders:
- Created email templates for shipment notifications
- Added background job processor for async sending
- Integrated SendGrid for email delivery

Emails are queued when order status changes to 'shipped'.
```

---

## Key Points

1. **Use the most specific type**: `perf` for performance, `style` for formatting
2. **Scopes help readers**: They know where to look without reading the full message
3. **Bodies explain "why"**: The diff shows what changed; the body explains the reasoning
4. **Keep headers under 72 characters**: Move details to the body
5. **Imperative mood**: "add" not "added" or "adds"
