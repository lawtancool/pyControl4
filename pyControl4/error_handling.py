"""Handles errors received from the Control4 API."""

from __future__ import annotations

from typing import Any

import json
import xmltodict


class C4Exception(Exception):
    """Base error for pyControl4."""

    def __init__(self, message: str) -> None:
        self.message = message


class NotFound(C4Exception):
    """Raised when a 404 response is received from the Control4 API.
    Occurs when the requested controller, etc. could not be found."""


class Unauthorized(C4Exception):
    """Raised when unauthorized, but no other recognized details are provided.
    Occurs when token is invalid."""


class BadCredentials(Unauthorized):
    """Raised when provided credentials are incorrect."""


class BadToken(Unauthorized):
    """Raised when director bearer token is invalid."""


class InvalidCategory(C4Exception):
    """Raised when an invalid category is provided when calling
    `pyControl4.director.C4Director.get_all_items_by_category`."""


ERROR_CODES = {"401": Unauthorized, "404": NotFound}

ERROR_DETAILS = {
    "Permission denied Bad credentials": BadCredentials,
}

DIRECTOR_ERRORS = {"Unauthorized": Unauthorized, "Invalid category": InvalidCategory}

DIRECTOR_ERROR_DETAILS = {"Expired or invalid token": BadToken}


def _check_response_format(response_text: str) -> str:
    """Known Control4 authentication API error message formats:
    ```json
    {
        "C4ErrorResponse": {
            "code": 401,
            "details": "Permission denied Bad credentials",
            "message": "Permission denied",
            "subCode": 0
        }
    }
    ```
    ```json
    {
        "code": 404,
        "details": "Account with id:000000 not found in DB",
        "message": "Account not found",
        "subCode": 0
    }```
    ```xml
    <?xml version="1.0" encoding="UTF-8" standalone="yes"?>
    <C4ErrorResponse>
        <code>401</code>
        <details></details>
        <message>Permission denied</message>
        <subCode>0</subCode>
    </C4ErrorResponse>
    ```
    Known Control4 director error message formats:
    ```json
    {
        "error": "Unauthorized",
        "details": "Expired or invalid token"
    }
    ```
    """
    if response_text.startswith("<"):
        return "XML"
    return "JSON"


def _extract_error_info(dictionary: dict[str, Any]) -> dict[str, Any] | None:
    """Extract error information from a parsed Control4 response.

    Returns a dict with 'details', 'code', or 'error' key, or None if no error found.
    """
    # Check for C4ErrorResponse format
    if "C4ErrorResponse" in dictionary:
        error_resp = dictionary.get("C4ErrorResponse", {})
        return {
            "details": error_resp.get("details"),
            "code": error_resp.get("code"),
            "type": "C4ErrorResponse",
        }

    # Check for direct code format
    if "code" in dictionary:
        return {
            "details": dictionary.get("details"),
            "code": dictionary.get("code"),
            "type": "code",
        }

    # Check for error format (director)
    if "error" in dictionary:
        return {
            "details": dictionary.get("details"),
            "error": dictionary.get("error"),
            "type": "error",
        }

    return None


def _raise_error(error_info: dict[str, Any], response_text: str) -> None:
    """Raise appropriate exception based on error info."""
    details = error_info.get("details")
    code = error_info.get("code")
    error = error_info.get("error")

    # Try to match by details first (most specific)
    if details:
        if details in ERROR_DETAILS:
            raise ERROR_DETAILS[details](response_text)
        if details in DIRECTOR_ERROR_DETAILS:
            raise DIRECTOR_ERROR_DETAILS[details](response_text)

    # Try to match by code/error (less specific)
    if code is not None:
        raise ERROR_CODES.get(str(code), C4Exception)(response_text)
    if error is not None:
        raise DIRECTOR_ERRORS.get(str(error), C4Exception)(response_text)

    # If nothing matched, raise generic error
    raise C4Exception(response_text)


def check_response_for_error(response_text: str) -> None:
    """Checks a string response from the Control4 API for error codes.

    Parameters:
        `response_text` - JSON or XML response from Control4, as a string.
    """
    response_format = _check_response_format(response_text)

    if response_format == "JSON":
        dictionary = json.loads(response_text)
    else:  # XML
        dictionary = xmltodict.parse(response_text)

    error_info = _extract_error_info(dictionary)
    if error_info:
        _raise_error(error_info, response_text)
