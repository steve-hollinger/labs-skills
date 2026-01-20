"""Exercise 3: Multi-Tenant SaaS Schema Design

Design a DynamoDB schema for a multi-tenant SaaS application
where data isolation between tenants is critical.

Scenario: Project Management SaaS
- Multiple organizations (tenants)
- Each org has users, projects, and tasks
- Strong isolation: tenants must never see each other's data
- Each tenant can have different subscription tiers

Access Patterns:
1. Get all users in an organization
2. Get all projects for an organization
3. Get all tasks in a project
4. Get tasks assigned to a user (across projects)
5. Get overdue tasks for an organization
6. Get organization subscription/billing info

Security Considerations:
- Every query should be scoped to a tenant
- Partition key should include tenant ID for isolation
- Consider using tenant ID prefix in ALL queries

Instructions:
1. Design key schema with tenant isolation
2. Implement entity creation functions
3. Create query functions that enforce tenant scope
4. Think about cross-tenant reporting (admin use case)

Hints:
- Prefix all PKs with tenant: TENANT#{tenant_id}#ENTITY#{id}
- GSIs might need tenant prefix too for isolation
- Think about IAM conditions on PK prefix (beyond this exercise)
"""

from datetime import datetime, timedelta
from typing import Any

import boto3
from moto import mock_aws


# Subscription tiers
TIER_FREE = "free"
TIER_PRO = "pro"
TIER_ENTERPRISE = "enterprise"


def create_multi_tenant_table() -> dict[str, Any]:
    """Create the multi-tenant SaaS table.

    TODO: Design schema with tenant isolation.

    Key considerations:
    - Every entity should be queryable within tenant scope
    - GSI1: Tasks by assignee within tenant
    - GSI2: Overdue tasks within tenant
    - Consider a GSI for admin cross-tenant queries (optional)

    Returns:
        Table creation parameters
    """
    return {
        "TableName": "ProjectManagementSaaS",
        "KeySchema": [
            {"AttributeName": "PK", "KeyType": "HASH"},
            {"AttributeName": "SK", "KeyType": "RANGE"},
        ],
        "AttributeDefinitions": [
            {"AttributeName": "PK", "AttributeType": "S"},
            {"AttributeName": "SK", "AttributeType": "S"},
            # TODO: Add GSI attributes for tenant-scoped queries
        ],
        "GlobalSecondaryIndexes": [
            # TODO: Add GSIs with tenant isolation
        ],
        "BillingMode": "PAY_PER_REQUEST",
    }


def create_organization(
    org_id: str,
    name: str,
    tier: str = TIER_FREE,
    created_at: str | None = None,
) -> dict[str, Any]:
    """Create an organization (tenant).

    TODO: Implement organization item.

    The org item stores subscription and billing info.

    Args:
        org_id: Unique organization ID
        name: Organization name
        tier: Subscription tier
        created_at: Creation timestamp

    Returns:
        Organization item
    """
    if created_at is None:
        created_at = datetime.utcnow().isoformat() + "Z"

    # TODO: Implement
    # Consider: PK = TENANT#{org_id}, SK = ORG#{org_id}
    return {}


def create_user(
    org_id: str,
    user_id: str,
    name: str,
    email: str,
    role: str = "member",
) -> dict[str, Any]:
    """Create a user within an organization.

    TODO: Implement user item with tenant scope.

    Args:
        org_id: Organization (tenant) ID
        user_id: User ID (unique within org)
        name: User's name
        email: User's email
        role: User's role (admin, member)

    Returns:
        User item
    """
    # TODO: Implement
    # Ensure PK includes tenant ID for isolation
    return {}


def create_project(
    org_id: str,
    project_id: str,
    name: str,
    description: str = "",
    owner_id: str = "",
) -> dict[str, Any]:
    """Create a project within an organization.

    TODO: Implement project item with tenant scope.

    Args:
        org_id: Organization ID
        project_id: Project ID
        name: Project name
        description: Project description
        owner_id: Project owner's user ID

    Returns:
        Project item
    """
    # TODO: Implement
    return {}


