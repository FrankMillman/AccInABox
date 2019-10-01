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

# find position of n'th occurrence of substring in string, else -1
def find_occurrence(string, substring, occurrence):
    # string - a string to be searched
    # substring - a substring to search for
    # occurrence - the occurrence to search for, starting from 0
    # if not present, return -1
    found = 0
    return_value = -1
    start_pos = 0
    pos = string.find(substring)
    while pos > -1:
        return_value = pos + start_pos
        if found == occurrence:
            break
        found += 1
        start_pos += (pos + 1)
        pos = string[start_pos:].find(substring)
        if pos == -1:
            return_value = -1
    return return_value
