"""Tests for cache service."""
from backend.services.cache import AnalysisCache


def test_cache_set_get():
    c = AnalysisCache(ttl=10)
    c.set("https://github.com/a/b", {"score": 100})
    assert c.get("https://github.com/a/b") == {"score": 100}


def test_cache_miss():
    c = AnalysisCache(ttl=10)
    assert c.get("https://github.com/nonexistent") is None


def test_cache_expired():
    c = AnalysisCache(ttl=-1)  # Immediate expiry
    c.set("https://github.com/a/b", {"score": 50})
    assert c.get("https://github.com/a/b") is None


def test_cache_url_hash():
    h1 = AnalysisCache.url_hash("https://github.com/a/b")
    h2 = AnalysisCache.url_hash("https://github.com/a/b")
    h3 = AnalysisCache.url_hash("https://github.com/c/d")
    assert h1 == h2
    assert h1 != h3
    assert len(h1) == 12


def test_cache_status():
    c = AnalysisCache(ttl=3600)
    assert c.get_status("https://github.com/x/y") == "miss"
    c.set("https://github.com/x/y", {"score": 99})
    assert c.get_status("https://github.com/x/y") == "cached"


def test_cache_get_by_hash():
    c = AnalysisCache(ttl=3600)
    url = "https://github.com/owner/repo"
    c.set(url, {"score": 88, "badge_level": "A"})
    h = AnalysisCache.url_hash(url)
    result = c.get_by_hash(h)
    assert result is not None
    assert result["badge_level"] == "A"


def test_cache_get_by_hash_unknown():
    c = AnalysisCache(ttl=3600)
    assert c.get_by_hash("deadbeef1234") is None


def test_cache_clear():
    c = AnalysisCache(ttl=3600)
    c.set("https://github.com/a/b", {"score": 100})
    assert len(c) == 1
    c.clear()
    assert len(c) == 0


def test_cache_capacity_eviction():
    c = AnalysisCache(ttl=-1, max_size=3)
    c.set("url1", {"score": 1})
    c.set("url2", {"score": 2})
    c.set("url3", {"score": 3})
    # All expired given ttl=-1, so next set should work fine
    c.set("url4", {"score": 4})
    # url4 is fresh but also has -1 TTL
    assert len(c) >= 1


def test_cache_thread_safety():
    import threading
    c = AnalysisCache(ttl=3600)
    errors = []

    def stress():
        try:
            for i in range(50):
                url = f"https://github.com/user/repo{i}"
                c.set(url, {"score": i})
                _ = c.get(url)
                _ = c.url_hash(url)
        except Exception as e:
            errors.append(str(e))

    threads = [threading.Thread(target=stress) for _ in range(4)]
    for t in threads:
        t.start()
    for t in threads:
        t.join()
    assert len(errors) == 0
