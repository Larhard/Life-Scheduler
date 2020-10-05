from flask_wtf import FlaskForm
from wtforms import StringField, SubmitField


class AddTrelloQuestSourceForm(FlaskForm):
    board = StringField()
    list = StringField()
    submit = SubmitField("Create")
