import json
from datetime import datetime
from functools import partial

from flask import Blueprint, render_template
from flask_login import login_required, current_user

from life_scheduler.auth.utils import approval_required
from life_scheduler.board.models import Quest
from life_scheduler.utils.json import dump_attrs

blueprint = Blueprint("board_api", __name__, url_prefix="/api/board")


@blueprint.route("/quests/today")
@login_required
@approval_required
def quests_today():
    quests = current_user.quests.filter(Quest.start_date >= datetime.utcnow()).all()

    attrs = [
        "id",
        "title",
        "description",
        "start_date",
        "deadline",
    ]

    dumped_quests = list(map(partial(dump_attrs, attrs), quests))

    return json.dumps(dumped_quests)


@blueprint.route("/quests/pull")
@login_required
@approval_required
def quests_pull():
    for source in current_user.quest_sources:
        source.get_manager().pull()
