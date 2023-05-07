"""An AWS Python Pulumi program"""

import pulumi

from api_gateway import create_api_gateway

api_id, invoke_url = create_api_gateway()

pulumi.export("REST API id", api_id)
pulumi.export("Invoke URL", invoke_url)
