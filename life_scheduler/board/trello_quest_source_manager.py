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
            Quest(
                name=quest["name"],
                description=quest["description"],
                deadline=quest["due"],
                user=backend.user,
                source=self.source,
                external_id=quest["id"],
            )
            for quest in new_raw_quests
        ]

        new_quests_external_ids = [quest.external_id for quest in new_quests]

        for quest in new_quests:
            Quest.create_or_update(quest)

        for quest in Quest.get_by_source(self.source):
            if quest.external_id not in new_quests_external_ids:
                quest.set_archived(True)

    def __str__(self):
        return f"Trello: {self.board_display_name}/{self.list_display_name}"
