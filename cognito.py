import pulumi
import pulumi_aws as aws

config = pulumi.Config()
project_name = config.require("projectName")

def create_cognito_authorizer(
    rest_api: aws.apigateway.RestApi,
    redirect_url: pulumi.Output[str]
) -> aws.apigateway.Authorizer:
    # Cognito User Pool
    user_pool = aws.cognito.UserPool(f"{project_name}UserPool", name=f"{project_name}UserPool")

    # Cognito User Pool Client
    user_pool_client = aws.cognito.UserPoolClient(
        f"{project_name}PoolClient",
        user_pool_id=user_pool.id,
        callback_urls=[
            "http://localhost:3000",
            "http://localhost:8080",
            "https://localhost",
            redirect_url
        ],
        supported_identity_providers=["COGNITO"],
        explicit_auth_flows=["USER_PASSWORD_AUTH"],
        allowed_oauth_flows_user_pool_client=True,
        allowed_oauth_scopes=["phone", "email", "openid"],
        allowed_oauth_flows=["code", "implicit"],
        generate_secret=False
    )

    user_pool_domain = aws.cognito.UserPoolDomain(
        f"{project_name}UserPoolDomain",
        domain="todoapi-pulumi-demo",
        user_pool_id=user_pool.id
    )

    # Create the Authorizer resource.
    authorizer = aws.apigateway.Authorizer(
        resource_name=f"{project_name}CognitoAuthorizer",
        rest_api=rest_api.id,
        name=f"{project_name}Authorizer",
        type="COGNITO_USER_POOLS",
        identity_source="method.request.header.Authorization",
        provider_arns=[user_pool.arn],
        opts=pulumi.ResourceOptions(depends_on=[rest_api]),
    )
    pulumi.export("aws_user_pool_id", user_pool.id)
    pulumi.export("aws_user_pools_web_client_id", user_pool_client.id)
    pulumi.export("cognito_custom_domain",
                  pulumi.Output.format("{0}.auth.{1}.amazoncognito.com",
                                       user_pool_domain.domain,
                                       pulumi.config.Config("aws").require("region")
                                       )
                  )
    return authorizer
