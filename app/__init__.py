import traceback
from logging.config import dictConfig

from flask import Flask, render_template, current_app
from flask_login import LoginManager

from config import current_config
from app.user import User
from app.exceptions import TokenError, UserError, PaymentError, EmailProviderError

dictConfig({
    'version': 1,
    'formatters': {'default': {
        'format': '[%(asctime)s] %(levelname)s: %(message)s',
    }},
    'handlers': {'wsgi': {
        'class': 'logging.StreamHandler',
        'stream': 'ext://flask.logging.wsgi_errors_stream',
        'formatter': 'default'
    }},
    'root': {
        'level': 'INFO',
        'handlers': ['wsgi']
    }
})


def create_app():
    app = Flask(__name__, static_folder='static')
    app.config.from_object(current_config)
    current_config.init_app(app)
    login_manager = LoginManager()
    login_manager.init_app(app)
    login_manager.user_loader(User.load)
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

    from .email_callbacks import email_blueprint
    app.register_blueprint(email_blueprint, url_prefix='/email')

    app.register_error_handler(TokenError, error_handler)
    app.register_error_handler(UserError, error_handler)
    app.register_error_handler(PaymentError, error_handler)
    app.register_error_handler(EmailProviderError, error_handler)
    return app


def error_handler(e):
    current_app.logger.error(f"Handling application exception: {e}")
    traceback.print_exc()
    return render_template("msg.html", msg='Something went wrong! Try again later.')
