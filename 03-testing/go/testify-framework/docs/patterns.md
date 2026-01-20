# Common Patterns - Testify Framework

## Overview

This document covers common patterns and best practices for testing with Testify.

## Pattern 1: Test Fixtures in Suites

### When to Use

When multiple tests need the same test data or database state.

### Implementation

```go
type UserServiceSuite struct {
    suite.Suite
    db       *sql.DB
    repo     *UserRepository
    service  *UserService
    testUser *User
}

func (s *UserServiceSuite) SetupSuite() {
    var err error
    s.db, err = sql.Open("postgres", testDSN)
    s.Require().NoError(err)
    s.repo = NewUserRepository(s.db)
    s.service = NewUserService(s.repo)
}

func (s *UserServiceSuite) SetupTest() {
    // Clean slate for each test
    _, err := s.db.Exec("DELETE FROM users")
    s.Require().NoError(err)

    // Create standard test fixture
    s.testUser = &User{
        Name:  "Test User",
        Email: "test@example.com",
    }
    err = s.repo.Create(s.testUser)
    s.Require().NoError(err)
}

func (s *UserServiceSuite) TestGetUser() {
    user, err := s.service.GetUser(s.testUser.ID)
    s.NoError(err)
    s.Equal(s.testUser.Name, user.Name)
}

func (s *UserServiceSuite) TestUpdateUser() {
    s.testUser.Name = "Updated Name"
    err := s.service.UpdateUser(s.testUser)
    s.NoError(err)

    user, err := s.service.GetUser(s.testUser.ID)
    s.NoError(err)
    s.Equal("Updated Name", user.Name)
}
```

## Pattern 2: Mock with Callbacks

### When to Use

When you need to verify arguments or compute return values dynamically.

### Implementation

```go
func TestWithCallback(t *testing.T) {
    mockRepo := new(MockUserRepository)

    // Capture the saved user
    var savedUser *User
    mockRepo.On("SaveUser", mock.Anything).
        Run(func(args mock.Arguments) {
            savedUser = args.Get(0).(*User)
            savedUser.ID = 42 // Simulate ID assignment
        }).
        Return(nil)

    service := NewUserService(mockRepo)
    user := &User{Name: "Alice", Email: "alice@example.com"}
    err := service.CreateUser(user)

    require.NoError(t, err)
    assert.Equal(t, int64(42), user.ID)
    assert.NotNil(t, savedUser)
    assert.Equal(t, "alice@example.com", savedUser.Email)
}
```

## Pattern 3: Testing Error Paths

### When to Use

Every function that can return an error should have error path tests.

### Implementation

```go
func TestUserService_ErrorPaths(t *testing.T) {
    tests := []struct {
        name        string
        setupMock   func(*MockUserRepository)
        operation   func(*UserService) error
        expectedErr error
    }{
        {
            name: "get user not found",
            setupMock: func(m *MockUserRepository) {
                m.On("GetUser", mock.Anything).Return(nil, ErrNotFound)
            },
            operation: func(s *UserService) error {
                _, err := s.GetUser(999)
                return err
            },
            expectedErr: ErrNotFound,
        },
        {
            name: "save user database error",
            setupMock: func(m *MockUserRepository) {
                m.On("SaveUser", mock.Anything).Return(errors.New("db connection lost"))
            },
            operation: func(s *UserService) error {
                return s.CreateUser(&User{Name: "Test"})
            },
            expectedErr: ErrDatabaseError,
        },
        {
            name: "update non-existent user",
            setupMock: func(m *MockUserRepository) {
                m.On("GetUser", mock.Anything).Return(nil, ErrNotFound)
            },
            operation: func(s *UserService) error {
                return s.UpdateUser(&User{ID: 999, Name: "Test"})
            },
            expectedErr: ErrNotFound,
        },
    }

    for _, tt := range tests {
        t.Run(tt.name, func(t *testing.T) {
            mockRepo := new(MockUserRepository)
            tt.setupMock(mockRepo)

            service := NewUserService(mockRepo)
            err := tt.operation(service)

            require.Error(t, err)
            assert.ErrorIs(t, err, tt.expectedErr)
            mockRepo.AssertExpectations(t)
        })
    }
}
```

## Pattern 4: Testing Concurrent Code

### When to Use

When testing code that uses goroutines or must be thread-safe.

### Implementation

```go
func TestConcurrentAccess(t *testing.T) {
    cache := NewCache()
    var wg sync.WaitGroup

    // Concurrent writes
    for i := 0; i < 100; i++ {
        wg.Add(1)
        go func(id int) {
            defer wg.Done()
            cache.Set(fmt.Sprintf("key%d", id), id)
        }(i)
    }

    // Concurrent reads
    for i := 0; i < 100; i++ {
        wg.Add(1)
        go func(id int) {
            defer wg.Done()
            cache.Get(fmt.Sprintf("key%d", id))
        }(i)
    }

    wg.Wait()

    assert.Equal(t, 100, cache.Len())
}

func TestEventualConsistency(t *testing.T) {
    service := NewAsyncService()
    service.ProcessAsync("test-data")

    // Use Eventually for async operations
    assert.Eventually(t, func() bool {
        result, err := service.GetResult("test-data")
        return err == nil && result.Status == "completed"
    }, 5*time.Second, 100*time.Millisecond, "result should be completed")
}
```

## Pattern 5: HTTP Handler Testing

### When to Use

When testing HTTP handlers with mocked dependencies.

### Implementation

