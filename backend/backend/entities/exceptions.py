class IllegalArgumentException(Exception):
    def __init__(self, message):
        self.message = message
        super().__init__(self.message)

class IllegalStateException(Exception):
    def __init__(self, message):
        self.message = message
        super().__init__(self.message)

class NotFoundException(Exception):
    def __init__(self, message):
        self.message = message
        super().__init__(self.message)

class DatabaseConflictError(Exception):
    def __init__(self, message):
        self.message = message
        super().__init__(self.message)

class UnauthorizedError(Exception):
    def __init__(self, message):
        self.message = message
        super().__init__(self.message)
