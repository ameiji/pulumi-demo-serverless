import json
import mimetypes
import os
from pulumi import FileAsset, Output, ResourceOptions
from pulumi_aws import s3


FRONTEND_SRC_PATH = "./frontend-src"


def _upload_dir_to_s3(content_dir: str, bucket: s3.Bucket):
    for root, _, files in os.walk(content_dir):
        for file in files:
            file_path = os.path.join(root, file)
            relative_path = os.path.relpath(file_path, content_dir)

            bucket_object = s3.BucketObject(
                relative_path.replace('\\', '/'),
                # Replace backslashes with forward slashes for Windows compatibility
                bucket=bucket.id,
                source=FileAsset(file_path),
                acl='private',
                opts=ResourceOptions(parent=bucket),
            )


def _public_read_policy_for_bucket(bucket_id: Output[str]) -> Output:
    return Output.json_dumps(
        {
            "Version": "2012-10-17",
            "Statement": [
                {
                    "Effect": "Allow",
                    "Principal": "*",
                    "Action": ["s3:GetObject"],
                    "Resource": [
                        Output.format("arn:aws:s3:::{0}/*", bucket_id),
                    ],
                    "Condition": {
                        "IpAddress": {
                            "aws:SourceIp": [
                                "93.86.137.18/32",
                            ]
                        }
                    }
                }
            ],
        }
    )


def _create_s3_bucket(bucket_name: str) -> s3.Bucket:
    web_bucket = s3.Bucket(
        bucket_name,
        website=s3.BucketWebsiteArgs(index_document="index.html"),
    )
    bucket_policy = s3.BucketPolicy(
        f"{bucket_name}Policy",
        bucket=web_bucket.id,
        policy=_public_read_policy_for_bucket(web_bucket.id),
        opts=ResourceOptions(depends_on=[web_bucket], parent=web_bucket),
    )
    return web_bucket


def upload_frontend() -> s3.Bucket:
    bucket_name = "TodoAPIFrontendBucket"
    web_bucket = _create_s3_bucket(bucket_name)
    _upload_dir_to_s3(content_dir=FRONTEND_SRC_PATH, bucket=web_bucket)
    return web_bucket
