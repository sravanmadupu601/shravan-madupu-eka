class MCPServiceError(Exception):
    def __init__(self, code: str, message: str):
        super().__init__(message)
        self.code = code
        self.message = message


class DownstreamUnavailableError(MCPServiceError):
    pass


class DownstreamResponseError(MCPServiceError):
    pass


class DocumentNotFoundError(MCPServiceError):
    pass


class InvalidToolInputError(MCPServiceError):
    pass
