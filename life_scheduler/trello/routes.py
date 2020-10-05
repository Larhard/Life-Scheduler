from datetime import timedelta, datetime

from flask import Blueprint, current_app, request, url_for, redirect
from flask_login import login_required, current_user

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
    response = token.get_raw_session().fetch_request_token(token_request_url)

    oauth_token = response["oauth_token"]
    oauth_token_secret = response["oauth_token_secret"]

    token.token = oauth_token
    token.secret = oauth_token_secret

    TrelloTemporaryToken.create(token)

    url = token.get_raw_session().authorization_url(
        url=authorization_url,
        return_url=url_for("trello.login_callback", _external=True),
        expiration="never",
        scope="read,write",
    )

    return redirect(url)


@blueprint.route("/login/callback")
def login_callback():
    oauth_token = request.args.get("oauth_token")
    oauth_verifier = request.args.get("oauth_verifier")

    access_token_request_url = current_app.config["TRELLO_ACCESS_TOKEN_REQUEST_URL"]

    temporary_token = TrelloTemporaryToken.get_by_token(oauth_token)

    oauth = temporary_token.get_raw_session(verifier=oauth_verifier)

    response = oauth.fetch_access_token(access_token_request_url)

    oauth_token = response["oauth_token"]
    oauth_token_secret = response["oauth_token_secret"]

    trello = Trello(
        token=oauth_token,
        secret=oauth_token_secret,
        user=temporary_token.user,
    )
    Trello.create(trello)

    return redirect(url_for("board.index"))


@blueprint.route("/logout")
@login_required
@approval_required
def logout():
    Trello.remove(current_user.trello)
    return "OK"
