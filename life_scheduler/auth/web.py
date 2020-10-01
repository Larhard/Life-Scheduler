import requests
from flask import request, redirect, current_app
from flask.blueprints import Blueprint

from life_scheduler.auth.google import get_google_provider_config, get_google_oauth2_client

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

    userinfo_endpoint = provider_config["userinfo_endpoint"]
    uri, headers, body = oauth2_client.add_token(userinfo_endpoint)
    userinfo_response = requests.get(uri, headers=headers, data=body)

    userinfo = userinfo_response.json()

    if userinfo.get("email_verified"):
        return userinfo_response.content

    else:
        return "Failed to authenticate via Google", 400


@blueprint.route("/logout")
def logout():
    pass
