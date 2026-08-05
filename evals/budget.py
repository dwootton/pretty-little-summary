"""Size and dependency budget checks.

    python -m evals.budget check

1. Zero-dep core: in a subprocess, import pretty_little_summary and describe
   basic objects; assert no third-party module was imported. Also assert
   pyproject declares dependencies = [].
2. LOC ratchet: non-blank, non-comment lines in src/**/*.py must stay within
   evals/budget.json's max_src_loc. Raising the cap means editing that
   committed file, which surfaces the decision in review.
"""

from __future__ import annotations

import json
import subprocess
import sys
import tomllib
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parent.parent
SRC = REPO_ROOT / "src"
BUDGET_PATH = Path(__file__).resolve().parent / "budget.json"

# Runs in a subprocess launched with -S (site-packages disabled), so every
# third-party import raises ImportError. This verifies the library WORKS with
# no optional dependency installed — adapters may opportunistically use extras
# when present, which is fine and expected.
_ZERO_DEP_SNIPPET = """
import sys
import pretty_little_summary as pls
from pathlib import Path

for obj in (42, "hello", [1, 2, 3], {"a": 1}, 3.14, None, Path(".")):
    result = pls.describe(obj)
    assert result.content, f"empty description for {obj!r}"

for name in sys.modules:
    top = name.split(".")[0]
    assert top in sys.stdlib_module_names or top in (
        "pretty_little_summary", "__main__", "_virtualenv",
    ), f"non-stdlib module imported despite -S: {top}"
print("zero-dep core: OK")
"""


def count_loc(path: Path) -> int:
    count = 0
    for line in path.read_text(encoding="utf-8", errors="replace").splitlines():
        stripped = line.strip()
        if stripped and not stripped.startswith("#"):
            count += 1
    return count


def check_zero_dep() -> list[str]:
    problems = []
    pyproject = tomllib.loads((REPO_ROOT / "pyproject.toml").read_text())
    deps = pyproject.get("project", {}).get("dependencies", None)
    if deps != []:
        problems.append(f"pyproject project.dependencies must be [], got: {deps}")

    result = subprocess.run(
        [sys.executable, "-S", "-c", _ZERO_DEP_SNIPPET],
        capture_output=True,
        text=True,
        cwd=REPO_ROOT,
        env={"PYTHONPATH": str(SRC)},
    )
    if result.returncode != 0:
        problems.append(
            "zero-dep import check failed:\n"
            + (result.stdout + result.stderr).strip()
        )
    return problems


def check_loc() -> list[str]:
    budget = json.loads(BUDGET_PATH.read_text())
    max_loc = budget["max_src_loc"]
    per_file = {p: count_loc(p) for p in sorted(SRC.rglob("*.py"))}
    total = sum(per_file.values())
    top = sorted(per_file.items(), key=lambda kv: -kv[1])[:10]
    print(f"src LOC: {total} / {max_loc} budget")
    for path, loc in top:
        print(f"  {loc:5d}  {path.relative_to(REPO_ROOT)}")
    if total > max_loc:
        return [
            f"src LOC {total} exceeds budget {max_loc}. Trim code or, if growth "
            f"is justified, raise max_src_loc in evals/budget.json (a reviewed change)."
        ]
    return []


def check() -> int:
    problems = check_zero_dep() + check_loc()
    if problems:
        for p in problems:
            print(f"BUDGET FAIL: {p}", file=sys.stderr)
        return 1
    print("budget: OK")
    return 0


def main(argv: list[str] | None = None) -> int:
    args = argv if argv is not None else sys.argv[1:]
    if args != ["check"]:
        print("usage: python -m evals.budget check", file=sys.stderr)
        return 2
    return check()


if __name__ == "__main__":
    raise SystemExit(main())
