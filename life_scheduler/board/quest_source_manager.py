from life_scheduler.board.models import QuestSource


class QuestSourceManager:
    supports_scheduler = False
    supports_postpone = False

    def __init__(self, source: QuestSource, **kwargs):
        self.source = source

        for key in kwargs:
            setattr(self, key, kwargs[key])

    def pull(self):
        raise NotImplementedError()

    def set_quest_archived(self, quest, value):
        raise NotImplementedError()

    def set_quest_done(self, quest, value):
        raise NotImplementedError()

    def set_quest_postponed_date(self, quest, value):
        raise NotImplementedError()

    def get_quest_source_url(self, quest):
        return None
