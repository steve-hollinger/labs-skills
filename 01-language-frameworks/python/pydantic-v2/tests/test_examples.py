"""Tests for Pydantic v2 examples."""

from datetime import date, datetime
from decimal import Decimal

import pytest
from pydantic import ValidationError


class TestExample1BasicModels:
    """Tests for Example 1: Basic Models."""

    def test_user_creation(self) -> None:
        """Test basic user model creation."""
        from pydantic_v2.examples.example_1_basic_models import User, UserRole

        user = User(
            username="testuser",
            email="test@example.com",
            age=25,
        )
        assert user.username == "testuser"
        assert user.email == "test@example.com"
        assert user.age == 25
        assert user.role == UserRole.USER
        assert user.is_active is True

    def test_user_email_validation(self) -> None:
        """Test email validation."""
        from pydantic_v2.examples.example_1_basic_models import User

        with pytest.raises(ValidationError) as exc_info:
            User(username="testuser", email="not-an-email")
        assert "email" in str(exc_info.value).lower()

    def test_user_age_constraints(self) -> None:
        """Test age field constraints."""
        from pydantic_v2.examples.example_1_basic_models import User

        # Valid age
        user = User(username="testuser", email="test@example.com", age=100)
        assert user.age == 100

        # Age too high
        with pytest.raises(ValidationError):
            User(username="testuser", email="test@example.com", age=200)

        # Negative age
        with pytest.raises(ValidationError):
            User(username="testuser", email="test@example.com", age=-5)

    def test_product_sku_pattern(self) -> None:
        """Test SKU pattern validation."""
        from pydantic_v2.examples.example_1_basic_models import Product

        # Valid SKU
        product = Product(name="Test", price=10.0, sku="ABC-1234")
        assert product.sku == "ABC-1234"

        # Invalid SKU format
        with pytest.raises(ValidationError):
            Product(name="Test", price=10.0, sku="invalid")

    def test_product_price_constraint(self) -> None:
        """Test price must be positive."""
        from pydantic_v2.examples.example_1_basic_models import Product

        with pytest.raises(ValidationError):
            Product(name="Test", price=0, sku="ABC-1234")

        with pytest.raises(ValidationError):
            Product(name="Test", price=-10, sku="ABC-1234")

    def test_type_coercion(self) -> None:
        """Test automatic type coercion."""
        from pydantic_v2.examples.example_1_basic_models import User

        # String to int coercion
        user = User(username="testuser", email="test@example.com", age="30")  # type: ignore
        assert user.age == 30
        assert isinstance(user.age, int)


