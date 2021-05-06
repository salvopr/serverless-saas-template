from uuid import uuid4

import boto3
from botocore.exceptions import ClientError

from app.exceptions import TokenError
from config import current_config


def token_table():
    dynamodb = boto3.resource('dynamodb', region_name=current_config.AWS_REGION)
    table = dynamodb.Table(current_config.AUTH_TOKENS_TABLE)
    return table


def create_token(token_type, user_id):
    table = token_table()
    token = str(uuid4())
    try:
        table.put_item(
            Item={"token": token,
                  "type": token_type,
                  "user_id": user_id}
        )
        return token
    except ClientError as e:
        raise TokenError("Cannot crete token " + e.response['Error']['Message']) from e


def token_user_id(token, token_type):
    table = token_table()
    try:
        response = table.get_item(Key={"token": token})
        if response['Item']["type"] != token_type:
            raise TokenError(f"token_type in not valid {token} {token_type}")
        else:
            return response['Item']["user_id"]
    except ClientError as e:
        raise TokenError("Cannot get token " + e.response['Error']['Message']) from e
    except KeyError as e:
        raise TokenError(f"Token in not valid {token} {token_type}") from e
