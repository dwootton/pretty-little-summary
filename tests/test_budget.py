"""Pytest gate: zero-dep core and src LOC budget (see evals/budget.py)."""

from __future__ import annotations

import sys
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parent.parent
if str(REPO_ROOT) not in sys.path:
    sys.path.insert(0, str(REPO_ROOT))

from evals import budget


def test_budget() -> None:
    assert budget.check() == 0
