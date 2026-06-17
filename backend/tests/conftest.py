"""Shared test fixtures."""
import sys
from pathlib import Path

# Ensure backend is importable from test directory
sys.path.insert(0, str(Path(__file__).resolve().parent.parent.parent))
