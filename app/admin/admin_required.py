from functools import wraps
from flask import redirect, url_for, flash
from flask_login import current_user


def admin_required(f):
    """ Decorator that protects views available only to platform owner """
    @wraps(f)
    def wrapper(*args, **kwargs):
        if not (current_user.is_authenticated and current_user.is_admin):
            flash("Need admin right to access this page!", "danger")
            return redirect(url_for("auth_blueprint.login"))
        return f(*args, **kwargs)
    return wrapper
