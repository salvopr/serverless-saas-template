class UserError(Exception):
    pass


class UserDoesNotExists(UserError):
    pass


class TokenError(Exception):
    pass
