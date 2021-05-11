import json


def test_register_bad_password(client_no_login):
    r = client_no_login.post("payments/create-checkout-session",
                             data=json.dumps({"priceId": "price_id"}))

    assert r.json['sessionId'] == 'checkout_session_id'
