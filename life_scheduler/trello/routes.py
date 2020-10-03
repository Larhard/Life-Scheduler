from datetime import timedelta, datetime
from urllib.parse import parse_qs

import requests

from flask import Blueprint, current_app, request, url_for, redirect
from flask_login import login_required, current_user

from life_scheduler.auth.utils import approval_required
from life_scheduler.trello.auth import get_oauth1_client
from life_scheduler.trello.models import Trello, TrelloTemporaryToken

blueprint = Blueprint("trello", __name__, url_prefix="/trello")


@blueprint.route("/login")
@login_required
@approval_required
def login():
    client = get_oauth1_client()
    uri, headers, body = client.sign(current_app.config["TRELLO_TOKEN_REQUEST_URL"])

    response = requests.get(uri, headers=headers, data=body)
    data = parse_qs(response.content)

    oauth_token = data[b"oauth_token"][0].decode()
    oauth_token_secret = data[b"oauth_token_secret"][0].decode()

    token = TrelloTemporaryToken(
        token=oauth_token,
        secret=oauth_token_secret,
        user=current_user,
        expires=datetime.utcnow() + timedelta(days=1),
    )
    Trello.create(token)

    data = {
        "oauth_token": oauth_token,
        "return_url": url_for("trello.login_callback", _external=True),
        "expiration": "never",
        "scope": "read,write",
    }
    r = requests.Request(
        "GET",
        current_app.config["TRELLO_TOKEN_AUTHORIZATION_URL"],
        params=data
    )
    uri = r.prepare().url

    return redirect(uri)


@blueprint.route("/login/callback")
@login_required
@approval_required
def login_callback():
    oauth_token = request.args.get("oauth_token")
    oauth_verifier = request.args.get("oauth_verifier")

    client = get_oauth1_client()

    temporary_token = TrelloTemporaryToken.get_by_token(oauth_token)
    client.resource_owner_key = temporary_token.token
    client.resource_owner_secret = temporary_token.secret
    client.verifier = oauth_verifier

    uri, headers, body = client.sign(current_app.config["TRELLO_ACCESS_TOKEN_REQUEST_URL"])
    response = requests.get(uri, headers=headers, data=body)
    data = parse_qs(response.content)

    oauth_token = data[b"oauth_token"][0].decode()
    oauth_token_secret = data[b"oauth_token_secret"][0].decode()

    trello = Trello(
        token=oauth_token,
        secret=oauth_token_secret,
        user=temporary_token.user,
    )
    Trello.create(trello)

    return redirect(url_for("board.index"))
