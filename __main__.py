"""An AWS Python Pulumi program"""

import pulumi

from api_gateway import create_api_gateway
from s3 import upload_frontend

frontend_s3_bucket = upload_frontend()
frontend_url = pulumi.Output.format("http://{0}", frontend_s3_bucket.website_endpoint)
api_id, stage_name, invoke_url = create_api_gateway(redirect_url=frontend_url)

pulumi.export("rest_api_id", api_id)
pulumi.export("stage_name", stage_name)
pulumi.export("backend_invoke_url", invoke_url)
pulumi.export("s3_bucket_name", frontend_s3_bucket.id)
pulumi.export("website_url", frontend_url)
