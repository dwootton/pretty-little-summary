"""Synthetic edge-case corpus: scripted constructors, fully reproducible.

Prefer stdlib-only builders; use `requires=` when a case needs an extra.
Fixed seeds everywhere — goldens depend on deterministic output.
"""

from __future__ import annotations

import codecs
import json

from evals.cases import CaseCtx, case

# ---------------------------------------------------------------------------
# Files: empty / truncated / misleading


@case(
    "synth/empty_csv",
    tags=("sniffer", "csv", "edge"),
    display_input="0-byte file named data.csv",
    notes="Should say the file is empty; must not crash or invent columns.",
)
def empty_csv(ctx: CaseCtx):
    p = ctx.tmp / "data.csv"
    p.write_bytes(b"")
    return p


@case(
    "synth/header_only_csv",
    tags=("sniffer", "csv", "edge"),
    display_input="CSV with a header row and zero data rows",
    notes="Should report columns but 0 data rows.",
)
def header_only_csv(ctx: CaseCtx):
    p = ctx.tmp / "header_only.csv"
    p.write_text("id,name,score\n")
    return p


@case(
    "synth/binary_as_txt",
    tags=("sniffer", "edge", "misnamed"),
    display_input="PNG image bytes saved with a .txt extension",
    notes="Should notice the content is binary/PNG, not trust the extension.",
)
def binary_as_txt(ctx: CaseCtx):
    p = ctx.tmp / "notes.txt"
    # Minimal valid PNG header + IHDR for a 4x2 image.
    ihdr = b"\x00\x00\x00\x0dIHDR" + (4).to_bytes(4, "big") + (2).to_bytes(4, "big") + b"\x08\x02\x00\x00\x00"
    p.write_bytes(b"\x89PNG\r\n\x1a\n" + ihdr + b"\x00" * 32)
    return p


@case(
    "synth/truncated_json",
    tags=("sniffer", "json", "edge"),
    display_input='file.json containing \'{"a": [1, 2\' (truncated mid-array)',
    notes="Should flag invalid/truncated JSON rather than error or misreport.",
)
def truncated_json(ctx: CaseCtx):
    p = ctx.tmp / "file.json"
    p.write_text('{"a": [1, 2')
    return p


# ---------------------------------------------------------------------------
# Files: encodings


@case(
    "synth/csv_utf16_bom",
    tags=("sniffer", "csv", "encoding"),
    display_input="UTF-16LE CSV with BOM, 3 cols x 100 rows",
    notes="Should detect the encoding (not describe as binary) and see the table.",
)
def csv_utf16(ctx: CaseCtx):
    p = ctx.tmp / "u16.csv"
    rows = "a,b,c\n" + "\n".join(f"{i},{i * 2},x{i}" for i in range(100))
    p.write_bytes(codecs.BOM_UTF16_LE + rows.encode("utf-16-le"))
    return p


@case(
    "synth/csv_utf16be_bom",
    tags=("sniffer", "csv", "encoding"),
    display_input="UTF-16BE CSV with BOM, 3 cols x 100 rows",
    notes="Same as the LE case but big-endian; should also decode as CSV, not binary.",
)
def csv_utf16be(ctx: CaseCtx):
    p = ctx.tmp / "u16be.csv"
    rows = "a,b,c\n" + "\n".join(f"{i},{i * 2},x{i}" for i in range(100))
    p.write_bytes(codecs.BOM_UTF16_BE + rows.encode("utf-16-be"))
    return p


@case(
    "synth/csv_utf8_bom",
    tags=("sniffer", "csv", "encoding"),
    display_input="UTF-8 CSV with a BOM (utf-8-sig), 3 cols x 100 rows",
    notes="A common Excel-exported CSV; the BOM must not leak into the first column name.",
)
def csv_utf8_bom(ctx: CaseCtx):
    p = ctx.tmp / "u8bom.csv"
    rows = "a,b,c\n" + "\n".join(f"{i},{i * 2},x{i}" for i in range(100))
    p.write_bytes(codecs.BOM_UTF8 + rows.encode("utf-8"))
    return p


@case(
    "synth/csv_latin1",
    tags=("sniffer", "csv", "encoding"),
    display_input="latin-1 CSV with accented city names (non-UTF8 bytes)",
    notes="Should not crash on non-UTF8 bytes; ideally still sees CSV structure.",
)
def csv_latin1(ctx: CaseCtx):
    p = ctx.tmp / "cities.csv"
    text = "city,pop\nS\xe3o Paulo,12000000\nZ\xfcrich,400000\nMalm\xf6,300000\n"
    p.write_bytes(text.encode("latin-1"))
    return p


