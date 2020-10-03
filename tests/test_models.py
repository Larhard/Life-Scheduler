from life_scheduler.auth.models import User
from tests.fixtures import *


def test_user_trello_foreign_keys(app):
    User()
