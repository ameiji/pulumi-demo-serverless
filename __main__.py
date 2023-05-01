"""An AWS Python Pulumi program"""

import pulumi

from api_gateway import create_api_gateway

api_id = create_api_gateway()

pulumi.export('rest_api id', api_id)