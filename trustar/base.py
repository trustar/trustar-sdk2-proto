from collections import namedtuple
from datetime import datetime
import pytz
import functools
import inspect

from enum import Enum


def get_timestamp(date):
    timestamp = (date - datetime(1970, 1, 1, tzinfo=pytz.UTC)).total_seconds()
    return int(timestamp)


class Methods(Enum):
    POST = 1
    GET = 2
    DELETE = 3
    UPDATE = 4
    PUT = 5


def chained(method):
    """Method decorator to allow chaining."""
    @functools.wraps(method)
    def wrapper(self, *args, **kwargs):
        result = method(self, *args, **kwargs)
        return self if result is None else result
    return wrapper


def fluent(cls):
    """Class decorator to allow method chaining."""
    for name, member in cls.__dict__.items():
        if inspect.isfunction(member) and name.startswith("set_"):
            setattr(cls, name, chained(member))
    return cls


Param = namedtuple('Param', 'key value')


class Params:

    def __init__(self, *args):
        self._dict = {}
        for arg in args:
            self.add(arg)

    def __repr__(self):
        elements = map(repr, self._dict.keys())
        return "%s(%s)" % (self.__class__.__name__, ', '.join(elements))

    def extend(self, args):
        """ Add several items at once. """
        for arg in args:
            self.add(arg)

    def add(self, item):
        """ Add one item to the set. """
        self._dict[item.key] = item

    def get(self, key, default=None):
        try:
            return self._dict[key].value
        except KeyError:
            return default

    def remove(self, item):
        """ Remove an item from the set. """
        del self._dict[item]

    def contains(self, item):
        """ Check whether the set contains a certain item. """
        return item in self._dict.keys()

    # High-performance membership test for Python 2.0 and later
    __contains__ = contains

    def __getitem__(self, index):
        """ Support the 'for item in set:' protocol. """
        return list(self._dict.keys())[index]

    def __iter__(self):
        return iter([value for key, value in self._dict.items()])

    def __len__(self):
        """ Return the number of items in the set """
        return len(self._dict)

    def items(self):
        """ Return a list containing all items in sorted order, if possible (Python 3 only) """
        return self._dict.keys()

    def __copy__(self):
        return Params(self)
