import sys

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
