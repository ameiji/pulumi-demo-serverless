"""An AWS Python Pulumi program"""
import pulumi

from api_gateway import create_api_gateway
api_id, stage_name, invoke_url = create_api_gateway(redirect_url="https://example.com", lambda_policies=[])

pulumi.export("rest_api_id", api_id)
pulumi.export("stage_name", stage_name)
pulumi.export("backend_invoke_url", invoke_url)
