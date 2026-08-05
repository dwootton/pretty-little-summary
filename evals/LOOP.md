# Improvement Loop Protocol

Goal: `pls.describe(obj)` produces a GREAT, deterministic, fast natural-language
data profile for any Python object or file path — zero required dependencies,
extras for richer behavior. This loop makes it better one focused change at a
time without regressing what's already good.

All commands run from the repo root inside the project venv.

## One-time setup

```bash
pip install -e ".[dev,all]"        # or a subset; missing extras just skip cases
python -m evals.runner fetch       # download manifest datasets to evals/cache
```

## Each iteration

**1. RUN**

```bash
python -m evals.runner run
```

Read `evals/out/digest.md`. It lists only cases needing attention.

**2. TRIAGE** — in strict priority order:

1. `status=error` — crashes are always first.
2. `golden_match=false` — regressions: fix the code, or if the change was
   intentional and better, re-judge and re-bless (step 7).
3. `score_state=stale` — output changed since it was judged; re-judge.
4. `score_state=unscored` — new cases; judge.
5. Lowest `overall` in `evals/scores.json` — the improvement queue.

**3. JUDGE** — score stale + unscored cases against the rubric, using
`digest.md` ONLY (input spec, output, meta excerpt). Do not read adapter
source before scoring — judge the output as a user would see it. Each
dimension is 1–5:

- **accuracy** — every stated fact is correct for this input.
- **informativeness** — says the things a data-savvy user would most want to
  know about THIS object (shape, types, nulls, the defining feature). A
  technically-true-but-vacuous summary scores low.
- **conciseness** — no filler, no dumps of 500 column names, no repetition.
- **hallucination_free** — 5 = nothing claimed that isn't supported by the
  input/meta; any invented detail caps this at 2.

Record each score:

```bash
python -m evals.score_tool set <case_id> \
  --accuracy N --informativeness N --conciseness N --hallucination-free N \
  --critique "one or two sentences: what's good, what's missing" \
  --hash <output_hash from digest>
```

If there are more than ~10 cases to judge, spawn parallel subagents (~15
cases each); each subagent gets its digest sections and writes scores via
`score_tool` itself.

**4. PICK WORK** — take the lowest-`overall` cluster sharing a tag or adapter
(one synthesizer/adapter fix usually lifts several cases). Make ONE focused
change per iteration.

**5. IMPLEMENT** in `src/`. Constraints:

- New sniffers must stay zero-dep (head-bytes only, never execute content).
- New adapter dependencies go in a pyproject extra, never in `dependencies`.
- `describe()` stays deterministic: same input → same string.

**6. GATE** — all three must pass before anything else:

```bash
pytest -q
python -m evals.runner check-goldens
python -m evals.budget check
```

**7. RE-RUN & LOCK IN**

```bash
python -m evals.runner run --tags <affected-tag>   # or --ids ...
```

Re-judge changed outputs. Then:

- Case scores ≥ 4.5 and has no golden → `python -m evals.runner bless <id>`.
- A golden case changed intentionally and the new score ≥ the old score →
  re-judge, then re-bless the same way.

**8. GROW CORPUS** — if the fix revealed adjacent untested territory, add 1–3
new cases to `evals/cases/synthetic.py`, `live_objects.py`, or
`manifest.json` + `real_files.py`. Give each a `display_input` and `notes`
(what a good summary should mention).

**9. COMMIT** — code + `evals/scores.json` + `evals/goldens/` + new cases in
one commit. The message states the score delta, e.g.
`csv encoding sniffing: 4 cases 2.1 -> 4.8 avg`.

## Rules

- Never hand-edit files in `evals/goldens/` — only `runner bless` writes them.
- Never edit a scores.json entry except via `score_tool` after actually
  judging the current output.
- Never delete a case to improve the numbers. If a case is genuinely out of
  scope, keep it and record a critique saying why (tag `wontfix` in the
  critique text).
- API/ergonomics changes are allowed, but must update README and all affected
  goldens in the same iteration.
- A budget failure blocks the commit, full stop. Raising `max_src_loc` in
  `evals/budget.json` is allowed only with justification in the commit message.
