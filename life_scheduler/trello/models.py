import requests
from sqlalchemy.orm import backref

from life_scheduler import db
from life_scheduler.trello.auth import get_oauth1_client


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

    def get_oauth1_client(self):
        return get_oauth1_client(
            resource_owner_key=self.token,
            resource_owner_secret=self.secret,
        )

    def get(self, url):
        client = self.get_oauth1_client()
        uri, headers, body = client.sign(url)
        response = requests.get(uri, headers=headers, data=body)
        return response.content

    @classmethod
    def create(cls, trello_oauth_token):
        db.session.add(trello_oauth_token)
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

    def __init__(self, token, secret, user, expires=None):
        self.token = token
        self.secret = secret
        self.user = user
        self.expires = expires

    def get_oauth1_client(self):
        return get_oauth1_client(
            resource_owner_key=self.token,
            resource_owner_secret=self.secret,
        )

    @classmethod
    def create(cls, trello_oauth_token):
        db.session.add(trello_oauth_token)
        db.session.commit()

    @classmethod
    def get_by_token(cls, token):
        return cls.query.filter_by(token=token).first()
