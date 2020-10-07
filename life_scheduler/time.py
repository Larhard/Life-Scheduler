import dateutil.parser

from dateutil.tz import gettz

TZ_UTC = gettz("utc")


def sanitize_timezone(tz):
    if isinstance(tz, str):
        tz = gettz(tz)

    return tz


def sanitize_datetime(dt, tz=None):
    tz = sanitize_timezone(tz)

    if isinstance(dt, str):
        dt = dateutil.parser.parse(dt)

    if tz is not None:
        dt = dt.replace(tzinfo=tz)

    return dt


def get_timezone(tz=None):
    if tz is None:
        tz = gettz()

    tz = sanitize_timezone(tz)

    return tz


def to_utc(dt, tz=None):
    if dt is not None:
        dt = sanitize_datetime(dt, tz)
        return dt.astimezone(TZ_UTC)


def to_local(dt, tz=None, source_tz=None):
    if dt is not None:
        dt = sanitize_datetime(dt, source_tz)
        tz = get_timezone(tz)

        return dt.astimezone(tz)
