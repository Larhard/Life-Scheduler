from flask import Flask, url_for
from flask_login import LoginManager
from flask_migrate import Migrate
from flask_sqlalchemy import SQLAlchemy
from sassutils.wsgi import SassMiddleware

db = SQLAlchemy()
db_migrate = Migrate()
login_manager = LoginManager()

import config

import life_scheduler.auth.models

import life_scheduler.routes

import life_scheduler.auth.routes
import life_scheduler.board.routes
import life_scheduler.trello.routes


def create_app(config_object=config.Config):
    app = Flask(
        __name__,
        template_folder="../templates",
        static_folder="../static",
    )
    app.config.from_object(config_object)

    db.init_app(app)
    db_migrate.init_app(app, db)
    login_manager.init_app(app)

    app.register_blueprint(life_scheduler.routes.blueprint)

    app.register_blueprint(life_scheduler.auth.routes.blueprint)
    app.register_blueprint(life_scheduler.board.routes.blueprint)
    app.register_blueprint(life_scheduler.trello.routes.blueprint)

    app.wsgi_app = SassMiddleware(
        app.wsgi_app,
        {
            'life_scheduler': {
                'sass_path': '../static/sass',
                'css_path': '../static/css',
                'wsgi_path': '/static/css',
                'strip_extension': True,
            },
        },
    )

    return app
