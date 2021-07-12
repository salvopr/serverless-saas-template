def test_no_admin_access(registered_user_client):
    r = registered_user_client.post("admin/")
    assert r.status_code == 302
    assert r.location.endswith("/auth/login")


def test_admin_access(registered_user_client, user_table, email):
    user_table.update_item(
        Key={'email': email},
        UpdateExpression=f"set is_admin=:a",
        ExpressionAttributeValues={':a': True},
        ReturnValues="UPDATED_NEW"
    )
    r = registered_user_client.post("admin/")
    assert r.status_code == 200