def test_get(client):
    r = client.get('/auth/login')
    assert r.status_code == 200


def test_login_not_activated(client, email):
    client.post("auth/register",
                data={"email": email,
                      "password": "123",
                      "password2": "123"},
                follow_redirects=True)
    r = client.post("auth/login",
                    data={"email": email,
                          "password": "123"},
                    follow_redirects=True)
    assert b'User is not activated yet!' in r.data
