def test_customer_portal_url_generation(registered_user_client):
    r = registered_user_client.post("payments/customer-portal", follow_redirects=True)
    assert r.json['url'] == 'test_customer_portal_url'
