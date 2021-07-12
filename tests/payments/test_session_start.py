import json


def test_start_checkout_session(registered_user_client):
    r = registered_user_client.post("payments/create-checkout-session",
                                    data=json.dumps({"priceId": "price_id"}))

    assert r.json['sessionId'] == 'checkout_session_id'
