from . import front_blueprint


@front_blueprint.route('/', methods=["GET"])
def index():
    return 'this is landing page'
