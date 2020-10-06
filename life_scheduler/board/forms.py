from flask_wtf import FlaskForm
from wtforms import StringField, SubmitField, IntegerField


class AddTrelloQuestSourceForm(FlaskForm):
    board = StringField()
    list = StringField()
    submit = SubmitField("Create")


class AddImageGraphSourceForm(FlaskForm):
    url = StringField()
    refresh_rate = IntegerField(default=0)
    submit = SubmitField("Create")
