import click
import requests
from flask import request, redirect, current_app, url_for
from flask.blueprints import Blueprint
from flask_login import login_user, logout_user, current_user

from life_scheduler.auth.google import get_google_provider_config, get_google_oauth2_client
from life_scheduler.auth.models import User

blueprint = Blueprint("auth", __name__)


@blueprint.route("/login")
def login():
    provider_config = get_google_provider_config()
    authorization_endpoint = provider_config["authorization_endpoint"]
    oauth2_client = get_google_oauth2_client()

    request_uri = oauth2_client.prepare_request_uri(
        authorization_endpoint,
        redirect_uri=request.base_url + "/callback",
        scope=["openid", "email", "profile"],
    )
    return redirect(request_uri)


@blueprint.route("/login/callback")
def login_callback():
    code = request.args.get("code")

    provider_config = get_google_provider_config()
    token_endpoint = provider_config["token_endpoint"]

    oauth2_client = get_google_oauth2_client()
    google_client_id = current_app.config["GOOGLE_CLIENT_ID"]
    google_client_secret = current_app.config["GOOGLE_CLIENT_SECRET"]

    token_url, headers, body = oauth2_client.prepare_token_request(
        token_endpoint,
        authorization_response=request.url,
        redirect_url=request.base_url,
        code=code,
    )

    response = requests.post(
        token_url,
        headers=headers,
        data=body,
        auth=(google_client_id, google_client_secret),
    )

    oauth2_client.parse_request_body_response(response.content)

    user_info_endpoint = provider_config["userinfo_endpoint"]
    uri, headers, body = oauth2_client.add_token(user_info_endpoint)
    user_info_response = requests.get(uri, headers=headers, data=body)

    user_info = user_info_response.json()

    if user_info.get("email_verified"):
        user = User(
            email=user_info["email"],
            name=user_info["name"],
            given_name=user_info["given_name"],
            family_name=user_info["family_name"],
            picture=user_info["picture"],
        )

        user = User.get_or_create(user)

        login_user(user)
        return redirect(url_for("board.index"))

    else:
        return "Failed to authenticate via Google", 400


@blueprint.route("/logout")
def logout():
    logout_user()
    return redirect(url_for("board.index"))


@blueprint.cli.command("approve")
@click.argument("email")
def approve(email):
    user = User(email=email)
    user = User.get(user)
    user.set_approved(True)


@blueprint.cli.command("block")
@click.argument("email")
def block(email):
    user = User(email=email)
    user = User.get(user)
    user.set_approved(False)
