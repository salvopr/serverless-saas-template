from flask import Blueprint
auth_blueprint = Blueprint('auth_blueprint', __name__)
from . import views
