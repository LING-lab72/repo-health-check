"""Tests for clone service."""
from pathlib import Path
from unittest.mock import MagicMock, patch

import pytest

from backend.services.clone import _run_clone, _test_github_direct, validate_url, InvalidURLError


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


@patch("backend.services.clone.subprocess.run")
def test_direct_probe_puts_git_config_before_subcommand(mock_run):
    mock_run.return_value = MagicMock(returncode=0)

    assert _test_github_direct(timeout=1) is True

    cmd = mock_run.call_args.args[0]
    assert cmd[:5] == ["git", "-c", "http.proxy=", "-c", "https.proxy="]
    assert cmd[5] == "ls-remote"


@patch("backend.services.clone.subprocess.run")
def test_clone_puts_git_config_before_clone_subcommand(mock_run, tmp_path: Path):
    mock_run.return_value = MagicMock(returncode=0, stderr="")

    _run_clone("https://github.com/psf/requests", tmp_path / "requests", tmp_path)

    cmd = mock_run.call_args.args[0]
    assert cmd[:5] == ["git", "-c", "http.proxy=", "-c", "https.proxy="]
    assert cmd[5] == "clone"
