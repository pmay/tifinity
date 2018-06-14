class Error(Exception):
    pass

class InvalidTiffError(Error):
    def __init__(self, filename, message):
        self.filename = filename
        self.message = message