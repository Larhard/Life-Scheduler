from flask_login import current_user

from datetime import datetime, date, time


def process_attr(attr):
    if isinstance(attr, (datetime, date, time)):
        attr = current_user.to_local(attr, "UTC").isoformat()

    return attr


def dump_attrs(parameters, obj):
    return {
        parameter: process_attr(getattr(obj, parameter))
        for parameter in parameters
    }
