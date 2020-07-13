"""Handles errors recieved from the Control4 API."""
import json
import xmltodict


class C4Exception(Exception):
    """Base error for pyControl4."""

    def __init__(self, message):
        self.message = message


class NotFound(C4Exception):
    """Raised when a 404 response is recieved from the Control4 API.
    Occurs when the requested controller, etc. could not be found."""


class Unauthorized(C4Exception):
    """Raised when unauthorized, but no other recognized details are provided.
    Occurs when token is invalid."""


class BadCredentials(Unauthorized):
    """Raised when provided credentials are incorrect."""


class BadToken(Unauthorized):
    """Raised when director bearer token is invalid."""


ERROR_CODES = {"401": Unauthorized, "404": NotFound}

ERROR_DETAILS = {
    "Permission denied Bad credentials": BadCredentials,
}

DIRECTOR_ERRORS = {
    "Unauthorized": Unauthorized,
}

DIRECTOR_ERROR_DETAILS = {"Expired or invalid token": BadToken}


async def __checkResponseFormat(response_text: str):
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


async def checkResponseForError(response_text: str):
    """Checks a string response from the Control4 API for error codes.

    Parameters:
        `response_text` - JSON or XML response from Control4, as a string.
    """
    if await __checkResponseFormat(response_text) == "JSON":
        dictionary = json.loads(response_text)
    elif await __checkResponseFormat(response_text) == "XML":
        dictionary = xmltodict.parse(response_text)
    if "C4ErrorResponse" in dictionary:
        if dictionary["C4ErrorResponse"]["details"] in ERROR_DETAILS:
            exception = ERROR_DETAILS.get(dictionary["C4ErrorResponse"]["details"])
            raise exception(response_text)
        else:
            exception = ERROR_CODES.get(
                str(dictionary["C4ErrorResponse"]["code"]), C4Exception
            )
            raise exception(response_text)
    elif "code" in dictionary:
        if dictionary["details"] in ERROR_DETAILS:
            exception = ERROR_DETAILS.get(dictionary["details"])
            raise exception(response_text)
        else:
            exception = ERROR_CODES.get(str(dictionary["code"]), C4Exception)
            raise exception(response_text)
    elif "error" in dictionary:
        if dictionary["details"] in DIRECTOR_ERROR_DETAILS:
            exception = DIRECTOR_ERROR_DETAILS.get(dictionary["details"])
            raise exception(response_text)
        else:
            exception = DIRECTOR_ERRORS.get(str(dictionary["error"]), C4Exception)
            raise exception(response_text)
