import pulumi
import pulumi_aws as aws


def create_cognito_authorizer(rest_api: aws.apigateway.RestApi) -> aws.apigateway.Authorizer:
    # Cognito User Pool
    user_pool = aws.cognito.UserPool("todoAPI-user-pool", name="todoAPIUserPool")

    # Cognito User Pool Client
    user_pool_client = aws.cognito.UserPoolClient("todoAPIUserPoolClient", user_pool_id=user_pool.id)

    # Create the Authorizer resource.
    authorizer = aws.apigateway.Authorizer(
        resource_name="todoAPICognitoAuthorizer",
        rest_api=rest_api.id,
        name="todoAPIAuthorizer",
        type="COGNITO_USER_POOLS",
        identity_source="method.request.header.Authorization",
        provider_arns=[user_pool.arn],
        opts=pulumi.ResourceOptions(depends_on=[rest_api]),
    )

    return authorizer
