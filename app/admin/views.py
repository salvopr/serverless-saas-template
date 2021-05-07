from flask import abort
from flask_login import login_required, current_user
from . import admin_blueprint


@admin_blueprint.route("/", methods=["GET", "POST"])
@login_required
def index():
    if current_user.is_authenticated and current_user.is_admin:
        return 'this page is for platform owner'
    else:
        abort(401)
