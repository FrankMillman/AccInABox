class AibError(Exception):
    """Base class for errors in AccInABox."""
    def __init__(self, *, head, body):  # must be keyword arguments
        self.head = head
        self.body = body

    def __str__(self):
        return '{}: {}'.format(self.head, self.body)

class AibPerms(AibError):
    """Database permissions error in AccInABox."""
    pass
