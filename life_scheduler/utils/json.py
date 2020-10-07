from datetime import datetime, date, time


def process_attr(attr):
    if isinstance(attr, (datetime, date, time)):
        attr = attr.isoformat()

    return attr


def dump_attrs(parameters, obj):
    return {
        parameter: process_attr(getattr(obj, parameter))
        for parameter in parameters
    }
