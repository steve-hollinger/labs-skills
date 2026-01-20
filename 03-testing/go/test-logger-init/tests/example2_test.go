package tests

import (
	"fmt"
	"testing"
	"time"

	"github.com/stretchr/testify/assert"
	"github.com/stretchr/testify/require"
)

// ============================================================================
// Example 2: Test Fixtures
// ============================================================================

// Domain types
type User struct {
	ID        int64
	Name      string
	Email     string
	Role      string
	Active    bool
	CreatedAt time.Time
}

type Product struct {
	ID          int64
	Name        string
	Price       float64
	CategoryID  int64
	InStock     bool
}

type Order struct {
	ID        int64
	UserID    int64
	Items     []OrderItem
	Total     float64
	Status    string
	CreatedAt time.Time
}

type OrderItem struct {
	ProductID int64
	Quantity  int
	Price     float64
}

// ============================================================================
// Simple Fixtures
// ============================================================================

type UserFixtures struct {
	StandardUser *User
	AdminUser    *User
	InactiveUser *User
}

func NewUserFixtures() *UserFixtures {
	now := time.Now()
	return &UserFixtures{
		StandardUser: &User{
			ID:        1,
			Name:      "Standard User",
			Email:     "user@example.com",
			Role:      "user",
			Active:    true,
			CreatedAt: now,
		},
		AdminUser: &User{
			ID:        2,
			Name:      "Admin User",
			Email:     "admin@example.com",
			Role:      "admin",
			Active:    true,
			CreatedAt: now,
		},
		InactiveUser: &User{
			ID:        3,
			Name:      "Inactive User",
			Email:     "inactive@example.com",
			Role:      "user",
			Active:    false,
			CreatedAt: now.Add(-30 * 24 * time.Hour),
		},
	}
}

func TestExample2_SimpleFixtures(t *testing.T) {
	fixtures := NewUserFixtures()

	t.Run("standard user", func(t *testing.T) {
		user := fixtures.StandardUser
		assert.Equal(t, "user", user.Role)
		assert.True(t, user.Active)
	})

	t.Run("admin user", func(t *testing.T) {
		user := fixtures.AdminUser
		assert.Equal(t, "admin", user.Role)
		assert.True(t, user.Active)
	})

	t.Run("inactive user", func(t *testing.T) {
		user := fixtures.InactiveUser
		assert.False(t, user.Active)
	})
}

// ============================================================================
// Builder Pattern Fixtures
// ============================================================================

type UserBuilder struct {
	user User
}

func NewUserBuilder() *UserBuilder {
	return &UserBuilder{
		user: User{
			Name:      "Default Name",
			Email:     "default@example.com",
			Role:      "user",
			Active:    true,
			CreatedAt: time.Now(),
		},
	}
}

func (b *UserBuilder) WithID(id int64) *UserBuilder {
	b.user.ID = id
	return b
}

func (b *UserBuilder) WithName(name string) *UserBuilder {
	b.user.Name = name
	return b
}

func (b *UserBuilder) WithEmail(email string) *UserBuilder {
	b.user.Email = email
	return b
}

func (b *UserBuilder) WithRole(role string) *UserBuilder {
	b.user.Role = role
	return b
}

func (b *UserBuilder) AsAdmin() *UserBuilder {
	b.user.Role = "admin"
	return b
}

func (b *UserBuilder) AsInactive() *UserBuilder {
	b.user.Active = false
	return b
}

func (b *UserBuilder) Build() User {
	return b.user
}

func (b *UserBuilder) BuildPtr() *User {
	user := b.user
	return &user
}

func TestExample2_BuilderPattern(t *testing.T) {
	t.Run("default user", func(t *testing.T) {
		user := NewUserBuilder().Build()
		assert.Equal(t, "Default Name", user.Name)
		assert.Equal(t, "user", user.Role)
		assert.True(t, user.Active)
	})

	t.Run("custom user", func(t *testing.T) {
		user := NewUserBuilder().
			WithID(42).
			WithName("Alice").
			WithEmail("alice@example.com").
			Build()

		assert.Equal(t, int64(42), user.ID)
		assert.Equal(t, "Alice", user.Name)
		assert.Equal(t, "alice@example.com", user.Email)
	})

	t.Run("admin user", func(t *testing.T) {
		user := NewUserBuilder().
			WithName("Super Admin").
			AsAdmin().
			Build()

		assert.Equal(t, "admin", user.Role)
	})

	t.Run("inactive user", func(t *testing.T) {
		user := NewUserBuilder().
			AsInactive().
			Build()

		assert.False(t, user.Active)
	})
}

