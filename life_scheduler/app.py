from flask import Flask
from flask_login import LoginManager

import life_scheduler.auth.web
import life_scheduler.config

login_manager = LoginManager()


def create_app(config_object=life_scheduler.config.Config):
    app = Flask(__name__)
    app.config.from_object(config_object)

    login_manager.init_app(app)

    app.register_blueprint(life_scheduler.auth.web.blueprint)

    return app