@case(
    "synth/csv_semicolon",
    tags=("sniffer", "csv", "dialect"),
    display_input="semicolon-delimited CSV (European style), 4 cols x 50 rows",
    notes="Should detect the ; delimiter, not treat each line as one column.",
)
def csv_semicolon(ctx: CaseCtx):
    p = ctx.tmp / "euro.csv"
    rows = ["date;amount;currency;note"]
    rows += [f"2024-01-{i + 1:02d};{i * 10},5;EUR;row {i}" for i in range(50)]
    p.write_text("\n".join(rows) + "\n")
    return p


# ---------------------------------------------------------------------------
# Files: scale


@case(
    "synth/wide_csv_500_cols",
    tags=("sniffer", "csv", "scale"),
    display_input="CSV with 500 columns and 10 rows",
    notes="Should report the column count without dumping all 500 names.",
)
def wide_csv(ctx: CaseCtx):
    p = ctx.tmp / "wide.csv"
    header = ",".join(f"col_{i}" for i in range(500))
    row = ",".join(str(i % 7) for i in range(500))
    p.write_text(header + "\n" + "\n".join(row for _ in range(10)) + "\n")
    return p


@case(
    "synth/long_csv_200k_rows",
    tags=("sniffer", "csv", "scale"),
    display_input="CSV with 200,000 rows and 3 columns (~3 MB)",
    notes="Shallow sniff should be fast and estimate the row count.",
)
def long_csv(ctx: CaseCtx):
    p = ctx.tmp / "long.csv"
    with p.open("w") as f:
        f.write("id,value,flag\n")
        for i in range(200_000):
            f.write(f"{i},{i % 997},{i % 2}\n")
    return p


@case(
    "synth/long_csv_200k_rows_deep",
    tags=("sniffer", "csv", "scale", "deep"),
    requires=("pandas",),
    describe_kwargs={"deep": True},
    display_input="Same 200,000-row CSV with deep=True (100K sample cap applies)",
    notes="Should profile from a sample and clearly disclose the sampling.",
)
def long_csv_deep(ctx: CaseCtx):
    return long_csv(ctx)


# ---------------------------------------------------------------------------
# Files: JSON oddities


@case(
    "synth/json_nan_inf",
    tags=("sniffer", "json", "edge"),
    display_input="JSON file containing NaN and Infinity literals (non-standard)",
    notes="Python json accepts these; summary should not crash and should describe the structure.",
)
def json_nan_inf(ctx: CaseCtx):
    p = ctx.tmp / "weird.json"
    p.write_text('{"score": NaN, "limit": Infinity, "vals": [1, -Infinity, 3]}')
    return p


@case(
    "synth/jsonl_mixed_schemas",
    tags=("sniffer", "jsonl", "edge"),
    display_input="JSONL where each line has different keys",
    notes="Should describe it as JSONL and ideally note schema inconsistency.",
)
def jsonl_mixed(ctx: CaseCtx):
    p = ctx.tmp / "events.jsonl"
    lines = [
        {"event": "click", "x": 10, "y": 20},
        {"user": "ann", "ts": "2024-01-01T00:00:00"},
        {"error": "timeout", "retries": 3, "fatal": False},
    ] * 20
    p.write_text("\n".join(json.dumps(line) for line in lines) + "\n")
    return p


@case(
    "synth/json_deep_nesting",
    tags=("sniffer", "json", "edge"),
    display_input="JSON nested 40 levels deep",
    notes="Should not recurse into an unreadable dump; depth is the story.",
)
def json_deep(ctx: CaseCtx):
    obj: dict = {"leaf": 1}
    for _ in range(40):
        obj = {"child": obj}
    p = ctx.tmp / "deep.json"
    p.write_text(json.dumps(obj))
    return p


# ---------------------------------------------------------------------------
# In-memory objects: pathological containers


@case(
    "synth/deep_nested_dict",
    tags=("adapter", "collections", "edge"),
    display_input="dict nested 60 levels deep",
    notes="Must not hit recursion limits; should convey nesting depth.",
)
def deep_dict(ctx: CaseCtx):
    d: dict = {"leaf": True}
    for _ in range(60):
        d = {"child": d}
    return d


@case(
    "synth/recursive_list",
    tags=("adapter", "collections", "edge"),
    display_input="list that contains itself (l.append(l))",
    notes="Must not infinite-loop; should mention self-reference if possible.",
)
def recursive_list(ctx: CaseCtx):
    l: list = [1, 2, 3]
    l.append(l)
    return l


