from flask_login import UserMixin

from life_scheduler.app import db, login_manager


class User(UserMixin, db.Model):
    id = db.Column(db.Integer, primary_key=True)
    email = db.Column(db.String(120), unique=True)
    name = db.Column(db.String(120))
    given_name = db.Column(db.String(120))
    family_name = db.Column(db.String(120))
    picture = db.Column(db.String(120))

    is_approved = db.Column(db.Boolean, default=False)

    trello_secret = db.Column(db.String(120))

    def __init__(self, email=None, name=None, given_name=None, family_name=None, picture=None):
        self.email = email
        self.name = name
        self.given_name = given_name
        self.family_name = family_name
        self.picture = picture

    def set_approved(self, value):
        self.is_approved = value
        db.session.commit()

    def __repr__(self):
        return f"<User {self.email}>"

    @classmethod
    def get_or_create(cls, user):
        result = cls.query.filter_by(email=user.email).first()

        if not result:
            db.session.add(user)
            db.session.commit()
            result = user

        return result

    @classmethod
    def get(cls, user):
        result = cls.query.filter_by(email=user.email).first()

        return result


@login_manager.user_loader
def load_user(user_id):
    return User.query.get(user_id)
