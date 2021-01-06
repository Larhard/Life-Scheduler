import re

from datetime import datetime

from sqlalchemy.orm import backref

from life_scheduler import db
from life_scheduler.auth.models import User
from life_scheduler.google.models import Google
from life_scheduler.trello.models import Trello


class Quest(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.UnicodeText, nullable=False)
    description = db.Column(db.UnicodeText)

    start_date = db.Column(db.Date)
    start_time = db.Column(db.Time)
    end_date = db.Column(db.Date)
    end_time = db.Column(db.Time)
    deadline = db.Column(db.DateTime)

    user_id = db.Column(db.Integer, db.ForeignKey("user.id"), nullable=False)
    user = db.relationship("User", backref=backref("quests", lazy="dynamic"))

    source_id = db.Column(db.Integer, db.ForeignKey("quest_source.id"), nullable=False)
    source = db.relationship("QuestSource", backref=backref("quests", lazy="dynamic", cascade="all, delete-orphan"))

    external_id = db.Column(db.Unicode(256), index=True)

    labels = db.Column(db.JSON)

    is_archived = db.Column(db.Boolean, default=False, index=True)
    is_done = db.Column(db.Boolean, default=False)

    extra = db.Column(db.JSON)

    def __init__(
            self,
            name=None,
            description=None,
            start_date=None,
            start_time=None,
            start_datetime=None,
            end_date=None,
            end_time=None,
            end_datetime=None,
            deadline=None,
            user=None,
            source=None,
            external_id=None,
            labels=None,
            is_archived=False,
            is_done=False,
            extra=None,
    ):
        self.name = name
        self.description = description

        if start_datetime is not None:
            self.start_datetime = start_datetime
        else:
            self.start_date = start_date
            self.start_time = start_time

        if end_datetime is not None:
            self.end_datetime = end_datetime
        else:
            self.end_date = end_date
            self.end_time = end_time

        self.deadline = deadline

        self.user = user

        self.source = source
        self.external_id = external_id

        self.labels = labels

        self.is_archived = is_archived
        self.is_done = is_done

        self.extra = extra

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

    @property
    def start_datetime(self):
        if self.start_time is not None:
            return datetime.combine(self.start_date, self.start_time)
        return self.start_date

    @property
    def end_datetime(self):
        if self.end_time is not None:
            return datetime.combine(self.end_date, self.end_time)
        return self.end_date

    @property
    def source_url(self):
        manager = self.source.get_manager()
        return manager.get_quest_source_url(self)

    @start_datetime.setter
    def start_datetime(self, value):
        if value is None:
            self.start_date = None
            self.start_time = None
        else:
            self.start_date = value.date()
            self.start_time = value.time()

    @end_datetime.setter
    def end_datetime(self, value):
        if value is None:
            self.start_date = None
            self.start_time = None
        else:
            self.end_date = value.date()
            self.end_time = value.time()

    @classmethod
    def create(cls, quest):
        db.session.add(quest)
        db.session.commit()

    @classmethod
    def create_or_update(cls, quest_dict):
        source = quest_dict["source"]
        if not source.validate_quest_dict(quest_dict):
            quest_dict["is_archived"] = True

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

    label_name = db.Column(db.Unicode(128), default="")
    label_fg_color = db.Column(db.Unicode(128), default="white")
    label_bg_color = db.Column(db.Unicode(128), default="gray")

    blacklist = db.Column(db.UnicodeText)

    def __init__(
            self,
            user=None,
            backend_type=None,
            backend_id=None,
            label_name=None,
            label_fg_color=None,
            label_bg_color=None,
    ):
        self.user = user
        self.backend_type = backend_type
        self.backend_id = backend_id
        self.label_name = label_name
        self.label_fg_color = label_fg_color
        self.label_bg_color = label_bg_color

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

    @property
    def supports_scheduler(self):
        manager = self.get_manager()
        return manager.supports_scheduler

    def set_label_name(self, value):
        self.label_name = value
        db.session.commit()

    def set_label_fg_color(self, value):
        self.label_fg_color = value
        db.session.commit()

    def set_label_bg_color(self, value):
        self.label_bg_color = value
        db.session.commit()

    def set_blacklist(self, value):
        self.blacklist = value
        db.session.commit()

    def validate_quest_dict(self, quest_dict):
        if self.blacklist is not None:
            for line in self.blacklist.splitlines():
                if re.match(f"^{line}$", quest_dict["name"]):
                    return False

        return True

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
    refresh_rate = db.Column(db.Integer)  # TODO remove
    priority = db.Column(db.Integer)

    user_id = db.Column(db.Integer, db.ForeignKey("user.id"), nullable=False)
    user = db.relationship("User", backref=backref("image_graph_sources", lazy="dynamic"))

    def __init__(self, url=None, user=None):
        self.url = url
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


class QuestOrder(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    order = db.Column(db.JSON)

    user_id = db.Column(db.Integer, db.ForeignKey("user.id"), nullable=False)
    user = db.relationship("User", backref=backref("quest_order", uselist=False))

    def __init__(self, order=None, user=None):
        self.order = order
        self.user = user

    @classmethod
    def create_or_update(cls, order_dict):
        user = order_dict["user"]
        order = order_dict["order"]

        if user.quest_order is None:
            quest_order = QuestOrder(
                user=user,
                order=order,
            )

            db.session.add(quest_order)
            db.session.commit()
        else:
            user.quest_order.order = order
            db.session.commit()
