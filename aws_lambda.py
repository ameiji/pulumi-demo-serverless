import json
import pulumi
import pulumi_aws as aws


# An execution role to use for the Lambda function
role = aws.iam.Role(
    "role",
    assume_role_policy=json.dumps(
        {
            "Version": "2012-10-17",
            "Statement": [
                {
                    "Action": "sts:AssumeRole",
                    "Effect": "Allow",
                    "Principal": {
                        "Service": "lambda.amazonaws.com",
                    },
                }
            ],
        }
    ),
    managed_policy_arns=[aws.iam.ManagedPolicy.AWS_LAMBDA_BASIC_EXECUTION_ROLE],
)


def create_lambda(name: str, runtime: str, handler: str, code_path: str):
    return aws.lambda_.Function(
        name,
        runtime=runtime,
        handler=handler,
        role=role.arn,
        code=pulumi.FileArchive(code_path),
    )
