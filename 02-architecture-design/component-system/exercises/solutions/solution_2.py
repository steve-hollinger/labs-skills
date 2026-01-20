"""Solution for Exercise 2: Build a Component with Multiple Dependencies

This solution demonstrates a complete NotificationService with proper
dependency injection and error handling.
"""

import asyncio
from typing import Any, ClassVar

from component_system import Component, Registry, Requires


class UserRepository(Component):
    """Repository for user data."""

    name: ClassVar[str] = "user-repository"

    def __init__(self, config: dict[str, Any] | None = None) -> None:
        super().__init__(config)
        self._users: dict[str, dict[str, Any]] = {}

    async def initialize(self) -> None:
        """Load initial users."""
        await super().initialize()
        self._users = {
            "u1": {"id": "u1", "name": "Alice", "email": "alice@example.com"},
            "u2": {"id": "u2", "name": "Bob", "email": "bob@example.com"},
            "u3": {"id": "u3", "name": "Charlie", "email": "charlie@example.com"},
        }
        print(f"  [UserRepository] Loaded {len(self._users)} users")

    async def start(self) -> None:
        """Start the repository."""
        await super().start()
        print("  [UserRepository] Ready")

    async def stop(self) -> None:
        """Stop the repository."""
        print("  [UserRepository] Stopped")
        await super().stop()

    async def get_user(self, user_id: str) -> dict[str, Any] | None:
        """Get user by ID."""
        return self._users.get(user_id)

    async def add_user(self, user: dict[str, Any]) -> None:
        """Add a user."""
        self._users[user["id"]] = user


class TemplateEngine(Component):
    """Template rendering engine."""

    name: ClassVar[str] = "template-engine"

    def __init__(self, config: dict[str, Any] | None = None) -> None:
        super().__init__(config)
        self._templates: dict[str, str] = {}

    async def initialize(self) -> None:
        """Load templates."""
        await super().initialize()
        self._templates = {
            "welcome": "Hello {name}! Welcome to our service.",
            "notification": "Hi {name}, you have a new notification: {message}",
            "password_reset": "Hi {name}, click here to reset your password: {link}",
            "order_shipped": "Hi {name}, your order #{order_id} has shipped!",
        }
        print(f"  [TemplateEngine] Loaded {len(self._templates)} templates")

    async def start(self) -> None:
        """Start the engine."""
        await super().start()
        print("  [TemplateEngine] Ready")

    async def stop(self) -> None:
        """Stop the engine."""
        print("  [TemplateEngine] Stopped")
        await super().stop()

    def render(self, template_name: str, data: dict[str, Any]) -> str | None:
        """Render a template with data."""
        template = self._templates.get(template_name)
        if template is None:
            return None
        try:
            return template.format(**data)
        except KeyError as e:
            print(f"  [TemplateEngine] Missing template variable: {e}")
            return None

    def add_template(self, name: str, template: str) -> None:
        """Add a new template."""
        self._templates[name] = template


class EmailSender(Component):
    """Email sending component."""

    name: ClassVar[str] = "email-sender"

    def __init__(self, config: dict[str, Any] | None = None) -> None:
        super().__init__(config)
        self._sent_emails: list[dict[str, str]] = []
        self._from_address: str = "noreply@example.com"

    async def initialize(self) -> None:
        """Configure email settings."""
        await super().initialize()
        self._from_address = self.config.get("from_address", "noreply@example.com")
        print(f"  [EmailSender] From address: {self._from_address}")

    async def start(self) -> None:
        """Start email service."""
        await super().start()
        print("  [EmailSender] Ready")

    async def stop(self) -> None:
        """Stop email service."""
        print(f"  [EmailSender] Sent {len(self._sent_emails)} emails total")
        await super().stop()

    async def send(self, to: str, subject: str, body: str) -> bool:
        """Send an email (simulated)."""
        email = {
            "from": self._from_address,
            "to": to,
            "subject": subject,
            "body": body,
        }
        self._sent_emails.append(email)
        print(f"  [EmailSender] Sent email to {to}: {subject}")
        return True

    @property
    def sent_emails(self) -> list[dict[str, str]]:
        """Get list of sent emails."""
        return self._sent_emails


