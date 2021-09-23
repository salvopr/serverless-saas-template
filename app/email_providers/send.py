from config import current_config

import boto3
from botocore.exceptions import ClientError

from app.exceptions import EmailProviderError
from app.email.templates import TEMPLATES


def send_email(user, template, render_params):
    """ Prepares an email to be sent via AWS SES """
    subject = TEMPLATES[template]["subject"].format(domain=current_config.DOMAIN)
    body = TEMPLATES[template]["body"].format(**render_params)
    if user.unsubscribed:
        raise EmailProviderError(f"Failed to send email to {user.email}\n user unsubscribed {user.unsubscribed}")
    try:
        client = boto3.client('ses')
        client.send_email(
            Source=f'notification@{current_config.DOMAIN}',
            Destination={
                'ToAddresses': [user.email]
            },
            Message={
                'Subject': {'Data': subject},
                'Body': {'Text': {'Data': body},
                         'Html': {'Data': body}
                         }
            }
        )

    except ClientError as e:
        raise EmailProviderError(f"Failed to send email to {user.email}\n{subject}\n{body}") from e
