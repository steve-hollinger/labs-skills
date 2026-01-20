# Exercise 3: Solutions

## Part A: Initial Setup

### Commit 1: Database Schema
```
feat(db): add notification_preferences table

Create migration for storing user notification settings:
- user_id (foreign key to users)
- email_enabled (boolean)
- push_enabled (boolean)
- sms_enabled (boolean)
- marketing_enabled (boolean)
- created_at, updated_at timestamps
```

### Commit 2: Data Models
```
feat(models): add NotificationPreferences data model
```

Or with more detail:
```
feat(models): add NotificationPreferences schema

Pydantic model with validation for all preference fields.
Includes default values and JSON serialization support.
```

---

## Part B: Core Implementation

### Commit 3: Service Layer
```
feat(notifications): implement preferences service

Added NotificationPreferencesService with:
- get(user_id): retrieve user preferences
- update(user_id, preferences): update preferences
- reset_to_defaults(user_id): reset all to defaults

Includes caching for frequently accessed preferences.
```

### Commit 4: API Endpoints
```
feat(api): add notification preferences endpoints

New endpoints:
- GET /users/:id/preferences - retrieve preferences
- PUT /users/:id/preferences - update preferences

Includes request validation and proper error responses.
```

---

## Part C: Breaking Change

### Commit 5: Default Behavior Change
```
feat(notifications)!: change default to opt-in for notifications

BREAKING CHANGE: Notifications now require explicit opt-in.

Previously, users received all notifications by default (opt-out).
Now, all notification types default to disabled (opt-in).

Migration required:
1. Run migration script to preserve existing user preferences
2. New users will need to explicitly enable notifications
3. Update onboarding flow to prompt for notification preferences

This change ensures GDPR compliance and better user experience.
```

---

## Part D: Testing and Documentation

### Commit 6: Unit Tests
```
test(notifications): add unit tests for preferences service

Coverage for:
- get/update/reset operations
- validation edge cases
- caching behavior
```

### Commit 7: Integration Tests
```
test(api): add integration tests for preferences endpoints

End-to-end tests for:
- GET /users/:id/preferences
- PUT /users/:id/preferences
- Authentication and authorization
- Error handling
```

### Commit 8: API Documentation
```
docs(api): document notification preferences endpoints

Added OpenAPI specs for:
- GET /users/:id/preferences
- PUT /users/:id/preferences

Includes request/response examples and error codes.
```

### Commit 9: User Documentation
```
docs: add notification preferences user guide

Documentation covering:
- How to access notification settings
- Available notification types
- How to update preferences
- Troubleshooting common issues
```

---

## Part E: Final Touches

### Commit 10: Code Cleanup
```
chore(notifications): remove debug statements and fix lint
```

Or:
```
style(notifications): clean up code and fix linting warnings
```

---

## Review Questions: Answers

### 1. Which commit(s) would trigger a MAJOR version bump? Why?

**Commit 5** (the breaking change commit) would trigger a MAJOR version bump because:
- It changes the default behavior that existing users depend on
- It's marked with `!` and has a `BREAKING CHANGE` footer
- Existing integrations may break if they assume opt-out behavior

### 2. Which commit(s) would trigger a MINOR version bump? Why?

**Commits 1, 2, 3, and 4** would trigger MINOR version bumps because:
- They are `feat:` commits that add new functionality
- They don't break existing functionality
- The notification preferences feature is additive

Note: In practice, these would often be combined into a single release.

### 3. Which commit(s) would NOT trigger any version bump? Why?

The following commits would NOT trigger version bumps:
- **Commit 6** (test): Tests don't affect the public API
- **Commit 7** (test): Tests don't affect the public API
- **Commit 8** (docs): Documentation doesn't change code
- **Commit 9** (docs): Documentation doesn't change code
- **Commit 10** (chore/style): Cleanup doesn't change functionality

### 4. If you were to squash some of these commits, which ones might be combined?

Reasonable squash combinations:

**Option A: By logical unit**
- Squash 1 + 2 (schema + models = data layer)
- Squash 3 + 4 (service + api = feature implementation)
- Squash 6 + 7 (all tests together)
- Squash 8 + 9 (all docs together)

**Option B: Single feature commit**
Squash 1-4, 6-10 into a single feature commit (keeping 5 separate):
```
feat(notifications): add user notification preferences

Implemented complete notification preferences system:
- Database schema and models
- Service layer with caching
- REST API endpoints
- Comprehensive test coverage
- API and user documentation
```

Then keep the breaking change as a separate commit.

**Never squash the breaking change** with other commits - it needs to be clearly visible in history.

---

## Summary

This exercise demonstrates a realistic feature implementation workflow:

1. **Start with infrastructure** (database, models)
2. **Build the core feature** (service, API)
3. **Handle breaking changes carefully** (clear documentation)
4. **Add tests** (unit and integration)
5. **Document everything** (API and user docs)
6. **Clean up** (remove debug code, fix linting)

Each commit should be atomic and self-contained, making it easy to:
- Review changes
- Revert if needed
- Understand history
- Generate accurate changelogs
