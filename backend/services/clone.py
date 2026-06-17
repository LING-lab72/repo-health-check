"""GitHub repository cloning service."""
from __future__ import annotations

import logging
import os
import re
import shutil
import socket
import subprocess
import tempfile
from pathlib import Path
from urllib.parse import urlparse

GITHUB_URL_PATTERN = re.compile(r"^https?://github\.com/[\w.-]+/[\w.-]+/?$", re.IGNORECASE)
CLONE_TIMEOUT = 120
DIRECT_CONNECT_TIMEOUT = 15  # seconds to wait before giving up on direct connection

logger = logging.getLogger("backend.clone")


def _get_proxy() -> str | None:
    """Get proxy URL from environment or .env file.

    Checks GIT_HTTP_PROXY, https_proxy, HTTPS_PROXY, http_proxy, HTTP_PROXY
    in that order. Also reads .env file directly if dotenv hasn't loaded yet.
    """
    # Check environment variables first
    proxy = (
        os.environ.get("GIT_HTTP_PROXY")
        or os.environ.get("https_proxy")
        or os.environ.get("HTTPS_PROXY")
        or os.environ.get("http_proxy")
        or os.environ.get("HTTP_PROXY")
    )
    if proxy:
        return proxy

    # Fallback: read .env file directly (in case load_dotenv hasn't run yet)
    env_path = Path(__file__).resolve().parent.parent.parent.parent / ".env"
    if env_path.exists():
        for line in env_path.read_text(encoding="utf-8").splitlines():
            line = line.strip()
            if line.startswith("#") or "=" not in line:
                continue
            key, _, value = line.partition("=")
            key = key.strip()
            value = value.strip()
            if key in ("GIT_HTTP_PROXY", "https_proxy", "HTTPS_PROXY", "http_proxy", "HTTP_PROXY") and value:
                return value

    return None


def _is_proxy_reachable(proxy_url: str, timeout: float = 3.0) -> bool:
    """Check if the proxy server is actually listening and reachable."""
    try:
        parsed = urlparse(proxy_url)
        host = parsed.hostname or "127.0.0.1"
        port = parsed.port or 7890
        with socket.create_connection((host, port), timeout=timeout):
            return True
    except (socket.timeout, ConnectionRefusedError, OSError):
        return False


def _test_github_direct(timeout: int = DIRECT_CONNECT_TIMEOUT) -> bool:
    """Test if GitHub is reachable WITHOUT any proxy.

    Uses git ls-remote with -c http.proxy="" to override global proxy config,
    ensuring a true direct-connection test.
    """
    try:
        result = subprocess.run(
            [
                "git", "ls-remote", "--heads",
                "-c", "http.proxy=",       # override global proxy to empty
                "-c", "https.proxy=",
                "https://github.com/torvalds/linux.git",
            ],
            capture_output=True,
            text=True,
            timeout=timeout,
        )
        return result.returncode == 0
    except (subprocess.TimeoutExpired, Exception):
        return False


class CloneError(Exception):
    """Raised when cloning fails."""
    pass


class InvalidURLError(CloneError):
    """Raised for invalid repo URL."""
    pass


class CloneTimeoutError(CloneError):
    """Raised when clone exceeds timeout."""
    pass


def validate_url(url: str) -> str:
    """Validate and normalize a GitHub repository URL.

    Returns the stripped URL if valid, raises InvalidURLError otherwise.
    """
    url = url.strip().rstrip("/")
    if not url:
        raise InvalidURLError("Repository URL is empty")
    if not GITHUB_URL_PATTERN.match(url):
        raise InvalidURLError(f"Invalid GitHub URL: {url}. Must be https://github.com/owner/repo")
    return url


