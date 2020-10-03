import requests
from flask_login import current_user


def get(url):
    requests.Request(url)
    client = current_user.trello_oauth_token.get_oauth1_client()
    client.sign(url)