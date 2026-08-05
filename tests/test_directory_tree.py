"""Tests for directory-tree truncation and filename-family collapsing."""

from __future__ import annotations

from pathlib import Path

import pretty_little_summary as pls
from pretty_little_summary.adapters._directory_grouping import (
    MIN_FAMILY_SIZE,
    FilenameFamily,
    _strip_size_suffix,
    format_family_line,
    group_filename_families,
)
from pretty_little_summary.adapters.pathlib_adapter import (
    DEFAULT_MAX_DIRS_PER_FOLDER,
    DEFAULT_MAX_FILES_PER_FOLDER,
)

# --- per-folder truncation ----------------------------------------------------


def test_per_folder_cap_truncates_non_matching_files(tmp_path: Path) -> None:
    n = DEFAULT_MAX_FILES_PER_FOLDER + 10
    for i in range(n):
        (tmp_path / f"distinct_item_{i}_zzz.bin").write_bytes(bytes([i % 256]) * (i + 1))
    content = pls.describe(tmp_path, deep=True).content
    shown = content.count(" - A ") + content.count(" - (error")
    assert shown <= DEFAULT_MAX_FILES_PER_FOLDER
    assert "more files in this folder" in content


def test_sibling_not_starved_by_large_family(tmp_path: Path) -> None:
    big = tmp_path / "big"
    big.mkdir()
    for i in range(DEFAULT_MAX_FILES_PER_FOLDER * 3):
        (big / f"seq_{i:04d}.txt").write_text("same content")
    (tmp_path / "sibling.txt").write_text("hi")

    content = pls.describe(tmp_path, deep=True).content
    assert "sibling.txt" in content


def test_per_folder_cap_truncates_subdirectories(tmp_path: Path) -> None:
    n = DEFAULT_MAX_DIRS_PER_FOLDER + 30
    for i in range(n):
        d = tmp_path / f"station_{i:04d}"
        d.mkdir()
        (d / "readings.csv").write_text("id,val\n1,2\n")
    content = pls.describe(tmp_path, deep=True).content
    shown_dir_lines = [line for line in content.splitlines() if "station_" in line and line.rstrip().endswith("/")]
    assert len(shown_dir_lines) == DEFAULT_MAX_DIRS_PER_FOLDER
    hidden_count = n - DEFAULT_MAX_DIRS_PER_FOLDER
    assert f"({hidden_count} more folders in this folder)" in content
    # Hidden subdirectories must not be recursed into — readings.csv should
    # only be described for the shown stations, not for all of them.
    assert content.count("readings.csv") == DEFAULT_MAX_DIRS_PER_FOLDER


def test_sibling_not_starved_by_many_subdirectories(tmp_path: Path) -> None:
    for i in range(DEFAULT_MAX_DIRS_PER_FOLDER * 3):
        d = tmp_path / f"station_{i:04d}"
        d.mkdir()
        (d / "readings.csv").write_text("id,val\n1,2\n")
    (tmp_path / "sibling.txt").write_text("hi")

    content = pls.describe(tmp_path, deep=True).content
    assert "sibling.txt" in content


# --- family collapsing --------------------------------------------------------


def test_basic_family_collapses(tmp_path: Path) -> None:
    n = MIN_FAMILY_SIZE + 2
    for i in range(n):
        (tmp_path / f"item_{i:03d}.txt").write_text("hello")
    content = pls.describe(tmp_path, deep=True).content
    assert f"item_{{000..{n - 1:03d}}}.txt ({n} files)" in content
    # No per-file lines for the collapsed members remain.
    assert "item_000.txt -" not in content


def test_family_with_varying_size_still_collapses(tmp_path: Path) -> None:
    n = MIN_FAMILY_SIZE + 2
    for i in range(n):
        (tmp_path / f"pic_{i:03d}.txt").write_text("x" * (i + 1))
    # deep=True is what actually walks a directory's tree; a shallow describe
    # of a directory only head-sniffs (which fails for a directory) and
    # never reaches the tree walker.
    content = pls.describe(tmp_path, deep=True).content
    assert f"pic_{{000..{n - 1:03d}}}.txt ({n} files)" in content
    # The collapsed description must not carry a stray per-file byte size.
    assert "KB)" not in content and " B)" not in content


def test_below_min_family_size_does_not_collapse(tmp_path: Path) -> None:
    n = MIN_FAMILY_SIZE - 1
    for i in range(n):
        (tmp_path / f"solo_{i:03d}.txt").write_text("hello")
    content = pls.describe(tmp_path, deep=True).content
    assert "{" not in content
    for i in range(n):
        assert f"solo_{i:03d}.txt" in content


def test_width_change_breaks_family(tmp_path: Path) -> None:
    for i in range(1, 12):
        (tmp_path / f"file_{i}.txt").write_text("hello")
    content = pls.describe(tmp_path, deep=True).content
    # Sorted order is file_1, file_10, file_11, file_2, ..., file_9 (lexical),
    # so the width-2 pair breaks the run immediately; 2..9 (width 1) then
    # form their own contiguous, collapsible family.
    assert "file_{2..9}.txt (8 files)" in content
    assert "file_1.txt" in content
    assert "file_10.txt" in content
    assert "file_11.txt" in content


