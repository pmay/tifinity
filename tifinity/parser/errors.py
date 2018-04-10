class Error(Exception):
    pass

class InvalidTiffError(Error):
    def __init__(self, message):
        self.message = message