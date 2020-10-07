from flask import current_app
from requests_oauthlib import OAuth2Session

from life_scheduler import db
from life_scheduler.google.api import GoogleAPISession


class Google(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    token = db.Column(db.JSON, nullable=False)
    email = db.Column(db.String(256))

    user_id = db.Column(db.Integer, db.ForeignKey("user.id"), nullable=False)
    user = db.relationship("User", backref="googles")

    def __init__(self, token=None, email=None, user=None):
        self.token = token
        self.email = email

        self.user = user

    def __str__(self):
        return f"{self.email}@Google"

    def get_raw_session(self, **kwargs):
        client_id = current_app.config["GOOGLE_CLIENT_ID"]
        client_secret = current_app.config["GOOGLE_CLIENT_SECRET"]
        refresh_url = "https://oauth2.googleapis.com/token"

        refresh_kwargs = {
            "client_id": client_id,
            "client_secret": client_secret,
        }

        return OAuth2Session(
            client_id=client_id,
            token=self.token,
            token_updater=self.update_token,
            auto_refresh_url=refresh_url,
            auto_refresh_kwargs=refresh_kwargs,
            **kwargs
        )

    def update_token(self, token):
        self.token = token
        db.session.commit()

    def get_session(self):
        return GoogleAPISession(self.get_raw_session())

    @classmethod
    def create(cls, google):
        db.session.add(google)
        db.session.commit()

    @classmethod
    def remove(cls, google):
        from life_scheduler.board.models import QuestSource
        sources = QuestSource.query.filter_by(backend_type="google", backend_id=google.id).all()
        for source in sources:
            db.session.delete(source)

        db.session.delete(google)
        db.session.commit()

    @classmethod
    def get_by_id(cls, i):
        return cls.query.get(i)
