import json
from typing import Sequence, Optional
import pulumi_aws as aws
from app_config import config


DYNAMODB_ATTRS = "./dynamodb/attributes.json"

# Example for create dynamodb
# dynamodb_table = create_dynamodb_table("todo-table",
#                                        attributes=get_dynamodb_table_attributes(),
#                                        hash_key=get_key('hash_key'),
#                                        range_key=get_key('range_key'))


def _load_attributes_from_file(filename: str) -> list[dict]:
    with open(filename, "r", encoding="utf-8") as f:
        attributes = json.load(f)
    return attributes


def _create_dynamodb_table_attribute_args(
    name: str, data_type: str
) -> aws.dynamodb.TableAttributeArgs:
    return aws.dynamodb.TableAttributeArgs(name=name, type=data_type)


def _get_secondary_index_name(hash_key: str, range_key: str) -> str:
    return f"{hash_key}-{range_key}"


def _create_dynamodb_table_secondary_index_args(
    hash_key: str, range_key: str, non_index_attrs: Sequence[str]
) -> aws.dynamodb.TableGlobalSecondaryIndexArgs:
    return aws.dynamodb.TableGlobalSecondaryIndexArgs(
        name=_get_secondary_index_name(hash_key, range_key),
        hash_key=hash_key,
        range_key=range_key,
        non_key_attributes=non_index_attrs,
        projection_type="INCLUDE",
        write_capacity=10,
        read_capacity=10,
    )


def get_dynamodb_secondary_index() -> aws.dynamodb.TableGlobalSecondaryIndexArgs:
    attributes_list = _load_attributes_from_file(DYNAMODB_ATTRS)
    secondary_index_attrs = {}
    for attribute in attributes_list:
        secondary_attribute_name = attribute.get("secondary_index")
        if secondary_attribute_name == "non_key_attribute":
            non_key_list = secondary_index_attrs.get("non_key_attribute", [])
            non_key_list.append(attribute["name"])
            secondary_index_attrs.update({"non_key_attribute": non_key_list})
            continue
        if secondary_attribute_name:
            secondary_index_attrs[secondary_attribute_name] = attribute["name"]

    return _create_dynamodb_table_secondary_index_args(
        hash_key=secondary_index_attrs["hash_key"],
        range_key=secondary_index_attrs["range_key"],
        non_index_attrs=secondary_index_attrs["non_key_attribute"],
    )


def get_key(key_type: str) -> str:
    attributes_list = _load_attributes_from_file(DYNAMODB_ATTRS)
    for attribute in attributes_list:
        if attribute.get("index") == key_type:
            return attribute["name"]


def get_dynamodb_table_attributes() -> Sequence[aws.dynamodb.TableAttributeArgs]:
    attributes_list = _load_attributes_from_file(DYNAMODB_ATTRS)
    result = []
    for attribute in attributes_list:
        result.append(
            _create_dynamodb_table_attribute_args(attribute["name"], attribute["type"])
        )
    return result

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
        ttl=aws.dynamodb.TableTtlArgs(
            attribute_name="TimeToExist",
            enabled=False,
        ),
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
    )
    return todo_table
