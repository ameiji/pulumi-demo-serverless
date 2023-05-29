import sys
import os.path
from collections import OrderedDict
from typing import Optional, Dict, Literal, Any
from pydantic import validator, BaseModel, ValidationError
from app_config import config


backend_src_path = config.require("backendSRCPath")


class APIResourceFunction(BaseModel):
    name: str
    filename: Optional[str]
    handler: Optional[str]
    lambda_: Any
    authorization: Literal["COGNITO_USER_POOLS", "NONE"] = "COGNITO_USER_POOLS"
    allowed_path: str
    runtime: str = "nodejs16.x"
    timeout: Optional[int] = 30
    environment: Dict[str, str] = {}
    description: Optional[str] = ""
    integration_type: Literal["HTTP", "AWS", "AWS_PROXY", "MOCK"] = "AWS_PROXY"
    integration_method: Literal["GET", "POST", "PUT", "DELETE", "HEAD", "OPTIONS", "ANY", "PATCH"] = "POST"  # For Lambdas it is always POST

    @validator("filename", always=True)
    def _filename_validator(cls, filename: Optional[str], values) -> str:
        if filename:
            return filename
        return os.path.join(backend_src_path, values["name"])


class APIResourceDescription(BaseModel):
    name: str
    is_root: bool = False
    methods: Dict[
        Literal["GET", "POST", "UPDATE", "DELETE", "PUT", "OPTIONS"],
        APIResourceFunction
    ]
    description: Optional[str]

    @validator("description", always=True)
    def _description_validator(cls, description: Optional[str], values) -> str:
        if description:
            return description
        return values["name"]


addTodo = APIResourceFunction(
    name="addTodo",
    allowed_path="*/POST/item",
    handler="app.addToDoItem",
    environment={
        "AWS_NODEJS_CONNECTION_REUSE_ENABLED": "1",
        "ENDPOINT_OVERRIDE": ""
    }
)
getAllTodo = APIResourceFunction(
    name="getAllTodo",
    allowed_path="*/GET/item",
    handler="app.getAllTodo",
    environment={
        "AWS_NODEJS_CONNECTION_REUSE_ENABLED": "1",
        "ENDPOINT_OVERRIDE": ""
    }
)
completeTodo = APIResourceFunction(
    name="completeTodo",
    allowed_path="*/POST/item/*/done",
    handler="app.completeTodo",
    environment={
        "AWS_NODEJS_CONNECTION_REUSE_ENABLED": "1",
        "ENDPOINT_OVERRIDE": ""
    }
)
getTodo = APIResourceFunction(
    name="getTodo",
    allowed_path="*/GET/item/*",
    handler="app.getTodo",
    environment={
        "AWS_NODEJS_CONNECTION_REUSE_ENABLED": "1",
        "USE_DYNAMODB_LOCAL": "0",
        "DYNAMODB_LOCAL_URI": ""
    }
)
updateTodo = APIResourceFunction(
    name="updateTodo",
    allowed_path="*/PUT/item/*",
    handler="app.updateTodo",
    environment={
        "AWS_NODEJS_CONNECTION_REUSE_ENABLED": "1"
    }
)
deleteTodo = APIResourceFunction(
    name="deleteTodo",
    allowed_path="*/DELETE/item/*",
    handler="app.deleteTodo",
    environment={
        "AWS_NODEJS_CONNECTION_REUSE_ENABLED": "1",
        "ENDPOINT_OVERRIDE": ""
    }
)

mockItem = APIResourceFunction(
    name="mockItem",
    allowed_path="*/OPTIONS/item",
    authorization="NONE",
    integration_type="MOCK",
    integration_method="OPTIONS"
)

mockItemId = APIResourceFunction(
    name="mockItemId",
    allowed_path="*/OPTIONS/item/*",
    authorization="NONE",
    integration_type="MOCK",
    integration_method="OPTIONS"
)

mockItemDoneId = APIResourceFunction(
    name="mockItemDoneId",
    allowed_path="*/OPTIONS/item/*/done",
    authorization="NONE",
    integration_type="MOCK",
    integration_method="OPTIONS"
)


try:
    api_resources = OrderedDict(
        {
            "/item": APIResourceDescription(
                name="item",
                is_root=True,
                methods={"GET": getAllTodo,
                         "POST": addTodo,
                         "OPTIONS": mockItem}
            ),
            "/item/{id}": APIResourceDescription(
                name="itemId",
                methods={"GET": getTodo,
                         "PUT": updateTodo,
                         "DELETE": deleteTodo,
                         "OPTIONS": mockItemId},
            ),
            "/item/{id}/done": APIResourceDescription(
                name="itemIdDone",
                methods={
                    "POST": completeTodo,
                    "OPTIONS": mockItemDoneId
                }
            ),
        }
    )
except ValidationError as err:
    print(err)
    sys.exit(1)
