import os

from flask import Blueprint, redirect, url_for, send_from_directory, current_app

blueprint = Blueprint("app", __name__)


@blueprint.route("/favicon.ico")
def favicon():
    current_app.logger.warning(
        os.path.join(current_app.root_path, current_app.static_folder)
    )
    return send_from_directory(
        os.path.join(current_app.root_path, current_app.static_folder, "images"),
        "favicon.ico",
        mimetype="image/vnd.microsoft.icon",
    )
