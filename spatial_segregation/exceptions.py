class SpatialSegregationException(Exception):
    pass


class KDEException(SpatialSegregationException):
    pass


class DataException(SpatialSegregationException):
    pass


class SegregationIndicesException(SpatialSegregationException):
    pass


class AnalysesException(SpatialSegregationException):
    pass


class SegregationSurfaceAnalysisException(SpatialSegregationException):
    pass


class SegregationIndexAnalysisException(SpatialSegregationException):
    pass


class UtilsException(SpatialSegregationException):
    pass