def test_non_conforming_member_breaks_run(tmp_path: Path) -> None:
    for i in range(1, 19):
        (tmp_path / f"montage_{i:02d}_x.png").write_text("hello")
    (tmp_path / "montage_legend.png").write_text("hello")
    content = pls.describe(tmp_path, deep=True).content
    assert "montage_{01..18}_x.png (18 files)" in content
    assert "montage_legend.png" in content


def test_non_conforming_member_mid_run_splits_into_two_families(tmp_path: Path) -> None:
    # A non-conforming name that sorts *between* two halves of an otherwise
    # contiguous run (not just at an edge) ends the first run there and
    # starts a fresh one after — it does not merge the two halves.
    for i in range(1, 11):
        (tmp_path / f"scan_{i:03d}.tif").write_text("hello")
    (tmp_path / "scan_005b_extra.tif").write_text("hello")  # sorts after scan_005
    content = pls.describe(tmp_path, deep=True).content
    assert "scan_{001..005}.tif (5 files)" in content
    assert "scan_005b_extra.tif" in content
    assert "scan_{006..010}.tif (5 files)" in content


def test_two_distinct_families_in_one_folder_both_collapse(tmp_path: Path) -> None:
    # Two unrelated filename shapes (different prefixes) that don't
    # alphabetically interleave each form their own contiguous block and
    # both collapse independently.
    for i in range(20):
        (tmp_path / f"photo_{i:03d}.jpg").write_text("hello")
    for i in range(20):
        (tmp_path / f"report_{i:03d}.csv").write_text("id,val\n1,2")
    content = pls.describe(tmp_path, deep=True).content
    assert "photo_{000..019}.jpg (20 files)" in content
    assert "report_{000..019}.csv (20 files)" in content


def test_interleaved_families_do_not_collapse(tmp_path: Path) -> None:
    # Two shapes that alphabetically interleave (m_000_alpha, m_000_beta,
    # m_001_alpha, m_001_beta, ...) never form a contiguous same-shape run,
    # since grouping only merges *immediately adjacent* sorted entries with
    # an identical (prefix, suffix, width) key. This is a known limitation,
    # not a crash: every file still renders individually (subject to the
    # per-folder cap), just without the collapsing benefit.
    for i in range(10):
        (tmp_path / f"m_{i:03d}_alpha.txt").write_text("hello")
        (tmp_path / f"m_{i:03d}_beta.txt").write_text("hello")
    content = pls.describe(tmp_path, deep=True).content
    assert "{" not in content
    assert "m_000_alpha.txt" in content
    assert "m_000_beta.txt" in content


def test_gap_in_numeric_run_still_collapses_silently(tmp_path: Path) -> None:
    # A missing item inside the numeric range (e.g. a real dataset missing
    # one year) is silently absorbed into the {first..last} display —
    # grouping only checks prefix/suffix/width, not that every intermediate
    # number is present. The collapsed range therefore overstates coverage
    # by exactly the gap; this is a deliberate simplicity tradeoff (see
    # module docstring) rather than a bug, and this test pins the behavior
    # down so a future change to it is a conscious decision.
    years = [y for y in range(1850, 1900) if y != 1892]
    for y in years:
        (tmp_path / f"sibt_ext_ease2_{y}01.png").write_text("hello")
    content = pls.describe(tmp_path, deep=True).content
    assert f"sibt_ext_ease2_{{185001..189901}}.png ({len(years)} files)" in content
    assert "1892" not in content


def test_directory_describe_is_deterministic(tmp_path: Path) -> None:
    for i in range(10):
        (tmp_path / f"item_{i:02d}.txt").write_text("hello")
    (tmp_path / "notes.txt").write_text("hi")
    first = pls.describe(tmp_path, deep=True).content
    second = pls.describe(tmp_path, deep=True).content
    assert first == second


# --- direct unit tests of the grouping module ---------------------------------


def test_group_filename_families_rejects_mismatched_descriptions() -> None:
    paths = [Path(f"item_{i:03d}.dat") for i in range(MIN_FAMILY_SIZE + 2)]

    def describe(p: Path) -> str:
        return "type A" if p.name != paths[-1].name else "type B"

    groups = group_filename_families(paths, describe)
    assert all(isinstance(g, Path) for g in groups)
    assert len(groups) == len(paths)


def test_group_filename_families_confirms_matching_run() -> None:
    paths = [Path(f"item_{i:03d}.dat") for i in range(MIN_FAMILY_SIZE + 2)]
    groups = group_filename_families(paths, lambda p: "same description")
    assert len(groups) == 1
    assert isinstance(groups[0], FilenameFamily)
    assert format_family_line(groups[0]) == (
        f"item_{{000..{len(paths) - 1:03d}}}.dat ({len(paths)} files) - same description"
    )


def test_strip_size_suffix_removes_trailing_parenthetical() -> None:
    assert _strip_size_suffix("A PNG image, 360x360 pixels (6.9 KB).") == (
        "A PNG image, 360x360 pixels."
    )
    assert _strip_size_suffix("A PIL image 360x360 in P mode.") == (
        "A PIL image 360x360 in P mode."
    )
