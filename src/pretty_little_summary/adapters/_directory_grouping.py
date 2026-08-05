"""Detect families of similarly-named files within one directory listing.

A "family" is a maximal run of consecutive (in sorted order) files sharing a
prefix, a zero-padded numeric run, and a suffix — e.g. ``sibt_ext_ease2_185001.png``
.. ``sibt_ext_ease2_201712.png``. When every sampled member also has the same
content description (modulo an exact byte size, which legitimately varies
file-to-file), the whole run collapses into a single display line instead of
one line per file.
"""

from __future__ import annotations

import re
from collections.abc import Callable
from dataclasses import dataclass
from pathlib import Path

MIN_FAMILY_SIZE = 4
SAMPLE_CHECK_COUNT = 5

_NUMERIC_RUN_RE = re.compile(r"^(?P<prefix>.*?)(?P<num>\d+)(?P<suffix>\D*)$")
_SIZE_SUFFIX_RE = re.compile(r"\s*\([\d,.]+ ?(B|KB|MB|GB|TB)\)\.?$")


@dataclass(frozen=True)
class FilenameFamily:
    """A collapsed run of structurally-identical filenames."""

    prefix: str
    suffix: str
    width: int
    first_num: str
    last_num: str
    members: list[Path]
    shared_description: str


def _strip_size_suffix(description: str) -> str:
    """Remove a trailing ' (N.N KB)'-style clause used only for grouping."""
    stripped = _SIZE_SUFFIX_RE.sub("", description)
    if stripped != description and not stripped.endswith((".", "!", "?")):
        stripped += "."
    return stripped


def _numeric_key(name: str) -> tuple[str, str, int] | None:
    """Return (prefix, suffix, digit-width) if name fits the numeric-run shape."""
    match = _NUMERIC_RUN_RE.match(name)
    if not match:
        return None
    return match.group("prefix"), match.group("suffix"), len(match.group("num"))


def _sample_indices(n: int, count: int) -> list[int]:
    """Evenly spaced sample indices across [0, n), always including 0 and n-1."""
    if n <= count:
        return list(range(n))
    step = (n - 1) / (count - 1)
    return sorted({round(i * step) for i in range(count)})


def group_filename_families(
    entries: list[Path],
    describe: Callable[[Path], str],
    min_family_size: int = MIN_FAMILY_SIZE,
) -> list[Path | FilenameFamily]:
    """Group a sorted list of file paths into singles and collapsed families.

    ``describe`` is called lazily and only on a small sample of each candidate
    run (not every member) so a family of thousands of files costs a handful
    of sniffs rather than one per file.
    """
    result: list[Path | FilenameFamily] = []
    run: list[Path] = []
    run_key: tuple[str, str, int] | None = None

    def flush() -> None:
        if not run:
            return
        if len(run) >= min_family_size:
            family = _confirm_family(run, run_key, describe)
            if family is not None:
                result.append(family)
                return
        result.extend(run)

    for entry in entries:
        key = _numeric_key(entry.name)
        if key is not None and key == run_key:
            run.append(entry)
            continue
        flush()
        run = [entry] if key is not None else []
        run_key = key
        if key is None:
            result.append(entry)
    flush()

    return result


def _confirm_family(
    run: list[Path],
    key: tuple[str, str, int] | None,
    describe: Callable[[Path], str],
) -> FilenameFamily | None:
    assert key is not None
    prefix, suffix, width = key

    indices = _sample_indices(len(run), SAMPLE_CHECK_COUNT)
    stripped_descriptions = set()
    sample_description = ""
    for i in indices:
        desc = describe(run[i])
        stripped = _strip_size_suffix(desc)
        stripped_descriptions.add(stripped)
        if i == 0:
            sample_description = stripped

    if len(stripped_descriptions) != 1:
        return None

    first_match = _NUMERIC_RUN_RE.match(run[0].name)
    last_match = _NUMERIC_RUN_RE.match(run[-1].name)
    assert first_match and last_match

    return FilenameFamily(
        prefix=prefix,
        suffix=suffix,
        width=width,
        first_num=first_match.group("num"),
        last_num=last_match.group("num"),
        members=run,
        shared_description=sample_description,
    )


def format_family_line(family: FilenameFamily) -> str:
    """Render a collapsed family as one tree-line fragment (no connector/prefix)."""
    name = f"{family.prefix}{{{family.first_num}..{family.last_num}}}{family.suffix}"
    count = len(family.members)
    unit = "file" if count == 1 else "files"
    return f"{name} ({count} {unit}) - {family.shared_description}"
