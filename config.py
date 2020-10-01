import os

import life_scheduler.utils.git

basedir = os.path.abspath(os.path.dirname(__file__))


class Config:
    VERSION = life_scheduler.utils.git.get_revision_hash()

    SECRET_KEY = os.getenv("SECRET_KEY") or os.urandom(24)

    GOOGLE_CLIENT_ID = os.getenv("GOOGLE_CLIENT_ID")
    GOOGLE_CLIENT_SECRET = os.getenv("GOOGLE_CLIENT_SECRET")
    GOOGLE_DISCOVERY_URL = "https://accounts.google.com/.well-known/openid-configuration"

    SQLALCHEMY_DATABASE_URI = os.getenv("DATABASE_URL") or "sqlite:///" + os.path.join(basedir, "db.sqlite3")
    SQLALCHEMY_TRACK_MODIFICATIONS = False
