import sys
from json import loads
from decimal import Decimal as D
from datetime import date as dt

delwatcher_set = set()

class AibError(Exception):
    """Base class for errors in AccInABox."""
    def __init__(self, *, head, body):  # must be keyword arguments
        self.head = head
        self.body = body

    def __str__(self):
        return f'{self.head}: {self.body}'

class AibDenied(AibError):
    """Database permission denied."""
    pass

#sys.stdout = open('/dev/null', 'w')
#sys.stdout = open('nul', 'w')

#log = open('log.txt', 'w', errors='backslashreplace')
log = sys.stderr
debug = False

#db_log = open('db_log.txt', 'w', errors='backslashreplace')
db_log = sys.stderr
log_db = False

def find_occurrence(string, substring, occurrence):
    """Find position of n'th occurrence of substring in string, else -1."""

    # string - a string to be searched
    # substring - a substring to search for
    # occurrence - the occurrence to search for, starting from 0
    # if not present, return -1

    found = -1
    start_pos = 0
    while (pos := string.find(substring, start_pos)) > -1:
        found += 1
        if found == occurrence:
            break
        start_pos = pos + 1
    return pos

def deserialise(value):
    """
    JSON deserialiser - further processing after loads()
    1) JSON cannot handle datetime.date or Decimal objects
       the 'dump' was created with dumps(object, default=repr)
       this assumes that any string starting with 'datetime.date(' is a date object, and instantiates it
       this assumes that any string starting with 'Decimal(' is a Decimal object, and instantiates it
    2) JSON converts any 'integer' dict keys to strings :-(
       this assumes that any 'isdigit' dict key was originally an integer, and converts it back to an int
    3) JSON converts a None dict key to the string 'null' (*not* the JSON null)
       this assumes that a dict key of 'null' was originally None, and converts it back
    """
    def deserialise_list(value):
        new_val = []
        for val in value:
            if isinstance(val, str):
                if val.startswith('datetime.date('):
                    new_val.append(dt(*map(int, val[14:-1].split(','))))
                elif val.startswith('Decimal('):
                    new_val.append(D(val[9:-2]))
                else:
                    new_val.append(val)
            elif isinstance(val, list):
                new_val.append(deserialise_list(val))
            elif isinstance(val, dict):
                new_val.append(deserialise_dict(val))
            else:  # e.g. None
                new_val.append(val)
        return new_val
    def deserialise_dict(value):
        new_val = {}
        for key, val in value.items():
            if key.isdigit():
                key = int(key)
            elif key == 'null':
                key = None
            if isinstance(val, str):
                if val.startswith('datetime.date('):
                    new_val[key] = dt(*map(int, val[14:-1].split(',')))
                elif val.startswith('Decimal('):
                    new_val[key] = D(val[9:-2])
                else:
                    new_val[key] = val
            elif isinstance(val, list):
                new_val[key] = deserialise_list(val)
            elif isinstance(val, dict):
                new_val[key] = deserialise_dict(val)
            else:  # e.g. None
                new_val[key] = val
        return new_val
    value = loads(value)
    if isinstance(value, list):
        value = deserialise_list(value)
    elif isinstance(value, dict):
        value = deserialise_dict(value)
    return value

# thanks to Ian Kelly for this one
from itertools import count
async def aenumerate(aiterable, start=0):
    counter = count(start)
    async for x in aiterable:
        yield next(counter), x
