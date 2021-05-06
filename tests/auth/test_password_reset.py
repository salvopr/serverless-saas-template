def test_bad_token(client):
    r = client.get("/auth/activate/bad_token")
    assert b"Token not valid!" in r.data
