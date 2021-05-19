from flask_login import current_user


def test_console_paying(registered_user_client, user_table, email):
    user_table.update_item(
        Key={'email': email},
        UpdateExpression=f"set is_paying=:a",
        ExpressionAttributeValues={':a': True},
        ReturnValues="UPDATED_NEW"
    )
    r = registered_user_client.get("payments", follow_redirects=True)
    assert b'Manage Billing' in r.data


def test_console_not_paying(registered_user_client):
    r = registered_user_client.get("payments", follow_redirects=True)
    assert b'Subscribe to' in r.data