@case(
    "synth/dict_10k_keys",
    tags=("adapter", "collections", "scale"),
    display_input="dict with 10,000 string keys -> int values",
    notes="Should summarize (count, key/value types), not enumerate keys.",
)
def big_dict(ctx: CaseCtx):
    return {f"key_{i}": i * 3 for i in range(10_000)}


@case(
    "synth/heterogeneous_list",
    tags=("adapter", "collections", "edge"),
    display_input="list mixing int, str, None, dict, bytes, and a nested list",
    notes="Should characterize the mix of element types.",
)
def hetero_list(ctx: CaseCtx):
    return [1, "two", None, {"three": 3}, b"four", [5, 6], 7.0]


@case(
    "synth/empty_containers",
    tags=("adapter", "collections", "edge"),
    display_input="tuple of ({}, [], set(), '') — all empty containers",
    notes="Each element is empty; summary should be crisp, not repetitive.",
)
def empty_containers(ctx: CaseCtx):
    return ({}, [], set(), "")


@case(
    "synth/unicode_string_emoji",
    tags=("adapter", "primitives", "encoding"),
    display_input="500-char string of mixed emoji, CJK, and RTL text",
    notes="Length/character handling should be correct for non-ASCII.",
)
def unicode_string(ctx: CaseCtx):
    return ("héllo wörld 你好世界 مرحبا 🎉🚀" * 20)[:500]


# ---------------------------------------------------------------------------
# In-memory objects: dataframe/array pathologies (need extras)


@case(
    "synth/df_all_null_column",
    tags=("adapter", "pandas", "edge"),
    requires=("pandas", "numpy"),
    display_input="DataFrame 100x3 where column 'c' is entirely NaN",
    notes="Should call out the all-null column.",
)
def df_all_null(ctx: CaseCtx):
    import numpy as np
    import pandas as pd

    return pd.DataFrame(
        {"a": range(100), "b": [f"s{i}" for i in range(100)], "c": [np.nan] * 100}
    )


@case(
    "synth/df_mixed_dtype_column",
    tags=("adapter", "pandas", "edge"),
    requires=("pandas",),
    display_input="DataFrame with an object column mixing ints, strings, and None",
    notes="Should flag the mixed-type column rather than calling it plain 'object'.",
)
def df_mixed(ctx: CaseCtx):
    import pandas as pd

    return pd.DataFrame({"mixed": [1, "two", None, 4.5, "five"] * 10})


@case(
    "synth/df_500_columns",
    tags=("adapter", "pandas", "scale"),
    requires=("pandas", "numpy"),
    display_input="DataFrame with 500 numeric columns, 20 rows",
    notes="Should summarize column count, not list all names.",
)
def df_wide(ctx: CaseCtx):
    import numpy as np
    import pandas as pd

    rng = np.random.default_rng(0)
    return pd.DataFrame(rng.random((20, 500)), columns=[f"c{i}" for i in range(500)])


@case(
    "synth/df_datetime_index",
    tags=("adapter", "pandas", "timeseries"),
    requires=("pandas", "numpy"),
    display_input="DataFrame with hourly DatetimeIndex over 30 days, 2 value cols",
    notes="Should mention the time index / range — that's the defining feature.",
)
def df_ts(ctx: CaseCtx):
    import numpy as np
    import pandas as pd

    idx = pd.date_range("2024-01-01", periods=24 * 30, freq="h")
    rng = np.random.default_rng(1)
    return pd.DataFrame(
        {"temp": rng.normal(15, 5, len(idx)), "load": rng.random(len(idx))}, index=idx
    )


@case(
    "synth/np_zero_len",
    tags=("adapter", "numpy", "edge"),
    requires=("numpy",),
    display_input="numpy array of shape (0, 5)",
    notes="Zero-length dimension should be stated plainly; no stats possible.",
)
def np_zero(ctx: CaseCtx):
    import numpy as np

    return np.empty((0, 5))


@case(
    "synth/np_nan_inf",
    tags=("adapter", "numpy", "edge"),
    requires=("numpy",),
    display_input="float array containing NaN and +/-inf among normal values",
    notes="Should surface the NaN/inf presence, not just mean/std.",
)
def np_nan_inf(ctx: CaseCtx):
    import numpy as np

    a = np.linspace(0, 1, 50)
    a[3] = np.nan
    a[10] = np.inf
    a[20] = -np.inf
    return a
