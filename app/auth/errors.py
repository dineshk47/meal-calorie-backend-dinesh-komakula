from fastapi.responses import JSONResponse
from typing import Any, Union


# Success Response Handler
def success_response(
    status_code: str, data: Union[str, list, dict], http_status_code: int = 200
) -> JSONResponse:
    """
    Create a standardized success response.
    :param status_code: The internal status code (e.g., "CE20101")
    :param data: A dictionary containing the response data
    :param http_status_code: The HTTP status code to return (default is 200)
    :return: JSONResponse with success structure
    """
    return JSONResponse(
        content={"status": status_code, "data": data},
        status_code=http_status_code,
    )


# Error Response Handler
def error_response(
    status_code: str, error: Union[str, list, dict], http_status_code: int
) -> JSONResponse:
    """
    Create a standardized error response.
    :param status_code: The internal error code (e.g., "CE40001")
    :param error: The error details (can be a string, list, or dict)
    :param http_status_code: The HTTP status code to return
    :return: JSONResponse with error structure
    """
    return JSONResponse(
        content={"status": status_code, "error": error},
        status_code=http_status_code,
    )
