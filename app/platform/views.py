from flask_login import login_required
from . import admin_blueprint


@admin_blueprint.route("/", methods=["GET", "POST"])
@login_required
def index():
    return 'ok'
