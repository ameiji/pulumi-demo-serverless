"""An AWS Python Pulumi program"""
import pulumi

from lambda_functions import create_lambda_resource
from api import addTodo, getAllTodo, completeTodo, getTodo, updateTodo, deleteTodo


def main():
    add_todo_resource = create_lambda_resource(addTodo, lambda_policies=[])
    get_all_todo_resource = create_lambda_resource(getAllTodo, lambda_policies=[])
    complete_todo_resource = create_lambda_resource(completeTodo, lambda_policies=[])
    get_todo_resource = create_lambda_resource(getTodo, lambda_policies=[])
    update_todo_resource = create_lambda_resource(updateTodo, lambda_policies=[])
    delete_todo_resource = create_lambda_resource(deleteTodo, lambda_policies=[])

    pulumi.export("addTodo.arn", add_todo_resource.arn)
    pulumi.export("getAllTodo.arn", get_all_todo_resource.arn)
    pulumi.export("completeTodo.arn", complete_todo_resource.arn)
    pulumi.export("getTodo.arn", get_todo_resource.arn)
    pulumi.export("updateTodo.arn", update_todo_resource.arn)
    pulumi.export("deleteTodo.arn", delete_todo_resource.arn)


if __name__ == '__main__':
    main()
