from flask_wtf import FlaskForm
from wtforms import StringField, SubmitField, IntegerField, SelectField


class AddTrelloQuestSourceForm(FlaskForm):
    board = StringField()
    list = StringField()
    submit = SubmitField("Create")


class AddImageGraphSourceForm(FlaskForm):
    url = StringField()
    refresh_rate = IntegerField(default=0)
    submit = SubmitField("Create")


class AddGoogleQuestSourceForm(FlaskForm):
    calendar = SelectField(validate_choice=False)
    submit = SubmitField("Create")


class EditQuestSourceForm(FlaskForm):
    label_name = StringField()
    label_fg_color = StringField()
    label_bg_color = StringField()
    submit = SubmitField("Save")
