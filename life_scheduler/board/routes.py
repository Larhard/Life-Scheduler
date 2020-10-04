from flask import Blueprint
from flask_login import login_required, current_user

from life_scheduler.auth.utils import approval_required

blueprint = Blueprint("board", __name__)


@blueprint.route("/")
@login_required
@approval_required
def index():
    oauth = current_user.trello.get_session()
    return oauth.get("https://trello.com/1/members/me/boards/").content
