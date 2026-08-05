"""Register every tests/input example module as an eval case."""

from __future__ import annotations

from typing import Any

from evals.cases import Case, CaseCtx, register
from tests.input import build_input, list_example_ids, load_example


def _make_build(example: Any):
    def build(ctx: CaseCtx) -> Any:
        if getattr(example, "REQUIRES_TMP_PATH", False):
            return build_input(example, tmp_path=ctx.tmp)
        return build_input(example)

    return build


for _example_id in list_example_ids():
    _mod = load_example(_example_id)
    register(
        Case(
            id=f"gallery/{_example_id}",
            build=_make_build(_mod),
            tags=("gallery", *getattr(_mod, "TAGS", [])),
            requires=tuple(getattr(_mod, "REQUIRES", [])),
            display_input=getattr(_mod, "DISPLAY_INPUT", ""),
        )
    )
