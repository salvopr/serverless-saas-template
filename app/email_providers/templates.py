from enum import Enum


class EmailTemplateNames(Enum):
    """ Types of emails """
    REGISTRATION = 'REGISTRATION'
    PASSWORD_RESET = "PASSWORD_RESET"
    PAYMENT_PROBLEM = "PAYMENT_PROBLEM"
    TRIAL_END = "TRIAL_END"
    SUBSCRIPTION_DELETED = "SUBSCRIPTION_DELETED"


# A dict with email templates
TEMPLATES = {EmailTemplateNames.REGISTRATION: {"subject": "Successful registration at {domain}",
                                               "body": ("You have been registered. "
                                                        "Follow this link to activate your account {url}")},
             EmailTemplateNames.PASSWORD_RESET:
                 {"subject": "Password reset request from {domain}",
                  "body": ("You have asked for a password reset. "
                           "Follow this link to reset your password {url}"),
                  },
             EmailTemplateNames.PAYMENT_PROBLEM:
                 {"subject": "Payment problem at {domain}",
                  "body": ("Payment provider notified us about payment problem for you account. "
                           "Your subscription status is {subscription_status}. "
                           "Open a payment console to fix that {payment_console}"),
                  },
             EmailTemplateNames.TRIAL_END:
                 {"subject": "Your trial at {domain} will end soon",
                  "body": ("Payment provider notified us about the end of your trial period. "
                           "Open a payment console to manage your billing {payment_console}"),
                  },
             EmailTemplateNames.SUBSCRIPTION_DELETED:
                 {"subject": "Your subscription at {domain} is deleted",
                  "body": ("Payment provider notified us that the subscription is cancelled. "
                           "Open a payment console to manage your billing {payment_console}"),
                  }
             }
