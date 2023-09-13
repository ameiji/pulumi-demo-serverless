"""An AWS Python Pulumi program"""

import pulumi

from api_gateway import create_api_gateway
from cloudfront import upload_frontend
from dynamodb import create_todo_table
from lambda_functions import create_lambda_dynamodb_policy


# DynamoDB
table_name = "todo-api"
todo_table = create_todo_table(table_name)
dynamodb_policy = create_lambda_dynamodb_policy(name=f"lambdaDynamoDBTodoPolicy",
                                                dynamodb_table_arn=todo_table.arn)

# Frontend S3 and CloudFront
cdn, frontend_s3_bucket = upload_frontend()
frontend_url = pulumi.Output.concat("https://", cdn.domain_name)

# API Gateway and Lambdas
api_id, stage_name, invoke_url = create_api_gateway(redirect_url=frontend_url,
                                                    lambda_policies=[dynamodb_policy],
                                                    dynamodb_table=table_name)


# Export the URLs and hostnames of the bucket and distribution.
# pulumi.export(
#     "originURL", pulumi.Output.concat("http://", frontend_s3_bucket.website_endpoint)
# )
# pulumi.export("originHostname", frontend_s3_bucket.website_endpoint)

pulumi.export("s3_bucket_name", frontend_s3_bucket.id)
pulumi.export("cdnURL", frontend_url)
pulumi.export("cdnHostname", cdn.domain_name)

pulumi.export("rest_api_id", api_id)
pulumi.export("stage_name", stage_name)
pulumi.export("backend_invoke_url", invoke_url)
pulumi.export("website_url", frontend_url)
