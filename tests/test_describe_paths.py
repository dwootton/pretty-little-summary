"""Tests for path-aware describe(): string promotion, deep profiling (the
default), sampling, the shallow=True hint, and deep directory profiling."""

from __future__ import annotations

from pathlib import Path

import pytest

import pretty_little_summary as pls

pd = pytest.importorskip("pandas")


# --- string -> Path promotion ------------------------------------------------


def test_existing_path_string_is_promoted(tmp_path: Path) -> None:
    p = tmp_path / "d.csv"
    p.write_text("name,age\nalice,30\nbob,25\n")
    result = pls.describe(str(p))
    # Promoted to a Path and described as a file, not as the literal string.
    # describe() defaults to deep, so a promoted CSV loads into a DataFrame.
    assert result.meta["object_type"] == "pandas.DataFrame"
    assert "A string" not in result.content


def test_nonexistent_path_string_stays_a_string() -> None:
    result = pls.describe("data/does_not_exist_12345.csv")
    assert "A string" in result.content


def test_ordinary_string_is_not_promoted() -> None:
    result = pls.describe("hello world")
    assert "A string" in result.content


# --- shallow=True hint --------------------------------------------------------


def test_shallow_file_describe_appends_full_profile_hint(tmp_path: Path) -> None:
    p = tmp_path / "d.csv"
    p.write_text("name,age\nalice,30\nbob,25\n")
    content = pls.describe(p, shallow=True).content
    assert "shallow=True" in content
    assert "profile this file" in content


def test_deep_file_describe_has_no_hint(tmp_path: Path) -> None:
    p = tmp_path / "d.csv"
    p.write_text("name,age\nalice,30\nbob,25\n")
    content = pls.describe(p).content
    assert "Tip: drop shallow=True" not in content


def test_non_path_object_gets_no_hint() -> None:
    content = pls.describe([1, 2, 3]).content
    assert "shallow=True" not in content


# --- deep single-file profiling (the default) --------------------------------


def test_deep_csv_yields_dataframe_profile(tmp_path: Path) -> None:
    p = tmp_path / "d.csv"
    p.write_text("name,age\nalice,30\nbob,25\ncarol,40\n")
    result = pls.describe(p)
    assert result.meta["object_type"] == "pandas.DataFrame"
    assert "rows" in result.content and "columns" in result.content


def test_deep_jsonl_yields_dataframe_profile(tmp_path: Path) -> None:
    p = tmp_path / "d.jsonl"
    p.write_text('{"a": 1, "b": "x"}\n{"a": 2, "b": "y"}\n{"a": 3, "b": "z"}\n')
    result = pls.describe(p)
    assert result.meta["object_type"] == "pandas.DataFrame"
    assert result.meta["shape"] == (3, 2)


def test_deep_stata_yields_dataframe_profile(tmp_path: Path) -> None:
    df = pd.DataFrame({"x": [1, 2, 3], "y": [1.0, 2.0, 3.0]})
    p = tmp_path / "d.dta"
    df.to_stata(p, write_index=False)
    result = pls.describe(p)
    assert result.meta["object_type"] == "pandas.DataFrame"
    assert result.meta["shape"] == (3, 2)


# --- sampling ----------------------------------------------------------------


def test_deep_load_samples_over_cap(tmp_path: Path, monkeypatch) -> None:
    # Force a tiny cap so a small fixture triggers the sampling path.
    monkeypatch.setattr(
        "pretty_little_summary.file_loader.DEFAULT_SAMPLE_ROWS", 5
    )
    rows = "\n".join(f"{i},{i * 2}" for i in range(50))
    p = tmp_path / "big.csv"
    p.write_text("a,b\n" + rows + "\n")

    result = pls.describe(p)
    assert result.meta["metadata"]["sampled"] is True
    assert result.meta["metadata"]["sampled_rows"] == 5
    assert "sample of the first 5 rows" in result.content


def test_full_reads_all_rows(tmp_path: Path, monkeypatch) -> None:
    monkeypatch.setattr(
        "pretty_little_summary.file_loader.DEFAULT_SAMPLE_ROWS", 5
    )
    rows = "\n".join(f"{i},{i * 2}" for i in range(50))
    p = tmp_path / "big.csv"
    p.write_text("a,b\n" + rows + "\n")

    result = pls.describe(p, full=True)
    assert result.meta["shape"][0] == 50
    assert not result.meta["metadata"].get("sampled")
    assert "sample of" not in result.content


# --- deep directory profiling (the default) -----------------------------------


def test_deep_directory_profiles_each_dataset(tmp_path: Path) -> None:
    (tmp_path / "a.csv").write_text("x,y\n1,2\n3,4\n")
    (tmp_path / "notes.txt").write_text("just some prose here\n")

    content = pls.describe(tmp_path).content
    # The CSV is loaded and profiled, not merely head-sniffed.
    assert "pandas DataFrame" in content
    assert "a.csv" in content


def test_shallow_directory_appends_directory_hint(tmp_path: Path) -> None:
    (tmp_path / "a.csv").write_text("x,y\n1,2\n")
    content = pls.describe(tmp_path, shallow=True).content
    assert "profile this directory" in content
