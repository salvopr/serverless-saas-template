class UserError(Exception):
    pass


class UserDoesNotExists(UserError):
    pass


class TokenError(Exception):
    pass


class PaymentError(Exception):
    pass


class EmailProviderError(Exception):
    pass
