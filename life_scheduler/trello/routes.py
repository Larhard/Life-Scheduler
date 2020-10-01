from flask import Blueprint, current_app
from flask_login import login_required

from life_scheduler.auth.utils import approval_required
from life_scheduler.trello.auth import get_oauth1_client

blueprint = Blueprint("trello", __name__, url_prefix="/trello")


@blueprint.route("/authenticate")
@login_required
@approval_required
def authenticate():
    client = get_oauth1_client()
    uri, headers, body = client.sign(current_app.config["TRELLO_AUTHORIZATION_URL"])

    return f"{uri};{headers};{body}"
