import life_scheduler.config

from flask import Flask


def create_app(config_object=life_scheduler.config.Config):
    app = Flask(__name__)
    app.config.from_object(config_object)

    return app
