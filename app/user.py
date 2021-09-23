import boto3
from botocore.exceptions import ClientError
from cryptography.fernet import Fernet

from flask import url_for

from config import current_config
from app.exceptions import UserError, UserDoesNotExists
from app.email_providers.send import send_email
from app.email_providers.templates import EmailTemplateNames
from app.events import EventTypes, new_event


def decrypt(token):
    """ decrypts a password stored in DB """
    try:
        f = Fernet(current_config.SECRET_KEY)
        return f.decrypt(token.encode('ascii'))
    except Exception as e:
        raise UserError(f"Decrypt exception for user data {token} {e}") from e


class User:
    def __init__(self, email):
        self.email = email
        self.password_token = None
        self.activated = False
        self.is_admin = False
        self.is_paying = False
        self.subscription_status = None
        self.stripe_customer_id = None
        self.unsubscribed = None
        dynamodb = boto3.resource('dynamodb', region_name=current_config.AWS_REGION)
        self.table = dynamodb.Table(current_config.USERS_TABLE)

    @classmethod
    def load(cls, user_id):
        """ Constructs a user object by email """
        user = cls(user_id)
        user._load_from_db()
        new_event(EventTypes.ACTIVITY, user.email)
        return user

    def exists(self):
        """ Check is a user exists in DynamoDB users table """
        try:
            response = self.table.get_item(Key={'email': self.email})
            if 'Item' in response:
                return True
        except ClientError:
            pass
        return False

    def _load_from_db(self):
        """ Loads user data from DynamoDB users table """
        try:
            response = self.table.get_item(Key={'email': self.email})
            user_data = response['Item']
            self.password_token = user_data["password_token"]
            self.activated = bool(user_data["activated"])
            self.is_admin = bool(user_data.get("is_admin", False))
            self.is_paying = bool(user_data.get("is_paying", False))
            self.stripe_customer_id = user_data.get("stripe_customer_id")
            self.subscription_status = user_data.get("subscription_status", "Not started")
            self.unsubscribed = user_data.get("unsubscribed")
        except ClientError as e:
            raise UserError("Cannot load user data from DB " + e.response['Error']['Message']) from e
        except KeyError as e:
            raise UserDoesNotExists(f"User does not exists {self.email}") from e

    def authenticate(self, password):
        """ Checks user's password """
        if self.password_token:
            return password == decrypt(self.password_token).decode('ascii')
        else:
            return False

    @property
    def is_authenticated(self):
        return True

    @property
    def is_active(self):
        return True

    @property
    def is_anonymous(self):
        return False

    def get_id(self):
        return self.email

    def activate(self):
        """ Flips activated field for a user to True"""
        self._update("activated", True)

    def unsubscribe(self, reason):
        """ Flips activated field for a user to True"""
        self._update("unsubscribed", reason)

    def register(self, password):
        """ Stores a new user in DynamoDB users table"""
        try:
            f = Fernet(current_config.SECRET_KEY)
            token = f.encrypt(password.encode("ascii")).decode('ascii')
            if not self.exists():
                self.table.put_item(
                    Item={"email": self.email,
                          "password_token": token,
                          "activated": False}
                )
        except ClientError as e:
            raise UserError("Cannot register user password " + e.response['Error']['Message']) from e

    def reset_password(self, password):
        """ Puts new password for a user in DynamoDB users table """
        try:
            f = Fernet(current_config.SECRET_KEY)
            token = f.encrypt(password.encode("ascii")).decode('ascii')
            self._update("password_token", token)
        except ClientError as e:
            raise UserError("Cannot reset user password " + e.response['Error']['Message']) from e

    def send_password_reset_email(self, token):
        """ Sends an email with password reset instructions """
        url = f"https://{current_config.DOMAIN}{url_for('auth_blueprint.password_reset', token=token)}"
        send_email(self, EmailTemplateNames.PASSWORD_RESET,
                   render_params={
                       "url": url
                   })

    def send_activation_email(self, token):
        """ Sends an email with activation instructions """
        url = f"https://{current_config.DOMAIN}{url_for('auth_blueprint.activate', token=token)}"
        send_email(self, EmailTemplateNames.REGISTRATION,
                   render_params={
                       "url": url
                   })

    def _update(self, param, value):
        """ Updates a field in database and in the object attributes """
        try:
            self.table.update_item(
                Key={
                    'email': self.email
                },
                UpdateExpression=f"set {param}=:a",
                ExpressionAttributeValues={
                    ':a': value
                },
                ReturnValues="UPDATED_NEW"
            )
            setattr(self, param, value)
        except ClientError as e:
            raise UserError("Cannot update user data from DB " + e.response['Error']['Message']) from e

    def checkout_completed(self, stripe_customer_id):
        """ Process an event of completing a payment with Stripe """
        self._update("subscription_status", "checkout_completed")
        self._update("is_paying", True)
        self._update("stripe_customer_id", stripe_customer_id)

    def invoice_paid(self):
        """ Process an event of getting new invoice paid with Stripe """
        self._update("subscription_status", "invoice_paid")
        self._update("is_paying", True)

    def invoice_payment_failed(self):
        """ Process an event of failed payment with Stripe """
        self._update("subscription_status", "invoice_payment_failed")
        self._update("is_paying", False)
        send_email(self, EmailTemplateNames.PAYMENT_PROBLEM,
                   render_params={
                       "subscription_status": "invoice_payment_failed",
                       "payment_console": f"https://{current_config.DOMAIN}{url_for('payments_blueprint.index')}"
                   })

    def payment_action_required(self):
        """ Notify a user when something needs to be done manually to continue with payment """
        self._update("subscription_status", "payment_action_required")
        self._update("is_paying", False)
        send_email(self, EmailTemplateNames.PAYMENT_PROBLEM,
                   render_params={
                       "subscription_status": "payment_action_required",
                       "payment_console": f"https://{current_config.DOMAIN}{url_for('payments_blueprint.index')}"
                   })

    def trial_end(self):
        """ Notify a user when a trial ends """
        send_email(self, EmailTemplateNames.TRIAL_END,
                   render_params={
                       "payment_console": f"https://{current_config.DOMAIN}{url_for('payments_blueprint.index')}"
                   })

    def subscription_invalid(self, status):
        """ Process an event when subscription has invalid status """
        self._update("subscription_status", status)
        self._update("is_paying", False)
        send_email(self, EmailTemplateNames.PAYMENT_PROBLEM,
                   render_params={
                       "subscription_status": status,
                       "payment_console": f"https://{current_config.DOMAIN}{url_for('payments_blueprint.index')}"
                   })

    def subscription_deleted(self):
        """ Process an event of deleting a subscription in Stripe """
        self._update("subscription_status", "deleted")
        self._update("is_paying", False)
        send_email(self, EmailTemplateNames.SUBSCRIPTION_DELETED,
                   render_params={
                       "payment_console": f"https://{current_config.DOMAIN}{url_for('payments_blueprint.index')}"
                   })

    def subscription_default_event(self, status):
        """ Process an unknown event from Stripe """
        self._update("subscription_status", status)
