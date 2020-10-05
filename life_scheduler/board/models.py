from sqlalchemy.orm import backref

from life_scheduler import db
from life_scheduler.board.trello_source_wrapper import TrelloSourceWrapper
from life_scheduler.trello.models import Trello


class Quest(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.UnicodeText, nullable=False)
    description = db.Column(db.UnicodeText)

    start_date = db.Column(db.DateTime)
    deadline = db.Column(db.DateTime)

    user_id = db.Column(db.Integer, db.ForeignKey("user.id"), nullable=False)
    user = db.relationship("User", backref=backref("quests", lazy="dynamic"))

    source_id = db.Column(db.Integer, db.ForeignKey("quest_source.id"), nullable=False)
    source = db.relationship("QuestSource", backref="quests")

    external_id = db.Column(db.Unicode(256))

    def __init__(
            self,
            title=None,
            description=None,
            start_date=None,
            deadline=None,
            user=None,
            source=None,
            external_id=None,
    ):
        self.title = title
        self.description = description

        self.start_date = start_date
        self.deadline = deadline

        self.user = user

        self.source = source
        self.external_id = external_id

    @classmethod
    def create(cls, quest):
        db.session.add(quest)
        db.session.commit()


class QuestSource(db.Model):
    id = db.Column(db.Integer, primary_key=True)

    user_id = db.Column(db.Integer, db.ForeignKey("user.id"), nullable=False)
    user = db.relationship("User", backref="quest_sources")

    backend_type = db.Column(db.Unicode(256))
    backend_id = db.Column(db.Integer)
    args = db.Column(db.JSON)

    def __init__(
            self,
            user=None,
            backend_type=None,
            backend_id=None,
    ):
        self.user = user
        self.backend_type = backend_type
        self.backend_id = backend_id

    def get_backend(self):
        if self.backend_type == "trello":
            return Trello.get_by_id(self.backend_id)
        else:
            raise ValueError(f"Unknown backend type: {self.backend_type}")

    def get_wrapper(self):
        if self.backend_type == "trello":
            return TrelloSourceWrapper(self, **self.args)
        else:
            raise ValueError(f"Unknown backend type: {self.backend_type}")

    def __str__(self):
        return str(self.get_wrapper())

    @classmethod
    def get_by_id(cls, source_id):
        return cls.query.get(source_id)

    @classmethod
    def create(cls, quest):
        db.session.add(quest)
        db.session.commit()

    @classmethod
    def remove(cls, source):
        db.session.delete(source)
        db.session.commit()

    @classmethod
    def register(cls, backend, **kwargs):
        source = cls()

        if isinstance(backend, Trello):
            source.user = backend.user
            source.backend_type = "trello"
            source.backend_id = backend.id
            source.args = kwargs
        else:
            raise ValueError(f"Unknown backend: {backend}")

        cls.create(source)
