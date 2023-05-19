"""An AWS Python Pulumi program"""

import pulumi

from api_gateway import create_api_gateway
from s3 import upload_frontend

api_id, invoke_url = create_api_gateway()
frontend_s3_bucket = upload_frontend()

pulumi.export("REST API id", api_id)
pulumi.export("Backend invoke URL", invoke_url)
pulumi.export("S3 bucket name", frontend_s3_bucket.id)
pulumi.export("Website URL", frontend_s3_bucket.website_endpoint)
