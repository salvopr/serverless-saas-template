TEMPLATES = {"REGISTRATION": "",
             "PASSWORD_RESET": ""}


def send_email(email, template, token=None):
    print(email, template, token)