def create_task(
    org_id: str,
    project_id: str,
    task_id: str,
    title: str,
    assignee_id: str | None = None,
    due_date: str | None = None,
    status: str = "todo",
    priority: str = "medium",
) -> dict[str, Any]:
    """Create a task within a project.

    TODO: Implement task item with GSI attributes.

    GSI considerations:
    - Tasks by assignee: GSI1PK = TENANT#{org_id}#ASSIGNEE#{assignee_id}
    - Overdue tasks: GSI2PK = TENANT#{org_id}#OVERDUE (sparse, only if overdue)

    Args:
        org_id: Organization ID
        project_id: Project ID
        task_id: Task ID
        title: Task title
        assignee_id: Assigned user ID (optional)
        due_date: Due date in ISO format (optional)
        status: Task status (todo, in_progress, done)
        priority: Task priority (low, medium, high)

    Returns:
        Task item
    """
    # TODO: Implement
    # Remember:
    # - Store under project for "get tasks in project"
    # - GSI1 for "tasks assigned to user"
    # - GSI2 sparse index for "overdue tasks"
    return {}


def get_org_users(table: Any, org_id: str) -> list[dict[str, Any]]:
    """Get all users in an organization.

    TODO: Implement query scoped to tenant.

    Args:
        table: DynamoDB table
        org_id: Organization ID

    Returns:
        List of users
    """
    # TODO: Implement
    return []


def get_org_projects(table: Any, org_id: str) -> list[dict[str, Any]]:
    """Get all projects in an organization.

    TODO: Implement query scoped to tenant.

    Args:
        table: DynamoDB table
        org_id: Organization ID

    Returns:
        List of projects
    """
    # TODO: Implement
    return []


def get_project_tasks(
    table: Any,
    org_id: str,
    project_id: str,
) -> list[dict[str, Any]]:
    """Get all tasks in a project.

    TODO: Implement query scoped to tenant and project.

    Args:
        table: DynamoDB table
        org_id: Organization ID
        project_id: Project ID

    Returns:
        List of tasks
    """
    # TODO: Implement
    return []


def get_user_tasks(
    table: Any,
    org_id: str,
    user_id: str,
) -> list[dict[str, Any]]:
    """Get all tasks assigned to a user across projects.

    TODO: Implement GSI query scoped to tenant.

    Args:
        table: DynamoDB table
        org_id: Organization ID
        user_id: User ID

    Returns:
        List of assigned tasks
    """
    # TODO: Implement using GSI1
    return []


def get_overdue_tasks(table: Any, org_id: str) -> list[dict[str, Any]]:
    """Get overdue tasks for an organization.

    TODO: Implement GSI query for overdue tasks.

    Args:
        table: DynamoDB table
        org_id: Organization ID

    Returns:
        List of overdue tasks
    """
    # TODO: Implement using GSI2 sparse index
    return []


def mark_task_overdue(
    table: Any,
    task_pk: str,
    task_sk: str,
    org_id: str,
) -> None:
    """Mark a task as overdue (add to sparse index).

    When a task becomes overdue, add GSI2 attributes so it
    appears in the overdue tasks query.

    TODO: Implement update to add GSI2 attributes.

    Args:
        table: DynamoDB table
        task_pk: Task partition key
        task_sk: Task sort key
        org_id: Organization ID
    """
    # TODO: Implement
    pass


@mock_aws
def exercise() -> None:
    """Test your multi-tenant schema."""
    print("Exercise 3: Multi-Tenant SaaS Schema")
    print("=" * 50)

    # Create resources
    dynamodb = boto3.resource("dynamodb", region_name="us-east-1")
    client = boto3.client("dynamodb", region_name="us-east-1")

    # Create table
    schema = create_multi_tenant_table()
    client.create_table(**schema)
    table = dynamodb.Table("ProjectManagementSaaS")

    # TODO: Test your implementation with multiple tenants
    # 1. Create two organizations (tenants)
    # 2. Create users in each org
    # 3. Create projects and tasks
    # 4. Verify tenant isolation - org A can't see org B's data
    # 5. Test user task assignment query
    # 6. Test overdue task query

    print("\nImplement the TODO sections and verify:")
    print("1. Users are scoped to their organization")
    print("2. Projects are scoped to their organization")
    print("3. Tasks within projects are accessible")
    print("4. User task assignment query works across projects")
    print("5. Overdue tasks query returns only overdue items")
    print("6. *** CRITICAL: Org A cannot query Org B's data ***")

    print("\nBonus challenges:")
    print("- How would you implement org-wide search?")
    print("- How would you handle org migration/rename?")
    print("- What IAM policies would enforce tenant isolation?")


if __name__ == "__main__":
    exercise()
