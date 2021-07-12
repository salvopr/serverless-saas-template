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


def test_login_no_user(client):
    r = client.post("auth/login",
                    data={"email": "do_not_exists@test.com",
                          "password": "123"},
                    follow_redirects=True)
    assert b'User is not registered' in r.data


def test_login_invalid_password(client, email, email_user_service):
    client.post("auth/register",
                data={"email": email,
                      "password": "123",
                      "password2": "123"},
                follow_redirects=True)
    token = email_user_service.call_args.kwargs['render_params']['url'].split('/')[-1]
    client.get(f"auth/activate/{token}", follow_redirects=True)
    r = client.post("auth/login",
                    data={"email": email,
                          "password": "3321"},
                    follow_redirects=True)
    assert b'Invalid password' in r.data
