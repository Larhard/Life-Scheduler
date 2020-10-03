from flask_login import UserMixin

from life_scheduler import db, login_manager


class User(UserMixin, db.Model):
    id = db.Column(db.Integer, primary_key=True)
    email = db.Column(db.String(120), unique=True)
    name = db.Column(db.String(120))
    given_name = db.Column(db.String(120))
    family_name = db.Column(db.String(120))
    picture = db.Column(db.String(120))

    is_approved = db.Column(db.Boolean, default=False)

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
        result = cls.get_by_email(user.email)

        if not result:
            db.session.add(user)
            db.session.commit()
            result = user

        return result

    @classmethod
    def get_by_email(cls, email):
        result = cls.query.filter_by(email=email).first()

        return result


@login_manager.user_loader
def load_user(user_id):
    return User.query.get(user_id)
