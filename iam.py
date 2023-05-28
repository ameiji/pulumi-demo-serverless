from typing import Sequence, Optional
import pulumi
from pulumi_aws.iam import Role, RoleInlinePolicyArgs


def _load_json_from_file(filename: str) -> str:
    with open(filename, "r", encoding="utf-8") as f:
        json_string = f.read()
    return json_string


def _get_inline_policy_args(json_string: str) -> RoleInlinePolicyArgs:
    policy = RoleInlinePolicyArgs(policy=json_string)
    return policy


def _create_role(
    name: str,
    assume_role_policy_json: str,
    policy_args: Optional[Sequence[RoleInlinePolicyArgs]] = None,
) -> Role:
    boundary_policy = pulumi.Config().get("boundaryPolicy")
    return Role(
        name,
        name=name,
        assume_role_policy=assume_role_policy_json,
        inline_policies=policy_args,
        permissions_boundary=boundary_policy,
    )


def create_lambda_exec_role(
    name, assume_policy_filename: str, policy_filenames: Optional[list[str]] = None
) -> pulumi.Output[str]:
    policy_args: list[RoleInlinePolicyArgs] = []
    if policy_filenames:
        for policy_file in policy_filenames:
            json_string = _load_json_from_file(policy_file)
            policy_args.append(_get_inline_policy_args(json_string))

    return _create_role(
        name, assume_role_policy_json=_load_json_from_file(assume_policy_filename)
    ).arn

