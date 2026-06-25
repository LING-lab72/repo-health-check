"""Shared test fixtures."""
import os
import sys
from pathlib import Path

# Ensure backend is importable from test directory
sys.path.insert(0, str(Path(__file__).resolve().parent.parent.parent))

os.environ.setdefault("SESSION_SECRET", "test-session-secret")
_test_data_dir = Path(__file__).resolve().parent / ".tmp-data"
os.environ.setdefault("REPO_HEALTH_DATA_DIR", str(_test_data_dir))
os.environ.setdefault("REPO_HEALTH_DB_FILE", str(_test_data_dir / "repo_health_test.db"))
