package tests

import (
	"errors"
	"testing"

	"github.com/stretchr/testify/assert"
	"github.com/stretchr/testify/require"
)

// ============================================================================
// Example 1: Basic Assertions with assert and require
// ============================================================================

// User for testing
type User struct {
	ID       int64
	Name     string
	Email    string
	Active   bool
	Tags     []string
	Metadata map[string]string
}

func NewUser(name, email string) (*User, error) {
	if name == "" {
		return nil, errors.New("name is required")
	}
	if email == "" {
		return nil, errors.New("email is required")
	}
	return &User{
		ID:       1,
		Name:     name,
		Email:    email,
		Active:   true,
		Tags:     []string{"new"},
		Metadata: map[string]string{"source": "api"},
	}, nil
}

// Calculator for testing
type Calculator struct{}

func (c *Calculator) Add(a, b int) int {
	return a + b
}

func (c *Calculator) Divide(a, b int) (int, error) {
	if b == 0 {
		return 0, errors.New("division by zero")
	}
	return a / b, nil
}

// TestExample1_EqualityAssertions demonstrates equality assertions
func TestExample1_EqualityAssertions(t *testing.T) {
	calc := &Calculator{}

	// assert.Equal - checks deep equality
	assert.Equal(t, 5, calc.Add(2, 3), "2 + 3 should equal 5")
	assert.Equal(t, 0, calc.Add(-5, 5), "negative plus positive")

	// assert.NotEqual
	assert.NotEqual(t, 10, calc.Add(2, 3), "2 + 3 should not equal 10")

	// Comparing structs
	user1 := User{ID: 1, Name: "Alice"}
	user2 := User{ID: 1, Name: "Alice"}
	user3 := User{ID: 2, Name: "Bob"}

	assert.Equal(t, user1, user2, "same values should be equal")
	assert.NotEqual(t, user1, user3, "different users should not be equal")
}

// TestExample1_NilAssertions demonstrates nil checking
func TestExample1_NilAssertions(t *testing.T) {
	// Valid user
	user, err := NewUser("Alice", "alice@example.com")
	assert.NoError(t, err)
	assert.NotNil(t, user)

	// Invalid user - missing name
	nilUser, err := NewUser("", "test@example.com")
	assert.Error(t, err)
	assert.Nil(t, nilUser)
}

// TestExample1_BooleanAssertions demonstrates boolean assertions
func TestExample1_BooleanAssertions(t *testing.T) {
	user, err := NewUser("Alice", "alice@example.com")
	require.NoError(t, err)

	// assert.True / assert.False
	assert.True(t, user.Active, "new users should be active")
	assert.False(t, user.ID == 0, "user should have an ID")

	// Boolean expressions
	assert.True(t, len(user.Name) > 0, "name should not be empty")
	assert.True(t, user.Email != "", "email should not be empty")
}

// TestExample1_CollectionAssertions demonstrates collection assertions
func TestExample1_CollectionAssertions(t *testing.T) {
	user, err := NewUser("Alice", "alice@example.com")
	require.NoError(t, err)

	// assert.Contains - strings
	assert.Contains(t, user.Email, "@", "email should contain @")
	assert.Contains(t, user.Email, "example.com", "email should contain domain")

	// assert.Contains - slices
	assert.Contains(t, user.Tags, "new", "tags should contain 'new'")

	// assert.Contains - maps
	assert.Contains(t, user.Metadata, "source", "metadata should have 'source' key")

	// assert.Len - check length
	assert.Len(t, user.Tags, 1, "should have exactly one tag")
	assert.Len(t, user.Metadata, 1, "should have exactly one metadata entry")

	// assert.Empty / assert.NotEmpty
	assert.NotEmpty(t, user.Name, "name should not be empty")
	assert.NotEmpty(t, user.Tags, "tags should not be empty")

	emptyTags := []string{}
	assert.Empty(t, emptyTags, "empty slice should be empty")

	// assert.ElementsMatch - same elements, any order
	expected := []string{"new"}
	assert.ElementsMatch(t, expected, user.Tags)

	// Multiple elements
	list1 := []int{1, 2, 3}
	list2 := []int{3, 1, 2}
	assert.ElementsMatch(t, list1, list2, "same elements in different order")
}

