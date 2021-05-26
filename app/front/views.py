from . import front_blueprint

from flask import render_template


@front_blueprint.route('/', methods=["GET"])
def index():
    return render_template('landing.html')
