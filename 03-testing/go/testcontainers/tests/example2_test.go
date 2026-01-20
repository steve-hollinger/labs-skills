//go:build integration

package tests

import (
	"context"
	"fmt"
	"testing"
	"time"

	"github.com/aws/aws-sdk-go-v2/aws"
	"github.com/aws/aws-sdk-go-v2/config"
	"github.com/aws/aws-sdk-go-v2/credentials"
	"github.com/aws/aws-sdk-go-v2/service/dynamodb"
	"github.com/aws/aws-sdk-go-v2/service/dynamodb/types"
	"github.com/stretchr/testify/assert"
	"github.com/stretchr/testify/require"
	"github.com/testcontainers/testcontainers-go"
	"github.com/testcontainers/testcontainers-go/wait"
)

// ============================================================================
// Example 2: DynamoDB Local Container
// ============================================================================

// setupDynamoDBLocal starts a DynamoDB Local container and returns a client
func setupDynamoDBLocal(ctx context.Context) (testcontainers.Container, *dynamodb.Client, error) {
	container, err := testcontainers.GenericContainer(ctx, testcontainers.GenericContainerRequest{
		ContainerRequest: testcontainers.ContainerRequest{
			Image:        "amazon/dynamodb-local:latest",
			ExposedPorts: []string{"8000/tcp"},
			WaitingFor:   wait.ForListeningPort("8000/tcp").WithStartupTimeout(60 * time.Second),
		},
		Started: true,
	})
	if err != nil {
		return nil, nil, err
	}

	host, _ := container.Host(ctx)
	port, _ := container.MappedPort(ctx, "8000")
	endpoint := fmt.Sprintf("http://%s:%s", host, port.Port())

	cfg, err := config.LoadDefaultConfig(ctx,
		config.WithRegion("us-east-1"),
		config.WithCredentialsProvider(credentials.NewStaticCredentialsProvider("dummy", "dummy", "")),
	)
	if err != nil {
		container.Terminate(ctx)
		return nil, nil, err
	}

	client := dynamodb.NewFromConfig(cfg, func(o *dynamodb.Options) {
		o.BaseEndpoint = aws.String(endpoint)
	})

	return container, client, nil
}

// createUsersTable creates a users table for testing
func createUsersTable(ctx context.Context, client *dynamodb.Client) error {
	_, err := client.CreateTable(ctx, &dynamodb.CreateTableInput{
		TableName: aws.String("users"),
		KeySchema: []types.KeySchemaElement{
			{
				AttributeName: aws.String("pk"),
				KeyType:       types.KeyTypeHash,
			},
			{
				AttributeName: aws.String("sk"),
				KeyType:       types.KeyTypeRange,
			},
		},
		AttributeDefinitions: []types.AttributeDefinition{
			{
				AttributeName: aws.String("pk"),
				AttributeType: types.ScalarAttributeTypeS,
			},
			{
				AttributeName: aws.String("sk"),
				AttributeType: types.ScalarAttributeTypeS,
			},
		},
		BillingMode: types.BillingModePayPerRequest,
	})
	return err
}

func TestExample2_DynamoDBBasic(t *testing.T) {
	ctx := context.Background()

	container, client, err := setupDynamoDBLocal(ctx)
	require.NoError(t, err)
	defer container.Terminate(ctx)

	// List tables (should be empty initially)
	result, err := client.ListTables(ctx, &dynamodb.ListTablesInput{})
	require.NoError(t, err)
	assert.Empty(t, result.TableNames)

	t.Log("DynamoDB Local container started successfully!")
}

func TestExample2_CreateTable(t *testing.T) {
	ctx := context.Background()

	container, client, err := setupDynamoDBLocal(ctx)
	require.NoError(t, err)
	defer container.Terminate(ctx)

	// Create users table
	err = createUsersTable(ctx, client)
	require.NoError(t, err)

	// Verify table exists
	result, err := client.ListTables(ctx, &dynamodb.ListTablesInput{})
	require.NoError(t, err)
	assert.Contains(t, result.TableNames, "users")
}

func TestExample2_PutAndGetItem(t *testing.T) {
	ctx := context.Background()

	container, client, err := setupDynamoDBLocal(ctx)
	require.NoError(t, err)
	defer container.Terminate(ctx)

	// Create table
	err = createUsersTable(ctx, client)
	require.NoError(t, err)

	// Put item
	_, err = client.PutItem(ctx, &dynamodb.PutItemInput{
		TableName: aws.String("users"),
		Item: map[string]types.AttributeValue{
			"pk":    &types.AttributeValueMemberS{Value: "USER#1"},
			"sk":    &types.AttributeValueMemberS{Value: "PROFILE"},
			"name":  &types.AttributeValueMemberS{Value: "Alice"},
			"email": &types.AttributeValueMemberS{Value: "alice@example.com"},
		},
	})
	require.NoError(t, err)

	// Get item
	result, err := client.GetItem(ctx, &dynamodb.GetItemInput{
		TableName: aws.String("users"),
		Key: map[string]types.AttributeValue{
			"pk": &types.AttributeValueMemberS{Value: "USER#1"},
			"sk": &types.AttributeValueMemberS{Value: "PROFILE"},
		},
	})
	require.NoError(t, err)

	assert.NotNil(t, result.Item)
	assert.Equal(t, "Alice", result.Item["name"].(*types.AttributeValueMemberS).Value)
	assert.Equal(t, "alice@example.com", result.Item["email"].(*types.AttributeValueMemberS).Value)
}

