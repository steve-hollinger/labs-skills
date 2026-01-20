"""Exercise 2: Build a Component with Multiple Dependencies

Create a NotificationService component that depends on:
1. A UserRepository component (for fetching user data)
2. An EmailSender component (for sending emails)
3. A TemplateEngine component (for rendering email templates)

The NotificationService should:
- Look up user by ID to get their email
- Render an email template with user data
- Send the email using the EmailSender

Instructions:
1. Implement the three dependency components (stubs are provided)
2. Create NotificationService that uses Requires() for dependencies
3. Implement send_notification(user_id, template_name, data)
4. Handle cases where user is not found

Expected Output:
- Dependencies should be injected automatically
- Notification should be "sent" successfully
- Proper error handling for missing users

Hints:
- Use the Requires() descriptor for each dependency
- Dependencies are available after initialize() is called
- The registry handles dependency ordering automatically
"""

import asyncio
from typing import Any, ClassVar

from component_system import Component, Requires


class UserRepository(Component):
    """Repository for user data.

    TODO: Implement a simple in-memory user store.
    """

    name: ClassVar[str] = "user-repository"

    def __init__(self, config: dict[str, Any] | None = None) -> None:
        super().__init__(config)
        self._users: dict[str, dict[str, Any]] = {}

    async def initialize(self) -> None:
        """Load initial users."""
        await super().initialize()
        # Add some test users
        self._users = {
            "u1": {"id": "u1", "name": "Alice", "email": "alice@example.com"},
            "u2": {"id": "u2", "name": "Bob", "email": "bob@example.com"},
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
        # TODO: Return user data or None if not found
        pass


class TemplateEngine(Component):
    """Template rendering engine.

    TODO: Implement simple template rendering.
    """

    name: ClassVar[str] = "template-engine"

    def __init__(self, config: dict[str, Any] | None = None) -> None:
        super().__init__(config)
        self._templates: dict[str, str] = {}

    async def initialize(self) -> None:
        """Load templates."""
        await super().initialize()
        # Add some templates
        self._templates = {
            "welcome": "Hello {name}! Welcome to our service.",
            "notification": "Hi {name}, you have a new notification: {message}",
            "password_reset": "Hi {name}, click here to reset your password: {link}",
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
        # TODO: Return rendered template or None if not found
        # Use str.format(**data) for simple templating
        pass


class EmailSender(Component):
    """Email sending component.

    TODO: Implement simulated email sending.
    """

    name: ClassVar[str] = "email-sender"

    def __init__(self, config: dict[str, Any] | None = None) -> None:
        super().__init__(config)
        self._sent_emails: list[dict[str, str]] = []

    async def initialize(self) -> None:
        """Configure email settings."""
        await super().initialize()
        print("  [EmailSender] Configured")

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
        # TODO: Store the email in _sent_emails and return True
        # Include: to, subject, body in the stored dict
        pass

    @property
    def sent_emails(self) -> list[dict[str, str]]:
        """Get list of sent emails."""
        return self._sent_emails


class NotificationService(Component):
    """Service for sending notifications to users.

    TODO: Implement this service with dependencies on:
    - UserRepository
    - TemplateEngine
    - EmailSender
    """

    name: ClassVar[str] = "notification-service"

    # TODO: Declare dependencies using Requires()
    # user_repo: UserRepository = Requires()
    # template_engine: TemplateEngine = Requires()
    # email_sender: EmailSender = Requires()

    async def initialize(self) -> None:
        """Initialize the notification service."""
        await super().initialize()
        # TODO: Log that dependencies are injected
        print("  [NotificationService] Dependencies injected")

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
    ) -> bool:
        """Send a notification to a user.

        Args:
            user_id: The user ID to send notification to
            template_name: Name of the template to use
            data: Data to render in the template

        Returns:
            True if notification was sent, False otherwise
        """
        # TODO: Implement this method:
        # 1. Look up user from user_repo
        # 2. Return False if user not found
        # 3. Add user name to data
        # 4. Render template with template_engine
        # 5. Return False if template not found
        # 6. Send email with email_sender
        # 7. Return the result
        pass


# Test your implementation
async def main() -> None:
    """Test the notification service."""
    from component_system import Registry

    print("Testing NotificationService with Dependencies...")
    print("=" * 50)

    registry = Registry()

    # Register components (in any order - registry handles dependencies)
    print("\n1. Registering components...")
    registry.register(NotificationService)
    registry.register(UserRepository)
    registry.register(TemplateEngine)
    registry.register(EmailSender)

    # Start all
    print("\n2. Starting all components...")
    await registry.start_all()

    # Test notifications
    print("\n3. Sending notifications...")
    service = registry.get(NotificationService)

    # Send to existing user
    result1 = await service.send_notification(
        "u1", "welcome", {}
    )
    print(f"   Notification to u1: {'Sent' if result1 else 'Failed'}")

    # Send to another user with data
    result2 = await service.send_notification(
        "u2", "notification", {"message": "Your order has shipped!"}
    )
    print(f"   Notification to u2: {'Sent' if result2 else 'Failed'}")

    # Send to non-existent user
    result3 = await service.send_notification(
        "u999", "welcome", {}
    )
    print(f"   Notification to u999: {'Sent' if result3 else 'Failed'}")

    # Check sent emails
    print("\n4. Checking sent emails...")
    email_sender = registry.get(EmailSender)
    for email in email_sender.sent_emails:
        print(f"   To: {email['to']}, Subject: {email['subject']}")

    # Stop all
    print("\n5. Stopping all components...")
    await registry.stop_all()

    print("\n" + "=" * 50)
    print("Test complete!")


if __name__ == "__main__":
    asyncio.run(main())
