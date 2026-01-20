# Exercise 3: Feature Implementation Commit Series

## Objective

Practice writing a realistic series of commits for implementing a complete feature, including breaking changes, documentation, and tests.

## Scenario

You've been assigned to implement a **user notification preferences system** for your application. The feature includes:

1. Database schema for storing preferences
2. API endpoints for getting and updating preferences
3. Backend service logic
4. Breaking change: notifications now require explicit opt-in (previously opt-out)
5. Documentation
6. Tests

Write the commit messages for each step of this implementation.

---

## Part A: Initial Setup

### Commit 1: Database Schema
Add the database migration for the notification_preferences table with columns for user_id, email_enabled, push_enabled, sms_enabled, and marketing_enabled.

```
Your commit message:




```

### Commit 2: Data Models
Create the Pydantic/TypeScript models for notification preferences.

```
Your commit message:

```

---

## Part B: Core Implementation

### Commit 3: Service Layer
Implement the NotificationPreferencesService with methods for get, update, and reset to defaults.

```
Your commit message:




```

### Commit 4: API Endpoints
Add REST endpoints: GET /users/:id/preferences and PUT /users/:id/preferences.

```
Your commit message:




```

---

## Part C: Breaking Change

### Commit 5: Default Behavior Change
Change the default notification behavior from opt-out to opt-in. This is a breaking change that affects existing users.

```
Your commit message:




```

---

## Part D: Testing and Documentation

### Commit 6: Unit Tests
Add unit tests for the NotificationPreferencesService.

```
Your commit message:

```

### Commit 7: Integration Tests
Add API integration tests for the preferences endpoints.

```
Your commit message:

```

### Commit 8: API Documentation
Update the API documentation with the new preferences endpoints.

```
Your commit message:

```

### Commit 9: User Documentation
Add user-facing documentation explaining how to manage notification preferences.

```
Your commit message:

```

---

## Part E: Final Touches

### Commit 10: Code Cleanup
Remove console.log statements and fix linting warnings from the new code.

```
Your commit message:

```

---

## Review Questions

After writing your commits, answer these questions:

1. Which commit(s) would trigger a MAJOR version bump? Why?


2. Which commit(s) would trigger a MINOR version bump? Why?


3. Which commit(s) would NOT trigger any version bump? Why?


4. If you were to squash some of these commits, which ones might be combined?


---

## Validation

Test your commit messages:

```bash
# Test each message
echo "your commit message" | npx commitlint
```

---

When you're ready, check your answers in [solutions/exercise-3-solution.md](./solutions/exercise-3-solution.md).