// ============================================================================
// Factory Pattern Fixtures
// ============================================================================

type OrderFactory struct {
	sequence int64
}

func NewOrderFactory() *OrderFactory {
	return &OrderFactory{}
}

func (f *OrderFactory) nextID() int64 {
	f.sequence++
	return f.sequence
}

type OrderOption func(*Order)

func WithUserID(id int64) OrderOption {
	return func(o *Order) {
		o.UserID = id
	}
}

func WithStatus(status string) OrderOption {
	return func(o *Order) {
		o.Status = status
	}
}

func WithItems(items ...OrderItem) OrderOption {
	return func(o *Order) {
		o.Items = items
		var total float64
		for _, item := range items {
			total += item.Price * float64(item.Quantity)
		}
		o.Total = total
	}
}

func (f *OrderFactory) Create(opts ...OrderOption) *Order {
	order := &Order{
		ID:        f.nextID(),
		UserID:    1,
		Status:    "pending",
		Items:     []OrderItem{},
		Total:     0,
		CreatedAt: time.Now(),
	}

	for _, opt := range opts {
		opt(order)
	}

	return order
}

func TestExample2_FactoryPattern(t *testing.T) {
	factory := NewOrderFactory()

	t.Run("default order", func(t *testing.T) {
		order := factory.Create()
		assert.NotZero(t, order.ID)
		assert.Equal(t, "pending", order.Status)
	})

	t.Run("custom order", func(t *testing.T) {
		order := factory.Create(
			WithUserID(42),
			WithStatus("shipped"),
			WithItems(
				OrderItem{ProductID: 1, Quantity: 2, Price: 10.00},
				OrderItem{ProductID: 2, Quantity: 1, Price: 25.00},
			),
		)

		assert.Equal(t, int64(42), order.UserID)
		assert.Equal(t, "shipped", order.Status)
		assert.Len(t, order.Items, 2)
		assert.Equal(t, 45.00, order.Total)
	})

	t.Run("unique ids", func(t *testing.T) {
		order1 := factory.Create()
		order2 := factory.Create()
		order3 := factory.Create()

		assert.NotEqual(t, order1.ID, order2.ID)
		assert.NotEqual(t, order2.ID, order3.ID)
	})
}

// ============================================================================
// Test Helpers
// ============================================================================

// assertUserValid is a helper that validates a user
func assertUserValid(t *testing.T, user *User) {
	t.Helper() // IMPORTANT: marks this as a helper function

	require.NotNil(t, user, "user should not be nil")
	assert.NotZero(t, user.ID, "user should have an ID")
	assert.NotEmpty(t, user.Name, "user should have a name")
	assert.NotEmpty(t, user.Email, "user should have an email")
	assert.Contains(t, user.Email, "@", "email should contain @")
}

// requireOrderComplete is a helper that checks order completion
func requireOrderComplete(t *testing.T, order *Order) {
	t.Helper()

	require.NotNil(t, order)
	require.NotEmpty(t, order.Items, "order must have items")
	require.Greater(t, order.Total, 0.0, "order total must be positive")
	require.Equal(t, "completed", order.Status)
}

func TestExample2_TestHelpers(t *testing.T) {
	t.Run("valid user", func(t *testing.T) {
		user := NewUserBuilder().
			WithID(1).
			WithName("Alice").
			WithEmail("alice@example.com").
			BuildPtr()

		assertUserValid(t, user)
	})

	t.Run("complete order", func(t *testing.T) {
		factory := NewOrderFactory()
		order := factory.Create(
			WithStatus("completed"),
			WithItems(OrderItem{ProductID: 1, Quantity: 1, Price: 10.00}),
		)

		requireOrderComplete(t, order)
	})
}

