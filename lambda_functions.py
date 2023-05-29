from typing import Optional, Mapping
import json
import pulumi
import pulumi_aws as aws
from app_config import config
from iam import create_lambda_exec_role


project_name = config.require("projectName")


def create_lambda_dynamodb_policy(name: str, dynamodb_table_arn: pulumi.Output[str]) -> aws.iam.RoleInlinePolicyArgs:
    policy = json.dumps({
                "Statement": [
                    {
                        "Action": [
                            "dynamodb:BatchGetItem"
                            "dynamodb:BatchWriteItem"
                            "dynamodb:ConditionCheckItem"
                            "dynamodb:DeleteItem"
                            "dynamodb:DescribeTable"
                            "dynamodb:GetItem"
                            "dynamodb:PutItem"
                            "dynamodb:Query"
                            "dynamodb:Scan"
                            "dynamodb:UpdateItem"
                        ],
                        "Resource": [
                            f"{dynamodb_table_arn}",
                            f"{dynamodb_table_arn}/index/*"
                        ],
                        "Effect": "Allow"
                    }
                ]}
    )
    return aws.iam.RoleInlinePolicyArgs(name, policy)


def create_lambda_function(
    name: str,
    filename: str,
    runtime: str,
    handler: str,
    timeout: int,
    lambda_policies: list[aws.iam.RoleInlinePolicyArgs],
    role_arn: Optional[str] = None,
    environment: Mapping[str, str] = None,
    description: Optional[str] = None,
) -> aws.lambda_.Function:

    if role_arn is None:
        role_arn = create_lambda_exec_role(f"{project_name}Lambda{name}ExecRole",
                                           assume_policy_filename="lambdas/execution_role.json",
                                           policy_args=lambda_policies)

    func = aws.lambda_.Function(
        name,
        name=name,
        runtime=runtime,
        role=role_arn,
        handler=handler,
        code=pulumi.asset.AssetArchive({"folder": pulumi.FileArchive(filename)}),
        timeout=timeout,
        description=description,
        environment={"variables": environment},
    )
    return func
