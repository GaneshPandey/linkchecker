import math


def date_diff(older, newer):
    """
    Returns a humanized string representing time difference

    The output rounds up to days, hours, minutes, or seconds.
    4 days 5 hours returns '4 days'
    0 days 4 hours 3 minutes returns '4 hours', etc...
    """

    time_diff = newer - older
    days = time_diff.days
    hours = time_diff.seconds / 3600
    minutes = time_diff.seconds % 3600 / 60
    seconds = time_diff.seconds % 3600 % 60

    str = ""
    t_str = ""
    if days > 0:
        if days == 1:
            t_str = "day"
        else:
            t_str = "days"
        str += "%s %s" % (days, t_str)
        return str
    elif hours > 0:
        if hours == 1:
            t_str = "hour"
        else:
            t_str = "hours"
        str += "%s %s" % (hours, t_str)
        return str
    elif minutes > 0:
        if minutes == 1:
            t_str = "min"
        else:
            t_str = "mins"
        str += "%s %s" % (minutes, t_str)
        return str
    elif seconds > 0:
        if seconds == 1:
            t_str = "sec"
        else:
            t_str = "secs"
        str += "%s %s" % (seconds, t_str)
        return str
    else:
        return None


def convert_size(size):
    """Convert Bytes to a readable format"""

    size_name = ("B", "KB", "MB", "GB", "TB", "PB", "EB", "ZB", "YB")
    i = int(math.floor(math.log(size, 1024)))
    p = math.pow(1024, i)
    s = round(size / p, 2)
    if s > 0:
        return '%s %s' % (s, size_name[i])
    else:
        return '0B'
