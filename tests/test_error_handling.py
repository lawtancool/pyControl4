"""Tests for error_handling.py — all branches of check_response_for_error."""

import json

import pytest

from pyControl4.error_handling import (
    BadCredentials,
    BadToken,
    C4Exception,
    InvalidCategory,
    NotFound,
    Unauthorized,
    check_response_for_error,
)

# --- Happy paths (no exception raised) ---


def test_json_no_error_keys():
    """JSON response without error keys should not raise."""
    check_response_for_error(json.dumps({"result": "ok"}))


def test_xml_no_error_keys():
    """XML response without error keys should not raise."""
    check_response_for_error("<result>ok</result>")


# --- C4ErrorResponse format ---


def test_c4error_bad_credentials():
    """C4ErrorResponse with matching details raises BadCredentials."""
    payload = json.dumps(
        {
            "C4ErrorResponse": {
                "code": 401,
                "details": "Permission denied Bad credentials",
                "message": "Permission denied",
            }
        }
    )
    with pytest.raises(BadCredentials):
        check_response_for_error(payload)


def test_c4error_401_no_matching_details():
    """C4ErrorResponse with code 401 but non-matching details raises Unauthorized."""
    payload = json.dumps(
        {
            "C4ErrorResponse": {
                "code": 401,
                "details": "",
                "message": "Permission denied",
            }
        }
    )
    with pytest.raises(Unauthorized):
        check_response_for_error(payload)


def test_c4error_404():
    """C4ErrorResponse with code 404 raises NotFound."""
    payload = json.dumps(
        {
            "C4ErrorResponse": {
                "code": 404,
                "message": "Not found",
            }
        }
    )
    with pytest.raises(NotFound):
        check_response_for_error(payload)


def test_c4error_unknown_code_falls_back_to_base():
    """C4ErrorResponse with unrecognized code raises exactly C4Exception (not a subclass)."""
    payload = json.dumps(
        {
            "C4ErrorResponse": {
                "code": 999,
                "message": "Unknown error",
            }
        }
    )
    with pytest.raises(C4Exception) as exc_info:
        check_response_for_error(payload)
    assert type(exc_info.value) is C4Exception


# --- Flat JSON code format ---


def test_flat_json_404():
    """Flat JSON with code 404 raises NotFound."""
    payload = json.dumps({"code": 404, "message": "Account not found"})
    with pytest.raises(NotFound):
        check_response_for_error(payload)


def test_flat_json_bad_credentials():
    """Flat JSON with matching details raises BadCredentials (details take priority)."""
    payload = json.dumps(
        {
            "code": 401,
            "details": "Permission denied Bad credentials",
            "message": "Permission denied",
        }
    )
    with pytest.raises(BadCredentials):
        check_response_for_error(payload)


# --- Director error format ---


def test_director_error_bad_token():
    """Director error with matching details raises BadToken."""
    payload = json.dumps(
        {"error": "Unauthorized", "details": "Expired or invalid token"}
    )
    with pytest.raises(BadToken):
        check_response_for_error(payload)


def test_director_error_unauthorized_no_matching_details():
    """Director 'Unauthorized' without matching details raises Unauthorized."""
    payload = json.dumps({"error": "Unauthorized"})
    with pytest.raises(Unauthorized):
        check_response_for_error(payload)


def test_director_error_invalid_category():
    """Director 'Invalid category' raises InvalidCategory."""
    payload = json.dumps({"error": "Invalid category"})
    with pytest.raises(InvalidCategory):
        check_response_for_error(payload)


def test_director_error_unknown_falls_back_to_base():
    """Director error with unrecognized string raises exactly C4Exception (not a subclass)."""
    payload = json.dumps({"error": "Something else"})
    with pytest.raises(C4Exception) as exc_info:
        check_response_for_error(payload)
    assert type(exc_info.value) is C4Exception


# --- XML C4ErrorResponse ---


def test_xml_c4error_401():
    """XML C4ErrorResponse with code 401 raises Unauthorized."""
    xml = (
        '<?xml version="1.0" encoding="UTF-8" standalone="yes"?>'
        "<C4ErrorResponse>"
        "<code>401</code>"
        "<details></details>"
        "<message>Permission denied</message>"
        "<subCode>0</subCode>"
        "</C4ErrorResponse>"
    )
    with pytest.raises(Unauthorized):
        check_response_for_error(xml)


# --- Exception hierarchy and behavior ---


def test_exception_hierarchy():
    """Verify the exception inheritance chain."""
    assert issubclass(BadCredentials, Unauthorized)
    assert issubclass(BadToken, Unauthorized)
    assert issubclass(Unauthorized, C4Exception)
    assert issubclass(NotFound, C4Exception)
    assert issubclass(InvalidCategory, C4Exception)
    assert issubclass(C4Exception, Exception)


def test_exception_stores_message():
    """C4Exception stores the response text as .message."""
    exc = C4Exception("some response text")
    assert exc.message == "some response text"


def test_raised_exception_preserves_response_text():
    """Exception raised by check_response_for_error carries the original response."""
    payload = json.dumps({"error": "Invalid category"})
    with pytest.raises(InvalidCategory) as exc_info:
        check_response_for_error(payload)
    assert exc_info.value.message == payload
