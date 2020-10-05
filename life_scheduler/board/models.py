from sqlalchemy.orm import backref

from life_scheduler import db
from life_scheduler.trello.models import Trello


class Quest(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.UnicodeText, nullable=False)
    description = db.Column(db.UnicodeText)

    start_date = db.Column(db.DateTime)
    deadline = db.Column(db.DateTime)

    user_id = db.Column(db.Integer, db.ForeignKey("user.id"), nullable=False)
    user = db.relationship("User", backref=backref("quests", lazy="dynamic"))

    source_id = db.Column(db.Integer, db.ForeignKey("quest_source.id"), nullable=False)
    source = db.relationship("QuestSource", backref=backref("quests", lazy="dynamic"))

    external_id = db.Column(db.Unicode(256), index=True)

    is_archived = db.Column(db.Boolean, default=False, index=True)

    def __init__(
            self,
            name=None,
            description=None,
            start_date=None,
            deadline=None,
            user=None,
            source=None,
            external_id=None,
            is_archived=False,
    ):
        self.name = name
        self.description = description

        self.start_date = start_date
        self.deadline = deadline

        self.user = user

        self.source = source
        self.external_id = external_id

        self.is_archived = is_archived

    def update(self, other):
        self.name = other.name
        self.description = other.description
        self.start_date = other.start_date
        self.deadline = other.deadline

    def set_archived(self, value):
        self.is_archived = value
        db.session.commit()

    @classmethod
    def create(cls, quest):
        db.session.add(quest)
        db.session.commit()

    @classmethod
    def create_or_update(cls, quest):
        old_quest = cls.get_by_external_id(quest.external_id, quest.source)
        if not old_quest:
            cls.create(quest)
        else:
            old_quest.update(quest)

    @classmethod
    def get_by_external_id(cls, external_id, source):
        return cls.query.filter_by(external_id=external_id, source=source).first()

    @classmethod
    def get_by_source(cls, source):
        return cls.query.filter_by(source=source).first()


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

    def get_manager(self):
        if self.backend_type == "trello":
            from life_scheduler.board.trello_quest_source_manager import TrelloQuestSourceManager
            return TrelloQuestSourceManager(self, **self.args)
        else:
            raise ValueError(f"Unknown backend type: {self.backend_type}")

    def __str__(self):
        return str(self.get_manager())

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