class TestExample2Validators:
    """Tests for Example 2: Custom Validators."""

    def test_username_normalization(self) -> None:
        """Test username is normalized to lowercase."""
        from pydantic_v2.examples.example_2_validators import UserRegistration

        user = UserRegistration(
            username="TestUser_123",
            email="test@example.com",
            password="SecurePass1",
            password_confirm="SecurePass1",
        )
        assert user.username == "testuser_123"

    def test_username_alphanumeric_check(self) -> None:
        """Test username must be alphanumeric with underscores."""
        from pydantic_v2.examples.example_2_validators import UserRegistration

        with pytest.raises(ValidationError) as exc_info:
            UserRegistration(
                username="test@user",
                email="test@example.com",
                password="SecurePass1",
                password_confirm="SecurePass1",
            )
        assert "alphanumeric" in str(exc_info.value).lower()

    def test_password_strength(self) -> None:
        """Test password strength requirements."""
        from pydantic_v2.examples.example_2_validators import UserRegistration

        # No uppercase
        with pytest.raises(ValidationError) as exc_info:
            UserRegistration(
                username="testuser",
                email="test@example.com",
                password="weakpassword1",
                password_confirm="weakpassword1",
            )
        assert "uppercase" in str(exc_info.value).lower()

        # No digit
        with pytest.raises(ValidationError) as exc_info:
            UserRegistration(
                username="testuser",
                email="test@example.com",
                password="WeakPassword",
                password_confirm="WeakPassword",
            )
        assert "digit" in str(exc_info.value).lower()

    def test_password_match(self) -> None:
        """Test password confirmation must match."""
        from pydantic_v2.examples.example_2_validators import UserRegistration

        with pytest.raises(ValidationError) as exc_info:
            UserRegistration(
                username="testuser",
                email="test@example.com",
                password="SecurePass1",
                password_confirm="DifferentPass1",
            )
        assert "match" in str(exc_info.value).lower()

    def test_date_range_validation(self) -> None:
        """Test date range cross-field validation."""
        from pydantic_v2.examples.example_2_validators import DateRange

        # Valid range
        range_valid = DateRange(
            start_date=date(2024, 1, 1),
            end_date=date(2024, 12, 31),
        )
        assert range_valid.start_date < range_valid.end_date

        # Invalid range (end before start)
        with pytest.raises(ValidationError) as exc_info:
            DateRange(
                start_date=date(2024, 12, 31),
                end_date=date(2024, 1, 1),
            )
        assert "after" in str(exc_info.value).lower()

    def test_price_string_conversion(self) -> None:
        """Test price string to float conversion."""
        from pydantic_v2.examples.example_2_validators import PriceWithDiscount

        price = PriceWithDiscount(
            original_price="$1,299.99",
            discount_percent="15",
        )
        assert price.original_price == 1300.00  # Rounded
        assert price.discount_percent == 15.0

    def test_credit_card_luhn(self) -> None:
        """Test credit card Luhn validation."""
        from pydantic_v2.examples.example_2_validators import CreditCard

        # Valid test card number
        card = CreditCard(
            number="4111111111111111",
            expiry_month=12,
            expiry_year=2030,
            cvv="123",
        )
        assert card.number == "4111111111111111"

        # Invalid Luhn
        with pytest.raises(ValidationError):
            CreditCard(
                number="4111111111111112",
                expiry_month=12,
                expiry_year=2030,
                cvv="123",
            )


class TestExample3Serialization:
    """Tests for Example 3: Serialization."""

    def test_money_serialization(self) -> None:
        """Test Money amount serializes to 2 decimal string."""
        from pydantic_v2.examples.example_3_serialization import Money

        money = Money(amount=Decimal("99.999"))
        data = money.model_dump()
        assert data["amount"] == "100.00"

    def test_order_computed_fields(self) -> None:
        """Test Order computed fields."""
        from pydantic_v2.examples.example_3_serialization import (
            Money,
            Order,
            OrderItem,
        )

        order = Order(
            customer_email="test@example.com",
            items=[
                OrderItem(
                    product_name="Item 1",
                    quantity=2,
                    unit_price=Money(amount=Decimal("10.00")),
                ),
                OrderItem(
                    product_name="Item 2",
                    quantity=1,
                    unit_price=Money(amount=Decimal("25.00")),
                ),
            ],
        )
        assert order.item_count == 3
        assert order.order_total.amount == Decimal("45.00")

    def test_excluded_field(self) -> None:
        """Test internal_reference is excluded from serialization."""
        from pydantic_v2.examples.example_3_serialization import Money, Order, OrderItem

        order = Order(
            customer_email="test@example.com",
            items=[
                OrderItem(
                    product_name="Item",
                    quantity=1,
                    unit_price=Money(amount=Decimal("10.00")),
                )
            ],
            internal_reference="SECRET-123",
        )
        data = order.model_dump()
        assert "internal_reference" not in data

    def test_user_profile_aliases(self) -> None:
        """Test UserProfile alias serialization."""
        from pydantic_v2.examples.example_3_serialization import UserProfile

        # Create from camelCase
        profile = UserProfile(
            userId=1,
            userName="Alice",
            emailAddress="alice@example.com",
        )
        assert profile.user_id == 1
        assert profile.user_name == "Alice"

        # Serialize with aliases
        data = profile.model_dump(by_alias=True)
        assert "userId" in data
        assert "userName" in data

    def test_order_copy_with_update(self) -> None:
        """Test model_copy with update."""
        from pydantic_v2.examples.example_3_serialization import (
            Money,
            Order,
            OrderItem,
            OrderStatus,
        )

        order = Order(
            customer_email="test@example.com",
            items=[
                OrderItem(
                    product_name="Item",
                    quantity=1,
                    unit_price=Money(amount=Decimal("10.00")),
                )
            ],
        )
        assert order.status == OrderStatus.PENDING

        updated = order.model_copy(update={"status": OrderStatus.SHIPPED})
        assert updated.status == OrderStatus.SHIPPED
        assert order.status == OrderStatus.PENDING  # Original unchanged


