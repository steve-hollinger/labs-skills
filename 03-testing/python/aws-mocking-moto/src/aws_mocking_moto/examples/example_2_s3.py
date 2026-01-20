"""Example 2: S3 Mocking with moto

This example demonstrates how to mock S3 operations using moto,
including bucket creation, object operations, and multipart uploads.
"""

import os


def setup_aws_credentials() -> None:
    """Set up fake AWS credentials for moto."""
    os.environ["AWS_ACCESS_KEY_ID"] = "testing"
    os.environ["AWS_SECRET_ACCESS_KEY"] = "testing"
    os.environ["AWS_DEFAULT_REGION"] = "us-east-1"


def main() -> None:
    """Demonstrate S3 mocking with moto."""
    print("Example 2: S3 Mocking with moto")
    print("=" * 50)
    print()

    # Show basic operations
    print("1. Basic S3 Operations")
    print("-" * 40)
    print("""
    import boto3
    from moto import mock_aws

    @mock_aws
    def test_s3_basic():
        s3 = boto3.client("s3", region_name="us-east-1")

        # Create bucket
        s3.create_bucket(Bucket="my-bucket")

        # Upload object
        s3.put_object(
            Bucket="my-bucket",
            Key="data/file.txt",
            Body=b"Hello, World!",
            ContentType="text/plain",
        )

        # Download object
        response = s3.get_object(Bucket="my-bucket", Key="data/file.txt")
        content = response["Body"].read()
        assert content == b"Hello, World!"
    """)

    # Show listing objects
    print("2. Listing Objects")
    print("-" * 40)
    print("""
    @mock_aws
    def test_list_objects():
        s3 = boto3.client("s3", region_name="us-east-1")
        s3.create_bucket(Bucket="my-bucket")

        # Upload multiple objects
        for i in range(5):
            s3.put_object(
                Bucket="my-bucket",
                Key=f"folder/file{i}.txt",
                Body=f"Content {i}".encode(),
            )

        # List all objects
        response = s3.list_objects_v2(Bucket="my-bucket")
        assert len(response["Contents"]) == 5

        # List with prefix
        response = s3.list_objects_v2(
            Bucket="my-bucket",
            Prefix="folder/"
        )
        assert len(response["Contents"]) == 5
    """)

    # Show copy and delete
    print("3. Copy and Delete Operations")
    print("-" * 40)
    print("""
    @mock_aws
    def test_copy_delete():
        s3 = boto3.client("s3", region_name="us-east-1")
        s3.create_bucket(Bucket="source-bucket")
        s3.create_bucket(Bucket="dest-bucket")

        # Upload original
        s3.put_object(
            Bucket="source-bucket",
            Key="original.txt",
            Body=b"Original content",
        )

        # Copy to new location
        s3.copy_object(
            Bucket="dest-bucket",
            Key="copy.txt",
            CopySource={"Bucket": "source-bucket", "Key": "original.txt"},
        )

        # Delete original
        s3.delete_object(Bucket="source-bucket", Key="original.txt")

        # Verify copy exists
        response = s3.get_object(Bucket="dest-bucket", Key="copy.txt")
        assert response["Body"].read() == b"Original content"
    """)

    # Show presigned URLs
    print("4. Presigned URLs")
    print("-" * 40)
    print("""
    @mock_aws
    def test_presigned_url():
        s3 = boto3.client("s3", region_name="us-east-1")
        s3.create_bucket(Bucket="my-bucket")
        s3.put_object(Bucket="my-bucket", Key="file.txt", Body=b"content")

        # Generate presigned URL for download
        url = s3.generate_presigned_url(
            "get_object",
            Params={"Bucket": "my-bucket", "Key": "file.txt"},
            ExpiresIn=3600,
        )

        assert "my-bucket" in url
        assert "file.txt" in url

        # Generate presigned URL for upload
        upload_url = s3.generate_presigned_url(
            "put_object",
            Params={"Bucket": "my-bucket", "Key": "upload.txt"},
            ExpiresIn=3600,
        )

        assert "upload.txt" in upload_url
    """)

    # Show bucket resource
    print("5. Using boto3 Resource API")
    print("-" * 40)
    print("""
    @mock_aws
    def test_s3_resource():
        s3 = boto3.resource("s3", region_name="us-east-1")

        # Create bucket
        bucket = s3.create_bucket(Bucket="my-bucket")

        # Upload using bucket object
        bucket.put_object(Key="file.txt", Body=b"content")

        # Download using object
        obj = bucket.Object("file.txt")
        content = obj.get()["Body"].read()
        assert content == b"content"

        # List objects in bucket
        objects = list(bucket.objects.all())
        assert len(objects) == 1
    """)

    # Run actual demo
    print("6. Live Demo")
    print("-" * 40)

    setup_aws_credentials()

    import boto3
    from moto import mock_aws

    with mock_aws():
        s3 = boto3.client("s3", region_name="us-east-1")

        # Create bucket
        s3.create_bucket(Bucket="demo-bucket")
        print("Created bucket: demo-bucket")

        # Upload files
        files = {
            "config/app.json": b'{"version": "1.0", "debug": false}',
            "data/users.csv": b"id,name,email\n1,Alice,alice@example.com\n2,Bob,bob@example.com",
            "images/logo.png": b"fake-png-data",
        }

        for key, body in files.items():
            s3.put_object(Bucket="demo-bucket", Key=key, Body=body)
            print(f"Uploaded: {key} ({len(body)} bytes)")

        # List all objects
        response = s3.list_objects_v2(Bucket="demo-bucket")
        print(f"\nTotal objects in bucket: {len(response['Contents'])}")
        for obj in response["Contents"]:
            print(f"  - {obj['Key']} ({obj['Size']} bytes)")

        # Download and display config
        response = s3.get_object(Bucket="demo-bucket", Key="config/app.json")
        config_content = response["Body"].read().decode()
        print(f"\nConfig content: {config_content}")

        # Delete an object
        s3.delete_object(Bucket="demo-bucket", Key="images/logo.png")
        print("\nDeleted: images/logo.png")

        # Verify deletion
        response = s3.list_objects_v2(Bucket="demo-bucket")
        print(f"Remaining objects: {len(response['Contents'])}")

    print()
    print("Run the tests with:")
    print("  pytest tests/test_s3.py -v")
    print()
    print("Example completed!")


if __name__ == "__main__":
    main()
