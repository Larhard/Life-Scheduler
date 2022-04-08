import os
from distutils.util import strtobool

import life_scheduler.utils.git
from constants import *

basedir = os.path.abspath(os.path.dirname(__file__))


class Config:
    VERSION = life_scheduler.utils.git.get_revision_hash()

    SECRET_KEY = os.getenv("SECRET_KEY") or os.urandom(24)

    GOOGLE_CLIENT_ID = os.getenv("GOOGLE_CLIENT_ID")
    GOOGLE_CLIENT_SECRET = os.getenv("GOOGLE_CLIENT_SECRET")
    GOOGLE_DISCOVERY_URL = "https://accounts.google.com/.well-known/openid-configuration"

    TRELLO_API_KEY = os.getenv("TRELLO_API_KEY")
    TRELLO_API_SECRET = os.getenv("TRELLO_API_SECRET")
    TRELLO_TOKEN_REQUEST_URL = "https://trello.com/1/OAuthGetRequestToken"
    TRELLO_TOKEN_AUTHORIZATION_URL = "https://trello.com/1/OAuthAuthorizeToken"
    TRELLO_ACCESS_TOKEN_REQUEST_URL = "https://trello.com/1/OAuthGetAccessToken"

    SQLALCHEMY_DATABASE_URI = os.getenv("DATABASE_URL") or "sqlite:///" + os.path.join(basedir, "db.sqlite3")
    SQLALCHEMY_TRACK_MODIFICATIONS = False

    DEBUG_FAST_LOGIN = os.getenv("DEBUG_FAST_LOGIN")

    FEATURE_FLAGS = {
        FEATURE_NAVIGATION_ON_BOARD: strtobool(os.getenv(FEATURE_NAVIGATION_ON_BOARD, "False")),
        FEATURE_NAVIGATION_VISIBLE_BY_DEFAULT: strtobool(os.getenv(FEATURE_NAVIGATION_VISIBLE_BY_DEFAULT, "False")),
        FEATURE_POSTPONE: strtobool(os.getenv(FEATURE_POSTPONE, "False")),
        FEATURE_SCHEDULER: strtobool(os.getenv(FEATURE_SCHEDULER, "False")),
    }

