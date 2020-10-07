class GoogleAPISession:
    BASE_URL = "https://www.googleapis.com"

    def __init__(self, raw_session):
        self.raw_session = raw_session

    def get(self, path, **kwargs):
        response = self.raw_session.get(
            f"{self.BASE_URL}{path}",
            params=kwargs
        )
        response.raise_for_status()
        return response.json()

    def iter_get_pages(self, path, **kwargs):
        data = self.get(path, **kwargs)
        while data:
            print(data)
            for item in data["items"]:
                yield item

            if "nextPageToken" in data:
                next_page_token = data["nextPageToken"]
                data = self.get(path, pageToken=next_page_token, **kwargs)
            else:
                data = None

    def iter_calendar_list(self, **kwargs):
        return self.iter_get_pages("/calendar/v3/users/me/calendarList", **kwargs)
