import importlib
import re
import pytz
import six
from datetime import datetime, timedelta, tzinfo

try:
    from urllib.parse import urlencode
except ImportError:
    from urllib import urlencode


"""
Start code from django utils/dateparse.py and utils/timezone.pymodule
"""
ZERO = timedelta(0)
utc = pytz.utc


class FixedOffset(tzinfo):
    """
    Fixed offset in minutes east from UTC. Taken from Python's docs.

    Kept as close as possible to the reference version. __init__ was changed
    to make its arguments optional, according to Python's requirement that
    tzinfo subclasses can be instantiated without arguments.
    """

    def __init__(self, offset=None, name=None):
        if offset is not None:
            self.__offset = timedelta(minutes=offset)
        if name is not None:
            self.__name = name

    def utcoffset(self, dt):
        return self.__offset

    def tzname(self, dt):
        return self.__name

    def dst(self, dt):
        return ZERO


def get_fixed_timezone(offset):
    """
    Returns a tzinfo instance with a fixed offset from UTC.
    """
    if isinstance(offset, timedelta):
        offset = offset.seconds // 60
    sign = '-' if offset < 0 else '+'
    hhmm = '%02d%02d' % divmod(abs(offset), 60)
    name = sign + hhmm
    return FixedOffset(offset, name)

date_re = re.compile(
    r'(?P<year>\d{4})-(?P<month>\d{1,2})-(?P<day>\d{1,2})$'
)

time_re = re.compile(
    r'(?P<hour>\d{1,2}):(?P<minute>\d{1,2})'
    r'(?::(?P<second>\d{1,2})(?:\.(?P<microsecond>\d{1,6})\d{0,6})?)?'
)

datetime_re = re.compile(
    r'(?P<year>\d{4})-(?P<month>\d{1,2})-(?P<day>\d{1,2})'
    r'[T ](?P<hour>\d{1,2}):(?P<minute>\d{1,2})'
    r'(?::(?P<second>\d{1,2})(?:\.(?P<microsecond>\d{1,6})\d{0,6})?)?'
    r'(?P<tzinfo>Z|[+-]\d{2}(?::?\d{2})?)?$'
)


def parse_date(value):
    """Parses a string and return a datetime.date.

    Raises ValueError if the input is well formatted but not a valid date.
    Returns None if the input isn't well formatted.
    """
    match = date_re.match(value)
    if match:
        kw = dict((k, int(v)) for k, v in six.iteritems(match.groupdict()))
        return datetime.date(**kw)


def parse_time(value):
    """Parses a string and return a datetime.time.

    This function doesn't support time zone offsets.

    Raises ValueError if the input is well formatted but not a valid time.
    Returns None if the input isn't well formatted, in particular if it
    contains an offset.
    """
    match = time_re.match(value)
    if match:
        kw = match.groupdict()
        if kw['microsecond']:
            kw['microsecond'] = kw['microsecond'].ljust(6, '0')
        kw = dict((k, int(v)) for k, v in six.iteritems(kw) if v is not None)
        return datetime.time(**kw)


def parse_datetime(value):
    """Parses a string and return a datetime.datetime.

    This function supports time zone offsets. When the input contains one,
    the output uses a timezone with a fixed offset from UTC.

    Raises ValueError if the input is well formatted but not a valid datetime.
    Returns None if the input isn't well formatted.
    """
    match = datetime_re.match(value)
    if match:
        kw = match.groupdict()
        if kw['microsecond']:
            kw['microsecond'] = kw['microsecond'].ljust(6, '0')
        tzinfo = kw.pop('tzinfo')
        if tzinfo == 'Z':
            tzinfo = utc
        elif tzinfo is not None:
            offset_mins = int(tzinfo[-2:]) if len(tzinfo) > 3 else 0
            offset = 60 * int(tzinfo[1:3]) + offset_mins
            if tzinfo[0] == '-':
                offset = -offset
            tzinfo = get_fixed_timezone(offset)
        kw = dict((k, int(v)) for k, v in six.iteritems(kw) if v is not None)
        kw['tzinfo'] = tzinfo
        return datetime(**kw)
"""
End code from
"""


def time_now():
    return datetime.utcnow().replace(tzinfo=utc)


def join_url(url, *paths):
    """
    Joins individual URL strings together, and returns a single string.

    >>> util.join_url("example.com", "index.html")
    'example.com/index.html'
    """
    for path in paths:
        url = re.sub(r'/?$', re.sub(r'^/?', '/', path), url)
    return url


def join_url_params(url, params):
    return url + "?" + urlencode(params)


def merge_dict(data, *override):
    """
    Merges any number of dictionaries together, and returns a single dictionary

    >>> util.merge_dict ({"foo": "bar"}, {1: 2}, {"Pay": "Pal"})
    {1: 2, 'foo': 'bar', 'Pay': 'Pal'}
    >>>
    """
    result = {}
    for current_dict in (data,) + override:
        result.update(current_dict)
    return result


def load_class(full_class_string):
    """
    dynamically load a class from a string
    """
    class_data = full_class_string.split(".")
    module_path = ".".join(class_data[:-1])
    class_str = class_data[-1]

    module = importlib.import_module(module_path)
    # Finally, we retrieve the Class
    return getattr(module, class_str)
