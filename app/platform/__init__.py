from flask import Blueprint
admin_blueprint = Blueprint('admin_blueprint', __name__)
from . import views
