from flask_login import current_user


def test_customer_portal_url_generation(client, email, email_user_service):
    client.post("auth/register",
                data={"email": email,
                      "password": "123",
                      "password2": "123"})
    token = email_user_service.call_args.kwargs['render_params']['url'].split('/')[-1]

    client.get(f"auth/activate/{token}")
    client.post("auth/login",
                data={"email": email,
                      "password": "123"},
                follow_redirects=True)
    r = client.post("payments/customer-portal",
                    follow_redirects=True)
    assert r.json['url'] == 'test_customer_portal_url'
