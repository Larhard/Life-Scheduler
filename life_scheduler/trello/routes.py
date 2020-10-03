from datetime import timedelta, datetime
from urllib.parse import parse_qs

import requests
from flask import Blueprint, current_app, request, url_for, redirect
from flask_login import login_required, current_user
from requests_oauthlib import OAuth1

from life_scheduler.auth.utils import approval_required
from life_scheduler.trello.models import Trello, TrelloTemporaryToken

blueprint = Blueprint("trello", __name__, url_prefix="/trello")


@blueprint.route("/login")
@login_required
@approval_required
def login():
    token_request_url = current_app.config["TRELLO_TOKEN_REQUEST_URL"]
    authorization_url = current_app.config["TRELLO_TOKEN_AUTHORIZATION_URL"]

    token = TrelloTemporaryToken(
        user=current_user,
        expires=datetime.utcnow() + timedelta(days=1),
    )
    response = requests.post(url=token_request_url, auth=token.auth)
    data = parse_qs(response.content)

    oauth_token = data[b"oauth_token"][0].decode()
    oauth_token_secret = data[b"oauth_token_secret"][0].decode()

    token.token = oauth_token
    token.secret = oauth_token_secret

    TrelloTemporaryToken.create(token)

    data = {
        "oauth_token": oauth_token,
        "return_url": url_for("trello.login_callback", _external=True),
        "expiration": "never",
        "scope": "read,write",
    }
    r = requests.Request(
        "GET",
        authorization_url,
        params=data
    )
    uri = r.prepare().url

    return redirect(uri)


@blueprint.route("/login/callback")
def login_callback():
    oauth_token = request.args.get("oauth_token")
    oauth_verifier = request.args.get("oauth_verifier")

    client_key = current_app.config["TRELLO_API_KEY"]
    client_secret = current_app.config["TRELLO_API_SECRET"]
    access_token_request_url = current_app.config["TRELLO_ACCESS_TOKEN_REQUEST_URL"]

    temporary_token = TrelloTemporaryToken.get_by_token(oauth_token)

    oauth_secret = temporary_token.secret

    oauth = OAuth1(
        client_key=client_key,
        client_secret=client_secret,
        resource_owner_key=oauth_token,
        resource_owner_secret=oauth_secret,
        verifier=oauth_verifier,
    )

    response = requests.post(url=access_token_request_url, auth=oauth)
    data = parse_qs(response.content)

    oauth_token = data[b"oauth_token"][0].decode()
    oauth_token_secret = data[b"oauth_token_secret"][0].decode()

    trello = Trello(
        token=oauth_token,
        secret=oauth_token_secret,
        user=temporary_token.user,
    )
    print(trello.token)
    print(trello.secret)
    print(trello.user)
    Trello.create(trello)

    return redirect(url_for("board.index"))


@blueprint.route("/logout")
@login_required
@approval_required
def logout():
    Trello.remove(current_user.trello)
    return "OK"
