def test_bad_token(client):
    r = client.get("/auth/activate/bad_token")
    assert b"Token is not valid" in r.data
