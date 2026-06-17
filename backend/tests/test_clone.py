"""Tests for clone service."""
import pytest

from backend.services.clone import validate_url, InvalidURLError


def test_validate_valid_url():
    url = validate_url("https://github.com/psf/requests")
    assert url == "https://github.com/psf/requests"


def test_validate_url_with_trailing_slash():
    url = validate_url("https://github.com/psf/requests/")
    assert url == "https://github.com/psf/requests"


def test_validate_empty_url():
    with pytest.raises(InvalidURLError, match="empty"):
        validate_url("")


def test_validate_invalid_url():
    with pytest.raises(InvalidURLError, match="Invalid GitHub URL"):
        validate_url("https://gitlab.com/user/repo")


def test_validate_not_a_url():
    with pytest.raises(InvalidURLError, match="Invalid GitHub URL"):
        validate_url("not-a-url")
