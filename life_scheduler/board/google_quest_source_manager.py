import json
from datetime import datetime, time, timedelta

from life_scheduler import db
from life_scheduler.board.models import Quest
from life_scheduler.board.quest_source_manager import QuestSourceManager
from life_scheduler.google.models import Google


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

        for event in session.iter_calendar_events(
                calendar_id=self.calendar_id,
                timeMin=formatted_time_min,
                timeMax=formatted_time_max,
                singleEvents=True,
        ):
            start_date = None
            end_date = None

            quest_dict = {
                "name": event["summary"],
                "description": event.get("description"),
                "user": backend.user,
                "source": self.source,
                "external_id": event["id"],
                "start_date": start_date,
                "end_date": end_date,
            }

            Quest.create_or_update(quest_dict)

    def set_quest_archived(self, quest, value):
        quest.is_archived = True
        db.session.commit()

    def set_quest_done(self, quest, value):
        quest.is_done = value
        db.session.commit()

    def __str__(self):
        return f"{self.calendar_display_name}@{self.source.get_backend()}"
