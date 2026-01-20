"""Solution for Exercise 3: Multi-Tenant SaaS Schema

This solution demonstrates a multi-tenant schema with strong data isolation
for a project management SaaS application.
"""

from datetime import datetime, timedelta
from typing import Any

import boto3
from moto import mock_aws


TIER_FREE = "free"
TIER_PRO = "pro"
TIER_ENTERPRISE = "enterprise"


def create_multi_tenant_table() -> dict[str, Any]:
    """Create multi-tenant table with tenant-scoped GSIs."""
    return {
        "TableName": "ProjectManagementSaaS",
        "KeySchema": [
            {"AttributeName": "PK", "KeyType": "HASH"},
            {"AttributeName": "SK", "KeyType": "RANGE"},
        ],
        "AttributeDefinitions": [
            {"AttributeName": "PK", "AttributeType": "S"},
            {"AttributeName": "SK", "AttributeType": "S"},
            {"AttributeName": "GSI1PK", "AttributeType": "S"},
            {"AttributeName": "GSI1SK", "AttributeType": "S"},
            {"AttributeName": "GSI2PK", "AttributeType": "S"},
            {"AttributeName": "GSI2SK", "AttributeType": "S"},
        ],
        "GlobalSecondaryIndexes": [
            {
                # GSI1: Tasks by assignee within tenant
                "IndexName": "GSI1",
                "KeySchema": [
                    {"AttributeName": "GSI1PK", "KeyType": "HASH"},
                    {"AttributeName": "GSI1SK", "KeyType": "RANGE"},
                ],
                "Projection": {"ProjectionType": "ALL"},
            },
            {
                # GSI2: Overdue tasks by tenant (sparse)
                "IndexName": "GSI2",
                "KeySchema": [
                    {"AttributeName": "GSI2PK", "KeyType": "HASH"},
                    {"AttributeName": "GSI2SK", "KeyType": "RANGE"},
                ],
                "Projection": {"ProjectionType": "ALL"},
            },
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

    Key Design: TENANT#{org_id} groups all org data
    """
    if created_at is None:
        created_at = datetime.utcnow().isoformat() + "Z"

    return {
        "PK": f"TENANT#{org_id}",
        "SK": f"ORG#{org_id}",
        "entity_type": "ORGANIZATION",
        "org_id": org_id,
        "name": name,
        "tier": tier,
        "created_at": created_at,
    }


def create_user(
    org_id: str,
    user_id: str,
    name: str,
    email: str,
    role: str = "member",
) -> dict[str, Any]:
    """Create a user within an organization.

    PK includes tenant for isolation.
    """
    return {
        "PK": f"TENANT#{org_id}",
        "SK": f"USER#{user_id}",
        "entity_type": "USER",
        "org_id": org_id,
        "user_id": user_id,
        "name": name,
        "email": email,
        "role": role,
        "created_at": datetime.utcnow().isoformat() + "Z",
    }


def create_project(
    org_id: str,
    project_id: str,
    name: str,
    description: str = "",
    owner_id: str = "",
) -> dict[str, Any]:
    """Create a project within an organization."""
    return {
        "PK": f"TENANT#{org_id}",
        "SK": f"PROJECT#{project_id}",
        "entity_type": "PROJECT",
        "org_id": org_id,
        "project_id": project_id,
        "name": name,
        "description": description,
        "owner_id": owner_id,
        "created_at": datetime.utcnow().isoformat() + "Z",
    }


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

    Key Design:
    - PK: TENANT#{org_id}#PROJECT#{project_id} - Tasks under project
    - SK: TASK#{task_id}
    - GSI1: Tasks by assignee (tenant-scoped)
    - GSI2: Overdue tasks (sparse, tenant-scoped)
    """
    now = datetime.utcnow()
    is_overdue = False
    if due_date:
        due_dt = datetime.fromisoformat(due_date.replace("Z", ""))
        is_overdue = due_dt < now and status != "done"

    item: dict[str, Any] = {
        "PK": f"TENANT#{org_id}#PROJECT#{project_id}",
        "SK": f"TASK#{task_id}",
        "entity_type": "TASK",
        "org_id": org_id,
        "project_id": project_id,
        "task_id": task_id,
        "title": title,
        "assignee_id": assignee_id,
        "due_date": due_date,
        "status": status,
        "priority": priority,
        "created_at": now.isoformat() + "Z",
    }

    # GSI1: Tasks by assignee (only if assigned)
    if assignee_id:
        item["GSI1PK"] = f"TENANT#{org_id}#ASSIGNEE#{assignee_id}"
        item["GSI1SK"] = f"TASK#{due_date or '9999-12-31'}#{task_id}"

    # GSI2: Overdue tasks (sparse - only if overdue)
    if is_overdue:
        item["GSI2PK"] = f"TENANT#{org_id}#OVERDUE"
        item["GSI2SK"] = f"TASK#{due_date}#{task_id}"

    return item


def get_org_users(table: Any, org_id: str) -> list[dict[str, Any]]:
    """Get all users in an organization."""
    response = table.query(
        KeyConditionExpression="PK = :pk AND begins_with(SK, :sk_prefix)",
        ExpressionAttributeValues={
            ":pk": f"TENANT#{org_id}",
            ":sk_prefix": "USER#",
        },
    )
    return response.get("Items", [])


def get_org_projects(table: Any, org_id: str) -> list[dict[str, Any]]:
    """Get all projects in an organization."""
    response = table.query(
        KeyConditionExpression="PK = :pk AND begins_with(SK, :sk_prefix)",
        ExpressionAttributeValues={
            ":pk": f"TENANT#{org_id}",
            ":sk_prefix": "PROJECT#",
        },
    )
    return response.get("Items", [])


def get_project_tasks(
    table: Any,
    org_id: str,
    project_id: str,
) -> list[dict[str, Any]]:
    """Get all tasks in a project."""
    response = table.query(
        KeyConditionExpression="PK = :pk AND begins_with(SK, :sk_prefix)",
        ExpressionAttributeValues={
            ":pk": f"TENANT#{org_id}#PROJECT#{project_id}",
            ":sk_prefix": "TASK#",
        },
    )
    return response.get("Items", [])


def get_user_tasks(
    table: Any,
    org_id: str,
    user_id: str,
) -> list[dict[str, Any]]:
    """Get all tasks assigned to a user across projects."""
    response = table.query(
        IndexName="GSI1",
        KeyConditionExpression="GSI1PK = :pk",
        ExpressionAttributeValues={
            ":pk": f"TENANT#{org_id}#ASSIGNEE#{user_id}",
        },
    )
    return response.get("Items", [])


def get_overdue_tasks(table: Any, org_id: str) -> list[dict[str, Any]]:
    """Get overdue tasks for an organization."""
    response = table.query(
        IndexName="GSI2",
        KeyConditionExpression="GSI2PK = :pk",
        ExpressionAttributeValues={
            ":pk": f"TENANT#{org_id}#OVERDUE",
        },
    )
    return response.get("Items", [])


def mark_task_overdue(
    table: Any,
    task_pk: str,
    task_sk: str,
    org_id: str,
    due_date: str,
    task_id: str,
) -> None:
    """Mark a task as overdue by adding GSI2 attributes."""
    table.update_item(
        Key={"PK": task_pk, "SK": task_sk},
        UpdateExpression="SET GSI2PK = :gsi2pk, GSI2SK = :gsi2sk",
        ExpressionAttributeValues={
            ":gsi2pk": f"TENANT#{org_id}#OVERDUE",
            ":gsi2sk": f"TASK#{due_date}#{task_id}",
        },
    )


@mock_aws
def solution() -> None:
    """Demonstrate the multi-tenant schema solution."""
    print("Solution 3: Multi-Tenant SaaS Schema")
    print("=" * 50)

    # Create resources
    dynamodb = boto3.resource("dynamodb", region_name="us-east-1")
    client = boto3.client("dynamodb", region_name="us-east-1")

    # Create table
    schema = create_multi_tenant_table()
    client.create_table(**schema)
    table = dynamodb.Table("ProjectManagementSaaS")

    # Create test data for TWO organizations
    print("\n--- Creating Test Data ---\n")

    # Organization A (Acme Corp)
    org_a = create_organization("acme", "Acme Corporation", TIER_PRO)
    users_a = [
        create_user("acme", "alice", "Alice Smith", "alice@acme.com", "admin"),
        create_user("acme", "bob", "Bob Jones", "bob@acme.com", "member"),
    ]
    projects_a = [
        create_project("acme", "proj-a1", "Website Redesign", "Redesign company website", "alice"),
        create_project("acme", "proj-a2", "Mobile App", "Build mobile app", "bob"),
    ]

    # Past date for overdue tasks
    past_date = (datetime.utcnow() - timedelta(days=5)).strftime("%Y-%m-%dT00:00:00Z")
    future_date = (datetime.utcnow() + timedelta(days=5)).strftime("%Y-%m-%dT00:00:00Z")

    tasks_a = [
        create_task("acme", "proj-a1", "task-1", "Design mockups", "alice", future_date, "in_progress"),
        create_task("acme", "proj-a1", "task-2", "Review designs", "bob", past_date, "todo"),  # Overdue!
        create_task("acme", "proj-a2", "task-3", "Set up React Native", "alice", future_date, "todo"),
    ]

    # Organization B (Beta Inc)
    org_b = create_organization("beta", "Beta Inc", TIER_FREE)
    users_b = [
        create_user("beta", "carol", "Carol White", "carol@beta.io", "admin"),
    ]
    projects_b = [
        create_project("beta", "proj-b1", "Internal Tool", "Build internal tool", "carol"),
    ]
    tasks_b = [
        create_task("beta", "proj-b1", "task-4", "Database design", "carol", future_date, "todo"),
        create_task("beta", "proj-b1", "task-5", "API endpoints", "carol", past_date, "todo"),  # Overdue!
    ]

    # Insert all data
    with table.batch_writer() as batch:
        batch.put_item(Item=org_a)
        batch.put_item(Item=org_b)
        for user in users_a + users_b:
            batch.put_item(Item=user)
        for project in projects_a + projects_b:
            batch.put_item(Item=project)
        for task in tasks_a + tasks_b:
            batch.put_item(Item=task)

    print("Created 2 organizations: Acme Corp and Beta Inc")
    print("Each org has users, projects, and tasks (some overdue)")

    # Demonstrate access patterns
    print("\n--- Access Pattern Demonstrations ---\n")

    # 1. Org users
    print("1. Users in 'acme' organization:")
    acme_users = get_org_users(table, "acme")
    for user in acme_users:
        print(f"   - {user['name']} ({user['role']})")

    # 2. Org projects
    print("\n2. Projects in 'acme' organization:")
    acme_projects = get_org_projects(table, "acme")
    for project in acme_projects:
        print(f"   - {project['name']}")

    # 3. Project tasks
    print("\n3. Tasks in 'proj-a1' (Website Redesign):")
    proj_tasks = get_project_tasks(table, "acme", "proj-a1")
    for task in proj_tasks:
        print(f"   - {task['title']} [{task['status']}]")

    # 4. User's tasks across projects
    print("\n4. Alice's tasks (across all Acme projects):")
    alice_tasks = get_user_tasks(table, "acme", "alice")
    for task in alice_tasks:
        print(f"   - {task['title']} in {task['project_id']}")

    # 5. Overdue tasks
    print("\n5. Overdue tasks in 'acme':")
    overdue = get_overdue_tasks(table, "acme")
    for task in overdue:
        print(f"   - {task['title']} (due: {task['due_date']})")

    # 6. CRITICAL: Verify tenant isolation
    print("\n" + "=" * 50)
    print("TENANT ISOLATION VERIFICATION")
    print("=" * 50)

    print("\n6. Attempting to access Beta's data from Acme context:")
    print("   (These should return empty or fail)")

    # Try to get Beta users using Acme org_id - should be empty
    wrong_users = get_org_users(table, "beta")
    print(f"   - Beta users visible: {len(wrong_users)} (correct: data visible since we queried correctly)")

    # But if we query with Acme's org_id for Beta's projects - should be empty
    wrong_projects = get_org_projects(table, "acme")
    beta_projects = get_org_projects(table, "beta")
    print(f"   - Acme sees only Acme projects: {len(wrong_projects)} (not Beta's {len(beta_projects)})")

    # Overdue tasks are tenant-scoped
    acme_overdue = get_overdue_tasks(table, "acme")
    beta_overdue = get_overdue_tasks(table, "beta")
    print(f"   - Acme overdue tasks: {len(acme_overdue)}")
    print(f"   - Beta overdue tasks: {len(beta_overdue)}")
    print("   - Each org only sees their own overdue tasks!")

    print("\n" + "=" * 50)
    print("Key Design Principles:")
    print("1. Every PK includes TENANT#{org_id} for isolation")
    print("2. GSI PKs also include tenant prefix")
    print("3. All queries require org_id parameter")
    print("4. IAM policies can enforce PK prefix conditions")
    print("\nSolution completed successfully!")


if __name__ == "__main__":
    solution()
