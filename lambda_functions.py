from typing import Optional, Mapping
import pulumi
import pulumi_aws as aws
from iam import create_lambda_exec_role
from app_config import config

project_name = config.require("projectName")

DEFAULT_LAMBDA_ROLE_ARN = create_lambda_exec_role(
    f"{project_name}LambdaExecRole", assume_policy_filename="lambdas/execution_role.json"
)


def create_lambda_function(
    name: str,
    filename: str,
    runtime: str,
    handler: str,
    role_arn: str = DEFAULT_LAMBDA_ROLE_ARN,
    environment: Mapping[str, str] = None,
    description: Optional[str] = None,
) -> aws.lambda_.Function:
    func = aws.lambda_.Function(
        name,
        name=name,
        runtime=runtime,
        role=role_arn,
        handler=handler,
        code=pulumi.asset.AssetArchive({"folder": pulumi.FileArchive(filename)}),
        description=description,
        environment=environment,
    )
    return func
