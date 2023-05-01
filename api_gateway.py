import pulumi
import pulumi_aws as aws

def create_api_gateway() -> pulumi.Output:
    rest_api = aws.apigateway.RestApi("workshopServerlessJukeBox")
    resource = aws.apigateway.Resource("workshopServerlessApiGateway",
        parent_id=rest_api.root_resource_id,
        path_part="test",
        rest_api=rest_api.id)
    test_get = aws.apigateway.Method("workshopServerlessApiGatewayTestGet",
        authorization="NONE",
        http_method="GET",
        resource_id=resource.id,
        rest_api=rest_api.id)
    example_integration = aws.apigateway.Integration("workshopServerlessApiGatewayTestIntegration",
        http_method=test_get.http_method,
        resource_id=resource.id,
        rest_api=rest_api.id,
        type="MOCK")

    return rest_api.id