from life_scheduler.auth.models import User

from .routes import blueprint


@blueprint.cli.command("pull")
def pull():
    for user in User.get_all():
        for source in user.quest_sources:
            source.get_manager().pull()
