"""Behavioral tests for eval-runner result stability."""

from pathlib import Path

from evals.cases import Case, CaseCtx
from evals.runner import run_case


def test_run_case_normalizes_generated_temp_paths(tmp_path: Path) -> None:
    def build(ctx: CaseCtx) -> Path:
        generated = ctx.tmp / "dataset"
        generated.mkdir(parents=True)
        (generated / "values.txt").write_text("1\n")
        return generated

    case = Case(id="test/temp-path", build=build)
    first_root = tmp_path / "first"
    second_root = tmp_path / "second"

    first = run_case(case, CaseCtx(tmp=first_root, cache=tmp_path))
    second = run_case(case, CaseCtx(tmp=second_root, cache=tmp_path))

    assert first["content"] == second["content"]
    assert first["output_hash"] == second["output_hash"]
    assert str(first_root) not in first["content"]
    assert first["content"].startswith("<eval-tmp>/dataset/")
