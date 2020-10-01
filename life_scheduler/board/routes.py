from flask import Blueprint
from flask_login import login_required

from life_scheduler.auth.utils import approval_required

blueprint = Blueprint("board", __name__)


@blueprint.route("/")
@login_required
@approval_required
def index():
    return "OK"
