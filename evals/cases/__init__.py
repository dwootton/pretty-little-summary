"""Case spec and registry for the eval corpus.

A Case unifies the three corpus sources (synthetic constructors, real
downloaded files, live library objects): every case ultimately builds one
object to pass to ``pls.describe()`` — a Path is just another object.
"""

from __future__ import annotations

import importlib
import importlib.util
from dataclasses import dataclass, field
from pathlib import Path
from typing import Any, Callable

EVALS_DIR = Path(__file__).resolve().parent.parent
CACHE_DIR = EVALS_DIR / "cache"
GOLDENS_DIR = EVALS_DIR / "goldens"
OUT_DIR = EVALS_DIR / "out"
SCORES_PATH = EVALS_DIR / "scores.json"
MANIFEST_PATH = EVALS_DIR / "manifest.json"

# Corpus modules imported by load_all_cases(); each registers cases on import.
_CORPUS_MODULES = ("gallery", "synthetic", "live_objects", "real_files")


@dataclass
class CaseCtx:
    """Filesystem context handed to every case builder."""

    tmp: Path  # per-run temp dir for synthetic files
    cache: Path  # evals/cache with downloaded datasets


@dataclass
class Case:
    id: str  # unique, e.g. "synth/csv_utf16_bom"
    build: Callable[[CaseCtx], Any]  # returns obj, or (obj, cleanup)
    tags: tuple[str, ...] = ()
    requires: tuple[str, ...] = ()  # importable module names; missing -> SKIP
    requires_file: str | None = None  # cache filename; not fetched -> SKIP
    describe_kwargs: dict = field(default_factory=dict)
    display_input: str = ""  # human-readable input spec, shown to the judge
    notes: str = ""  # what a good summary should mention
    source_url: str = ""  # public URL of the underlying data, if any

    def missing_requirement(self) -> str | None:
        """Return a skip reason if this case cannot run, else None."""
        for module in self.requires:
            if importlib.util.find_spec(module) is None:
                return f"missing dependency: {module}"
        if self.requires_file is not None:
            if not (CACHE_DIR / self.requires_file).exists():
                return f"file not fetched: {self.requires_file} (run: python -m evals.runner fetch)"
        return None


CASES: dict[str, Case] = {}


def register(case_obj: Case) -> None:
    if case_obj.id in CASES:
        raise ValueError(f"Duplicate case id: {case_obj.id}")
    CASES[case_obj.id] = case_obj


def case(
    id: str,
    *,
    tags: tuple[str, ...] = (),
    requires: tuple[str, ...] = (),
    requires_file: str | None = None,
    describe_kwargs: dict | None = None,
    display_input: str = "",
    notes: str = "",
    source_url: str = "",
) -> Callable[[Callable[[CaseCtx], Any]], Callable[[CaseCtx], Any]]:
    """Decorator registering a build function as a Case."""

    def decorator(build: Callable[[CaseCtx], Any]) -> Callable[[CaseCtx], Any]:
        register(
            Case(
                id=id,
                build=build,
                tags=tuple(tags),
                requires=tuple(requires),
                requires_file=requires_file,
                describe_kwargs=describe_kwargs or {},
                display_input=display_input,
                notes=notes,
                source_url=source_url,
            )
        )
        return build

    return decorator


_loaded = False


def load_all_cases() -> dict[str, Case]:
    """Import all corpus modules (idempotent) and return the registry."""
    global _loaded
    if not _loaded:
        for name in _CORPUS_MODULES:
            importlib.import_module(f"evals.cases.{name}")
        _loaded = True
    return CASES


def golden_filename(case_id: str) -> str:
    """Map a case id to its golden snapshot filename."""
    return case_id.replace("/", "__") + ".txt"
