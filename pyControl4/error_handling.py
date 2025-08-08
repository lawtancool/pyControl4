"""Handles errors returned by the Control4 Director."""
import json
import logging
from xml.parsers.expat import ExpatError

import xmltodict

_LOGGER = logging.getLogger(__name__)


class C4Exception(Exception):
    """Base class for pyControl4 exceptions."""
    pass


class Unauthorized(C4Exception):
    """Raised when the bearer token is invalid or expired."""
    pass


class NotFound(C4Exception):
    """Raised when the Control4 Director returns a 404 Not Found error."""
    pass


class BadCredentials(C4Exception):
    """Raised when the username or password for the Control4 account is invalid."""
    pass


class InvalidCategory(C4Exception):
    """Raised when a category does not exist on the Control4 system."""
    pass


class C4CorruptXMLResponse(C4Exception):
    """Raised when the Control4 Director sends a malformed XML response."""
    pass


async def checkResponseForError(response_text):
    """
    Checks a response from the Control4 Director for an error message.
    Returns if no error is found.
    Raises Unauthorized or NotFound if an error is found.
    Raises C4CorruptXMLResponse if the XML is malformed.
    """
    # Check for known plain-text error messages first.
    if "Cannot GET" in response_text:
        raise NotFound(f"Endpoint not found on Director: {response_text}")

    # First, try to parse the response as JSON, as some controllers return this.
    try:
        dictionary = json.loads(response_text)
        if "status_code" in dictionary:
            if dictionary["status_code"] == 404:
                raise NotFound("404 Not Found from Control4 Director.")
        if "error" in dictionary:
            if "Invalid category" in dictionary["error"]:
                raise InvalidCategory(dictionary["error"])
        # If it's valid JSON but not an error, we can return.
        return
    except json.JSONDecodeError:
        # Not a JSON response, so we'll try to parse it as XML.
        pass

    # If JSON parsing fails, try to parse the response as XML.
    try:
        dictionary = xmltodict.parse(response_text)
    except ExpatError as e:
        _LOGGER.error(
            (
                "Failed to parse XML response from Director due to a mismatched tag or other corruption. "
                "The raw text received from the controller was: \n%s"
            ),
            response_text,
        )
        # Re-raise the original error so the integration still fails as expected
        raise e
    except Exception:
        # Not a valid XML response, so it can't be a C4 error message.
        return

    # Check for C4 errors in the parsed XML
    if "c4soap" in dictionary:
        if "error" in dictionary["c4soap"]:
            error_code = int(dictionary["c4soap"]["error"])
            # 401 is Unauthorized
            if error_code == 401:
                raise Unauthorized(
                    "Invalid or expired bearer token. Re-authentication is required."
                )
            # Other error codes can be added here if necessary
            else:
                # Generic error for other codes
                raise Exception(
                    f"Control4 Director returned an unknown error: {dictionary['c4soap']['error_string']}"
                )
        return
