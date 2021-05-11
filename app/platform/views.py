from flask_login import login_required
from . import platform_blueprint
from app.payments.payment_required import payment_required


@platform_blueprint.route("/", methods=["GET", "POST"])
@login_required
@payment_required
def index():
    return 'this page is for platform user with active payment plan'
