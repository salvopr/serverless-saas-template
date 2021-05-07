from flask_login import login_required
from . import platform_blueprint


@platform_blueprint.route("/", methods=["GET", "POST"])
@login_required
def index():
    return 'this page is for platform user'
