import os
import json

import stripe
from flask import request, jsonify

from . import payments_blueprint

stripe.api_key = "sk_test_51IF07JIpW5sI31jNntEdiadLtquYkTmZMT5bWrzCtX"  # TODO


@payments_blueprint.route('/', methods=["POST"])
def index():
    return 'this is page with payment info for platform user'


@payments_blueprint.route('/create-checkout-session', methods=['POST'])
def create_checkout_session():
    data = json.loads(request.data)

    try:
        # See https://stripe.com/docs/api/checkout/sessions/create
        # for additional parameters to pass.
        # {CHECKOUT_SESSION_ID} is a string literal; do not change it!
        # the actual Session ID is returned in the query parameter when your customer
        # is redirected to the success page.
        checkout_session = stripe.checkout.Session.create(
            success_url='https://example.com/success.html?session_id={CHECKOUT_SESSION_ID}',  # TODO
            cancel_url='https://example.com/canceled.html',  # TODO
            payment_method_types=['card'],
            mode='subscription',
            line_items=[{
                'price': data['priceId'],
                # For metered billing, do not pass quantity
                'quantity': 1
            }],
        )
        return jsonify({'sessionId': checkout_session['id']})
    except Exception as e:
        return jsonify({'error': {'message': str(e)}}), 400


@payments_blueprint.route('/webhook', methods=['POST'])
def webhook_received():
    webhook_secret = {{'STRIPE_WEBHOOK_SECRET'}}  # TODO
    request_data = json.loads(request.data)

    if webhook_secret:
        # Retrieve the event by verifying the signature using the raw body and secret if webhook signing is configured.
        signature = request.headers.get('stripe-signature')
        try:
            event = stripe.Webhook.construct_event(
                payload=request.data, sig_header=signature, secret=webhook_secret)
            data = event['data']
        except Exception as e:
            return e
        # Get the type of webhook event sent - used to check the status of PaymentIntents.
        event_type = event['type']
    else:
        data = request_data['data']
        event_type = request_data['type']
    data_object = data['object']

    if event_type == 'checkout.session.completed':
        # Payment is successful and the subscription is created.
        # You should provision the subscription and save the customer ID to your database.
        print(data)  # TODO
    elif event_type == 'invoice.paid':
        # Continue to provision the subscription as payments continue to be made.
        # Store the status in your database and check when a user accesses your service.
        # This approach helps you avoid hitting rate limits.
        print(data)  # TODO
    elif event_type == 'invoice.payment_failed':
        # The payment failed or the customer does not have a valid payment method.
        # The subscription becomes past_due. Notify your customer and send them to the
        # customer portal to update their payment information.
        print(data)  # TODO
    else:
        print('Unhandled event type {}'.format(event_type))

    return jsonify({'status': 'success'})


@payments_blueprint.route('/customer-portal', methods=['POST'])
def customer_portal():
    # This is the URL to which the customer will be redirected after they are
    # done managing their billing with the portal.
    return_url = os.getenv("DOMAIN")  # TODO

    session = stripe.billing_portal.Session.create(
        customer='{{CUSTOMER_ID}}',
        return_url=return_url)
    return jsonify({'url': session.url})