```go
func TestUserHandler(t *testing.T) {
    tests := []struct {
        name           string
        method         string
        path           string
        body           string
        setupMock      func(*MockUserService)
        expectedStatus int
        expectedBody   string
    }{
        {
            name:   "get user success",
            method: "GET",
            path:   "/users/1",
            setupMock: func(m *MockUserService) {
                m.On("GetUser", int64(1)).Return(&User{ID: 1, Name: "Alice"}, nil)
            },
            expectedStatus: http.StatusOK,
            expectedBody:   `{"id":1,"name":"Alice"}`,
        },
        {
            name:   "get user not found",
            method: "GET",
            path:   "/users/999",
            setupMock: func(m *MockUserService) {
                m.On("GetUser", int64(999)).Return(nil, ErrNotFound)
            },
            expectedStatus: http.StatusNotFound,
            expectedBody:   `{"error":"user not found"}`,
        },
        {
            name:   "create user",
            method: "POST",
            path:   "/users",
            body:   `{"name":"Bob","email":"bob@example.com"}`,
            setupMock: func(m *MockUserService) {
                m.On("CreateUser", mock.MatchedBy(func(u *User) bool {
                    return u.Name == "Bob"
                })).Return(nil)
            },
            expectedStatus: http.StatusCreated,
        },
    }

    for _, tt := range tests {
        t.Run(tt.name, func(t *testing.T) {
            mockService := new(MockUserService)
            tt.setupMock(mockService)

            handler := NewUserHandler(mockService)
            router := setupRouter(handler)

            var body io.Reader
            if tt.body != "" {
                body = strings.NewReader(tt.body)
            }

            req := httptest.NewRequest(tt.method, tt.path, body)
            req.Header.Set("Content-Type", "application/json")
            rec := httptest.NewRecorder()

            router.ServeHTTP(rec, req)

            assert.Equal(t, tt.expectedStatus, rec.Code)
            if tt.expectedBody != "" {
                assert.JSONEq(t, tt.expectedBody, rec.Body.String())
            }
            mockService.AssertExpectations(t)
        })
    }
}
```

## Pattern 6: Custom Assertions

### When to Use

When you have domain-specific validation logic used across multiple tests.

### Implementation

```go
// Custom assertion function
func AssertValidUser(t *testing.T, user *User) {
    t.Helper() // Marks this as a helper function for better error reporting

    require.NotNil(t, user, "user should not be nil")
    assert.NotZero(t, user.ID, "user should have an ID")
    assert.NotEmpty(t, user.Name, "user should have a name")
    assert.NotEmpty(t, user.Email, "user should have an email")
    assert.Contains(t, user.Email, "@", "email should contain @")
    assert.False(t, user.CreatedAt.IsZero(), "created_at should be set")
}

// Custom assertion for API responses
func AssertAPISuccess(t *testing.T, resp *httptest.ResponseRecorder) {
    t.Helper()

    assert.Equal(t, http.StatusOK, resp.Code)
    assert.Contains(t, resp.Header().Get("Content-Type"), "application/json")

    var response map[string]interface{}
    err := json.Unmarshal(resp.Body.Bytes(), &response)
    require.NoError(t, err, "response should be valid JSON")
    assert.NotContains(t, response, "error", "response should not contain error")
}

// Usage
func TestCreateUser(t *testing.T) {
    user, err := service.CreateUser("Alice", "alice@example.com")
    require.NoError(t, err)
    AssertValidUser(t, user)
}
```

## Anti-Patterns

### Anti-Pattern 1: Testing Implementation Details

```go
// Bad: testing internal implementation
func TestBad(t *testing.T) {
    service := NewUserService(repo)
    service.cache["user:1"] = user // Accessing internal field!
    // ...
}

// Good: test through public interface
func TestGood(t *testing.T) {
    service := NewUserService(repo)
    service.CacheUser(user)
    cached, err := service.GetCachedUser(user.ID)
    // ...
}
```

### Anti-Pattern 2: Over-Mocking

```go
// Bad: mocking everything including simple value objects
func TestBad(t *testing.T) {
    mockUser := new(MockUser) // User is just a struct!
    mockUser.On("GetName").Return("Alice")
    // ...
}

// Good: only mock external dependencies and interfaces
func TestGood(t *testing.T) {
    user := &User{Name: "Alice"} // Use real objects when possible
    mockRepo := new(MockUserRepository) // Mock the repository
    // ...
}
```

### Anti-Pattern 3: Ignoring Test Failure Messages

```go
// Bad: no context on failure
assert.Equal(t, expected, actual)

// Good: descriptive message
assert.Equal(t, expected, actual, "user count after deletion should be %d", expected)
```

### Anti-Pattern 4: Not Cleaning Up in Suites

```go
// Bad: state leaks between tests
func (s *MySuite) TestA() {
    s.db.Exec("INSERT INTO users VALUES (1, 'Alice')")
    // TestB might fail because Alice already exists
}

// Good: clean up in SetupTest
func (s *MySuite) SetupTest() {
    s.db.Exec("DELETE FROM users")
}
```

## Best Practices Summary

1. **Use require for preconditions**, assert for validations
2. **One concept per test** - keep tests focused
3. **Name tests descriptively** - `TestUserService_CreateUser_WithInvalidEmail`
4. **Always verify mock expectations** - call `AssertExpectations`
5. **Clean up in TearDown** - don't leak resources
6. **Use table-driven tests** - reduce duplication
7. **Test error paths** - not just happy paths
8. **Use custom assertions** - for domain-specific checks
9. **Don't mock value objects** - only mock behavior
10. **Run tests with -race** - catch concurrency bugs
