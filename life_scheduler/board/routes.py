from flask import Blueprint, render_template, redirect, url_for, abort
from flask_login import login_required, current_user

from life_scheduler.auth.utils import approval_required
from life_scheduler.board.forms import AddTrelloQuestSourceForm, AddImageGraphSourceForm, AddGoogleQuestSourceForm, \
    EditQuestSourceForm
from life_scheduler.board.models import QuestSource, ImageGraphSource
from life_scheduler.google.api import GoogleAPISession
from life_scheduler.google.models import Google
from life_scheduler.trello.models import Trello

blueprint = Blueprint("board", __name__)


@blueprint.route("/")
@login_required
@approval_required
def index():
    return render_template("board/index.html")


@blueprint.route("/settings/")
@login_required
@approval_required
def settings():
    return render_template("board/settings.html")


@blueprint.route("/settings/add_trello_quest_source/<trello_id>/", methods=["GET", "POST"])
@login_required
@approval_required
def add_trello_quest_source(trello_id):
    trello = Trello.get_by_id(trello_id)
    if trello.user.id != current_user.id:
        abort(403)

    form = AddTrelloQuestSourceForm()

    if form.validate_on_submit():
        session = trello.get_session()

        board_id = form.board.data
        list_id = form.list.data
        queue_list_id = form.queue_list.data
        board_display_name = session.get_board(board_id)["name"]
        list_display_name = session.get_list(list_id)["name"]
        queue_list_display_name = session.get_list(queue_list_id)["name"]

        QuestSource.register(
            backend=trello,
            board_id=board_id,
            list_id=list_id,
            queue_list_id=queue_list_id,
            board_display_name=board_display_name,
            list_display_name=list_display_name,
            queue_list_display_name=queue_list_display_name,
        )

        return redirect(url_for("board.settings"))

    return render_template("board/add_trello_quest_source.html", form=form, trello=trello)


@blueprint.route("/settings/remove_quest_source/<source_id>/", methods=["GET"])
@login_required
@approval_required
def remove_quest_source(source_id):
    source = QuestSource.get_by_id(source_id)

    if source.user.id != current_user.id:
        abort(403)

    QuestSource.remove(source)
    return redirect(url_for("board.settings"))


@blueprint.route("/settings/edit_quest_source/<source_id>/", methods=["GET", "POST"])
@login_required
@approval_required
def edit_quest_source(source_id):
    source: QuestSource = QuestSource.get_by_id(source_id)

    if source.user.id != current_user.id:
        abort(403)

    form = EditQuestSourceForm()

    if form.validate_on_submit():
        source.set_label_name(form.label_name.data)
        source.set_label_fg_color(form.label_fg_color.data)
        source.set_label_bg_color(form.label_bg_color.data)
        source.set_blacklist(form.blacklist.data)

        return redirect(url_for("board.settings"))

    form.label_name.data = source.label_name
    form.label_fg_color.data = source.label_fg_color
    form.label_bg_color.data = source.label_bg_color
    form.blacklist.data = source.blacklist

    return render_template("board/edit_quest_source.html", form=form)


@blueprint.route("/settings/add_image_graph_source/", methods=["GET", "POST"])
@login_required
@approval_required
def add_image_graph_source():
    form = AddImageGraphSourceForm()

    if form.validate_on_submit():
        url = form.url.data

        source = ImageGraphSource(
            url=url,
            user=current_user,
        )
        ImageGraphSource.create(source)

        return redirect(url_for("board.settings"))

    return render_template("board/add_image_graph_source.html", form=form)


@blueprint.route("/settings/remove_image_graph_source/<source_id>/", methods=["GET"])
@login_required
@approval_required
def remove_image_graph_source(source_id):
    source = ImageGraphSource.get_by_id(source_id)

    if source.user.id != current_user.id:
        abort(403)

    ImageGraphSource.remove(source)
    return redirect(url_for("board.settings"))


@blueprint.route("/settings/add_google_quest_source/<google_id>/", methods=["GET", "POST"])
@login_required
@approval_required
def add_google_quest_source(google_id):
    google = Google.get_by_id(google_id)
    if google.user.id != current_user.id:
        abort(403)

    session: GoogleAPISession = google.get_session()
    form = AddGoogleQuestSourceForm()

    form.calendar.choices = [(c["id"], c["summary"]) for c in session.iter_calendars()]

    if form.validate_on_submit():
        calendar_id = form.calendar.data

        calendar_data = session.get_calendar(calendar_id)

        calendar_display_name = calendar_data["summary"]

        QuestSource.register(
            backend=google,
            calendar_id=calendar_id,
            calendar_display_name=calendar_display_name,
        )

        return redirect(url_for("board.settings"))

    return render_template("board/add_google_quest_source.html", form=form, google=google)
