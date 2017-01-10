class SpatialSegregationException(Exception):
    pass


class SSTypeError(TypeError, SpatialSegregationException):
    pass


class SSIndexError(IndexError, SpatialSegregationException):
    pass


class SSIOError(IOError, SpatialSegregationException):
    pass


class SSNotImplementedError(NotImplementedError, SpatialSegregationException):
    pass


class SSValueError(ValueError, SpatialSegregationException):
    pass


class SSKeyError(KeyError, SpatialSegregationException):
    pass