def _run_clone(url: str, dest: Path, base_dir: Path, proxy: str | None = None) -> None:
    """Execute git clone command.

    Args:
        url: Repository URL to clone.
        dest: Destination path for the cloned repo.
        base_dir: Working directory for the git command.
        proxy: Optional proxy URL to use for the clone.

    Raises:
        CloneError: If the clone command fails.
        CloneTimeoutError: If the clone exceeds the timeout.
    """
    cmd = ["git", "clone", "--depth", "1", "--filter=blob:none", "--quiet"]
    if proxy:
        cmd += ["-c", f"http.proxy={proxy}", "-c", f"https.proxy={proxy}"]
    else:
        # Explicitly clear any global proxy config for this clone
        cmd += ["-c", "http.proxy=", "-c", "https.proxy="]
    cmd += [url, str(dest)]

    try:
        result = subprocess.run(
            cmd,
            capture_output=True,
            text=True,
            timeout=CLONE_TIMEOUT,
            cwd=str(base_dir),
        )

        if result.returncode != 0:
            stderr = result.stderr.strip() or "Unknown error"
            raise CloneError(f"Git clone failed: {stderr}")

    except subprocess.TimeoutExpired:
        shutil.rmtree(base_dir, ignore_errors=True)
        raise CloneTimeoutError(f"Clone timed out after {CLONE_TIMEOUT}s")

    except CloneError:
        shutil.rmtree(base_dir, ignore_errors=True)
        raise

    except Exception as e:
        shutil.rmtree(base_dir, ignore_errors=True)
        raise CloneError(f"Clone failed: {e}")


def clone_repo(url: str) -> tuple[Path, str]:
    """Clone a GitHub repository to a temporary directory.

    Strategy (auto-fallback):
        1. Test if GitHub is directly reachable (bypassing any global proxy).
        2. If direct works → clone without proxy (fastest, no dependency).
        3. If direct fails → check if a proxy is configured AND reachable.
        4. If proxy is reachable → clone with proxy.
        5. If proxy configured but NOT reachable → suggest user start proxy.
        6. If no proxy at all → try direct clone anyway (GitHub occasionally
           works in China) and give a helpful error on failure.

    Args:
        url: GitHub repository URL (e.g. https://github.com/owner/repo).

    Returns:
        (repo_path, repo_name) tuple. Path is inside a TemporaryDirectory.

    Raises:
        InvalidURLError: URL is not a valid GitHub URL.
        CloneTimeoutError: Clone exceeded 60 seconds.
        CloneError: Other clone failures.
    """
    url = validate_url(url)
    repo_name = url.rstrip("/").split("/")[-1]

    # Create temp directory for the clone
    base_dir = Path(tempfile.mkdtemp(prefix="repo-check-"))
    dest = base_dir / repo_name

    proxy = _get_proxy()

    # Step 1: Quick connectivity test — can we reach GitHub directly?
    can_direct = _test_github_direct()

    if can_direct:
        logger.info("GitHub is directly reachable, cloning without proxy")
        _run_clone(url, dest, base_dir, proxy=None)
    elif proxy and _is_proxy_reachable(proxy):
        logger.info(f"GitHub not directly reachable, using proxy: {proxy}")
        _run_clone(url, dest, base_dir, proxy=proxy)
    elif proxy and not _is_proxy_reachable(proxy):
        # Proxy configured but not running
        logger.warning(f"Proxy {proxy} configured but not reachable")
        raise CloneError(
            "无法连接 GitHub，且配置的代理未启动。请尝试：\n"
            f"1. 启动代理服务（当前配置: {proxy}）\n"
            "2. 等待网络恢复后重试（GitHub 在国内偶尔可以直连）\n"
            "3. 使用 /api/analyze/local 接口分析本地仓库（无需网络）"
        )
    else:
        # No proxy available, try direct clone as last resort
        logger.warning("GitHub not reachable and no proxy configured, attempting direct clone")
        try:
            _run_clone(url, dest, base_dir, proxy=None)
        except CloneError:
            raise CloneError(
                "无法连接 GitHub，且未配置代理。请尝试：\n"
                "1. 开启代理（如 Clash）并在 .env 中设置 GIT_HTTP_PROXY=http://127.0.0.1:7890\n"
                "2. 等待网络恢复后重试（GitHub 在国内偶尔可以直连）\n"
                "3. 使用 /api/analyze/local 接口分析本地仓库（无需网络）"
            )

    # Check clone was successful
    if not dest.exists() or not (dest / ".git").exists():
        shutil.rmtree(base_dir, ignore_errors=True)
        raise CloneError(f"Clone verification failed for {url}")

    return dest, repo_name
