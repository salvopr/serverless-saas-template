import boto3
from botocore.exceptions import ClientError
from cryptography.fernet import Fernet

from config import current_config
from app.exceptions import UserError, UserDoesNotExists
from app.email import send_email


def load_user(user_id):
    user = User(user_id)
    user.load()
    return user


def decrypt(token):
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
        dynamodb = boto3.resource('dynamodb', region_name=current_config.AWS_REGION)
        self.table = dynamodb.Table(current_config.USERS_TABLE)

    def exists(self):
        try:
            response = self.table.get_item(Key={'email': self.email})
            if 'Item' in response:
                return True
        except ClientError:
            pass
        return False

    def load(self):
        try:
            response = self.table.get_item(Key={'email': self.email})
            user_data = response['Item']
            self.password_token = user_data["password_token"]
            self.activated = bool(user_data["activated"])
            self.is_admin = bool(user_data.get("is_admin", False))
            self.is_paying = bool(user_data.get("is_paying", False))
            self.stripe_customer_id = user_data.get("stripe_customer_id")
            self.subscription_status = user_data.get("subscription_status")
        except ClientError as e:
            raise UserError("Cannot load user data from DB " + e.response['Error']['Message']) from e
        except KeyError as e:
            raise UserDoesNotExists(f"User does not exists") from e

    def authenticate(self, password):
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
        self.update("activated", True)

    def register(self, password):
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
        try:
            f = Fernet(current_config.SECRET_KEY)
            token = f.encrypt(password.encode("ascii")).decode('ascii')
            self.update("password_token", token)
        except ClientError as e:
            raise UserError("Cannot reset user password " + e.response['Error']['Message']) from e

    def send_registration_email(self, token):
        send_email(self.email, "REGISTRATION", token=token)

    def send_password_reset_email(self, token):
        send_email(self.email, "PASSWORD_RESET", token=token)

    def update(self, param, value):
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
