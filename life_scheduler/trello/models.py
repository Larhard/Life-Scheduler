from flask import current_app
from requests_oauthlib import OAuth1Session
from sqlalchemy.orm import backref

from life_scheduler import db


class Trello(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    token = db.Column(db.String(256), index=True, unique=True, nullable=False)
    secret = db.Column(db.String(256), nullable=False)

    user_id = db.Column(db.Integer, db.ForeignKey("user.id"), nullable=False)
    user = db.relationship("User", backref=backref("trello", uselist=False))

    def __init__(self, token, secret, user):
        self.token = token
        self.secret = secret
        self.user = user

    def get_oauth(self, **kwargs):
        client_key = current_app.config["TRELLO_API_KEY"]
        client_secret = current_app.config["TRELLO_API_SECRET"]

        return OAuth1Session(
            client_key=client_key,
            client_secret=client_secret,
            resource_owner_key=self.token,
            resource_owner_secret=self.secret,
            **kwargs
        )

    @classmethod
    def create(cls, trello):
        db.session.add(trello)
        db.session.commit()

    @classmethod
    def remove(cls, trello):
        db.session.delete(trello)
        db.session.commit()

    @classmethod
    def get_by_token(cls, token):
        return cls.query.filter_by(token=token).first()


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

    def get_oauth(self, **kwargs):
        client_key = current_app.config["TRELLO_API_KEY"]
        client_secret = current_app.config["TRELLO_API_SECRET"]

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
