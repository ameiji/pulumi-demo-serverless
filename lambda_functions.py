import os

import pulumi
import pulumi_aws as aws
from typing import Optional
from zipfile import ZipFile

zip_files_list = []

def get_zip_filename(filename: str) -> str:
    zip_files_list.append(f"{filename}.zip")
    return f"{filename}.zip"


def create_zip_archive(filename: str) -> str:
    with ZipFile(get_zip_filename(filename), 'w') as zip_object:
        zip_object.write(filename)
    return get_zip_filename(filename)


def create_file_archive(filename: str) -> pulumi.Archive:
    zip_filename = create_zip_archive(filename)
    return pulumi.FileArchive(zip_filename)


# this is the core function
def create_lambda_function(name: str,
                           filename: str,
                           runtime: str,
                           role_arn: str,
                           description: Optional[str] = None
                           ) -> aws.lambda_.Function:
    func = aws.lambda_.Function(name,
                                name=name,
                                runtime=runtime,
                                role=role_arn,
                                handler="lambda_handler",
                                code=create_file_archive(filename),
                                description=description
                                )
    return func

