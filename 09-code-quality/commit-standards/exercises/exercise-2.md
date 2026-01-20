# Exercise 2: Fix Bad Commit Messages

## Objective

Practice identifying problems in poorly-written commit messages and rewriting them to follow conventional commit standards.

## Instructions

Each commit message below has one or more issues. Identify the problems and rewrite the message correctly.

---

## Problem 1

```
Fixed the bug
```

**Issues found:**


**Corrected message:**


---

## Problem 2

```
feat: Added new login page with validation and error handling.
```

**Issues found:**


**Corrected message:**


---

## Problem 3

```
UPDATE: changes to the api
```

**Issues found:**


**Corrected message:**


---

## Problem 4

```
feat(API): Add user endpoint
```

**Issues found:**


**Corrected message:**


---

## Problem 5

```
fix add logging and fix the null pointer exception in user service
```

**Issues found:**


**Corrected message:**


---

## Problem 6

```
wip
```

**Issues found:**


**Corrected message:**


---

## Problem 7

```
feat: updated dependencies, fixed some bugs, added new feature for search, and reformatted code
```

**Issues found:**


**Corrected message(s):**


---

## Problem 8

```
refactor

changed some code around
```

**Issues found:**


**Corrected message:**


---

## Problem 9

```
feat(auth): implement OAuth2 authentication flow with Google and GitHub providers including token refresh and session management with Redis storage

```

**Issues found:**


**Corrected message:**


---

## Problem 10

```
chore: Remove dead code
This commit removes unused variables and functions from the codebase.
```

**Issues found:**


**Corrected message:**


---

## Bonus Challenge

Rewrite this disaster of a commit message into proper conventional commits:

```
stuff - fixed things and added some features. also cleaned up the code a bit. PR feedback addressed. WIP on the new dashboard. Updated tests.
```

**Corrected message(s):**


---

## Validation

Test your corrected messages with commitlint:

```bash
echo "your corrected message" | npx commitlint
```

---

When you're ready, check your answers in [solutions/exercise-2-solution.md](./solutions/exercise-2-solution.md).
