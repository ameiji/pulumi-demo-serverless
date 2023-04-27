import pulumi
import pulumi_aws as aws

project_name = pulumi.get_project()


def create_cognito_authorizer(
    rest_api: aws.apigateway.RestApi,
    redirect_url: pulumi.Output[str]
) -> aws.apigateway.Authorizer:

    aws_config = pulumi.Config("aws")
    config = pulumi.Config()

    # Cognito User Pool
    user_pool = aws.cognito.UserPool(f"{project_name}UserPool")

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
        generate_secret=False,
        opts=pulumi.ResourceOptions(parent=user_pool),
    )

    cognito_domain = pulumi.Output.concat(project_name, "-", config.require("cognitoDomain"))
    user_pool_domain = aws.cognito.UserPoolDomain(
        f"{project_name}UserPoolDomain",
        domain=cognito_domain,
        user_pool_id=user_pool.id,
        opts=pulumi.ResourceOptions(parent=user_pool),
    )

    # Create the Authorizer resource.
    authorizer = aws.apigateway.Authorizer(
        resource_name=f"{project_name}CognitoAuthorizer",
        rest_api=rest_api.id,
        name=f"{project_name}Authorizer",
        type="COGNITO_USER_POOLS",
        identity_source="method.request.header.Authorization",
        provider_arns=[user_pool.arn],
        opts=pulumi.ResourceOptions(depends_on=[rest_api], parent=rest_api),
    )
    pulumi.export("aws_user_pool_id", user_pool.id)
    pulumi.export("aws_user_pools_web_client_id", user_pool_client.id)
    pulumi.export("cognito_custom_domain",
                  pulumi.Output.format("{0}.auth.{1}.amazoncognito.com",
                                       user_pool_domain.domain,
                                        aws_config.require("region")
                                       )
                  )
    return authorizer
