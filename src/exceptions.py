class SpatSegException(Exception):
    pass


class SpatSegTypeError(TypeError, SpatSegException):
    pass


class SpatSegIndexError(IndexError, SpatSegException):
    pass


class SpatSegIOError(IOError, SpatSegException):
    pass


class SpatSegNotImplementedError(NotImplementedError, SpatSegException):
    pass


class SpatSegValueError(ValueError, SpatSegException):
    pass


class SpatSegKeyError(KeyError, SpatSegException):
    pass
