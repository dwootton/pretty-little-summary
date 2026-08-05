"""Pytest gate: eval golden snapshots must match current describe() output.

Goldens live in evals/goldens/ and are managed by `python -m evals.runner
bless` — never edit them by hand. See evals/LOOP.md.
"""

from __future__ import annotations

import sys
import tempfile
from pathlib import Path

import pytest

REPO_ROOT = Path(__file__).resolve().parent.parent
if str(REPO_ROOT) not in sys.path:
    sys.path.insert(0, str(REPO_ROOT))

from evals.cases import CACHE_DIR, GOLDENS_DIR, CaseCtx, golden_filename, load_all_cases
from evals.runner import iter_golden_case_ids, run_case


def _golden_params():
    cases = load_all_cases()
    params = []
    for case_id in iter_golden_case_ids():
        case_obj = cases.get(case_id)
        if case_obj is None:
            params.append(
                pytest.param(
                    case_id,
                    marks=pytest.mark.xfail(
                        reason="golden exists but case is gone", strict=True
                    ),
                )
            )
            continue
        reason = case_obj.missing_requirement()
        if reason:
            params.append(
                pytest.param(case_id, marks=pytest.mark.skip(reason=reason))
            )
            continue
        params.append(pytest.param(case_id, id=case_id))
    return params


@pytest.mark.parametrize("case_id", _golden_params())
def test_eval_golden(case_id: str) -> None:
    cases = load_all_cases()
    case_obj = cases[case_id]
    golden = (GOLDENS_DIR / golden_filename(case_id)).read_text()
    with tempfile.TemporaryDirectory(prefix="pls-evals-") as tmp:
        record = run_case(case_obj, CaseCtx(tmp=Path(tmp), cache=CACHE_DIR))
    assert record["status"] == "ok", record.get("traceback", record.get("reason"))
    assert record["content"] == golden, (
        f"{case_id} output changed. If intentional, re-judge and re-bless via "
        f"`python -m evals.runner bless {case_id}` (see evals/LOOP.md)."
    )
