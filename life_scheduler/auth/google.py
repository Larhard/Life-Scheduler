import requests

from flask import current_app


def get_google_provider_config():
    return requests.get(current_app.config["GOOGLE_DISCOVERY_URL"]).json()
