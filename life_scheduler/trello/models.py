from flask import current_app
from requests_oauthlib import OAuth1Session

from life_scheduler import db
from life_scheduler.trello.api import TrelloAPISession


class Trello(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    token = db.Column(db.String(256), index=True, unique=True, nullable=False)
    secret = db.Column(db.String(256), nullable=False)
    username = db.Column(db.String(256))

    user_id = db.Column(db.Integer, db.ForeignKey("user.id"), nullable=False)
    user = db.relationship("User", backref="trellos")

    def __init__(self, token, secret, user, username=None):
        self.token = token
        self.secret = secret
        self.user = user
        self.username = username

    def get_raw_session(self, **kwargs):
        client_key = current_app.config["TRELLO_API_KEY"]
        client_secret = current_app.config["TRELLO_API_SECRET"]

        if client_key is None:
            raise ValueError("Unable to create Trello session: TRELLO_API_KEY is None")

        if client_secret is None:
            raise ValueError("Unable to create Trello session: TRELLO_API_SECRET is None")

        return OAuth1Session(
            client_key=client_key,
            client_secret=client_secret,
            resource_owner_key=self.token,
            resource_owner_secret=self.secret,
            **kwargs
        )

    def get_session(self):
        return TrelloAPISession(self.get_raw_session())

    def __str__(self):
        return f"{self.username}@Trello"

    @classmethod
    def create(cls, trello):
        db.session.add(trello)
        db.session.commit()

    @classmethod
    def remove(cls, trello):
        from life_scheduler.board.models import QuestSource
        sources = QuestSource.query.filter_by(backend_type="trello", backend_id=trello.id).all()
        for source in sources:
            db.session.delete(source)

        db.session.delete(trello)
        db.session.commit()

    @classmethod
    def get_by_token(cls, token):
        return cls.query.filter_by(token=token).first()

    @classmethod
    def get_by_id(cls, i):
        return cls.query.get(i)


class TrelloTemporaryToken(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    token = db.Column(db.String(256), index=True, unique=True, nullable=False)
    secret = db.Column(db.String(256), nullable=False)
    expires = db.Column(db.DateTime, nullable=True)

    user_id = db.Column(db.Integer, db.ForeignKey("user.id"), nullable=False)
    user = db.relationship("User")

    def __init__(self, token=None, secret=None, user=None, expires=None):
        self.token = token
        self.secret = secret
        self.user = user
        self.expires = expires

    def get_raw_session(self, **kwargs):
        client_key = current_app.config["TRELLO_API_KEY"]
        client_secret = current_app.config["TRELLO_API_SECRET"]

        if client_key is None:
            raise ValueError("Unable to create Trello temporary session: TRELLO_API_KEY is None")

        if client_secret is None:
            raise ValueError("Unable to create Trello temporary session: TRELLO_API_SECRET is None")

        return OAuth1Session(
            client_key=client_key,
            client_secret=client_secret,
            resource_owner_key=self.token,
            resource_owner_secret=self.secret,
            **kwargs
        )

    @classmethod
    def create(cls, trello_oauth_token):
        db.session.add(trello_oauth_token)
        db.session.commit()

    @classmethod
    def get_by_token(cls, token):
        return cls.query.filter_by(token=token).first()
