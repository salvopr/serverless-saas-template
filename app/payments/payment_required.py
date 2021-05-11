from functools import wraps
from flask import redirect, url_for, flash
from flask_login import current_user


def payment_required(f):
    @wraps(f)
    def wrapper(*args, **kwargs):
        if not current_user.is_paying:
            flash("You don't have active payment plan!", "danger")
            return redirect(url_for("payments_blueprint.index"))
        return f(*args, **kwargs)
    return wrapper
