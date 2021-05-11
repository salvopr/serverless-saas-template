from flask_login import login_required
from . import admin_blueprint
from app.admin.admin_required import admin_required


@admin_blueprint.route("/", methods=["GET", "POST"])
@login_required
@admin_required
def index():
    return 'this page is for platform owner'
