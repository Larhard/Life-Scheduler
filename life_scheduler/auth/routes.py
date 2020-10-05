import click
from flask import request, redirect, current_app, url_for, session
from flask.blueprints import Blueprint
from flask_login import login_user, logout_user
from requests_oauthlib import OAuth2Session

from life_scheduler import login_manager
from life_scheduler.auth.google import get_google_provider_config
from life_scheduler.auth.models import User

blueprint = Blueprint("auth", __name__)


@blueprint.route("/login")
def login():
    debug_fast_login = current_app.config["DEBUG_FAST_LOGIN"]
    if debug_fast_login:
        user = User.get_by_email(debug_fast_login)
        if user:
            login_user(user)
            return redirect(url_for("board.index"))

    provider_config = get_google_provider_config()
    authorization_url = provider_config["authorization_endpoint"]

    client_id = current_app.config["GOOGLE_CLIENT_ID"]
    scope = ["openid", "email", "profile"]
    redirect_uri = url_for("auth.login_callback", _external=True)

    oauth = OAuth2Session(
        client_id=client_id,
        scope=scope,
        redirect_uri=redirect_uri,
    )

    url, state = oauth.authorization_url(authorization_url)

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

    oauth.fetch_token(
        token_url=token_url,
        client_secret=client_secret,
        authorization_response=request.url,
        code=code,
    )

    user_info_url = provider_config["userinfo_endpoint"]
    user_info = oauth.get(user_info_url).json()

    if user_info.get("email_verified"):
        user = {
            "email": user_info["email"],
            "name": user_info["name"],
            "given_name": user_info["given_name"],
            "family_name": user_info["family_name"],
            "picture": user_info["picture"],
        }

        user = User.get_or_create(user)

        current_app.logger.info(f"User logged in: {user}")
        login_user(user)
        return redirect(url_for("board.index"))

    else:
        return "Failed to authenticate via Google", 400


@blueprint.route("/logout")
def logout():
    logout_user()
    return redirect(url_for("board.index"))


@login_manager.unauthorized_handler
def unauthorized_handler():
    return redirect(url_for("auth.login"))


@blueprint.cli.command("approve")
@click.argument("email")
def approve(email):
    user = User.get_by_email(email)
    user.set_approved(True)


@blueprint.cli.command("block")
@click.argument("email")
def block(email):
    user = User.get_by_email(email)
    user.set_approved(False)
