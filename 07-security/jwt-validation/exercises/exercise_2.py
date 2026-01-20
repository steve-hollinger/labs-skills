"""Exercise 2: Custom Claims Validator with RBAC.

Create a role-based access control (RBAC) system that:
1. Validates JWT claims against custom rules
2. Supports role hierarchies (admin > editor > user)
3. Implements permission-based access control
4. Provides detailed validation error messages

Expected usage:
    rbac = RBACValidator()
    rbac.define_role_hierarchy({"admin": ["editor", "user"], "editor": ["user"]})
    rbac.define_permission("posts:write", required_roles=["editor"])

    result = rbac.validate(token_payload, required_permission="posts:write")
    if result.authorized:
        # Allow access
    else:
        print(result.denial_reason)

Hints:
- Use sets for efficient role checking
- Implement role inheritance with recursion or iteration
- Consider caching resolved permissions
"""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import Any


@dataclass
class ValidationResult:
    """Result of RBAC validation.

    Attributes:
        authorized: Whether access is authorized
        denial_reason: Reason for denial (if any)
        matched_roles: Roles that matched the requirement
        missing_roles: Roles that were required but missing
    """

    authorized: bool
    denial_reason: str | None = None
    matched_roles: list[str] = field(default_factory=list)
    missing_roles: list[str] = field(default_factory=list)


@dataclass
class Permission:
    """A permission definition.

    Attributes:
        name: Permission name (e.g., "posts:write")
        required_roles: Roles that have this permission
        require_all: If True, user needs ALL roles; if False, ANY role
    """

    name: str
    required_roles: list[str] = field(default_factory=list)
    require_all: bool = False


class RBACValidator:
    """Role-Based Access Control validator for JWT claims.

    TODO: Implement:
    - define_role_hierarchy(hierarchy: dict[str, list[str]])
    - define_permission(name: str, required_roles: list[str], require_all: bool)
    - get_effective_roles(roles: list[str]) -> set[str]
    - validate(payload: dict, required_permission: str) -> ValidationResult
    - validate_roles(payload: dict, required_roles: list[str], require_all: bool) -> ValidationResult
    """

    def __init__(self, roles_claim: str = "roles"):
        """Initialize the validator.

        Args:
            roles_claim: Name of the claim containing user roles
        """
        self.roles_claim = roles_claim
        # TODO: Initialize storage for role hierarchy and permissions
        pass

    def define_role_hierarchy(self, hierarchy: dict[str, list[str]]) -> None:
        """Define role inheritance hierarchy.

        Args:
            hierarchy: Dict mapping roles to their inherited roles
                       e.g., {"admin": ["editor", "user"], "editor": ["user"]}

        Example:
            With hierarchy {"admin": ["editor"], "editor": ["user"]}:
            - admin has: admin, editor, user
            - editor has: editor, user
            - user has: user
        """
        # TODO: Store hierarchy for later resolution
        raise NotImplementedError("Implement define_role_hierarchy")

    def define_permission(
        self,
        name: str,
        required_roles: list[str],
        require_all: bool = False,
    ) -> None:
        """Define a permission.

        Args:
            name: Permission name (e.g., "posts:write")
            required_roles: Roles that grant this permission
            require_all: If True, user needs all roles; otherwise any
        """
        # TODO: Store permission definition
        raise NotImplementedError("Implement define_permission")

    def get_effective_roles(self, roles: list[str]) -> set[str]:
        """Get all effective roles including inherited ones.

        Args:
            roles: List of directly assigned roles

        Returns:
            Set of all effective roles

        Example:
            If user has ["admin"] and admin inherits editor, user:
            Returns {"admin", "editor", "user"}
        """
        # TODO: Resolve role hierarchy
        raise NotImplementedError("Implement get_effective_roles")

    def validate(
        self,
        payload: dict[str, Any],
        required_permission: str,
    ) -> ValidationResult:
        """Validate if payload has required permission.

        Args:
            payload: JWT payload with roles claim
            required_permission: Permission name to check

        Returns:
            ValidationResult
        """
        # TODO: Implement permission validation
        raise NotImplementedError("Implement validate")

    def validate_roles(
        self,
        payload: dict[str, Any],
        required_roles: list[str],
        require_all: bool = False,
    ) -> ValidationResult:
        """Validate if payload has required roles.

        Args:
            payload: JWT payload with roles claim
            required_roles: List of required roles
            require_all: If True, all roles required; otherwise any

        Returns:
            ValidationResult
        """
        # TODO: Implement role validation
        raise NotImplementedError("Implement validate_roles")

    def has_permission(
        self,
        payload: dict[str, Any],
        permission: str,
    ) -> bool:
        """Quick check if payload has permission.

        Args:
            payload: JWT payload
            permission: Permission to check

        Returns:
            True if authorized
        """
        # TODO: Implement quick permission check
        raise NotImplementedError("Implement has_permission")


def main() -> None:
    """Test your implementation."""
    print("Exercise 2: RBAC Validator")
    print("See the solution in solutions/solution_2.py")

    # Uncomment to test your implementation:
    #
    # rbac = RBACValidator()
    #
    # # Define role hierarchy
    # rbac.define_role_hierarchy({
    #     "admin": ["editor", "user"],
    #     "editor": ["user"],
    # })
    #
    # # Define permissions
    # rbac.define_permission("posts:read", required_roles=["user"])
    # rbac.define_permission("posts:write", required_roles=["editor"])
    # rbac.define_permission("posts:delete", required_roles=["admin"])
    # rbac.define_permission("system:admin", required_roles=["admin"])
    #
    # # Test payloads
    # admin_payload = {"sub": "admin1", "roles": ["admin"]}
    # editor_payload = {"sub": "editor1", "roles": ["editor"]}
    # user_payload = {"sub": "user1", "roles": ["user"]}
    #
    # # Test admin
    # print("\nAdmin tests:")
    # for perm in ["posts:read", "posts:write", "posts:delete", "system:admin"]:
    #     result = rbac.validate(admin_payload, perm)
    #     print(f"  {perm}: {result.authorized}")
    #
    # # Test editor
    # print("\nEditor tests:")
    # for perm in ["posts:read", "posts:write", "posts:delete"]:
    #     result = rbac.validate(editor_payload, perm)
    #     status = "Authorized" if result.authorized else f"Denied: {result.denial_reason}"
    #     print(f"  {perm}: {status}")
    #
    # # Test user
    # print("\nUser tests:")
    # for perm in ["posts:read", "posts:write"]:
    #     result = rbac.validate(user_payload, perm)
    #     status = "Authorized" if result.authorized else f"Denied: {result.denial_reason}"
    #     print(f"  {perm}: {status}")


if __name__ == "__main__":
    main()
