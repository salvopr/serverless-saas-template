from flask import Blueprint

email_blueprint = Blueprint('email_blueprint', __name__)
from . import views
