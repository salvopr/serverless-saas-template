from flask import Blueprint

payments_blueprint = Blueprint('payments_blueprint', __name__)
from . import views
