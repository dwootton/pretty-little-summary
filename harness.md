# Eval harness: running it and viewing results

This is the "how do I actually run this" reference. For the iteration
protocol (how to turn results into library improvements), see
`evals/LOOP.md`.

## Setup

```bash
.venv/bin/pip install -e ".[dev,all]"   # or a subset — missing extras just skip cases
.venv/bin/python -m evals.runner fetch  # download manifest.json datasets into evals/cache/
```

`fetch` is optional. Cases whose file/dependency isn't available are
reported as `skip`, not failures.

## Running the corpus

```bash
.venv/bin/python -m evals.runner run                    # everything
.venv/bin/python -m evals.runner run --tags csv sniffer  # only matching tags
.venv/bin/python -m evals.runner run --ids real/titanic_shallow synth/empty_csv
```

Each case builds one object (or file `Path`) and calls `pls.describe()` on
it inside a temp dir, catching errors as findings rather than aborting.
This writes two files into `evals/out/` (gitignored — regenerate anytime):

- **`evals/out/run.json`** — machine-readable: every case's status, full
  output, output hash, a truncated metadata excerpt, timing, golden-match
  and score-freshness state. This is the source of truth the other tools
  read from.
- **`evals/out/digest.md`** — a judge-facing report containing *only* cases
  that need attention (errors, golden regressions, stale scores, unscored
  cases), each with its input spec, notes, full output, and prior score if
  any. Read this to judge or triage — you shouldn't need to open anything
  else.

## Viewing results

**Quick numbers:** the last line `python -m evals.runner run` prints is a
one-line summary (ok/skip/error counts, golden mismatches, stale/unscored).

**What needs attention right now:** open `evals/out/digest.md`.

**Browse everything, including cases already scored and blessed:**

```bash
.venv/bin/python -m evals.viewer --open
```

Generates `evals/out/report.html` — a single self-contained static page (no
server, no JS framework) — and opens it in your browser. It lists every
case with searchable/filterable columns (status, tags, golden state, score)
and expands each row to show the input spec, notes, full `describe()`
output, metadata excerpt, and the judge's per-dimension scores + critique.

**Historical scores and critiques:** `evals/scores.json` — keyed by case
id, holds the last judged score (accuracy/informativeness/conciseness/
hallucination_free, each 1-5) plus a free-text critique and the output hash
it was judged against. Only ever written by `evals/score_tool.py`.

**Locked-in exemplar outputs:** `evals/goldens/<id-with-slashes-as-__>.txt`
— the exact `describe()` output for a case once it scored ≥4.5. `pytest`
(`tests/test_eval_goldens.py`) and `python -m evals.runner check-goldens`
both fail if current output drifts from these. Only ever written by
`runner bless`.

## What a case's input looks like

Every case is a `Case` (`evals/cases/__init__.py`): an id, a `build(ctx)`
function returning an object (or file `Path`) to hand to `describe()`, tags,
optional `requires`/`requires_file` (missing → skip), and two judge-facing
fields — `display_input` (a one-line description of what the input *is*)
and `notes` (what a good summary should mention about it). These two fields
are what you see in `digest.md` and the viewer without needing to read the
case source.

Cases come from four corpus modules under `evals/cases/`:

- **`gallery.py`** — auto-wraps every example in `tests/input/` (existing
  test fixtures) as a case, for free.
- **`synthetic.py`** — scripted edge cases: empty/truncated files, odd
  encodings, pathological containers, scale tests. Stdlib-only where
  possible, fixed seeds for determinism.
- **`live_objects.py`** — real library objects (fitted sklearn models,
  matplotlib figures, polars LazyFrames, etc.) exercising optional adapters.
- **`real_files.py`** — real-world files, either downloaded via
  `manifest.json` (`runner fetch`) or picked up from the gitignored local
  `data/` directory when present (skipped otherwise).

## Gate before committing any fix

```bash
pytest -q
python -m evals.runner check-goldens
python -m evals.budget check
```

`evals/budget.py check` also prints the current `src/` LOC against the cap
in `evals/budget.json`.
