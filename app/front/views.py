from . import front_blueprint


@front_blueprint.route('/', methods=["POST"])
def index():
    return 'this is landing page'
