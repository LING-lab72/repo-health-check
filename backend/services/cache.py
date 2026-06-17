"""In-memory analysis result cache with TTL and LRU eviction."""
from __future__ import annotations

import hashlib
import threading
import time
from typing import Any


class AnalysisCache:
    """Thread-safe in-memory cache for analysis results.

    Features:
    - TTL-based expiration (default 30 minutes).
    - LRU-style eviction: removes all expired entries on capacity overflow.
    - Thread-safe with threading.Lock.
    - Maximum 100 entries.
    """

    def __init__(self, ttl: int = 1800, max_size: int = 100):
        self._cache: dict[str, tuple[dict[str, Any], float]] = {}
        self._lock = threading.Lock()
        self._ttl = ttl
        self._max_size = max_size

    @staticmethod
    def normalize_url(repo_url: str) -> str:
        """Normalize a repo URL: strip trailing slash, .git suffix, whitespace."""
        url = repo_url.strip().rstrip("/")
        if url.lower().endswith(".git"):
            url = url[:-4]
        return url

    @staticmethod
    def url_hash(repo_url: str) -> str:
        """Generate a short hash for a repo URL (used as badge key)."""
        return hashlib.sha256(repo_url.encode()).hexdigest()[:12]

    def _evict_expired(self) -> int:
        """Evict all expired entries. Returns count removed."""
        now = time.time()
        expired = [k for k, (_, ts) in self._cache.items() if now - ts > self._ttl]
        for k in expired:
            del self._cache[k]
        return len(expired)

    def get(self, repo_url: str) -> dict[str, Any] | None:
        """Get cached result for a repo URL. Returns None if missing or expired."""
        with self._lock:
            entry = self._cache.get(repo_url)
            if entry is None:
                return None
            result, timestamp = entry
            if time.time() - timestamp > self._ttl:
                del self._cache[repo_url]
                return None
            # Return a copy to prevent mutation
            return dict(result)

    def set(self, repo_url: str, result: dict[str, Any]) -> None:
        """Store result in cache."""
        with self._lock:
            # Evict expired entries if at capacity
            if len(self._cache) >= self._max_size and repo_url not in self._cache:
                evicted = self._evict_expired()
                if evicted == 0 and len(self._cache) >= self._max_size:
                    # Still full: remove oldest entry
                    oldest_key = min(self._cache.keys(), key=lambda k: self._cache[k][1])
                    del self._cache[oldest_key]

            self._cache[repo_url] = (dict(result), time.time())

    def get_status(self, repo_url: str) -> str:
        """Get cache status for a repo URL: 'cached', 'expired', or 'miss'."""
        with self._lock:
            entry = self._cache.get(repo_url)
            if entry is None:
                return "miss"
            _, timestamp = entry
            if time.time() - timestamp > self._ttl:
                return "expired"
            return "cached"

    def get_by_hash(self, repo_hash: str, repo_url: str | None = None) -> dict[str, Any] | None:
        """Look up cached result by URL hash.

        If repo_url is provided, it will be used for precise matching
        (preferred, avoids hash collision risk).
        Otherwise falls back to iterating all entries by hash.
        """
        with self._lock:
            # Prefer exact lookup by URL when available (avoids hash collision)
            if repo_url is not None:
                entry = self._cache.get(repo_url)
                if entry is not None:
                    result, timestamp = entry
                    if time.time() - timestamp <= self._ttl:
                        return dict(result)
                return None

            # Fallback: iterate by hash (legacy path with collision risk)
            for url, (result, timestamp) in self._cache.items():
                if self.url_hash(url) == repo_hash and time.time() - timestamp <= self._ttl:
                    return dict(result)
        return None

    def clear(self) -> None:
        """Clear all cache entries."""
        with self._lock:
            self._cache.clear()

    def invalidate(self, repo_url: str) -> None:
        """Remove a specific entry from cache (public API for cache eviction)."""
        with self._lock:
            self._cache.pop(repo_url, None)

    def __len__(self) -> int:
        return len(self._cache)


# Module-level singleton
cache = AnalysisCache()
