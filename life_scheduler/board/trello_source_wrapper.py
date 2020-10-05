from life_scheduler.board.source_wrapper import SourceWrapper


class TrelloSourceWrapper(SourceWrapper):
    board_id = None
    list_id = None
    board_display_name = None
    list_display_name = None

    def pull(self):
        pass

    def __str__(self):
        return f"Trello: {self.board_display_name}/{self.list_display_name}"
