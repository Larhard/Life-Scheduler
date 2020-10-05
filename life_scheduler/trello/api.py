class TrelloAPISession:
    BASE_URL = "https://trello.com"

    def __init__(self, raw_session):
        self.raw_session = raw_session

    def get_board(self, board_id, **kwargs):
        response = self.raw_session.get(
            f"{self.BASE_URL}/1/boards/{board_id}",
            params=kwargs
        )
        response.raise_for_status()
        return response.json()

    def get_boards(self, member="me", **kwargs):
        response = self.raw_session.get(
            f"{self.BASE_URL}/1/members/{member}/boards",
            params=kwargs
        )
        response.raise_for_status()
        return response.json()

    def get_lists(self, board_id, **kwargs):
        response = self.raw_session.get(
            f"{self.BASE_URL}/1/boards/{board_id}/lists",
            params=kwargs
        )
        response.raise_for_status()
        return response.json()

    def get_list(self, list_id, **kwargs):
        response = self.raw_session.get(
            f"{self.BASE_URL}/1/list/{list_id}",
            params=kwargs
        )
        response.raise_for_status()
        return response.json()

    def get_cards_from_list(self, list_id, **kwargs):
        response = self.raw_session.get(
            f"{self.BASE_URL}/1/list/{list_id}/cards",
            params=kwargs
        )
        response.raise_for_status()
        return response.json()
