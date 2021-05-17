def test_bad_activate(client):
    r = client.post(f"auth/password_reset/bad_token",
                    data={"password": "321", "password2": "321"})
    assert b"Token is not valid" in r.data
