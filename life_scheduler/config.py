import life_scheduler.utils.git


class Config:
    VERSION = life_scheduler.utils.git.get_revision_hash()
