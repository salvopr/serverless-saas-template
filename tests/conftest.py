from unittest.mock import patch, MagicMock

import boto3
import pytest
from app import create_app
from config import current_config


@pytest.fixture
def client():
    test_app = create_app()
    test_app.config['TESTING'] = True
    test_app.config['WTF_CSRF_ENABLED'] = False

    with test_app.test_client() as client:
        yield client


@pytest.fixture
def client_no_login():
    test_app = create_app()
    test_app.config['TESTING'] = True
    test_app.config['LOGIN_DISABLED'] = True
    test_app.config['WTF_CSRF_ENABLED'] = False

    with test_app.test_client() as client:
        yield client


def email_generator():
    counter = 100
    while 1:
        yield f"user{counter}@test.com"
        counter += 1


email_generator_instance = email_generator()


@pytest.fixture
def email():
    e = next(email_generator_instance)
    return e


@pytest.fixture(autouse=True, scope="session")
def purge_ddb():
    yield
    for table_name, key in zip((current_config.USERS_TABLE, current_config.AUTH_TOKENS_TABLE),
                               ("email", "token")):
        dynamodb = boto3.resource('dynamodb', region_name=current_config.AWS_REGION)
        table = dynamodb.Table(table_name)
        for item in table.scan()['Items']:
            table.delete_item(Key={key: item[key]})


@pytest.fixture(autouse=True)
def email_user_service():
    with patch('app.user.send_email') as mock_send_email:
        yield mock_send_email


@pytest.fixture(autouse=True)
def stripe_plans():
    with patch('app.payments.plans.stripe') as mock_stripe:
        plans = [{"active": True,
                  "id": "priceid1",
                  "product": "productid1",
                  "unit_amount": 500,
                  "currency": "eur",
                  "recurring": {"interval": "month"}},
                 {"active": True,
                  "id": "priceid2",
                  "product": "productid2",
                  "unit_amount": 1000,
                  "currency": "eur",
                  "recurring": {"interval": "year"}}
                 ]
        mock_stripe.Price.list = MagicMock(return_value=plans)
        mock_stripe.Product.retrieve = MagicMock(return_value={"name": "product_name"})
        yield mock_stripe


@pytest.fixture(autouse=True)
def stripe_session(email):
    with patch('app.payments.views.stripe') as mock_stripe:
        mock_stripe.checkout.Session.create = MagicMock(return_value={"id": "checkout_session_id"})
        mock_stripe.Customer.retrieve = MagicMock(return_value={"email": email})
        customer_portal = MagicMock()
        customer_portal.url = 'test_customer_portal_url'
        mock_stripe.billing_portal.Session.create = MagicMock(return_value=customer_portal)
        yield mock_stripe


@pytest.fixture
def user_table():
    dynamodb = boto3.resource('dynamodb', region_name=current_config.AWS_REGION)
    table = dynamodb.Table(current_config.USERS_TABLE)
    return table


@pytest.fixture
def register_user(email, user_table):
    user_table.put_item(
        Item={"email": email,
              "password_token": 'token',
              "activated": True,
              "stripe_customer_id": "stripe_customer_id_123"}
    )


@pytest.fixture
def registered_user_client(email, client, email_user_service):
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
    return client
