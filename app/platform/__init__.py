from flask import Blueprint
platform_blueprint = Blueprint('platform_blueprint', __name__)
from . import views
