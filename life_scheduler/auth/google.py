import requests

from flask import current_app
from oauthlib import oauth2


def get_google_provider_config():
    return requests.get(current_app.config["GOOGLE_DISCOVERY_URL"]).json()


def get_google_oauth2_client():
    return oauth2.WebApplicationClient(current_app.config["GOOGLE_CLIENT_ID"])