func TestExample2_QueryItems(t *testing.T) {
	ctx := context.Background()

	container, client, err := setupDynamoDBLocal(ctx)
	require.NoError(t, err)
	defer container.Terminate(ctx)

	// Create table
	err = createUsersTable(ctx, client)
	require.NoError(t, err)

	// Put multiple items for same user
	userID := "USER#1"
	items := []map[string]types.AttributeValue{
		{
			"pk":    &types.AttributeValueMemberS{Value: userID},
			"sk":    &types.AttributeValueMemberS{Value: "PROFILE"},
			"name":  &types.AttributeValueMemberS{Value: "Alice"},
			"email": &types.AttributeValueMemberS{Value: "alice@example.com"},
		},
		{
			"pk":      &types.AttributeValueMemberS{Value: userID},
			"sk":      &types.AttributeValueMemberS{Value: "ORDER#001"},
			"total":   &types.AttributeValueMemberN{Value: "99.99"},
			"status":  &types.AttributeValueMemberS{Value: "shipped"},
		},
		{
			"pk":      &types.AttributeValueMemberS{Value: userID},
			"sk":      &types.AttributeValueMemberS{Value: "ORDER#002"},
			"total":   &types.AttributeValueMemberN{Value: "149.99"},
			"status":  &types.AttributeValueMemberS{Value: "pending"},
		},
	}

	for _, item := range items {
		_, err := client.PutItem(ctx, &dynamodb.PutItemInput{
			TableName: aws.String("users"),
			Item:      item,
		})
		require.NoError(t, err)
	}

	// Query all items for user
	result, err := client.Query(ctx, &dynamodb.QueryInput{
		TableName:              aws.String("users"),
		KeyConditionExpression: aws.String("pk = :pk"),
		ExpressionAttributeValues: map[string]types.AttributeValue{
			":pk": &types.AttributeValueMemberS{Value: userID},
		},
	})
	require.NoError(t, err)

	assert.Equal(t, int32(3), result.Count)

	// Query only orders (sk begins with "ORDER#")
	result, err = client.Query(ctx, &dynamodb.QueryInput{
		TableName:              aws.String("users"),
		KeyConditionExpression: aws.String("pk = :pk AND begins_with(sk, :sk_prefix)"),
		ExpressionAttributeValues: map[string]types.AttributeValue{
			":pk":        &types.AttributeValueMemberS{Value: userID},
			":sk_prefix": &types.AttributeValueMemberS{Value: "ORDER#"},
		},
	})
	require.NoError(t, err)

	assert.Equal(t, int32(2), result.Count)
}

func TestExample2_DeleteItem(t *testing.T) {
	ctx := context.Background()

	container, client, err := setupDynamoDBLocal(ctx)
	require.NoError(t, err)
	defer container.Terminate(ctx)

	// Create table and put item
	err = createUsersTable(ctx, client)
	require.NoError(t, err)

	_, err = client.PutItem(ctx, &dynamodb.PutItemInput{
		TableName: aws.String("users"),
		Item: map[string]types.AttributeValue{
			"pk":   &types.AttributeValueMemberS{Value: "USER#1"},
			"sk":   &types.AttributeValueMemberS{Value: "PROFILE"},
			"name": &types.AttributeValueMemberS{Value: "Alice"},
		},
	})
	require.NoError(t, err)

	// Delete item
	_, err = client.DeleteItem(ctx, &dynamodb.DeleteItemInput{
		TableName: aws.String("users"),
		Key: map[string]types.AttributeValue{
			"pk": &types.AttributeValueMemberS{Value: "USER#1"},
			"sk": &types.AttributeValueMemberS{Value: "PROFILE"},
		},
	})
	require.NoError(t, err)

	// Verify deleted
	result, err := client.GetItem(ctx, &dynamodb.GetItemInput{
		TableName: aws.String("users"),
		Key: map[string]types.AttributeValue{
			"pk": &types.AttributeValueMemberS{Value: "USER#1"},
			"sk": &types.AttributeValueMemberS{Value: "PROFILE"},
		},
	})
	require.NoError(t, err)
	assert.Nil(t, result.Item)
}
