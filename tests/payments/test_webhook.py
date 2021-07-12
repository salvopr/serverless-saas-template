import json
import pytest
from config import current_config


@pytest.mark.usefixtures("register_user")
def test_checkout_session_completed(client, email, user_table):
    current_config.STRIPE_ENDPOINT_KEY = None
    r = client.post("payments/webhook",
                    data=json.dumps(
                        {"type": "checkout.session.completed",
                         "data": {
                             "object": {
                                 'customer_email': email,
                                 'customer': 'customer_id_123'}
                         }
                         }))

    assert r.json['status'] == 'success'
    response = user_table.get_item(Key={'email': email})
    user_data = response['Item']
    assert user_data["subscription_status"] == "checkout_completed"
    assert user_data["is_paying"]
    assert user_data["stripe_customer_id"] == 'customer_id_123'


@pytest.mark.usefixtures("register_user")
def test_invoice_paid(client, email, user_table):
    current_config.STRIPE_ENDPOINT_KEY = None
    r = client.post("payments/webhook",
                    data=json.dumps(
                        {"type": "invoice.paid",
                         "data": {
                             "object": {
                                 'customer_email': email,
                                 'amount_paid': 123,
                             }
                         }
                         }))

    assert r.json['status'] == 'success'

    response = user_table.get_item(Key={'email': email})
    user_data = response['Item']
    assert user_data["subscription_status"] == "invoice_paid"
    assert user_data["is_paying"]


@pytest.mark.usefixtures("register_user")
def test_invoice_payment_failed(client, email, user_table):
    current_config.STRIPE_ENDPOINT_KEY = None
    r = client.post("payments/webhook",
                    data=json.dumps(
                        {"type": "invoice.payment_failed",
                         "data": {
                             "object": {
                                 'customer_email': email,
                             }
                         }
                         }))

    assert r.json['status'] == 'success'

    response = user_table.get_item(Key={'email': email})
    user_data = response['Item']
    assert user_data["subscription_status"] == "invoice_payment_failed"
    assert not user_data["is_paying"]


@pytest.mark.usefixtures("register_user")
def test_invoice_payment_action_required(client, email, user_table):
    current_config.STRIPE_ENDPOINT_KEY = None
    r = client.post("payments/webhook",
                    data=json.dumps(
                        {"type": "invoice.payment_action_required",
                         "data": {
                             "object": {
                                 'customer_email': email,
                             }
                         }
                         }))

    assert r.json['status'] == 'success'

    response = user_table.get_item(Key={'email': email})
    user_data = response['Item']
    assert user_data["subscription_status"] == "payment_action_required"
    assert not user_data["is_paying"]


@pytest.mark.usefixtures("register_user")
def test_trial_will_end(client):
    current_config.STRIPE_ENDPOINT_KEY = None
    r = client.post("payments/webhook",
                    data=json.dumps(
                        {"type": "customer.subscription.trial_will_end",
                         "data": {
                             "object": {
                                 'customer': "customer_id_123",
                             }
                         }
                         }))

    assert r.json['status'] == 'success'


@pytest.mark.usefixtures("register_user")
def test_subscription_updated(client, email, user_table):
    current_config.STRIPE_ENDPOINT_KEY = None
    r = client.post("payments/webhook",
                    data=json.dumps(
                        {"type": "customer.subscription.updated",
                         "data": {
                             "object": {
                                 'customer': "customer_id_123",
                                 'status': 'canceled'
                             }
                         }
                         }))

    assert r.json['status'] == 'success'
    response = user_table.get_item(Key={'email': email})
    user_data = response['Item']
    assert user_data["subscription_status"] == 'canceled'
    assert not user_data["is_paying"]


@pytest.mark.usefixtures("register_user")
def test_subscription_deleted(client, email, user_table):
    current_config.STRIPE_ENDPOINT_KEY = None
    r = client.post("payments/webhook",
                    data=json.dumps(
                        {"type": "customer.subscription.deleted",
                         "data": {
                             "object": {
                                 'customer': "customer_id_123",
                                 'status': 'canceled'
                             }
                         }
                         }))

    assert r.json['status'] == 'success'
    response = user_table.get_item(Key={'email': email})
    user_data = response['Item']
    assert user_data["subscription_status"] == 'deleted'
    assert not user_data["is_paying"]