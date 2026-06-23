from src.application.ports.out_.storage_port import StoragePort
from src.infrastructure.config.settings import settings


class S3Adapter(StoragePort):
    async def get_url(self, s3_key: str) -> str:
        if settings.environment == "development":
            return f"https://mock-s3.local/{s3_key}"
        import boto3

        client = boto3.client("s3", region_name=settings.aws_region)
        return client.generate_presigned_url(
            "get_object",
            Params={"Bucket": settings.aws_s3_bucket, "Key": s3_key},
            ExpiresIn=3600,
        )

    async def upload(self, s3_key: str, content: bytes, content_type: str) -> str:
        if settings.environment == "development":
            return s3_key
        import boto3

        boto3.client("s3", region_name=settings.aws_region).put_object(
            Bucket=settings.aws_s3_bucket,
            Key=s3_key,
            Body=content,
            ContentType=content_type,
        )
        return s3_key
