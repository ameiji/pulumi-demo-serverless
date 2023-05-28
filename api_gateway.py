import hashlib
import json
from typing import Dict, Tuple, List, Any
import pulumi
import pulumi_aws as aws
from lambda_functions import create_lambda_function
from cognito import create_cognito_authorizer
from api import api_resources, APIResourceDescription, APIResourceFunction


_integrations: List[pulumi.CustomResource] = []
_resources: Dict[str, aws.apigateway.Resource] = {}


def _create_lambda_resource(
    api_function: APIResourceFunction, rest_api: aws.apigateway.RestApi
) -> aws.lambda_.Function:
    # AWS Lambda
    lambda_ = create_lambda_function(
        name=api_function.name,
        filename=api_function.filename,
        runtime=api_function.runtime,
        handler=api_function.handler,
        description=api_function.description,
    )

    lambda_permission = aws.lambda_.Permission(
        f"{api_function.name}LambdaPermission",
        action="lambda:InvokeFunction",
        function=api_function.name,
        principal="apigateway.amazonaws.com",
        source_arn=rest_api.execution_arn.apply(
            lambda execution_arn: f"{execution_arn}/{api_function.allowed_path}"
        ),
        opts=pulumi.ResourceOptions(parent=rest_api),
    )

    # AWS GW Authorizer resource.

    return lambda_


def _create_resource(
    rest_api: aws.apigateway.RestApi,
    path: str,
    api_resource: APIResourceDescription,
    authorizer: aws.apigateway.Authorizer,
):
    path_part = path.split("/")[-1]

    for method, api_function in api_resource.methods.items():
        lambda_ = _create_lambda_resource(api_function, rest_api)
        api_resource.methods[method].lambda_ = lambda_

    # API GW Resource
    if api_resource.is_root:
        resource = aws.apigateway.Resource(
            api_resource.name,
            parent_id=rest_api.root_resource_id,
            path_part=path_part,
            rest_api=rest_api.id,
            opts=pulumi.ResourceOptions(parent=rest_api),
        )
        _resources[path] = resource
    else:
        parent_path = "/".join(path.split("/")[:-1])
        resource = aws.apigateway.Resource(
            api_resource.name,
            parent_id=_resources[parent_path].id,
            path_part=path_part,
            rest_api=rest_api.id,
            opts=pulumi.ResourceOptions(
                depends_on=[rest_api, _resources[parent_path]], parent=rest_api
            ),
        )
        _resources[path] = resource

    for api_resource_method, api_function in api_resource.methods.items():
        # API GW Method
        method = aws.apigateway.Method(
            f"{api_resource.name}{api_resource_method}",
            http_method=api_resource_method,
            resource_id=resource.id,
            rest_api=rest_api.id,
            authorization="COGNITO_USER_POOLS",
            authorizer_id=authorizer.id,
            opts=pulumi.ResourceOptions(parent=rest_api, depends_on=[authorizer]),
        )

        # API GW Integration
        integration = aws.apigateway.Integration(
            f"{api_resource.name}{api_resource_method}Integration",
            rest_api=rest_api.id,
            resource_id=resource.id,
            http_method=method.http_method,
            integration_http_method="POST",  # For Lambda it is always POST
            type=api_resource.type,
            uri=api_resource.methods[api_resource_method].lambda_.invoke_arn,
            opts=pulumi.ResourceOptions(parent=rest_api),
        )
        _integrations.append(integration)


def create_api_gateway(redirect_url: pulumi.Output[str]) -> Tuple[pulumi.Output]:
    # API Gateway
    rest_api_name = "workshopServerlessJukeBox"
    rest_api = aws.apigateway.RestApi(rest_api_name)

    # API GW Cognito authorizer
    cognito_authorizer = create_cognito_authorizer(rest_api=rest_api, redirect_url=redirect_url)

    for resource_path, resource in api_resources.items():
        _create_resource(
            rest_api=rest_api,
            path=resource_path,
            api_resource=resource,
            authorizer=cognito_authorizer,
        )

    # API GW Deployment
    deployment = aws.apigateway.Deployment(
        f"{rest_api_name}Deployment",
        rest_api=rest_api.id,
        triggers={
            "redeployment": rest_api.body.apply(lambda body: json.dumps(body)).apply(
                lambda to_json: hashlib.sha1(to_json.encode()).hexdigest()
            ),
        },
        opts=pulumi.ResourceOptions(
            depends_on=[*_resources.values(), *_integrations], parent=rest_api
        ),
    )
    # API GW Stage
    stage = aws.apigateway.Stage(
        f"{rest_api_name}Stage",
        deployment=deployment.id,
        rest_api=rest_api.id,
        stage_name=pulumi.Config().get("stageName"),
        opts=pulumi.ResourceOptions(parent=rest_api)
    )

    return rest_api.id, stage.stage_name, stage.invoke_url
