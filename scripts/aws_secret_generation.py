import json

import boto3

from ggt.configs.config_loader import __init_logging_config, cfg


def create(name, secret_value):
    """
    Creates a new secret. The secret value can be a string or bytes.
    """
    secrets_client = boto3.client("secretsmanager")
    kwargs = {"Name": name}
    if isinstance(secret_value, str):
        kwargs["SecretString"] = secret_value
    elif isinstance(secret_value, bytes):
        kwargs["SecretBinary"] = secret_value
    response = secrets_client.create_secret(**kwargs)
    return response


def get_secret_value(name, version=None):
    """Gets the value of a secret.

    Version (if defined) is used to retrieve a particular version of
    the secret.

    """
    secrets_client = boto3.client("secretsmanager")
    kwargs = {'SecretId': name}
    if version is not None:
        kwargs['VersionStage'] = version
    response = secrets_client.get_secret_value(**kwargs)
    return response


def delete_secret(name, without_recovery=False):
    """Deletes the secret."""
    secrets_client = boto3.client("secretsmanager")
    response = secrets_client.delete_secret(
        SecretId=name, ForceDeleteWithoutRecovery=without_recovery)
    return response


def update_secret_version(name, secret_value, versions=None):
    """Puts a value into an existing secret."""
    secrets_client = boto3.client("secretsmanager")

    kwargs = {'SecretId': name}
    if isinstance(secret_value, str):
        kwargs['SecretString'] = secret_value
    elif isinstance(secret_value, bytes):
        kwargs['SecretBinary'] = secret_value
    if versions is not None:
        kwargs['VersionStages'] = versions
    response = secrets_client.put_secret_value(**kwargs)
    return response


def update_secret(name, secret_value):
    """Updates the value of an existing secret"""
    secrets_client = boto3.client("secretsmanager")

    kwargs = {'SecretId': name}

    if isinstance(secret_value, str):
        kwargs["SecretString"] = secret_value
    elif isinstance(secret_value, bytes):
        kwargs["SecretBinary"] = secret_value

    response = secrets_client.update_secret(**kwargs)
    return response


# print(create("ggt_api_secrets", '{"app": "GGT API"}'))
# print(json.loads(get_secret_value("ggt_api_secrets", version='QA')['SecretString'])['databases'])
# print(json.dumps(cfg));
# update_secret_version("ggt_api_secrets", json.dumps(cfg), versions=['TEST'])