// ============================================================================
// Fixture with Cleanup
// ============================================================================

// TestContext holds test state with automatic cleanup
type TestContext struct {
	t        *testing.T
	users    []*User
	orders   []*Order
	cleanups []func()
}

func NewTestContext(t *testing.T) *TestContext {
	ctx := &TestContext{t: t}
	t.Cleanup(func() {
		ctx.cleanup()
	})
	return ctx
}

func (ctx *TestContext) cleanup() {
	// Run cleanups in reverse order
	for i := len(ctx.cleanups) - 1; i >= 0; i-- {
		ctx.cleanups[i]()
	}
}

func (ctx *TestContext) CreateUser(name, email string) *User {
	ctx.t.Helper()

	user := NewUserBuilder().
		WithID(int64(len(ctx.users) + 1)).
		WithName(name).
		WithEmail(email).
		BuildPtr()

	ctx.users = append(ctx.users, user)

	ctx.cleanups = append(ctx.cleanups, func() {
		ctx.t.Logf("Cleaning up user: %s", user.Email)
	})

	return user
}

func (ctx *TestContext) GetUserCount() int {
	return len(ctx.users)
}

func TestExample2_FixtureWithCleanup(t *testing.T) {
	ctx := NewTestContext(t)

	user1 := ctx.CreateUser("Alice", "alice@example.com")
	user2 := ctx.CreateUser("Bob", "bob@example.com")

	assert.Equal(t, 2, ctx.GetUserCount())
	assert.Equal(t, "Alice", user1.Name)
	assert.Equal(t, "Bob", user2.Name)

	// Cleanup runs automatically when test completes
}

// ============================================================================
// Table-Driven Tests with Fixtures
// ============================================================================

func TestExample2_TableDrivenWithFixtures(t *testing.T) {
	fixtures := NewUserFixtures()

	tests := []struct {
		name     string
		user     *User
		canAdmin bool
		isActive bool
	}{
		{
			name:     "standard user cannot admin",
			user:     fixtures.StandardUser,
			canAdmin: false,
			isActive: true,
		},
		{
			name:     "admin user can admin",
			user:     fixtures.AdminUser,
			canAdmin: true,
			isActive: true,
		},
		{
			name:     "inactive user",
			user:     fixtures.InactiveUser,
			canAdmin: false,
			isActive: false,
		},
	}

	for _, tt := range tests {
		t.Run(tt.name, func(t *testing.T) {
			canAdmin := tt.user.Role == "admin"
			assert.Equal(t, tt.canAdmin, canAdmin)
			assert.Equal(t, tt.isActive, tt.user.Active)
		})
	}
}

func TestExample2_TableDrivenWithBuilder(t *testing.T) {
	tests := []struct {
		name    string
		builder func() *UserBuilder
		check   func(*testing.T, User)
	}{
		{
			name: "default user is active",
			builder: func() *UserBuilder {
				return NewUserBuilder()
			},
			check: func(t *testing.T, u User) {
				assert.True(t, u.Active)
			},
		},
		{
			name: "admin has admin role",
			builder: func() *UserBuilder {
				return NewUserBuilder().AsAdmin()
			},
			check: func(t *testing.T, u User) {
				assert.Equal(t, "admin", u.Role)
			},
		},
		{
			name: "custom email is set",
			builder: func() *UserBuilder {
				return NewUserBuilder().WithEmail("custom@example.com")
			},
			check: func(t *testing.T, u User) {
				assert.Equal(t, "custom@example.com", u.Email)
			},
		},
	}

	for _, tt := range tests {
		t.Run(tt.name, func(t *testing.T) {
			user := tt.builder().Build()
			tt.check(t, user)
		})
	}
}

// Helper for generating unique test data
func uniqueEmail(prefix string) string {
	return fmt.Sprintf("%s_%d@example.com", prefix, time.Now().UnixNano())
}

func TestExample2_UniqueFixtures(t *testing.T) {
	// For parallel tests, use unique data
	t.Parallel()

	email := uniqueEmail("parallel_test")
	user := NewUserBuilder().
		WithEmail(email).
		Build()

	assert.Contains(t, user.Email, "parallel_test")
}
