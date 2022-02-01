import json
from functools import partial

from flask import Blueprint, request, abort, current_app
from flask_login import login_required, current_user

from life_scheduler.auth.utils import approval_required
from life_scheduler.board.models import Quest, ImageGraphSource, QuestOrder
from life_scheduler.utils.json import dump_attrs

blueprint = Blueprint("board_api", __name__, url_prefix="/api/board")


@blueprint.route("/quests/today/")
@login_required
@approval_required
def quests_today():
    quests = current_user.quests.filter_by(is_archived=False).all()

    attrs = [
        "id",
        "name",
        "description",
        "start_date",
        "start_time",
        "end_date",
        "end_time",
        "deadline",
        "is_done",
        "labels",
        "source_url",
    ]

    dumped_quests = list(map(partial(dump_attrs, attrs), quests))

    return json.dumps(dumped_quests)


@blueprint.route("/quests/pull/")
@login_required
@approval_required
def quests_pull():
    for source in current_user.quest_sources:
        current_app.logger.info(f"Pulling quest source: {source}")
        source.get_manager().pull()

    return ""


@blueprint.route("/quests/<quest_id>/", methods=["POST"])
@login_required
@approval_required
def quests(quest_id):
    quest = Quest.get_by_id(quest_id)
    if quest.user.id != current_user.id:
        abort(403)

    if request.method == "POST":
        if "is_done" in request.form:
            is_done = bool(json.loads(request.form["is_done"]))
            quest.set_done(is_done)

    return ""


@blueprint.route("/bulk/archivize/", methods=["POST"])
@login_required
@approval_required
def bulk_archivize():
    if request.method == "POST":
        if "quests[]" in request.form:
            quest_ids = request.form.getlist("quests[]")
            quest_ids = list(map(int, quest_ids))

            quests_list = [Quest.get_by_id(quest_id) for quest_id in quest_ids]

            for quest in quests_list:
                if quest.user.id != current_user.id:
                    abort(403)

            for quest in quests_list:
                quest.set_archived(True)

    return ""


@blueprint.route("/graphs/set_order/", methods=["POST"])
@login_required
@approval_required
def graphs_set_order():
    if request.method == "POST":
        if "order[]" in request.form:
            graphs_ids = request.form.getlist("order[]")
            graphs_ids = list(map(int, graphs_ids))

            for source in current_user.image_graph_sources.all():
                source.set_priority(None)

            for i, graph_id in enumerate(graphs_ids):
                graph = ImageGraphSource.get_by_id(graph_id)
                if graph.user.id != current_user.id:
                    abort(403)

                graph.set_priority(i)

    return ""


@blueprint.route("/quests/order/", methods=["GET", "PUT"])
@login_required
@approval_required
def quests_order():
    if request.method == "GET":
        if current_user.quest_order:
            return json.dumps(current_user.quest_order.order)
        else:
            return json.dumps([])

    elif request.method == "PUT":
        QuestOrder.create_or_update({
            "user": current_user,
            "order": request.json,
        })

    return ""
