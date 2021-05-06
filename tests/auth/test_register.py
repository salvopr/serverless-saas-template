def test_register_bad_email(client):
    r = client.post("auth/register",
                    data={"email": "abracadabra",
                          "password": "123",
                          "password2": "123"})
    assert b'Invalid email address.' in r.data


def test_register_bad_password(client):
    r = client.post("auth/register",
                    data={"email": "abracadabra",
                          "password": "",
                          "password2": ""})
    assert b'This field is required.' in r.data


def test_register_twice(client, email):
    client.post("auth/register",
                data={"email": email,
                      "password": "123",
                      "password2": "123"})
    r = client.post("auth/register",
                    data={"email": email,
                          "password": "123",
                          "password2": "123"},
                    follow_redirects=True)
    assert b'Please use a different email address.' in r.data

