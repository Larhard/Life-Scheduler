from datetime import datetime

import dateutil.parser

from flask import Blueprint, current_app, url_for, session, redirect, request
from flask_login import login_required, current_user
from requests_oauthlib import OAuth2Session

from life_scheduler.auth.google import get_google_provider_config
from life_scheduler.auth.utils import approval_required
from life_scheduler.google.models import Google

blueprint = Blueprint("google", __name__, url_prefix="/google")


@blueprint.route("/login")
@login_required
@approval_required
def login():
    provider_config = get_google_provider_config()
    authorization_url = provider_config["authorization_endpoint"]

    client_id = current_app.config["GOOGLE_CLIENT_ID"]
    scope = [
        "https://www.googleapis.com/auth/calendar",
    ]
    redirect_uri = url_for("google.login_callback", _external=True)

    oauth = OAuth2Session(
        client_id=client_id,
        scope=scope,
        redirect_uri=redirect_uri,
    )

    url, state = oauth.authorization_url(
        url=authorization_url,
        access_type="offline",
        prompt="consent",
    )

    current_app.logger.info(f"url = {url}")

    session["oauth_state"] = state
    return redirect(url)


@blueprint.route("/login/callback")
def login_callback():
    code = request.args.get("code")

    provider_config = get_google_provider_config()
    token_url = provider_config["token_endpoint"]

    client_id = current_app.config["GOOGLE_CLIENT_ID"]
    client_secret = current_app.config["GOOGLE_CLIENT_SECRET"]

    oauth = OAuth2Session(
        client_id=client_id,
        state=session["oauth_state"],
        redirect_uri=request.base_url,
    )

    token = oauth.fetch_token(
        token_url=token_url,
        client_secret=client_secret,
        authorization_response=request.url,
        code=code,
    )

    print(token.keys())
    print(token)

    google = Google(
        access_token=token["access_token"],
        refresh_token=token["refresh_token"],
        token_type=token["token_type"],
        expires_at=datetime.fromtimestamp(token["expires_at"]),
        user=current_user,
    )

    Google.create(google)

    return redirect(url_for("board.settings"))
