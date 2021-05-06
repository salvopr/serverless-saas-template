from . import front_blueprint


@front_blueprint.route('/', methods=["POST"])
def new_event():
    return 'ok'
