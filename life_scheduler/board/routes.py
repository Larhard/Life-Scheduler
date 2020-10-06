from flask import Blueprint, render_template, redirect, url_for, abort
from flask_login import login_required, current_user

from life_scheduler.auth.utils import approval_required
from life_scheduler.board.forms import AddTrelloQuestSourceForm, AddImageGraphSourceForm
from life_scheduler.board.models import QuestSource, ImageGraphSource

blueprint = Blueprint("board", __name__)


@blueprint.route("/")
@login_required
@approval_required
def index():
    return render_template("board/index.html")


@blueprint.route("/settings")
@login_required
@approval_required
def settings():
    return render_template("board/settings.html")


@blueprint.route("/settings/add_trello_quest_source", methods=["GET", "POST"])
@login_required
@approval_required
def add_trello_quest_source():
    form = AddTrelloQuestSourceForm()

    if form.validate_on_submit():
        session = current_user.trello.get_session()

        board_id = form.board.data
        list_id = form.list.data
        board_display_name = session.get_board(board_id)["name"]
        list_display_name = session.get_list(list_id)["name"]

        QuestSource.register(
            current_user.trello,
            board_id=board_id,
            list_id=list_id,
            board_display_name=board_display_name,
            list_display_name=list_display_name,
        )

        return redirect(url_for("board.settings"))

    return render_template("board/add_trello_quest_source.html", form=form)


@blueprint.route("/settings/remove_quest_source/<source_id>", methods=["GET"])
@login_required
@approval_required
def remove_quest_source(source_id):
    source = QuestSource.get_by_id(source_id)

    if source.user.id != current_user.id:
        abort(403)

    QuestSource.remove(source)
    return redirect(url_for("board.settings"))


@blueprint.route("/settings/add_image_graph_source", methods=["GET", "POST"])
@login_required
@approval_required
def add_image_graph_source():
    form = AddImageGraphSourceForm()

    if form.validate_on_submit():
        url = form.url.data
        refresh_rate = form.refresh_rate.data

        if refresh_rate <= 0:
            refresh_rate = None

        source = ImageGraphSource(
            url=url,
            refresh_rate=refresh_rate,
            user=current_user,
        )
        ImageGraphSource.create(source)

        return redirect(url_for("board.settings"))

    return render_template("board/add_image_graph_source.html", form=form)


@blueprint.route("/settings/remove_image_graph_source/<source_id>", methods=["GET"])
@login_required
@approval_required
def remove_image_graph_source(source_id):
    source = ImageGraphSource.get_by_id(source_id)

    if source.user.id != current_user.id:
        abort(403)

    ImageGraphSource.remove(source)
    return redirect(url_for("board.settings"))
