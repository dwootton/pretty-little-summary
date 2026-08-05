# pretty_little_summary (pls)

`pls.describe(obj)` returns a deterministic natural-language data profile for
any Python object or file path. Adapters handle live objects; sniffers
inspect files from head bytes only; `deep=True` loads files into rich objects.

## Invariants — never break these

- **Zero required dependencies.** `project.dependencies` stays `[]`. New
  adapter deps go in a pyproject extra. Sniffers are stdlib-only.
- **Determinism.** Same input → identical `describe()` output string.
- **Size budget.** `src/` LOC is capped by `evals/budget.json`
  (`python -m evals.budget check`). Raising the cap is a reviewed decision.
- **Sniffers never execute or fully load file content** (head bytes only;
  unpickling requires explicit opt-in).

## Improvement work

For any work on output quality, new adapters/sniffers, or the API, follow the
loop protocol in `evals/LOOP.md` (run corpus → judge → fix → gate → bless).

Gate before every commit:

```bash
pytest -q
python -m evals.runner check-goldens
python -m evals.budget check
```

Golden snapshots in `evals/goldens/` and score entries in `evals/scores.json`
are managed only via `evals/runner.py` and `evals/score_tool.py` — never by
hand.

Use the project venv: `.venv/bin/python`.
