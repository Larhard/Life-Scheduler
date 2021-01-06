from flask import Blueprint, render_template
from flask_login import login_required

from life_scheduler.auth.utils import approval_required

blueprint = Blueprint("scheduler", __name__, url_prefix="/scheduler")


@blueprint.route("/")
@login_required
@approval_required
def index():
    return render_template("scheduler/index.html")
