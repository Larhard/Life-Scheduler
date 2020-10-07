from life_scheduler import db


class Google(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    access_token = db.Column(db.String(256), nullable=False)
    refresh_token = db.Column(db.String(256))
    token_type = db.Column(db.String(256))
    expires_at = db.Column(db.DateTime)
    email = db.Column(db.String(256))

    user_id = db.Column(db.Integer, db.ForeignKey("user.id"), nullable=False)
    user = db.relationship("User", backref="googles")

    def __init__(self, access_token, refresh_token, token_type, expires_at, user, email):
        self.access_token = access_token
        self.refresh_token = refresh_token
        self.token_type = token_type
        self.expires_at = expires_at
        self.email = email

        self.user = user

    def __str__(self):
        return f"{self.email}@Google"

    @classmethod
    def create(cls, google):
        db.session.add(google)
        db.session.commit()

    @classmethod
    def remove(cls, google):
        db.session.delete(google)
        db.session.commit()

    @classmethod
    def get_by_id(cls, i):
        return cls.query.get(i)
