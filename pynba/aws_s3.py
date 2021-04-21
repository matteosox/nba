"""Module of utilities for working with s3"""

import boto3

from pynba.constants import S3


s3_client = boto3.client(S3)


def get_fileobject(bucket, key, **kwargs):
    """
    Wrapper function for client.get_object:
    https://boto3.amazonaws.com/v1/documentation/api/latest/reference/services/s3.html#S3.Client.get_object

    Parameters
    ----------
    bucket : str
        name of the AWS S3 bucket
    key: str
        key for file in the bucket

    Returns
    -------
    StreamingBody fileobject
    """
    response = s3_client.get_object(Bucket=bucket, Key=key, **kwargs)
    return response["Body"]


def list_objects(bucket, **kwargs):
    """
    Lists objects for a bucket in AWS S3,
    with the same syntax as client.list_objects_v2,
    only handling pagination. See here for full details:
    https://boto3.amazonaws.com/v1/documentation/api/latest/reference/services/s3.html#S3.Client.list_objects_v2

    Parameters
    ----------
    bucket : str
        name of the AWS S3 bucket

    Returns
    -------
    iterator yielding dictionaries
    """
    while True:
        response = s3_client.list_objects_v2(Bucket=bucket, **kwargs)
        for content in response["Contents"]:
            yield content
        if not response["IsTruncated"]:
            break
        kwargs["ContinuationToken"] = response["NextContinuationToken"]
