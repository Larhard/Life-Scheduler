import os

import life_scheduler.utils.git


class Config:
    VERSION = life_scheduler.utils.git.get_revision_hash()

    SECRET_KEY = os.getenv("SECRET_KEY") or os.urandom(24)

    GOOGLE_CLIENT_ID = os.getenv("GOOGLE_CLIENT_ID")
    GOOGLE_CLIENT_SECRET = os.getenv("GOOGLE_CLIENT_SECRET")
    GOOGLE_DISCOVERY_URL = (
        "https://accounts.google.com/.well-known/openid-configuration"
    )
