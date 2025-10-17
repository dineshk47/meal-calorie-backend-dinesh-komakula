from app.auth.errors import error_response
from fastapi import HTTPException, Request, status
from fastapi.responses import JSONResponse
from fastapi.exceptions import RequestValidationError
from fastapi.encoders import jsonable_encoder

import logging


async def validation_exception_handler(
    request: Request, exc: RequestValidationError
):
    details = exc.errors()
    modified_details = []
    # Constructing a user-friendly message
    for error in details:
        loc = error["loc"]  # Path to the error location (list of fields)

        # Initialize variables to hold parent field and field name
        parent_field = ""
        field_name = ""

        # Extract the parent field and the specific field
        if len(loc) > 1:
            parent_field = loc[-2]
            field_name = loc[-1]
        else:
            field_name = loc[-1]

        # Convert to string for safe manipulation
        parent_field_str = str(parent_field).replace("_", " ").capitalize()
        field_name_str = str(field_name).replace("_", " ").capitalize()

        # Create the full field name
        field_full_name = (
            f"{parent_field_str} {field_name_str}"
            if parent_field
            else field_name_str
        )

        # Create the custom message
        raw_message = error["msg"]
        custom_message = f"{field_full_name}: {raw_message}"

        # Append the modified details
        modified_details.append(
            {
                "loc": "->".join(map(str, loc)),
                "message": custom_message,
                "type": error["type"],
            }
        )

    # Return the custom error response using your error_response function
    return error_response(
        status_code="GE42200",
        error=modified_details,
        http_status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
    )


async def http_exception_handler(request: Request, ex: HTTPException):
    logging.exception("HTTP Exception")

    if (
        isinstance(ex.detail, dict)
        and "status" in ex.detail
        and "error" in ex.detail
    ):
        custom_status_code = ex.detail.get(
            "status", "GE50000"
        )  # Default code if missing
        error_message = ex.detail.get(
            "error", "An error occurred."
        )  # Default message if missing
    else:
        # Fallback for unexpected detail format

        custom_status_code = "GE50000"

        error_message = (
            str(ex.detail) if ex.detail else "An unexpected error occurred."
        )

    return error_response(
        status_code=custom_status_code,
        error=error_message,
        http_status_code=ex.status_code,
    )


async def exception_handler(request: Request, ex: Exception):
    logging.exception("Exception")
    error_resp = dict(
        error=True, message="Internal Server Error", type=str(ex)
    )
    return JSONResponse(
        content=error_resp, status_code=status.HTTP_500_INTERNAL_SERVER_ERROR
    )
