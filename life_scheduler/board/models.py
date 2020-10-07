from sqlalchemy.orm import backref

from life_scheduler import db
from life_scheduler.google.models import Google
from life_scheduler.trello.models import Trello


class Quest(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.UnicodeText, nullable=False)
    description = db.Column(db.UnicodeText)

    start_date = db.Column(db.DateTime)
    end_date = db.Column(db.DateTime)
    deadline = db.Column(db.DateTime)

    user_id = db.Column(db.Integer, db.ForeignKey("user.id"), nullable=False)
    user = db.relationship("User", backref=backref("quests", lazy="dynamic"))

    source_id = db.Column(db.Integer, db.ForeignKey("quest_source.id"), nullable=False)
    source = db.relationship("QuestSource", backref=backref("quests", lazy="dynamic", cascade="all, delete-orphan"))

    external_id = db.Column(db.Unicode(256), index=True)

    is_archived = db.Column(db.Boolean, default=False, index=True)
    is_done = db.Column(db.Boolean, default=False)

    def __init__(
            self,
            name=None,
            description=None,
            start_date=None,
            end_date=None,
            deadline=None,
            user=None,
            source=None,
            external_id=None,
            is_archived=False,
            is_done=False,
    ):
        self.name = name
        self.description = description

        self.start_date = start_date
        self.end_date = end_date
        self.deadline = deadline

        self.user = user

        self.source = source
        self.external_id = external_id

        self.is_archived = is_archived
        self.is_done = is_done

    def update(self, quest_dict):
        for key in quest_dict:
            setattr(self, key, quest_dict[key])
        db.session.commit()

    def set_archived(self, value):
        manager = self.source.get_manager()
        manager.set_quest_archived(self, value)

    def set_done(self, value):
        manager = self.source.get_manager()
        manager.set_quest_done(self, value)

    @classmethod
    def create(cls, quest):
        db.session.add(quest)
        db.session.commit()

    @classmethod
    def create_or_update(cls, quest_dict):
        old_quest = cls.get_by_external_id(quest_dict["external_id"], quest_dict["source"])
        if not old_quest:
            quest = Quest(**quest_dict)
            cls.create(quest)
        else:
            old_quest.update(quest_dict)

    @classmethod
    def get_by_external_id(cls, external_id, source):
        return cls.query.filter_by(external_id=external_id, source=source).first()

    @classmethod
    def get_by_source(cls, source):
        return cls.query.filter_by(source=source).all()

    @classmethod
    def get_by_id(cls, quest_id):
        return cls.query.get(quest_id)


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
        elif self.backend_type == "google":
            return Google.get_by_id(self.backend_id)
        else:
            raise ValueError(f"Unknown backend type: {self.backend_type}")

    def get_manager(self):
        if self.backend_type == "trello":
            from life_scheduler.board.trello_quest_source_manager import TrelloQuestSourceManager
            return TrelloQuestSourceManager(self, **self.args)
        elif self.backend_type == "google":
            from life_scheduler.board.google_quest_source_manager import GoogleQuestSourceManager
            return GoogleQuestSourceManager(self, **self.args)
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
        elif isinstance(backend, Google):
            source.user = backend.user
            source.backend_type = "google"
            source.backend_id = backend.id
            source.args = kwargs
        else:
            raise ValueError(f"Unknown backend: {backend}")

        cls.create(source)


class ImageGraphSource(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    url = db.Column(db.UnicodeText, nullable=False)
    refresh_rate = db.Column(db.Integer)
    priority = db.Column(db.Integer)

    user_id = db.Column(db.Integer, db.ForeignKey("user.id"), nullable=False)
    user = db.relationship("User", backref=backref("image_graph_sources", lazy="dynamic"))

    def __init__(self, url=None, refresh_rate=None, user=None):
        self.url = url
        self.refresh_rate = refresh_rate
        self.user = user

    def set_priority(self, value):
        self.priority = value
        db.session.commit()

    @classmethod
    def get_by_id(cls, source_id):
        return cls.query.get(source_id)

    @classmethod
    def create(cls, source):
        db.session.add(source)
        db.session.commit()

    @classmethod
    def remove(cls, source):
        db.session.delete(source)
        db.session.commit()
