from flask import Blueprint
front_blueprint = Blueprint('front_blueprint', __name__)
from . import views