class TestExample4Composition:
    """Tests for Example 4: Model Composition."""

    def test_model_inheritance(self) -> None:
        """Test model inheritance works correctly."""
        from pydantic_v2.examples.example_4_composition import AdminUser, User

        user = User(id=1, username="testuser", email="test@example.com")
        assert hasattr(user, "created_at")

        admin = AdminUser(
            id=2,
            username="admin",
            email="admin@example.com",
            admin_level=9,
        )
        assert admin.is_super_admin is True

        low_admin = AdminUser(
            id=3, username="lowadmin", email="low@example.com", admin_level=2
        )
        assert low_admin.is_super_admin is False

    def test_nested_models(self) -> None:
        """Test nested model creation and access."""
        from pydantic_v2.examples.example_4_composition import (
            Address,
            Company,
            ContactInfo,
            User,
        )

        company = Company(
            name="TestCorp",
            contact=ContactInfo(
                email="info@testcorp.com",
                address=Address(
                    street="123 Test St",
                    city="TestCity",
                    state="TS",
                    postal_code="12345",
                ),
            ),
        )
        assert company.contact.address.city == "TestCity"
        assert company.contact.address.full_address == "123 Test St, TestCity, TS 12345"

    def test_generic_paginated_response(self) -> None:
        """Test generic PaginatedResponse."""
        from pydantic_v2.examples.example_4_composition import (
            PaginatedResponse,
            User,
        )

        users = [
            User(id=i, username=f"user{i}", email=f"user{i}@test.com")
            for i in range(1, 6)
        ]

        paginated = PaginatedResponse[User](
            items=users, total=15, page=1, page_size=5
        )
        assert paginated.total_pages == 3
        assert paginated.has_next is True
        assert paginated.has_previous is False

    def test_discriminated_union(self) -> None:
        """Test discriminated union parsing."""
        from pydantic_v2.examples.example_4_composition import (
            EmailNotification,
            NotificationBatch,
            SMSNotification,
        )

        batch = NotificationBatch(
            batch_id="test-batch",
            notifications=[
                {"type": "email", "to": "test@example.com", "subject": "Hi", "body": "Hello"},
                {"type": "sms", "phone_number": "+1234567890", "message": "Hi there"},
            ],
        )

        assert len(batch.notifications) == 2
        assert isinstance(batch.notifications[0], EmailNotification)
        assert isinstance(batch.notifications[1], SMSNotification)
        assert batch.notification_counts["email"] == 1
        assert batch.notification_counts["sms"] == 1

    def test_api_response_generic(self) -> None:
        """Test generic APIResponse wrapper."""
        from pydantic_v2.examples.example_4_composition import APIResponse, User

        # Success response
        user = User(id=1, username="test", email="test@example.com")
        success = APIResponse[User](success=True, data=user)
        assert success.data is not None
        assert success.data.username == "test"

        # Error response
        error = APIResponse[User](success=False, error="Not found")
        assert error.data is None
        assert error.error == "Not found"
