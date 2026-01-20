# Exercise 2: Solutions

## Problem 1

```
Fixed the bug
```

**Issues:**
- Missing type prefix
- Past tense ("Fixed" instead of "fix")
- Too vague - what bug?

**Corrected:**
```
fix: resolve null pointer when user list is empty
```

---

## Problem 2

```
feat: Added new login page with validation and error handling.
```

**Issues:**
- Past tense ("Added" instead of "add")
- Capital letter in description
- Period at the end

**Corrected:**
```
feat: add login page with validation and error handling
```

Or split into multiple commits:
```
feat(auth): add login page
feat(auth): add form validation to login page
feat(auth): add error handling for login failures
```

---

## Problem 3

```
UPDATE: changes to the api
```

**Issues:**
- "UPDATE" is not a valid type
- Uppercase type
- Vague description

**Corrected:**
```
refactor(api): simplify request validation logic
```

Or if it's actually a feature:
```
feat(api): add rate limiting to public endpoints
```

---

## Problem 4

```
feat(API): Add user endpoint
```

**Issues:**
- Scope is uppercase (should be `api`)
- Description starts with capital letter

**Corrected:**
```
feat(api): add user endpoint
```

---

## Problem 5

```
fix add logging and fix the null pointer exception in user service
```

**Issues:**
- Missing colon after type
- Multiple changes in one commit
- Unclear what the actual fix is

**Corrected (split into separate commits):**
```
fix(users): resolve null pointer in user service
```
```
feat(users): add logging to user service operations
```

---

## Problem 6

```
wip
```

**Issues:**
- "wip" is not a valid type
- No description at all
- WIP commits shouldn't be in the main branch history

**Corrected:**
```
feat(dashboard): add initial dashboard layout
```

Note: WIP commits should be squashed before merging, or use `--amend` to update the message when the work is complete.

---

## Problem 7

```
feat: updated dependencies, fixed some bugs, added new feature for search, and reformatted code
```

**Issues:**
- Multiple unrelated changes in one commit
- Past tense
- Too long for a single commit
- Mixing types (feat, fix, build, style)

**Corrected (split into separate commits):**
```
build(deps): update project dependencies
```
```
fix(cart): resolve quantity validation error
```
```
feat(search): add full-text product search
```
```
style: format code with prettier
```

---

## Problem 8

```
refactor

changed some code around
```

**Issues:**
- Missing colon after type
- Missing description in header
- Body doesn't explain what was refactored

**Corrected:**
```
refactor(api): extract request validation to middleware

Moved duplicate validation logic from individual route handlers
into shared middleware. Reduces code duplication and ensures
consistent validation across all endpoints.
```

---

## Problem 9

```
feat(auth): implement OAuth2 authentication flow with Google and GitHub providers including token refresh and session management with Redis storage
```

**Issues:**
- Header exceeds 72 characters
- Too much detail in the header (should be in body)

**Corrected:**
```
feat(auth): implement OAuth2 authentication with Google and GitHub

Added OAuth2 support including:
- Google and GitHub provider integration
- Token refresh mechanism
- Session management with Redis storage
```

---

## Problem 10

```
chore: Remove dead code
This commit removes unused variables and functions from the codebase.
```

**Issues:**
- Capital letter in description ("Remove")
- Missing blank line between header and body

**Corrected:**
```
chore: remove dead code

Remove unused variables and functions from the codebase.
```

Or more specifically:
```
refactor: remove unused helper functions

Removed 5 unused functions from utils.js that were
deprecated in v2.0 and no longer referenced.
```

---

## Bonus Challenge

Original:
```
stuff - fixed things and added some features. also cleaned up the code a bit. PR feedback addressed. WIP on the new dashboard. Updated tests.
```

**Corrected (split into 5+ commits):**

```
fix(auth): resolve login redirect on expired tokens
```

```
feat(search): add autocomplete suggestions
```

```
refactor(api): simplify error handling middleware

Addressed PR feedback to extract common error handling
logic into shared middleware.
```

```
feat(dashboard): add initial layout structure
```

```
test(auth): add tests for token refresh flow
```

---

## Key Lessons

1. **One commit = one logical change**: Don't mix features, fixes, and refactoring
2. **Be specific**: "fix bug" tells us nothing; "fix null pointer in user lookup" tells us everything
3. **Follow the format exactly**: Type, colon, space, lowercase description
4. **Keep headers short**: Details go in the body
5. **Use correct types**: Each type has a specific meaning
