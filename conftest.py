"""Pytest configuration for project root.
Ensures backend package is on sys.path when running tests from the repository root."""
import sys
from pathlib import Path

root = Path(__file__).resolve().parent
backend_path = root / "backend"
if str(backend_path) not in sys.path:
    sys.path.insert(0, str(backend_path))
