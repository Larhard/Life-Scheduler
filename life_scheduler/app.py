from flask import Flask
from flask_login import LoginManager
from flask_migrate import Migrate
from flask_sqlalchemy import SQLAlchemy

db = SQLAlchemy()
db_migrate = Migrate()
login_manager = LoginManager()

import config
import life_scheduler.auth.models
import life_scheduler.auth.routes
import life_scheduler.board.routes


def create_app(config_object=config.Config):
    app = Flask(__name__)
    app.config.from_object(config_object)

    db.init_app(app)
    db_migrate.init_app(app, db)
    login_manager.init_app(app)

    app.register_blueprint(life_scheduler.auth.routes.blueprint)
    app.register_blueprint(life_scheduler.board.routes.blueprint)

    return app
