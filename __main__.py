"""An AWS Python Pulumi program"""

import pulumi

from api_gateway import create_api_gateway
from lambda_functions import create_lambda_function
from iam import create_lambda_exec_role

# api_id = create_api_gateway()

role_arn = create_lambda_exec_role("lambda-exec-role", assume_policy_filename="lambdas/execution_role.json")

func = create_lambda_function(name="test_lambda",
                              filename="./lambdas/test_lambda.py",
                              runtime="python3.9",
                              role_arn=role_arn,
                              description="Test python lambda function"
                              )


pulumi.export('rest_api id', func.arn)
