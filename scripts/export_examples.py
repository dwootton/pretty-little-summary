"""Export test example fixtures into docs/examples/*.txt files."""

from __future__ import annotations

import importlib.util
import sys
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


def export() -> None:
    DOCS_DIR.mkdir(parents=True, exist_ok=True)

    ids: list[str] = []
    for example_id in list_example_ids():
        example = load_example(example_id)
        ids.append(example_id)

        title = getattr(example, "TITLE", example_id.replace("_", " ").title())
        tags = getattr(example, "TAGS", [])
        display_input = getattr(example, "DISPLAY_INPUT", "")
        display_output = _display_output(example)

        (DOCS_DIR / f"{example_id}.meta.txt").write_text(
            f"Title: {title}\nTags: {', '.join(tags)}\n",
            encoding="utf-8",
        )
        (DOCS_DIR / f"{example_id}.input.txt").write_text(
            f"{display_input}\n", encoding="utf-8"
        )
        (DOCS_DIR / f"{example_id}.output.txt").write_text(
            f"{display_output}\n", encoding="utf-8"
        )

    (DOCS_DIR / "index.txt").write_text("\n".join(ids) + "\n", encoding="utf-8")


if __name__ == "__main__":
    export()
