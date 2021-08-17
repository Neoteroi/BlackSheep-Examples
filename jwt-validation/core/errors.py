from http.client import HTTPResponse


class AppException(Exception):
    """Base class for all exception risen by the application."""


class FailedRequestError(AppException):
    def __init__(self, response: HTTPResponse) -> None:
        super().__init__(
            f"Response status does not indicate success: {response.status}"
        )
        self.status = response.status
        self.data = response.read()
