import hashlib
import json
from typing import Dict, Tuple, List, Any, Optional
import pulumi
import pulumi_aws as aws
from lambda_functions import create_lambda_function
from cognito import create_cognito_authorizer
from api import api_resources, APIResourceDescription, APIResourceFunction
from app_config import config


_integrations: List[pulumi.CustomResource] = []
_integration_responses: List[pulumi.CustomResource] = []
_resources: Dict[str, aws.apigateway.Resource] = {}
project_name = config.require("projectName")


def _create_lambda_resource(
    api_function: APIResourceFunction,
    rest_api: aws.apigateway.RestApi,
    lambda_policies: list[aws.iam.RoleInlinePolicyArgs],
    environment: Optional[Dict[str, str]] = None,
) -> aws.lambda_.Function:
    # AWS Lambda
    _environment = api_function.environment

    if environment:
        _environment.update(environment)

    lambda_ = create_lambda_function(
        name=api_function.name,
        filename=api_function.filename,
        runtime=api_function.runtime,
        handler=api_function.handler,
        description=api_function.description,
        timeout=api_function.timeout,
        lambda_policies=lambda_policies,
        environment=_environment,
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

    return lambda_


def _create_integration_response(
    name: str,
    rest_api: aws.apigateway.RestApi,
    api_resource: aws.apigateway.Resource,
    api_integration: aws.apigateway.Integration,
    http_method: str,
):
    response200 = aws.apigateway.MethodResponse(
        f"{name}Response200",
        rest_api=rest_api.id,
        resource_id=api_resource.id,
        http_method=http_method,
        status_code="200",
        response_parameters={
            "method.response.header.Access-Control-Allow-Origin": True,
            "method.response.header.Access-Control-Allow-Methods": True,
            "method.response.header.Access-Control-Allow-Headers": True,
        },
        opts=pulumi.ResourceOptions(parent=api_integration, depends_on=api_integration)
    )
    integration_response = aws.apigateway.IntegrationResponse(
        f"{name}IntegrationResponse",
        rest_api=rest_api.id,
        resource_id=api_resource.id,
        http_method=http_method,
        status_code=response200.status_code,
        response_templates={"application/json": "{}\n"},
        response_parameters={
            "method.response.header.Access-Control-Allow-Origin": "'*'",
            "method.response.header.Access-Control-Allow-Methods": "'OPTIONS,HEAD,GET,PUT,POST,DELETE'",
            "method.response.header.Access-Control-Allow-Headers": "'Content-Type,X-Amz-Date,Authorization,X-Api-Key,X-Amz-Security-Token'",
        },
        opts=pulumi.ResourceOptions(
            parent=api_integration, depends_on=[api_integration, response200]
        ),
    )
    return integration_response


def _create_api_resource(
    rest_api: aws.apigateway.RestApi,
    path: str,
    api_resource_description: APIResourceDescription,
    authorizer: aws.apigateway.Authorizer,
    lambda_policies: list[aws.iam.RoleInlinePolicyArgs],
    lambda_environment: Optional[Dict[str, str]] = None,
):
    path_part = path.split("/")[-1]

    for method, api_function in api_resource_description.methods.items():
        # Create Lambda
        if api_function.integration_type != "MOCK":
            lambda_ = _create_lambda_resource(
                api_function,
                rest_api,
                lambda_policies=lambda_policies,
                environment=lambda_environment,
            )
            api_resource_description.methods[method].lambda_ = lambda_

    # API GW Resource
    if api_resource_description.is_root:
        api_resource = aws.apigateway.Resource(
            api_resource_description.name,
            parent_id=rest_api.root_resource_id,
            path_part=path_part,
            rest_api=rest_api.id,
            opts=pulumi.ResourceOptions(parent=rest_api),
        )
        _resources[path] = api_resource
    else:
        parent_path = "/".join(path.split("/")[:-1])
        api_resource = aws.apigateway.Resource(
            api_resource_description.name,
            parent_id=_resources[parent_path].id,
            path_part=path_part,
            rest_api=rest_api.id,
            opts=pulumi.ResourceOptions(
                depends_on=[rest_api, _resources[parent_path]], parent=rest_api
            ),
        )
        _resources[path] = api_resource

    for api_resource_method, api_function in api_resource_description.methods.items():

        # API GW Method
        method = aws.apigateway.Method(
            f"{api_resource_description.name}{api_resource_method}",
            http_method=api_resource_method,
            resource_id=api_resource.id,
            rest_api=rest_api.id,
            authorization=api_function.authorization,
            authorizer_id=authorizer.id,
            opts=pulumi.ResourceOptions(parent=api_resource, depends_on=[authorizer]),
        )

        # API GW Integration
        if api_function.integration_type == "MOCK":
            integration_uri = None
            request_templates = {"application/json": '{\n  "statusCode" : 200\n}\n'}
        else:
            integration_uri = api_resource_description.methods[api_resource_method].lambda_.invoke_arn
            request_templates = None

        integration = aws.apigateway.Integration(
            f"{api_resource_description.name}{api_resource_method}Integration",
            rest_api=rest_api.id,
            resource_id=api_resource.id,
            http_method=method.http_method,
            integration_http_method=api_function.integration_method,  # For Lambda it is always POST
            # passthrough_behavior="WHEN_NO_TEMPLATES",
            request_templates=request_templates,
            type=api_function.integration_type,
            uri=integration_uri,
            opts=pulumi.ResourceOptions(parent=api_resource),
        )

        if api_function.integration_type == "MOCK":
            _create_integration_response(
                name=f"{api_resource_description.name}{api_resource_method}Mock",
                rest_api=rest_api,
                api_resource=api_resource,
                api_integration=integration,
                http_method=api_resource_method,
            )
        _integrations.append(integration)


def create_api_gateway(
    redirect_url: pulumi.Output[str],
    lambda_policies: list[aws.iam.RoleInlinePolicyArgs],
    lambda_environment: Optional[Dict[str, str]] = None,
) -> Tuple[pulumi.Output[str]]:
    # API Gateway
    rest_api_name = "workshopServerlessJukeBox"
    rest_api = aws.apigateway.RestApi(rest_api_name)

    # API GW Cognito authorizer
    cognito_authorizer = create_cognito_authorizer(
        rest_api=rest_api, redirect_url=redirect_url
    )

    # API Resources
    for resource_path, resource in api_resources.items():
        _create_api_resource(
            rest_api=rest_api,
            path=resource_path,
            api_resource_description=resource,
            authorizer=cognito_authorizer,
            lambda_policies=lambda_policies,
            lambda_environment=lambda_environment,
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
        opts=pulumi.ResourceOptions(parent=rest_api),
    )

    return rest_api.id, stage.stage_name, stage.invoke_url
