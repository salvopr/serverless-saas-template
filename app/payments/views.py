import os
import json

import stripe
from flask import request, jsonify, redirect, url_for, flash, render_template
from flask_login import login_required

from . import payments_blueprint
from config import current_config
from app.payments.plans import get_prices_from_stripe, TRIAL_DAYS
stripe.api_key = current_config.STRIPE_SEC_KEY


@payments_blueprint.route('/', methods=["GET"])
@login_required
def index():
    payment_plans = get_prices_from_stripe()
    return render_template('payments/index.html', payment_plans=payment_plans)


@payments_blueprint.route('/success', methods=["GET"])
@login_required
def success():
    flash("Payment succeeded! Provisioning subscription.", "success")
    return redirect(url_for("payments_blueprint.index"))


@payments_blueprint.route('/cancel', methods=["GET"])
@login_required
def cancel():
    flash("Payment canceled!", "warning")
    return redirect(url_for("payments_blueprint.index"))


@payments_blueprint.route('/create-checkout-session', methods=['POST'])
@login_required
def create_checkout_session():
    data = json.loads(request.data)

    try:
        success_url = f"https://{current_config.DOMAIN}{url_for('payments_blueprint.success')}"
        cancel_url = f"https://{current_config.DOMAIN}{url_for('payments_blueprint.cancel')}"
        checkout_session_params = dict(
            success_url=success_url + "?session_id={CHECKOUT_SESSION_ID}",
            cancel_url=cancel_url,
            payment_method_types=['card'],
            mode='subscription',
            line_items=[{
                'price': data['priceId'],
                'quantity': 1
            }]
        )
        if TRIAL_DAYS >= 1:
            checkout_session_params["subscription_data"] = {"trial_period_days": TRIAL_DAYS}
        checkout_session = stripe.checkout.Session.create(**checkout_session_params)
        return jsonify({'sessionId': checkout_session['id']})
    except Exception as e:
        return jsonify({'error': {'message': str(e)}}), 400


@payments_blueprint.route('/webhook', methods=['POST'])
def webhook_received():
    webhook_secret = current_config.STRIPE_ENDPOINT_KEY
    request_data = json.loads(request.data)

    if webhook_secret:
        signature = request.headers.get('stripe-signature')
        try:
            event = stripe.Webhook.construct_event(
                payload=request.data, sig_header=signature, secret=webhook_secret)
            data = event['data']
        except Exception as e:
            return e
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
    elif event_type == 'invoice.payment_action_required':
        print(data)
    elif event_type == 'customer.subscription.trial_will_end':
        print(data)
    elif event_type == 'customer.subscription.updated':
        # track statuses past_due, cancelled, unpaid
        print(data)
    else:
        print('Unhandled event type {}'.format(event_type))

    return jsonify({'status': 'success'})


@payments_blueprint.route('/customer-portal', methods=['POST'])
@login_required
def customer_portal():
    # This is the URL to which the customer will be redirected after they are
    # done managing their billing with the portal.
    return_url = os.getenv("DOMAIN")  # TODO

    session = stripe.billing_portal.Session.create(
        customer='{{CUSTOMER_ID}}',
        return_url=return_url)
    return jsonify({'url': session.url})
