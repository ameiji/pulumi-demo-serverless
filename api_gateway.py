import json
import pulumi
import pulumi_aws as aws
import pulumi_aws_apigateway as apigw
import aws_lambda


def create_api_gateway():
    # A REST API to route requests to HTML content and the Lambda function
    rest_api = apigw.RestAPI(
        "api-gw-example",
        routes=[
            apigw.RouteArgs(path="/", local_path="www/public/"),
            apigw.RouteArgs(
                path="/date",
                method=apigw.Method.GET,
                event_handler=aws_lambda.create_lambda(
                    name="addTodo",
                    runtime="nodejs16.x",
                    handler="app.addToDoItem",
                    code_path="./todo-src/addTodo",
                ),
            ),
        ],
    )


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