// TestExample1_ErrorAssertions demonstrates error assertions
func TestExample1_ErrorAssertions(t *testing.T) {
	calc := &Calculator{}

	// assert.NoError - successful operation
	result, err := calc.Divide(10, 2)
	assert.NoError(t, err)
	assert.Equal(t, 5, result)

	// assert.Error - failed operation
	_, err = calc.Divide(10, 0)
	assert.Error(t, err)

	// assert.ErrorContains - check error message
	assert.ErrorContains(t, err, "division by zero")

	// assert.ErrorIs - check error type
	customErr := errors.New("custom error")
	wrappedErr := errors.New("custom error")
	assert.EqualError(t, customErr, wrappedErr.Error())
}

// TestExample1_ComparisonAssertions demonstrates numeric comparisons
func TestExample1_ComparisonAssertions(t *testing.T) {
	// assert.Greater
	assert.Greater(t, 5, 3, "5 should be greater than 3")

	// assert.GreaterOrEqual
	assert.GreaterOrEqual(t, 5, 5, "5 should be >= 5")
	assert.GreaterOrEqual(t, 5, 3, "5 should be >= 3")

	// assert.Less
	assert.Less(t, 3, 5, "3 should be less than 5")

	// assert.LessOrEqual
	assert.LessOrEqual(t, 3, 5, "3 should be <= 5")
	assert.LessOrEqual(t, 5, 5, "5 should be <= 5")

	// assert.Positive / assert.Negative
	assert.Positive(t, 5, "5 should be positive")
	assert.Negative(t, -5, "-5 should be negative")
	assert.Zero(t, 0, "0 should be zero")
}

// TestExample1_RequireVsAssert demonstrates when to use require vs assert
func TestExample1_RequireVsAssert(t *testing.T) {
	// require stops test immediately on failure
	// Use for preconditions that would cause panics if violated

	user, err := NewUser("Alice", "alice@example.com")

	// REQUIRE: Stop if these fail (would panic on user.Name otherwise)
	require.NoError(t, err, "user creation must succeed")
	require.NotNil(t, user, "user must not be nil")

	// ASSERT: Continue checking even if one fails
	assert.Equal(t, "Alice", user.Name)
	assert.Equal(t, "alice@example.com", user.Email)
	assert.True(t, user.Active)
	assert.NotZero(t, user.ID)
}

// TestExample1_TableDriven demonstrates table-driven tests with testify
func TestExample1_TableDriven(t *testing.T) {
	calc := &Calculator{}

	tests := []struct {
		name     string
		a        int
		b        int
		expected int
		wantErr  bool
	}{
		{
			name:     "positive numbers",
			a:        5,
			b:        3,
			expected: 8,
			wantErr:  false,
		},
		{
			name:     "negative numbers",
			a:        -5,
			b:        -3,
			expected: -8,
			wantErr:  false,
		},
		{
			name:     "mixed numbers",
			a:        5,
			b:        -3,
			expected: 2,
			wantErr:  false,
		},
		{
			name:     "zeros",
			a:        0,
			b:        0,
			expected: 0,
			wantErr:  false,
		},
	}

	for _, tt := range tests {
		t.Run(tt.name, func(t *testing.T) {
			result := calc.Add(tt.a, tt.b)
			assert.Equal(t, tt.expected, result)
		})
	}
}

// TestExample1_TableDrivenWithErrors demonstrates table-driven tests with error cases
func TestExample1_TableDrivenWithErrors(t *testing.T) {
	calc := &Calculator{}

	tests := []struct {
		name     string
		a        int
		b        int
		expected int
		wantErr  bool
		errMsg   string
	}{
		{
			name:     "valid division",
			a:        10,
			b:        2,
			expected: 5,
			wantErr:  false,
		},
		{
			name:     "division by zero",
			a:        10,
			b:        0,
			expected: 0,
			wantErr:  true,
			errMsg:   "division by zero",
		},
		{
			name:     "integer division",
			a:        10,
			b:        3,
			expected: 3, // Integer division truncates
			wantErr:  false,
		},
	}

	for _, tt := range tests {
		t.Run(tt.name, func(t *testing.T) {
			result, err := calc.Divide(tt.a, tt.b)

			if tt.wantErr {
				require.Error(t, err)
				assert.ErrorContains(t, err, tt.errMsg)
				return
			}

			require.NoError(t, err)
			assert.Equal(t, tt.expected, result)
		})
	}
}
