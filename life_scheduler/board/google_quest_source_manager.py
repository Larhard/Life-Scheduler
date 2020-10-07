import json
from datetime import datetime, time, timedelta

from life_scheduler import db
from life_scheduler.board.models import Quest
from life_scheduler.board.quest_source_manager import QuestSourceManager
from life_scheduler.google.models import Google
from life_scheduler.time import to_utc


class GoogleQuestSourceManager(QuestSourceManager):
    calendar_id = None
    calendar_display_name = None

    next_day_pull_time = "20:00"

    def pull(self):
        backend: Google = self.source.get_backend()
        session = backend.get_session()

        now = backend.user.datetime_now()

        current_time = now.time()
        next_day_pull_time = time.fromisoformat(self.next_day_pull_time)

        time_min = datetime.combine(now, backend.user.time_from_iso_format("00:00"))

        if current_time > next_day_pull_time:
            time_max = time_min + timedelta(days=2)
        else:
            time_max = time_min + timedelta(days=1)

        formatted_time_min = time_min.isoformat()
        formatted_time_max = time_max.isoformat()

        colors = session.get_calendar_colors()
        event_colors = colors["event"]

        for event in session.iter_calendar_events(
                calendar_id=self.calendar_id,
                timeMin=formatted_time_min,
                timeMax=formatted_time_max,
                singleEvents=True,
        ):
            quest_dict = {
                "name": event["summary"],
                "description": event.get("description"),
                "user": backend.user,
                "source": self.source,
                "external_id": event["id"],
                "labels": list(self.process_labels(event, event_colors)),
            }

            start_data = event.get("start")
            if start_data:
                start_timezone = start_data.get("timeZone")
                if "date" in start_data:
                    quest_dict["start_date"] = to_utc(start_data["date"], start_timezone)

                if "dateTime" in start_data:
                    quest_dict["start_datetime"] = to_utc(start_data["dateTime"], start_timezone)

            end_data = event.get("end")
            if end_data:
                end_timezone = end_data.get("timeZone")

                if "date" in end_data:
                    quest_dict["end_date"] = to_utc(end_data["date"], end_timezone)

                if "dateTime" in end_data:
                    quest_dict["end_datetime"] = to_utc(end_data["dateTime"], end_timezone)

            Quest.create_or_update(quest_dict)

    def set_quest_archived(self, quest, value):
        quest.is_archived = True
        db.session.commit()

    def set_quest_done(self, quest, value):
        quest.is_done = value
        db.session.commit()

    def __str__(self):
        return f"{self.calendar_display_name}@{self.source.get_backend()}"

    def process_labels(self, event, event_colors):
        result = {
            "type": "source",
            "name": self.source.label_name or "",
            "fg_color": self.source.label_fg_color or "white",
            "bg_color": self.source.label_bg_color or "gray",
        }
        yield result

        if "colorId" in event:
            color_id = event["colorId"]
            color = event_colors[color_id]

            result = {
                "type": "quest",
                "name": "",
                "fg_color": color["foreground"],
                "bg_color": color["background"],
            }
            yield result
