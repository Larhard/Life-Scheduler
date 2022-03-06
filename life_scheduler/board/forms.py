from flask_wtf import FlaskForm
from wtforms import StringField, SubmitField, IntegerField, SelectField, TextAreaField


class AddTrelloQuestSourceForm(FlaskForm):
    board = StringField()
    list = StringField()
    submit = SubmitField("Create")


class AddImageGraphSourceForm(FlaskForm):
    url = StringField()
    submit = SubmitField("Create")


class AddGoogleQuestSourceForm(FlaskForm):
    calendar = SelectField()
    submit = SubmitField("Create")


class EditQuestSourceForm(FlaskForm):
    label_name = StringField()
    label_fg_color = StringField()
    label_bg_color = StringField()
    blacklist = TextAreaField()
    submit = SubmitField("Save")
