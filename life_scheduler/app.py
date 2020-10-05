import os

from flask import Flask
from flask_login import LoginManager
from flask_migrate import Migrate
from flask_sqlalchemy import SQLAlchemy
from sassutils.wsgi import SassMiddleware

import config

db = SQLAlchemy()
db_migrate = Migrate()
login_manager = LoginManager()


def create_app(config_object=config.Config):
    import life_scheduler.auth.models
    import life_scheduler.board.models
    import life_scheduler.trello.models

    import life_scheduler.routes
    import life_scheduler.auth.routes
    import life_scheduler.board.routes
    import life_scheduler.board.api_routes
    import life_scheduler.trello.routes

    root_folder = os.path.dirname(os.path.dirname(__file__))

    app = Flask(
        __name__,
        static_folder=os.path.join(root_folder, "static"),
        template_folder=os.path.join(root_folder, "templates"),
    )

    app.config.from_object(config_object)

    db.init_app(app)
    db_migrate.init_app(app, db)
    login_manager.init_app(app)

    app.register_blueprint(life_scheduler.routes.blueprint)
    app.register_blueprint(life_scheduler.auth.routes.blueprint)
    app.register_blueprint(life_scheduler.board.api_routes.blueprint)
    app.register_blueprint(life_scheduler.board.routes.blueprint)
    app.register_blueprint(life_scheduler.trello.routes.blueprint)

    app.wsgi_app = SassMiddleware(
        app.wsgi_app,
        {
            'life_scheduler': {
                'sass_path': os.path.join(app.static_folder, 'sass'),
                'css_path': os.path.join(app.static_folder, 'css'),
                'wsgi_path': '/static/css',
                'strip_extension': True,
            },
        },
    )

    return app
