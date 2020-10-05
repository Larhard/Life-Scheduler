from life_scheduler.board.models import QuestSource


class QuestSourceManager:
    def __init__(self, source: QuestSource, **kwargs):
        self.source = source

        for key in kwargs:
            setattr(self, key, kwargs[key])

    def pull(self):
        raise NotImplementedError()
