class MLServiceError(Exception):
    def __init__(self, code: str, message: str):
        super().__init__(message)
        self.code = code
        self.message = message


class DatasetNotFoundError(MLServiceError):
    pass


class ModelNotFoundError(MLServiceError):
    pass


class DatasetValidationError(MLServiceError):
    pass


class ModelConflictError(MLServiceError):
    pass


class MLFrameworkUnavailableError(MLServiceError):
    pass


class InvalidPredictionError(MLServiceError):
    pass
