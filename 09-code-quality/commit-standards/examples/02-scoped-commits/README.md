# Example 2: Scoped Commit Messages

This example builds on basic commits by adding scopes and commit bodies for more contextual messages.

## Learning Goals

- Understand when and how to use scopes
- Write commit bodies that explain the "why"
- Add meaningful context to commit messages

## The Format with Scopes

```
<type>(<scope>): <description>

[optional body]
```

## What is a Scope?

A scope provides context about which part of the codebase is affected:

- **Module**: `auth`, `users`, `payments`
- **Layer**: `api`, `ui`, `db`
- **Package**: `core`, `utils`, `cli`
- **Feature**: `checkout`, `search`, `dashboard`

## Examples

### Basic Scoped Commits

```
feat(auth): add password reset functionality
fix(api): handle null response from external service
docs(readme): add troubleshooting section
refactor(db): optimize user queries
test(auth): add integration tests for login
```

### Commits with Bodies

```
feat(search): add fuzzy matching for product search

Implemented Levenshtein distance algorithm for typo-tolerant search.
Users can now find products even with minor spelling mistakes.
```

```
fix(cart): prevent race condition on quantity update

Multiple rapid clicks on the quantity buttons could result in
incorrect totals due to async state updates. Added debouncing
and optimistic locking to ensure consistency.
```

```
refactor(api): migrate from callbacks to async/await

Replaced all callback-based database queries with async/await.
This improves readability and makes error handling more consistent.

No functional changes - all existing tests pass.
```

## Demo Script

Run the demo to see these examples validated:

```bash
npm run example:2
# or
make example-2
```

## Choosing Good Scopes

### Project Structure Example

For a project with this structure:

```
src/
├── api/
│   ├── routes/
│   └── middleware/
├── services/
│   ├── auth/
│   ├── users/
│   └── payments/
├── models/
├── utils/
└── ui/
    ├── components/
    └── pages/
```

Appropriate scopes would be:

```
feat(api): add rate limiting middleware
feat(auth): implement two-factor authentication
fix(payments): handle declined card errors
refactor(users): extract validation to service layer
docs(api): document authentication endpoints
test(utils): add unit tests for date helpers
```

### Scope Best Practices

1. **Be consistent**: Use the same scope names throughout the project
2. **Keep it short**: `auth` not `authentication-service`
3. **Use lowercase**: `api` not `API`
4. **Match codebase**: Scopes should reflect your project structure

## When to Use a Body

Add a body when:

1. **The "why" isn't obvious** from the description
2. **You need to explain the approach** taken
3. **There are important details** to document
4. **Breaking down a complex change** for reviewers

### Body Guidelines

- Separate from header with a blank line
- Wrap at 72-100 characters
- Explain motivation and context
- Describe what changed and why
- Don't repeat what's in the diff

### Good Body Example

```
fix(auth): resolve session timeout inconsistency

Sessions were being invalidated based on creation time rather
than last activity time. This caused active users to be logged
out unexpectedly.

Changed session validation to use lastActivity timestamp.
Added background job to update lastActivity on each request.
```

### Bad Body Example

```
fix(auth): resolve session timeout

Changed the code in session.js to use lastActivity instead
of createdAt in the if statement on line 45.
```

(This just describes the diff, not the why)

## Practice

Rewrite these vague commits with appropriate scopes and bodies:

1. `fix: bug in checkout`
2. `feat: add feature`
3. `refactor: clean up code`

<details>
<summary>Click to see improved versions</summary>

1. ```
   fix(checkout): prevent duplicate order submission

   Users clicking the submit button multiple times could create
   duplicate orders. Added loading state and disabled button
   during processing.
   ```

2. ```
   feat(dashboard): add real-time notifications

   Implemented WebSocket connection for instant notifications.
   Users now see updates without refreshing the page.
   ```

3. ```
   refactor(api): extract common validation middleware

   Moved duplicate request validation from individual routes
   into shared middleware. Reduces code duplication and
   ensures consistent validation across endpoints.
   ```

</details>

## Key Takeaways

1. **Scopes add context**: They help readers quickly understand the affected area
2. **Bodies explain "why"**: The diff shows what changed; the body explains why
3. **Keep scopes consistent**: Define a scope vocabulary for your project
4. **Write for future readers**: Including yourself in 6 months

## Next Steps

Continue to [Example 3: Breaking Changes](../03-breaking-changes/) to learn about handling breaking changes properly.
