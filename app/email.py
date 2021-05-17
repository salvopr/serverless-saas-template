TEMPLATES = {"REGISTRATION": "",
             "PASSWORD_RESET": "",
             "PAYMENT_PROBLEM": "",
             "TRIAL_END": ""}


def send_email(email, template, token=None):
    print(email, template, token)
