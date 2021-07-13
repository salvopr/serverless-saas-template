from functools import wraps
from flask import redirect, url_for, flash
from flask_login import current_user


def payment_required(f):
    """ Decorate view that require your users to have
    active subscription with this decorator """
    @wraps(f)
    def wrapper(*args, **kwargs):
        if current_user.is_admin:
            return redirect(url_for("admin_blueprint.index"))
        if not current_user.is_paying:
            flash("You don't have active payment plan!", "danger")
            return redirect(url_for("payments_blueprint.index"))
        return f(*args, **kwargs)
    return wrapper
