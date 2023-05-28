import pulumi
import pulumi_aws as aws
import pulumi_synced_folder as synced_folder
from typing import List
from app_config import config


project_name = config.require("projectName")
frontend_src_path = config.require("frontendSRCPath")
index_document = config.get("indexDocument") or "index.html"
error_document = config.get("errorDocument") or "error.html"


def _create_s3_bucket() -> aws.s3.Bucket:

    # Create an S3 bucket and configure it as a website.
    bucket = aws.s3.Bucket(
        f"{project_name}FrontendBucket",
        website=aws.s3.BucketWebsiteArgs(
            index_document=index_document,
            error_document=error_document,
        ),
    )

    # Set ownership controls for the new bucket
    ownership_controls = aws.s3.BucketOwnershipControls(
        f"{project_name}BucketOwnershipControls",
        bucket=bucket.bucket,
        rule=aws.s3.BucketOwnershipControlsRuleArgs(
            object_ownership="ObjectWriter",
        )
    )

    # Configure public ACL block on the new bucket
    public_access_block = aws.s3.BucketPublicAccessBlock(
        f"{project_name}PublicAccessBlock",
        bucket=bucket.bucket,
        block_public_acls=False,
    )

    # Use a synced folder to manage the files of the website.
    bucket_folder = synced_folder.S3BucketFolder(
        f"{project_name}BucketFolder",
        acl="public-read",
        bucket_name=bucket.bucket,
        path=frontend_src_path,
        opts=pulumi.ResourceOptions(depends_on=[
            ownership_controls,
            public_access_block
        ])
    )

    return bucket


def _create_cf_cdn(bucket: aws.s3.Bucket, allowed_methods: List[str]) -> aws.cloudfront.Distribution:

    # Create a CloudFront CDN to distribute and cache the website.
    cdn = aws.cloudfront.Distribution(
        f"{project_name}CFDistribution",
        enabled=True,
        origins=[
            aws.cloudfront.DistributionOriginArgs(
                origin_id=bucket.arn,
                domain_name=bucket.website_endpoint,
                custom_origin_config=aws.cloudfront.DistributionOriginCustomOriginConfigArgs(
                    origin_protocol_policy="http-only",
                    http_port=80,
                    https_port=443,
                    origin_ssl_protocols=["TLSv1.2"],
                ),
            )
        ],
        default_cache_behavior=aws.cloudfront.DistributionDefaultCacheBehaviorArgs(
            target_origin_id=bucket.arn,
            viewer_protocol_policy="redirect-to-https",
            allowed_methods=allowed_methods,
            cached_methods=[
                "GET",
                "HEAD",
                "OPTIONS",
            ],
            default_ttl=600,
            max_ttl=600,
            min_ttl=600,
            forwarded_values=aws.cloudfront.DistributionDefaultCacheBehaviorForwardedValuesArgs(
                query_string=True,
                cookies=aws.cloudfront.DistributionDefaultCacheBehaviorForwardedValuesCookiesArgs(
                    forward="all",
                ),
            ),
        ),
        price_class="PriceClass_100",
        custom_error_responses=[
            aws.cloudfront.DistributionCustomErrorResponseArgs(
                error_code=404,
                response_code=404,
                response_page_path=f"/{error_document}",
            )
        ],
        restrictions=aws.cloudfront.DistributionRestrictionsArgs(
            geo_restriction=aws.cloudfront.DistributionRestrictionsGeoRestrictionArgs(
                restriction_type="none",
            ),
        ),
        viewer_certificate=aws.cloudfront.DistributionViewerCertificateArgs(
            cloudfront_default_certificate=True,
        ),
        opts=pulumi.ResourceOptions(depends_on=[bucket]),
    )
    return cdn


def upload_frontend() -> aws.s3.Bucket:
    allowed_methods = ["GET", "HEAD", "POST", "DELETE", "PUT", "PATCH", "OPTIONS"]
    s3_bucket = _create_s3_bucket()
    cdn = _create_cf_cdn(bucket=s3_bucket, allowed_methods=allowed_methods)
    return cdn, s3_bucket
