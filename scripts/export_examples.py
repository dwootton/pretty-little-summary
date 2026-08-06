"""Export test example fixtures into docs/examples/*.txt files."""

from __future__ import annotations

import importlib.util
import inspect
import sys
import textwrap
from pathlib import Path
from typing import Any

ROOT = Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))
src_root = ROOT / "src"
if str(src_root) not in sys.path:
    sys.path.insert(0, str(src_root))

import pretty_little_summary as pls
from tests.input import build_input, list_example_ids, load_example  # noqa: E402
DOCS_DIR = ROOT / "docs" / "examples"


def _missing_dependency(example: Any) -> str | None:
    for module in getattr(example, "REQUIRES", []):
        if importlib.util.find_spec(module) is None:
            return module
    return None


def _display_output(example: Any) -> str:
    if getattr(example, "REQUIRES_TMP_PATH", False):
        return "Output unavailable (requires tmp_path fixture)."
    if isinstance(getattr(example, "DISPLAY_OUTPUT", None), str):
        return example.DISPLAY_OUTPUT
    if isinstance(getattr(example, "EXPECTED", None), str):
        return example.EXPECTED

    missing = _missing_dependency(example)
    if missing:
        return f"Output unavailable (missing dependency: {missing})."

    obj = build_input(example)
    cleanup = None
    if isinstance(obj, tuple) and len(obj) == 2:
        obj, cleanup = obj
    try:
        return pls.describe(obj).content
    finally:
        if cleanup is not None:
            if hasattr(cleanup, "close"):
                cleanup.close()
            elif callable(cleanup):
                cleanup()


def _needs_cleanup(example: Any) -> bool:
    """True when build() returns a (value, cleanup) 2-tuple.

    Mirrors the convention _display_output already follows: closes the
    cleanup handle immediately since this is only a probe, not the real run.
    """
    if getattr(example, "REQUIRES_TMP_PATH", False) or _missing_dependency(example):
        return False
    try:
        obj = build_input(example)
    except Exception:
        return False
    if isinstance(obj, tuple) and len(obj) == 2:
        _, cleanup = obj
        if hasattr(cleanup, "close"):
            cleanup.close()
        elif callable(cleanup):
            cleanup()
        return True
    return False


def _code_snippet(example: Any) -> str:
    """Best-effort standalone script that reproduces this example's build().

    Inlines the body of build(), rewriting its `return X` into `obj = X`
    (or `obj, _cleanup = X` when build() returns a (value, cleanup) pair),
    then appends a pls.describe(obj) call — runnable as-is in the
    playground. Returns "" for examples that depend on a pytest tmp_path
    fixture, since there's no equivalent in the browser.
    """
    if getattr(example, "REQUIRES_TMP_PATH", False):
        return ""
    try:
        source = inspect.getsource(example.build)
    except (OSError, TypeError):
        return ""

    needs_cleanup = _needs_cleanup(example)
    target = "obj, _cleanup = " if needs_cleanup else "obj = "

    lines = source.splitlines()
    body_start = 0
    for i, line in enumerate(lines):
        if line.rstrip().endswith(":"):
            body_start = i + 1
            break
    body = textwrap.dedent("\n".join(lines[body_start:]))

    body_lines = []
    for line in body.splitlines():
        stripped = line.lstrip()
        indent = line[: len(line) - len(stripped)]
        if stripped.startswith("return "):
            body_lines.append(f"{indent}{target}{stripped[len('return '):]}")
        elif stripped == "return":
            continue
        else:
            body_lines.append(line)
    snippet = "\n".join(body_lines).rstrip()

    cleanup_line = "_cleanup.close()\n" if needs_cleanup else ""
    return (
        f"{snippet}\n\n"
        "import pretty_little_summary as pls\n"
        "result = pls.describe(obj)\n"
        "print(result.content)\n"
        f"{cleanup_line}"
    )


def export() -> None:
    DOCS_DIR.mkdir(parents=True, exist_ok=True)

    ids: list[str] = []
    for example_id in list_example_ids():
        example = load_example(example_id)
        ids.append(example_id)

        title = getattr(example, "TITLE", example_id.replace("_", " ").title())
        tags = getattr(example, "TAGS", [])
        requires = getattr(example, "REQUIRES", [])
        display_input = getattr(example, "DISPLAY_INPUT", "")
        display_output = _display_output(example)
        code = _code_snippet(example)

        (DOCS_DIR / f"{example_id}.meta.txt").write_text(
            f"Title: {title}\nTags: {', '.join(tags)}\nRequires: {', '.join(requires)}\n",
            encoding="utf-8",
        )
        (DOCS_DIR / f"{example_id}.input.txt").write_text(
            f"{display_input}\n", encoding="utf-8"
        )
        (DOCS_DIR / f"{example_id}.output.txt").write_text(
            f"{display_output}\n", encoding="utf-8"
        )
        (DOCS_DIR / f"{example_id}.code.txt").write_text(code, encoding="utf-8")

    (DOCS_DIR / "index.txt").write_text("\n".join(ids) + "\n", encoding="utf-8")


if __name__ == "__main__":
    export()
