from flask import current_app
from oauthlib import oauth1


def get_oauth1_client():
    return oauth1.Client(
        current_app.config["TRELLO_API_KEY"],
        client_secret=current_app.config["TRELLO_API_SECRET"],
    )
