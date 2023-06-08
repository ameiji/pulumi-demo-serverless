from typing import Optional, Mapping
import json
import pulumi
import pulumi_aws as aws
from app_config import config
from iam import create_lambda_exec_role


project_name = config.require("projectName")
lambda_roles_path = config.require("lambdasRolesPath")


def create_lambda_dynamodb_policy(name: str, dynamodb_table_arn: pulumi.Output[str]) -> aws.iam.RoleInlinePolicyArgs:
    policy = pulumi.Output.json_dumps({
                "Statement": [
                    {
                        "Action": [
                            "dynamodb:BatchGetItem",
                            "dynamodb:BatchWriteItem",
                            "dynamodb:ConditionCheckItem",
                            "dynamodb:DeleteItem",
                            "dynamodb:DescribeTable",
                            "dynamodb:GetItem",
                            "dynamodb:PutItem",
                            "dynamodb:Query",
                            "dynamodb:Scan",
                            "dynamodb:UpdateItem"
                        ],
                        "Resource": [
                            dynamodb_table_arn,
                            pulumi.Output.format("{0}/index/*", dynamodb_table_arn)
                        ],
                        "Effect": "Allow"
                    }
                ]})
    return aws.iam.RoleInlinePolicyArgs(name=name, policy=policy)


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
                                           assume_policy_filename=f"{lambda_roles_path}/execution_role.json",
                                           policy_args=lambda_policies)

    # asset_archive = pulumi.asset.AssetArchive({"folder": pulumi.FileArchive(filename)})
    asset_archive = pulumi.FileArchive(filename)
    func = aws.lambda_.Function(
        name,
        name=name,
        runtime=runtime,
        role=role_arn,
        handler=handler,
        code=asset_archive,
        timeout=timeout,
        description=description,
        environment={"variables": environment},
    )
    return func
