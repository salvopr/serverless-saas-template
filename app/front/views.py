from . import front_blueprint

from flask import render_template, send_from_directory, current_app


@front_blueprint.route('/', methods=["GET"])
def index():
    return render_template('landing.html')


@front_blueprint.route("/robots.txt", methods=["GET"])
def robots():
    return send_from_directory(current_app.static_folder, 'robots.txt')
