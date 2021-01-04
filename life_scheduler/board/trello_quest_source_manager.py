import dateutil.parser

from life_scheduler import db
from life_scheduler.board.models import Quest
from life_scheduler.board.quest_source_manager import QuestSourceManager
from life_scheduler.trello.models import Trello


class TrelloQuestSourceManager(QuestSourceManager):
    board_id = None
    list_id = None
    board_display_name = None
    list_display_name = None

    def pull(self):
        backend: Trello = self.source.get_backend()
        session = backend.get_session()

        new_raw_quests = session.get_cards_from_list(self.list_id)
        new_quests = [
            {
                "name": quest["name"],
                "deadline": dateutil.parser.parse(quest["due"]) if quest["due"] else None,
                "user": backend.user,
                "source": self.source,
                "external_id": quest["id"],
                "labels": list(self.process_labels(quest["labels"])),
                "is_archived": False,
            }
            for quest in new_raw_quests
        ]

        new_quests_external_ids = [quest["external_id"] for quest in new_quests]

        for quest in new_quests:
            Quest.create_or_update(quest)

        for quest in Quest.get_by_source(self.source):
            if quest.external_id not in new_quests_external_ids:
                quest.is_archived = True
                db.session.commit()

    def set_quest_archived(self, quest, value):
        backend: Trello = self.source.get_backend()
        session = backend.get_session()

        session.update_card(quest.external_id, closed=value)
        quest.is_archived = True
        db.session.commit()

    def set_quest_done(self, quest, value):
        quest.is_done = value
        db.session.commit()

    def get_quest_source_url(self, quest):
        return f"https://trello.com/c/{quest.external_id}"

    def __str__(self):
        return f"{self.board_display_name}/{self.list_display_name}@{self.source.get_backend()}"

    def process_labels(self, labels):
        result = {
            "type": "source",
            "name": self.source.label_name or "",
            "fg_color": self.source.label_fg_color or "white",
            "bg_color": self.source.label_bg_color or "gray",
        }
        yield result

        for label in labels:
            result = {
                "type": "quest",
                "name": label["name"],
                "fg_color": "white",
                "bg_color": label["color"],
            }
            yield result
