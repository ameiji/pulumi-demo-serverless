import json
from typing import Sequence, Optional
import pulumi_aws as aws


DYNAMODB_ATTRS = "./dynamodb/attributes.json"


def _create_dynamodb_table(
    table_name: str,
    attributes: Sequence[aws.dynamodb.TableAttributeArgs],
    hash_key: str,
    range_key: str,
    secondary_indexes: Optional[
        Sequence[aws.dynamodb.TableGlobalSecondaryIndexArgs]
    ] = None,
) -> aws.dynamodb.Table:
    _attributes: Sequence[aws.dynamodb.TableAttributeArgs] = []
    for attr in attributes:
        _attributes.append(
            aws.dynamodb.TableAttributeArgs(name=attr["name"], type=attr["type"])
        )

    if secondary_indexes is None:
        secondary_indexes = []
        dynamodb_table = aws.dynamodb.Table(
            table_name,
            name=table_name,
            tags={
                "Name": table_name,
            },
            # ttl=aws.dynamodb.TableTtlArgs(
            #     attribute_name="TimeToExist",
            #     enabled=False,
            # ),
            read_capacity=20,
            write_capacity=20,
            attributes=attributes,
            global_secondary_indexes=secondary_indexes,
            hash_key=hash_key,
            range_key=range_key,
        )
    return dynamodb_table


def create_todo_table(table_name: str) -> aws.dynamodb.Table:
    todo_table = _create_dynamodb_table(
        table_name=table_name,
        hash_key="cognito-username",
        range_key="id",
        attributes=[
            {"name": "cognito-username", "type": "S"},
            {"name": "id", "type": "S"},
        ],
    )  # TODO: load attributes from DYNAMODB_ATTRS
    return todo_table
