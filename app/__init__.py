import traceback

from flask import Flask, render_template
from flask_login import LoginManager

from config import current_config
from app.user import load_user
from app.exceptions import TokenError, UserError, PaymentError


def create_app():
    app = Flask(__name__)
    app.config.from_object(current_config)
    current_config.init_app(app)
    login_manager = LoginManager()
    login_manager.init_app(app)
    login_manager.user_loader(load_user)
    login_manager.login_view = "auth_blueprint.login"

    from .front import front_blueprint
    app.register_blueprint(front_blueprint, url_prefix='/')

    from .auth import auth_blueprint
    app.register_blueprint(auth_blueprint, url_prefix='/auth')

    from .admin import admin_blueprint
    app.register_blueprint(admin_blueprint, url_prefix='/admin')

    from .platform import platform_blueprint
    app.register_blueprint(platform_blueprint, url_prefix='/platform')

    from .payments import payments_blueprint
    app.register_blueprint(payments_blueprint, url_prefix='/payments')

    app.register_error_handler(TokenError, error_handler)
    app.register_error_handler(UserError, error_handler)
    app.register_error_handler(PaymentError, error_handler)
    return app


def error_handler(e):
    print(f"Application exception {e}")
    traceback.print_tb(e.__traceback__)
    return render_template("msg.html", msg=str(e))
