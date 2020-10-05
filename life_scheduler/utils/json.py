from datetime import datetime


def process_attr(attr):
    if isinstance(attr, datetime):
        return datetime.timestamp(attr)
    return attr


def dump_attrs(parameters, obj):
    return {
        parameter: process_attr(getattr(obj, parameter))
        for parameter in parameters
    }
