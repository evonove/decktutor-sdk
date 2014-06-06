import datetime
import importlib
import re
try:
    from urllib.parse import urlencode
except ImportError:
    from urllib import urlencode

"""
Start code from django-rest-framework compat.py module
"""

date_re = re.compile(
    r'(?P<year>\d{4})-(?P<month>\d{1,2})-(?P<day>\d{1,2})$'
)

datetime_re = re.compile(
    r'(?P<year>\d{4})-(?P<month>\d{1,2})-(?P<day>\d{1,2})'
    r'[T ](?P<hour>\d{1,2}):(?P<minute>\d{1,2})'
    r'(?::(?P<second>\d{1,2})(?:\.(?P<microsecond>\d{1,6})\d{0,6})?)?'
    r'(?P<tzinfo>Z|[+-]\d{1,2}:\d{1,2})?$'
)

time_re = re.compile(
    r'(?P<hour>\d{1,2}):(?P<minute>\d{1,2})'
    r'(?::(?P<second>\d{1,2})(?:\.(?P<microsecond>\d{1,6})\d{0,6})?)?'
)


def parse_date(value):
    match = date_re.match(value)
    if match:
        kw = dict((k, int(v)) for k, v in match.groupdict().iteritems())
        return datetime.date(**kw)


def parse_time(value):
    match = time_re.match(value)
    if match:
        kw = match.groupdict()
        if kw['microsecond']:
            kw['microsecond'] = kw['microsecond'].ljust(6, '0')
        kw = dict((k, int(v)) for k, v in kw.iteritems() if v is not None)
        return datetime.time(**kw)


def parse_datetime(value):
    """Parse datetime, but w/o the timezone awareness in 1.4"""
    match = datetime_re.match(value)
    if match:
        kw = match.groupdict()
        if kw['microsecond']:
            kw['microsecond'] = kw['microsecond'].ljust(6, '0')
        kw = dict((k, int(v)) for k, v in kw.iteritems() if v is not None)
        return datetime.datetime(**kw)
"""
End code from
"""


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
