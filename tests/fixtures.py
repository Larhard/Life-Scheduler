import tempfile

import pytest

import life_scheduler


@pytest.fixture
def app():
    app = life_scheduler.create_app()

    db_fd, db_path = tempfile.mkstemp()
    app.config['SQLALCHEMY_DATABASE_URI'] = f'sqlite:///{db_path}'
    app.config['TESTING'] = True
    app.config['WTF_CSRF_ENABLED'] = False

    with app.app_context():
        life_scheduler.db.create_all()

        yield app


@pytest.fixture
def client(app):
    client = app.test_client()
    with client:
        yield client


class FeatureFlagsHandler:
    def __init__(self, feature_flags=None):
        self.feature_flags = feature_flags or {}

    def handler(self, flag):
        return self.feature_flags.get(flag, False)

    def enable(self, flag):
        self.feature_flags[flag] = True

    def disable(self, flag):
        self.feature_flags[flag] = False


@pytest.fixture
def feature_flags(app):
    feature_flags_handler = FeatureFlagsHandler(app.config["FEATURE_FLAGS"])
    life_scheduler.feature_flags.clear_handlers()
    life_scheduler.feature_flags.add_handler(feature_flags_handler.handler)
    return feature_flags_handler
