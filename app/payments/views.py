import json

import stripe
from flask import request, jsonify, redirect, url_for, flash, render_template, current_app
from flask_login import login_required, current_user

from . import payments_blueprint
from config import current_config
from app.payments.plans import get_prices_from_stripe, TRIAL_DAYS
from app.user import User
from app.exceptions import PaymentError
from app.events import EventTypes, new_event

stripe.api_key = current_config.STRIPE_SEC_KEY


@payments_blueprint.route('/', methods=["GET"])
@login_required
def index():
    """ Serves a page for payment management """
    payment_plans = get_prices_from_stripe()
    return render_template('payments/index.html', payment_plans=payment_plans)


@payments_blueprint.route('/success', methods=["GET"])
@login_required
def success():
    """ Users are redirected to this page after successful purchase """
    # TODO test me
    flash("Payment succeeded! Provisioning subscription.", "success")
    return redirect(url_for("payments_blueprint.index"))


@payments_blueprint.route('/cancel', methods=["GET"])
@login_required
def cancel():
    """ Users are redirected to this page after cancelled purchase """
    # TODO test me
    flash("Payment canceled!", "warning")
    return redirect(url_for("payments_blueprint.index"))


@payments_blueprint.route('/create-checkout-session', methods=['POST'])
@login_required
def create_checkout_session():
    """ AJAX called when a users initiates payment.
    Returns a URL for Stripe Checkout """
    data = json.loads(request.data)
    try:
        success_url = f"https://{current_config.DOMAIN}{url_for('payments_blueprint.success')}"
        cancel_url = f"https://{current_config.DOMAIN}{url_for('payments_blueprint.cancel')}"
        checkout_session_params = dict(
            customer_email=current_user.email,
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
        current_app.logger.info(f'New Stripe payment session {checkout_session["id"]}')
        return jsonify({'sessionId': checkout_session['id']})
    except Exception as e:
        raise PaymentError(f"cannot create checkout session - {e}") from e


def webhook_data(webhook_request_data):
    """ Decrypts a webhook data received from Stripe """
    webhook_secret = current_config.STRIPE_ENDPOINT_KEY

    if webhook_secret:
        signature = webhook_request_data.headers.get('stripe-signature')
        try:
            event = stripe.Webhook.construct_event(
                payload=webhook_request_data.data,
                sig_header=signature,
                secret=webhook_secret
            )
            data = event['data']
        except Exception as e:
            raise PaymentError("cannot decode webhook request") from e
        event_type = event['type']
    else:
        request_data = json.loads(webhook_request_data.data)
        data = request_data['data']
        event_type = request_data['type']

    data_object = data['object']
    return event_type, data_object


def find_webhook_user(data_object):
    """ Extracts user information from a webhook data """
    if 'customer_email' in data_object:  # checkout session or invoice events
        email = data_object['customer_email']
    else:  # applied to subscription data object that has only customer ID
        customer = stripe.Customer.retrieve(data_object["customer"])
        email = customer['email']

    user = User.load(email)
    return user


@payments_blueprint.route('/webhook', methods=['POST'])
def webhook_received():
    """ Process async webhook events sent by Stripe """
    event_type, data_object = webhook_data(request)
    user = find_webhook_user(data_object)
    current_app.logger.info(f'New Stripe event {event_type} for user {user.email}')

    if event_type == 'checkout.session.completed':
        user.checkout_completed(data_object['customer'])

    elif event_type == 'invoice.paid':
        user.invoice_paid()
        new_event(EventTypes.PAYMENT, user.email, values={"amount_paid": data_object["amount_paid"]})

    elif event_type == 'invoice.payment_failed':
        user.invoice_payment_failed()

    elif event_type == 'invoice.payment_action_required':
        user.payment_action_required()

    elif event_type == 'customer.subscription.trial_will_end':
        user.trial_end()

    elif event_type == 'customer.subscription.updated' and data_object["status"] in ("past_due", "canceled", "unpaid"):
        user.subscription_invalid(data_object["status"])
        if data_object["status"] == "canceled":
            new_event(EventTypes.CHURN, user.email)
    elif event_type == 'customer.subscription.deleted':
        user.subscription_deleted()
        new_event(EventTypes.CHURN, user.email)
    else:
        # TODO test me
        user.subscription_default_event(event_type)
        current_app.logger.warning(f'Unhandled event type {event_type}\n{data_object}')

    return jsonify({'status': 'success'})


@payments_blueprint.route('/customer-portal', methods=['POST'])
@login_required
def customer_portal():
    """ When a user wants to manage thier subscriptions and AJAX call
    return a Stripe URL to do that """
    session = stripe.billing_portal.Session.create(
        customer=current_user.stripe_customer_id,
        return_url=f"https://{current_config.DOMAIN}{url_for('payments_blueprint.index')}")
    current_app.logger.info(f'New customer portal session started {session.url}')
    return jsonify({'url': session.url})