class NotificationService(Component):
    """Service for sending notifications to users."""

    name: ClassVar[str] = "notification-service"

    # Declare dependencies using Requires()
    user_repo: UserRepository = Requires()
    template_engine: TemplateEngine = Requires()
    email_sender: EmailSender = Requires()

    def __init__(self, config: dict[str, Any] | None = None) -> None:
        super().__init__(config)
        self._default_subject: str = "Notification"

    async def initialize(self) -> None:
        """Initialize the notification service."""
        await super().initialize()
        self._default_subject = self.config.get("default_subject", "Notification")
        print("  [NotificationService] Dependencies injected:")
        print(f"    - user_repo: {self.user_repo.name}")
        print(f"    - template_engine: {self.template_engine.name}")
        print(f"    - email_sender: {self.email_sender.name}")

    async def start(self) -> None:
        """Start the notification service."""
        await super().start()
        print("  [NotificationService] Ready")

    async def stop(self) -> None:
        """Stop the notification service."""
        print("  [NotificationService] Stopped")
        await super().stop()

    async def send_notification(
        self,
        user_id: str,
        template_name: str,
        data: dict[str, Any],
        subject: str | None = None,
    ) -> bool:
        """Send a notification to a user.

        Args:
            user_id: The user ID to send notification to
            template_name: Name of the template to use
            data: Data to render in the template
            subject: Optional email subject (uses default if not provided)

        Returns:
            True if notification was sent, False otherwise
        """
        # 1. Look up user from user_repo
        user = await self.user_repo.get_user(user_id)

        # 2. Return False if user not found
        if user is None:
            print(f"  [NotificationService] User not found: {user_id}")
            return False

        # 3. Add user data to template data
        template_data = {**data, "name": user["name"]}

        # 4. Render template with template_engine
        body = self.template_engine.render(template_name, template_data)

        # 5. Return False if template not found or rendering failed
        if body is None:
            print(f"  [NotificationService] Template error: {template_name}")
            return False

        # 6. Send email with email_sender
        email_subject = subject or f"{self._default_subject}: {template_name.replace('_', ' ').title()}"
        result = await self.email_sender.send(
            to=user["email"],
            subject=email_subject,
            body=body,
        )

        # 7. Return the result
        return result

    async def send_to_all(
        self,
        user_ids: list[str],
        template_name: str,
        data: dict[str, Any],
    ) -> dict[str, bool]:
        """Send notification to multiple users.

        Args:
            user_ids: List of user IDs
            template_name: Template to use
            data: Template data

        Returns:
            Dictionary mapping user_id to success status
        """
        results = {}
        for user_id in user_ids:
            results[user_id] = await self.send_notification(
                user_id, template_name, data
            )
        return results


async def main() -> None:
    """Test the notification service solution."""
    print("Solution 2: NotificationService with Dependencies")
    print("=" * 50)

    registry = Registry()

    # Register components (in any order)
    print("\n1. Registering components...")
    registry.register(NotificationService, config={"default_subject": "Alert"})
    registry.register(UserRepository)
    registry.register(TemplateEngine)
    registry.register(EmailSender, config={"from_address": "notifications@myapp.com"})

    # Start all
    print("\n2. Starting all components...")
    await registry.start_all()

    # Get service
    service = registry.get(NotificationService)

    # Test various notifications
    print("\n3. Sending notifications...")

    # Welcome notification
    result1 = await service.send_notification("u1", "welcome", {})
    print(f"   Welcome to u1: {'Success' if result1 else 'Failed'}")

    # Notification with data
    result2 = await service.send_notification(
        "u2",
        "notification",
        {"message": "Your profile was updated"},
    )
    print(f"   Notification to u2: {'Success' if result2 else 'Failed'}")

    # Order shipped
    result3 = await service.send_notification(
        "u3",
        "order_shipped",
        {"order_id": "12345"},
        subject="Your order is on the way!",
    )
    print(f"   Order shipped to u3: {'Success' if result3 else 'Failed'}")

    # Non-existent user
    result4 = await service.send_notification("u999", "welcome", {})
    print(f"   Welcome to u999: {'Success' if result4 else 'Failed'}")

    # Non-existent template
    result5 = await service.send_notification("u1", "nonexistent", {})
    print(f"   Nonexistent template to u1: {'Success' if result5 else 'Failed'}")

    # Send to all
    print("\n4. Sending to multiple users...")
    results = await service.send_to_all(
        ["u1", "u2", "u3", "u999"],
        "notification",
        {"message": "System maintenance tonight"},
    )
    for user_id, success in results.items():
        print(f"   {user_id}: {'Success' if success else 'Failed'}")

    # Show sent emails
    print("\n5. All sent emails:")
    email_sender = registry.get(EmailSender)
    for i, email in enumerate(email_sender.sent_emails, 1):
        print(f"   {i}. To: {email['to']}")
        print(f"      Subject: {email['subject']}")
        print(f"      Body: {email['body'][:50]}...")

    # Stop all
    print("\n6. Stopping all components...")
    await registry.stop_all()

    print("\n" + "=" * 50)
    print("Solution demonstration complete!")


if __name__ == "__main__":
    asyncio.run(main())
