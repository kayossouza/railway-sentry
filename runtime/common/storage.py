"""Separate bucket clients: Nodestore credentials also hold public Relay identity."""
import os
import boto3
from botocore.config import Config


def client(kind='NODE'):
    return boto3.client(
        's3', endpoint_url=os.environ[f'{kind}_ENDPOINT'],
        region_name=os.environ[f'{kind}_REGION'],
        aws_access_key_id=os.environ[f'{kind}_ACCESS_KEY'],
        aws_secret_access_key=os.environ[f'{kind}_SECRET_KEY'],
        config=Config(signature_version='s3v4', s3={'addressing_style': 'path'}),
    )
