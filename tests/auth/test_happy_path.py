from flask_login import current_user


def test_register_activate_login(client, email, email_user_service):
    r = client.post("auth/register",
                    data={"email": email,
                          "password": "123",
                          "password2": "123"},
                    follow_redirects=True)
    assert b'Congratulations, you are now a registered user! Check you email for an activation link' in r.data
    token = email_user_service.call_args.kwargs['render_params']['url'].split('/')[-1]
    r = client.get(f"auth/activate/{token}", follow_redirects=True)
    assert b'Login' in r.data
    client.post("auth/login",
                data={"email": email,
                      "password": "123"},
                follow_redirects=True)
    assert current_user.email == email


def test_password_reset_login(client, email, email_user_service):
    client.post("auth/register",
                data={"email": email,
                      "password": "123",
                      "password2": "123"})
    token = email_user_service.call_args.kwargs['render_params']['url'].split('/')[-1]
    client.get(f"auth/activate/{token}")
    client.post(f"auth/forgot_password", data={"email": email})
    token = email_user_service.call_args.kwargs['render_params']['url'].split('/')[-1]
    client.post(f"auth/password_reset/{token}",
                data={"password": "321", "password2": "321"})
    client.post("auth/login",
                data={"email": email,
                      "password": "321"},
                follow_redirects=True)
    assert current_user.email == email
