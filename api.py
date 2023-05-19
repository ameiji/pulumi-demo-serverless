import sys
import os.path
import pulumi_aws as aws
from collections import OrderedDict
from typing import Optional, Dict, List, Literal, Any
from pydantic import validator, BaseModel, ValidationError


BACKEND_SRC_PATH = "./backend-src"


class APIResourceFunction(BaseModel):
    name: str
    filename: Optional[str]
    handler: str
    allowed_path: str
    runtime: str = "nodejs16.x"
    lambda_: aws.lambda_.Function
    description: Optional[str] = ""

    @validator("filename", always=True)
    def _filename_validator(cls, filename: Optional[str], values) -> str:
        if filename:
            return filename
        return os.path.join(BACKEND_SRC_PATH, values["name"])


class APIResourceDescription(BaseModel):
    name: str
    is_root: bool = False
    type: str = "AWS_PROXY"
    methods: Dict[Literal["GET", "POST", "UPDATE", "DELETE", "PUT"], APIResourceFunction]
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
)
getAllTodo = APIResourceFunction(
    name="getAllTodo",
    allowed_path="*/GET/item",
    handler="app.getAllTodo",
)
completeTodo = APIResourceFunction(
    name="completeTodo",
    allowed_path="*/POST/item/*/done",
    handler="app.completeTodo",
)
getTodo = APIResourceFunction(
    name="getTodo",
    allowed_path="*/GET/item/*",
    handler="app.getTodo",
)
updateTodo = APIResourceFunction(
    name="updateTodo",
    allowed_path="*/PUT/item/*",
    handler="app.updateTodo",
)
deleteTodo = APIResourceFunction(
    name="deleteTodo",
    allowed_path="*/DELETE/item/*",
    handler="app.deleteTodo",
)


try:
    api_resources = OrderedDict({
            "/item": APIResourceDescription(
                name="item",
                is_root=True,
                methods={"GET": getAllTodo,
                         "POST": addTodo}
            ),
            "/item/{id}": APIResourceDescription(
                name="itemId",
                methods={"GET": getTodo,
                         "PUT": updateTodo,
                         "DELETE": deleteTodo},
            ),
            "/item/{id}/done": APIResourceDescription(
                name="itemIdDone",
                methods={"POST": completeTodo}
            )
        })
except ValidationError as err:
    print(err)
    sys.exit(1)
