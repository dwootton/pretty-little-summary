"""Cases over real-world files.

Two sources:
- evals/manifest.json datasets, fetched into evals/cache by
  `python -m evals.runner fetch` (skip when absent).
- pre-existing local files in data/ at the repo root (gitignored; skip when
  absent so the corpus still runs on a fresh clone).
"""

from __future__ import annotations

from pathlib import Path

from evals.cases import Case, CaseCtx, case, register

REPO_DATA = Path(__file__).resolve().parent.parent.parent / "data"


@case(
    "real/titanic_shallow",
    tags=("sniffer", "csv", "real"),
    requires_file="titanic.csv",
    display_input="seaborn titanic.csv (891 rows, 15 cols), shallow sniff",
    notes="Should identify a CSV with mixed types and nulls from the head alone.",
)
def titanic_shallow(ctx: CaseCtx):
    return ctx.cache / "titanic.csv"


@case(
    "real/titanic_deep",
    tags=("sniffer", "csv", "real", "deep"),
    requires=("pandas",),
    requires_file="titanic.csv",
    describe_kwargs={"deep": True},
    display_input="seaborn titanic.csv with deep=True",
    notes="Deep profile: dtypes, null counts, cardinality of key columns.",
)
def titanic_deep(ctx: CaseCtx):
    return ctx.cache / "titanic.csv"


@case(
    "real/penguins_deep",
    tags=("sniffer", "csv", "real", "deep"),
    requires=("pandas",),
    requires_file="penguins.csv",
    describe_kwargs={"deep": True},
    display_input="palmer penguins.csv with deep=True (has NA values)",
    notes="Should surface the NA values and the categorical species column.",
)
def penguins_deep(ctx: CaseCtx):
    return ctx.cache / "penguins.csv"


@case(
    "real/flights_json",
    tags=("sniffer", "json", "real"),
    requires_file="flights-200k.json",
    display_input="vega flights-200k.json (~2MB columnar JSON)",
    notes="A dict of parallel arrays; should convey size and structure.",
)
def flights_json(ctx: CaseCtx):
    return ctx.cache / "flights-200k.json"


# --- local repo data/ files (gitignored; skip when absent) -----------------

_LOCAL = [
    (
        "raw_soccer_data.csv",
        ("sniffer", "csv", "real", "messy"),
        "messy real-world soccer CSV from data/",
    ),
    (
        "population_A_mcp.jsonl",
        ("sniffer", "jsonl", "real"),
        "JSONL population data from data/",
    ),
    (
        "NLSY.dta",
        ("sniffer", "stata", "real"),
        "Stata .dta survey file from data/",
    ),
    (
        "G10010_sibt1850_v2.0.nc",
        ("sniffer", "netcdf", "real"),
        "NetCDF sea-ice dataset from data/",
    ),
    (
        "archive.zip",
        ("sniffer", "zip", "real"),
        "ZIP archive from data/",
    ),
]


def _make_local_build(path: Path):
    def build(ctx: CaseCtx):
        if not path.exists():
            raise FileNotFoundError(path)  # guarded by _exists check below
        return path

    return build


for _fname, _tags, _desc in _LOCAL:
    _path = REPO_DATA / _fname
    if not _path.exists():
        continue  # fresh clone: data/ is gitignored, silently omit
    register(
        Case(
            id=f"real/local_{_path.stem.lower().replace('.', '_')}",
            build=_make_local_build(_path),
            tags=_tags,
            display_input=_desc,
        )
    )
