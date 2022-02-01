from flask import current_app
from requests_oauthlib import OAuth1Session

from life_scheduler import db
from life_scheduler.trello.api import TrelloAPISession


# class SchedulerRule(db.Model):
#     id = db.Column(db.Integer, primary_key=True)
#
#     schedule = db.Column(db.UnicodeText)
#     last_scheduled = db.Column(db.DateTime)
#     repeats = db.Column(db.Integer)
#
#     quest_source = None  # TODO
#     quest_templates = None  # TODO
#     quests = None  # TODO
#
#
# class SchedulerQuestTemplate(db.Model):
#     title = db.Column(db.UnicodeText)
#     description = db.Column(db.UnicodeText)
#     lables = None
