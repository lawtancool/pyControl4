import pytest

from pyControl4.director import C4Director


@pytest.fixture
def director():
    """Create a C4Director with no real session (for mocked tests)."""
    return C4Director("192.168.1.1", "test-token")
