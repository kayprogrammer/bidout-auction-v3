from http import HTTPStatus
from typing import Optional
from starlite import HTTPException, ValidationException, Response, Request, status_codes


class Error(Exception):
    """Base class for exceptions in this module."""

    pass


class RequestError(Error):
    def __init__(self, status_code: int, error_msg: Optional[str] = None):
        self.status_code = HTTPStatus(status_code)
        self.error_msg = error_msg


class RequestErrorHandler:
    def __init__(self, exc: RequestError):
        self.status_code = exc.status_code
        self.error_msg = exc.error_msg

    def process_message(self):
        return Response(
            status_code=self.status_code,
            content={
                "status": "failure",
                "message": self.error_msg,
            },
        )


def http_exception_handler(request: Request, exc: HTTPException) -> Response:
    return Response(
        content={"status": "failure", "message": exc.detail},
        status_code=exc.status_code,
    )


def validation_exception_handler(
    request: Request, exc: ValidationException
) -> Response:
    # Get the original 'detail' list of errors
    details = exc.extra
    modified_details = {}
    for error in details:
        try:
            field_name = error["loc"][1]
        except:
            field_name = error["loc"][0]

        modified_details[f"{field_name}"] = error["msg"]
    return Response(
        status_code=status_codes.HTTP_422_UNPROCESSABLE_ENTITY,
        content={
            "status": "failure",
            "message": "Invalid Entry",
            "data": modified_details,
        },
    )


def internal_server_error_handler(request: Request, exc: Exception) -> Response:
    print(exc)
    return Response(
        content={
            "status": "failure",
            "message": "Server Error",
        },
        status_code=500,
    )
