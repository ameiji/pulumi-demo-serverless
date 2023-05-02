import json
import hashlib
import pulumi
import pulumi_aws as aws


def create_api_gateway() -> pulumi.Output:
    rest_api = aws.apigateway.RestApi("exampleRestApi")
    example_resource = aws.apigateway.Resource(
        "exampleResource",
        parent_id=rest_api.root_resource_id,
        path_part="example",
        rest_api=rest_api.id,
    )
    example_method = aws.apigateway.Method(
        "exampleMethod",
        authorization="NONE",
        http_method="GET",
        resource_id=example_resource.id,
        rest_api=rest_api.id,
    )
    example_integration = aws.apigateway.Integration(
        "exampleIntegration",
        http_method=example_method.http_method,
        resource_id=example_resource.id,
        rest_api=rest_api.id,
        type="MOCK",
    )
    example_deployment = aws.apigateway.Deployment(
        "exampleDeployment",
        rest_api=rest_api.id,
        # triggers={
        #     "redeployment": pulumi.Output.all(
        #         example_resource.id, example_method.id, example_integration.id
        #     )
        #     .apply(
        #         lambda exampleResourceId, exampleMethodId, exampleIntegrationId: json.dumps(
        #             [
        #                 example_resource.id,
        #                 example_method.id,
        #                 example_integration.id,
        #             ]
        #         )
        #     )
        #     .apply(lambda to_json: hashlib.sha1(to_json.encode()).hexdigest()),
        # },
    )
    example_stage = aws.apigateway.Stage(
        "exampleStage",
        deployment=example_deployment.id,
        rest_api=rest_api.id,
        stage_name="example",
    )

    return rest_api.id


# # A REST API to route requests to HTML content and the Lambda function
# api = apigateway.RestAPI(
#     "api-gw-example",
#     routes=[
#         apigateway.RouteArgs(path="/", local_path="www"),
#         apigateway.RouteArgs(
#             path="/date", method=apigateway.Method.GET, event_handler=fn
#         ),
#     ],
# )
