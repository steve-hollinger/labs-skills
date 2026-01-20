"""Solution 2: Custom Claims Validator with RBAC.

This solution demonstrates role-based access control with
role hierarchies and permission-based authorization.
"""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import Any


@dataclass
class ValidationResult:
    """Result of RBAC validation."""

    authorized: bool
    denial_reason: str | None = None
    matched_roles: list[str] = field(default_factory=list)
    missing_roles: list[str] = field(default_factory=list)


@dataclass
class Permission:
    """A permission definition."""

    name: str
    required_roles: list[str] = field(default_factory=list)
    require_all: bool = False


class RBACValidator:
    """Role-Based Access Control validator for JWT claims."""

    def __init__(self, roles_claim: str = "roles"):
        """Initialize the validator.

        Args:
            roles_claim: Name of the claim containing user roles
        """
        self.roles_claim = roles_claim
        self._hierarchy: dict[str, set[str]] = {}
        self._permissions: dict[str, Permission] = {}
        self._effective_roles_cache: dict[str, set[str]] = {}

    def define_role_hierarchy(self, hierarchy: dict[str, list[str]]) -> None:
        """Define role inheritance hierarchy.

        Args:
            hierarchy: Dict mapping roles to their inherited roles
        """
        self._hierarchy = {role: set(inherited) for role, inherited in hierarchy.items()}
        self._effective_roles_cache.clear()  # Clear cache when hierarchy changes

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
        self._permissions[name] = Permission(
            name=name,
            required_roles=required_roles,
            require_all=require_all,
        )

    def get_effective_roles(self, roles: list[str]) -> set[str]:
        """Get all effective roles including inherited ones.

        Args:
            roles: List of directly assigned roles

        Returns:
            Set of all effective roles
        """
        # Check cache
        cache_key = ",".join(sorted(roles))
        if cache_key in self._effective_roles_cache:
            return self._effective_roles_cache[cache_key]

        effective = set(roles)
        to_process = list(roles)

        while to_process:
            role = to_process.pop()
            inherited = self._hierarchy.get(role, set())
            for inherited_role in inherited:
                if inherited_role not in effective:
                    effective.add(inherited_role)
                    to_process.append(inherited_role)

        # Cache the result
        self._effective_roles_cache[cache_key] = effective
        return effective

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
        # Check if permission is defined
        permission = self._permissions.get(required_permission)
        if permission is None:
            return ValidationResult(
                authorized=False,
                denial_reason=f"Unknown permission: {required_permission}",
            )

        return self.validate_roles(
            payload,
            permission.required_roles,
            permission.require_all,
        )

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
        # Get user's roles from payload
        user_roles = payload.get(self.roles_claim, [])
        if isinstance(user_roles, str):
            user_roles = [user_roles]

        # Get effective roles (including inherited)
        effective_roles = self.get_effective_roles(user_roles)

        # Check which required roles are present
        matched = [r for r in required_roles if r in effective_roles]
        missing = [r for r in required_roles if r not in effective_roles]

        if require_all:
            # All roles required
            authorized = len(missing) == 0
            if not authorized:
                denial_reason = f"Missing required roles: {missing}"
            else:
                denial_reason = None
        else:
            # Any role sufficient
            authorized = len(matched) > 0
            if not authorized:
                denial_reason = f"None of the required roles present. Need one of: {required_roles}"
            else:
                denial_reason = None

        return ValidationResult(
            authorized=authorized,
            denial_reason=denial_reason,
            matched_roles=matched,
            missing_roles=missing,
        )

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
        return self.validate(payload, permission).authorized

    def list_permissions(self, payload: dict[str, Any]) -> list[str]:
        """List all permissions the user has.

        Args:
            payload: JWT payload

        Returns:
            List of permission names
        """
        permissions = []
        for name in self._permissions:
            if self.has_permission(payload, name):
                permissions.append(name)
        return permissions


def main() -> None:
    """Demonstrate the RBAC validator."""
    print("=" * 60)
    print("Solution 2: RBAC Validator")
    print("=" * 60)

    rbac = RBACValidator()

    # Define role hierarchy
    print("\n1. Defining role hierarchy:")
    rbac.define_role_hierarchy({
        "admin": ["editor", "moderator"],
        "editor": ["user"],
        "moderator": ["user"],
    })
    print("   admin -> editor, moderator")
    print("   editor -> user")
    print("   moderator -> user")

    # Define permissions
    print("\n2. Defining permissions:")
    permissions = [
        ("posts:read", ["user"], False),
        ("posts:write", ["editor"], False),
        ("posts:delete", ["editor", "moderator"], False),  # Either role
        ("posts:publish", ["editor", "moderator"], True),   # Both roles
        ("users:manage", ["admin"], False),
        ("system:admin", ["admin"], False),
    ]

    for name, roles, require_all in permissions:
        rbac.define_permission(name, roles, require_all)
        mode = "ALL" if require_all else "ANY"
        print(f"   {name}: {roles} ({mode})")

    # Test payloads
    test_users = [
        ("Admin", {"sub": "admin1", "roles": ["admin"]}),
        ("Editor", {"sub": "editor1", "roles": ["editor"]}),
        ("Moderator", {"sub": "mod1", "roles": ["moderator"]}),
        ("User", {"sub": "user1", "roles": ["user"]}),
        ("Editor+Mod", {"sub": "power1", "roles": ["editor", "moderator"]}),
    ]

    # Test each user
    for name, payload in test_users:
        print(f"\n3. Testing {name}:")
        print(f"   Direct roles: {payload['roles']}")

        effective = rbac.get_effective_roles(payload["roles"])
        print(f"   Effective roles: {sorted(effective)}")

        print("   Permissions:")
        for perm_name, _, _ in permissions:
            result = rbac.validate(payload, perm_name)
            status = "Yes" if result.authorized else "No"
            print(f"      {perm_name}: {status}")

        print(f"   All permissions: {rbac.list_permissions(payload)}")

    # Detailed validation result
    print("\n4. Detailed validation example:")
    editor_payload = {"sub": "editor1", "roles": ["editor"]}
    result = rbac.validate(editor_payload, "users:manage")

    print(f"   Permission: users:manage")
    print(f"   User roles: {editor_payload['roles']}")
    print(f"   Authorized: {result.authorized}")
    print(f"   Denial reason: {result.denial_reason}")
    print(f"   Matched roles: {result.matched_roles}")
    print(f"   Missing roles: {result.missing_roles}")

    # Test require_all permission
    print("\n5. Testing require_all permission (posts:publish):")
    for name, payload in test_users:
        result = rbac.validate(payload, "posts:publish")
        status = "Yes" if result.authorized else "No"
        details = f"matched: {result.matched_roles}" if result.authorized else result.denial_reason
        print(f"   {name}: {status} - {details}")

    print("\n" + "=" * 60)
    print("Solution 2 Complete!")
    print("=" * 60)


if __name__ == "__main__":
    main()
