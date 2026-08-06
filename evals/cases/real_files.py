"""Cases over real-world files.

Two sources:
- evals/manifest.json datasets, fetched into evals/cache by
  `python -m evals.runner fetch` (skip when absent).
- pre-existing local files in data/ at the repo root (gitignored; skip when
  absent so the corpus still runs on a fresh clone).
"""

from __future__ import annotations

import json
from pathlib import Path

from evals.cases import Case, CaseCtx, MANIFEST_PATH, case, register

REPO_DATA = Path(__file__).resolve().parent.parent.parent / "data"


def _manifest_urls() -> dict[str, str]:
    if not MANIFEST_PATH.exists():
        return {}
    manifest = json.loads(MANIFEST_PATH.read_text())
    return {d["filename"]: d["url"] for d in manifest.get("datasets", [])}


_MANIFEST_URLS = _manifest_urls()


@case(
    "real/titanic_shallow",
    tags=("sniffer", "csv", "real"),
    requires_file="titanic.csv",
    describe_kwargs={"shallow": True},
    display_input="seaborn titanic.csv (891 rows, 15 cols), shallow sniff",
    notes="Should identify a CSV with mixed types and nulls from the head alone.",
    source_url=_MANIFEST_URLS.get("titanic.csv", ""),
)
def titanic_shallow(ctx: CaseCtx):
    return ctx.cache / "titanic.csv"


@case(
    "real/titanic_deep",
    tags=("sniffer", "csv", "real", "deep"),
    requires=("pandas",),
    requires_file="titanic.csv",
    display_input="seaborn titanic.csv, deep profile (the default)",
    notes="Deep profile: dtypes, null counts, cardinality of key columns.",
    source_url=_MANIFEST_URLS.get("titanic.csv", ""),
)
def titanic_deep(ctx: CaseCtx):
    return ctx.cache / "titanic.csv"


@case(
    "real/penguins_deep",
    tags=("sniffer", "csv", "real", "deep"),
    requires=("pandas",),
    requires_file="penguins.csv",
    display_input="palmer penguins.csv, deep profile (has NA values)",
    notes="Should surface the NA values and the categorical species column.",
    source_url=_MANIFEST_URLS.get("penguins.csv", ""),
)
def penguins_deep(ctx: CaseCtx):
    return ctx.cache / "penguins.csv"


@case(
    "real/flights_json",
    tags=("sniffer", "json", "real"),
    requires_file="flights-200k.json",
    describe_kwargs={"shallow": True},
    display_input="vega flights-200k.json (~2MB columnar JSON)",
    notes="A dict of parallel arrays; should convey size and structure.",
    source_url=_MANIFEST_URLS.get("flights-200k.json", ""),
)
def flights_json(ctx: CaseCtx):
    return ctx.cache / "flights-200k.json"


@case(
    "real/flights_json_deep",
    tags=("sniffer", "json", "real", "deep"),
    requires_file="flights-200k.json",
    display_input="vega flights-200k.json (~2MB columnar JSON), deep profile (the default)",
    notes="Deep load parses the JSON into records; should report record/field counts, not just raw bytes.",
    source_url=_MANIFEST_URLS.get("flights-200k.json", ""),
)
def flights_json_deep(ctx: CaseCtx):
    return ctx.cache / "flights-200k.json"


# --- local repo data/ files (gitignored; skip when absent) -----------------
#
# Each entry also gets a deep=True sibling when the loader actually produces
# a richer object for that suffix (checked empirically: shallow vs. deep
# output differ) — deep-loading a suffix nothing rich-loads is otherwise a
# no-op duplicate case.

_LOCAL = [
    (
        "raw_soccer_data.csv",
        ("sniffer", "csv", "real", "messy"),
        "messy real-world soccer CSV from data/",
        True,
    ),
    (
        "population_A_mcp.jsonl",
        ("sniffer", "jsonl", "real"),
        "JSONL population data from data/",
        True,
    ),
    (
        "NLSY.dta",
        ("sniffer", "stata", "real"),
        "Stata .dta survey file from data/",
        True,
    ),
    (
        "G10010_sibt1850_v2.0.nc",
        ("sniffer", "netcdf", "real"),
        "NetCDF sea-ice dataset from data/",
        False,  # .nc isn't routed to a rich loader; deep output == shallow
    ),
    (
        "archive.zip",
        ("sniffer", "zip", "real"),
        "ZIP archive from data/",
        False,  # no zip content loader; deep output == shallow
    ),
]


def _make_local_build(path: Path):
    def build(ctx: CaseCtx):
        if not path.exists():
            raise FileNotFoundError(path)  # guarded by _exists check below
        return path

    return build


# A real directory with a dominant filename-pattern family (2016 near-
# identical PNGs) plus unrelated top-level siblings — the direct regression
# case for per-folder truncation (siblings must stay visible) and family
# collapsing (the PNG run should render as one line, not 2016).
_LOCAL_DIR = Path("G10010_SIBT1850_V2")

if (REPO_DATA / _LOCAL_DIR).exists():
    register(
        Case(
            id="real/local_sibt1850_dir",
            build=_make_local_build(REPO_DATA / _LOCAL_DIR),
            tags=("pathlib", "directory", "real"),
            describe_kwargs={"shallow": True},
            display_input="G10010_SIBT1850_V2/ directory (2000+ files, one dominant filename family)",
            notes=(
                "Should show source_montages/ and top-level CSV/cpt/nc files, not "
                "just the sibt1850_browse/ family; should collapse the "
                "sibt_ext_ease2_* PNG run into one line instead of one line per file."
            ),
        )
    )
    register(
        Case(
            id="real/local_sibt1850_dir_deep",
            build=_make_local_build(REPO_DATA / _LOCAL_DIR),
            tags=("pathlib", "directory", "real", "deep"),
            display_input="G10010_SIBT1850_V2/ directory, deep profile (the default)",
            notes=(
                "Deep-profiles each dataset in the tree; should still collapse "
                "the sibt_ext_ease2_* PNG family and keep every top-level "
                "sibling visible."
            ),
        )
    )


for _fname, _tags, _desc, _has_deep in _LOCAL:
    _path = REPO_DATA / _fname
    if not _path.exists():
        continue  # fresh clone: data/ is gitignored, silently omit
    _stem = _path.stem.lower().replace(".", "_")
    register(
        Case(
            id=f"real/local_{_stem}",
            build=_make_local_build(_path),
            tags=_tags,
            # When a deep sibling exists, this case is only interesting as
            # the shallow (sniffer-only) baseline, since deep is now the
            # describe() default. When no deep sibling exists (_has_deep is
            # False), this case runs deep (the default) since deep output
            # == shallow output for that suffix anyway.
            describe_kwargs={"shallow": True} if _has_deep else {},
            display_input=_desc,
        )
    )
    if _has_deep:
        register(
            Case(
                id=f"real/local_{_stem}_deep",
                build=_make_local_build(_path),
                tags=(*_tags, "deep"),
                display_input=f"{_desc}, deep profile (the default)",
            )
        )
