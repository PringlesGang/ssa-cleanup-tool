class NotAFileException(Exception):
    """Raised when a path does not lead to a file."""
    pass


class NotADirectoryException(Exception):
    """Raised when a path does not lead to a directory."""
    pass


class InvalidOutputNamesCountException(Exception):
    """Raised when the amount of output names does not equal the amount of input files."""
    pass
