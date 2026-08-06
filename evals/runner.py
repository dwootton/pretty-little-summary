"""Eval runner CLI.

Usage (from repo root, inside the project venv):

    python -m evals.runner run [--ids ID ...] [--tags TAG ...] [--fetch]
    python -m evals.runner bless ID... | --all-passing
    python -m evals.runner check-goldens
    python -m evals.runner fetch

`run` executes pls.describe() over the corpus and writes evals/out/run.json
(machine-readable) and evals/out/digest.md (judge-facing report of cases that
need attention). Errors are findings, not fatal.
"""

from __future__ import annotations

import argparse
import base64
import hashlib
import io
import json
import platform
import subprocess
import sys
import tempfile
import time
import traceback
import urllib.request
from contextlib import redirect_stderr, redirect_stdout
from pathlib import Path
from typing import Any

from evals.cases import (
    CACHE_DIR,
    GOLDENS_DIR,
    MANIFEST_PATH,
    OUT_DIR,
    SCORES_PATH,
    Case,
    CaseCtx,
    golden_filename,
    load_all_cases,
)

RUN_JSON = OUT_DIR / "run.json"
DIGEST_MD = OUT_DIR / "digest.md"
META_EXCERPT_BYTES = 2048
BLESS_THRESHOLD = 4.5


# ---------------------------------------------------------------------------
# Helpers


def output_hash(content: str) -> str:
    return hashlib.sha256(content.encode("utf-8")).hexdigest()[:16]


def load_scores() -> dict[str, Any]:
    if SCORES_PATH.exists():
        return json.loads(SCORES_PATH.read_text())
    return {"rubric_version": 1, "cases": {}}


def _json_safe(obj: Any, depth: int = 0) -> Any:
    """Best-effort conversion of metadata to JSON-serializable values."""
    if depth > 6:
        return "..."
    if obj is None or isinstance(obj, (bool, int, float, str)):
        return obj
    if isinstance(obj, dict):
        return {str(k): _json_safe(v, depth + 1) for k, v in list(obj.items())[:50]}
    if isinstance(obj, (list, tuple, set)):
        return [_json_safe(v, depth + 1) for v in list(obj)[:20]]
    return repr(obj)[:200]


def meta_excerpt(meta: Any) -> str:
    try:
        text = json.dumps(_json_safe(meta), default=repr, sort_keys=True)
    except Exception:
        text = repr(meta)
    if len(text) > META_EXCERPT_BYTES:
        text = text[:META_EXCERPT_BYTES] + "...<truncated>"
    return text


def _run_cleanup(cleanup: Any) -> None:
    if cleanup is None:
        return
    if hasattr(cleanup, "close"):
        cleanup.close()
    elif callable(cleanup):
        cleanup()


def installed_extras() -> list[str]:
    import importlib.util

    libs = (
        "pandas", "polars", "numpy", "pyarrow", "scipy", "matplotlib",
        "altair", "seaborn", "plotly", "bokeh", "PIL", "torch", "tensorflow",
        "jax", "sklearn", "statsmodels", "xarray", "networkx", "h5py",
        "pydantic", "attr", "requests", "IPython",
    )
    return [m for m in libs if importlib.util.find_spec(m) is not None]


def git_sha() -> str:
    try:
        return subprocess.run(
            ["git", "rev-parse", "--short", "HEAD"],
            capture_output=True, text=True, check=True,
        ).stdout.strip()
    except Exception:
        return "unknown"


def capture_thumbnail(obj: Any) -> str | None:
    """Best-effort PNG data-URI thumbnail for visual result objects.

    Never raises: returns None for non-visual objects or on any rendering
    failure, since this is a diagnostic nice-to-have, not part of describe().
    """
    try:
        fig = None
        try:
            from matplotlib.axes import Axes
            from matplotlib.figure import Figure

            if isinstance(obj, Figure):
                fig = obj
            elif isinstance(obj, Axes):
                fig = obj.figure
        except ImportError:
            pass

        if fig is not None:
            buf = io.BytesIO()
            fig.savefig(buf, format="png", dpi=90, bbox_inches="tight")
            return "data:image/png;base64," + base64.b64encode(buf.getvalue()).decode("ascii")

        try:
            from PIL.Image import Image

            img = None
            if isinstance(obj, Image):
                img = obj
            elif isinstance(obj, list) and obj and isinstance(obj[0], Image):
                img = obj[0]
            if img is not None:
                img = img.copy()
                img.thumbnail((320, 320))
                buf = io.BytesIO()
                img.save(buf, format="PNG")
                return "data:image/png;base64," + base64.b64encode(buf.getvalue()).decode("ascii")
        except ImportError:
            pass
    except Exception:
        return None
    return None


# ---------------------------------------------------------------------------
# run


def run_case(case_obj: Case, ctx: CaseCtx) -> dict[str, Any]:
    record: dict[str, Any] = {
        "id": case_obj.id,
        "tags": list(case_obj.tags),
        "display_input": case_obj.display_input,
        "notes": case_obj.notes,
        "describe_kwargs": case_obj.describe_kwargs,
        "source_url": case_obj.source_url,
    }
    skip_reason = case_obj.missing_requirement()
    if skip_reason:
        record.update(status="skip", reason=skip_reason)
        return record

    import pretty_little_summary as pls

    cleanup = None
    start = time.perf_counter()
    try:
        built = case_obj.build(ctx)
        if isinstance(built, tuple) and len(built) == 2 and callable(built[1]):
            obj, cleanup = built
        else:
            obj = built
        # Silence chatty libraries so runner output stays a clean report.
        with redirect_stdout(io.StringIO()), redirect_stderr(io.StringIO()):
            result = pls.describe(obj, **case_obj.describe_kwargs)
        thumbnail = capture_thumbnail(obj)
    except Exception:
        record.update(
            status="error",
            traceback=traceback.format_exc(limit=8),
            duration_ms=round((time.perf_counter() - start) * 1000, 2),
        )
        return record
    finally:
        try:
            _run_cleanup(cleanup)
        except Exception:
            pass

    record.update(
        status="ok",
        content=result.content,
        output_hash=output_hash(result.content),
        meta_excerpt=meta_excerpt(result.meta),
        duration_ms=round((time.perf_counter() - start) * 1000, 2),
        thumbnail=thumbnail,
    )
    return record


def annotate(record: dict[str, Any], scores: dict[str, Any]) -> None:
    """Add golden_match and score_state to an ok-record."""
    if record["status"] != "ok":
        record["golden_match"] = None
        record["score_state"] = "n/a"
        return
    golden = GOLDENS_DIR / golden_filename(record["id"])
    if golden.exists():
        record["golden_match"] = golden.read_text() == record["content"]
    else:
        record["golden_match"] = None
    entry = scores.get("cases", {}).get(record["id"])
    if entry is None:
        record["score_state"] = "unscored"
    elif entry.get("output_hash") == record["output_hash"]:
        record["score_state"] = "fresh"
        record["prior_score"] = entry
    else:
        record["score_state"] = "stale"
        record["prior_score"] = entry


def cmd_run(args: argparse.Namespace) -> int:
    if args.fetch:
        cmd_fetch(args)
    cases = load_all_cases()
    selected = []
    for case_obj in cases.values():
        if args.ids and case_obj.id not in args.ids:
            continue
        if args.tags and not (set(args.tags) & set(case_obj.tags)):
            continue
        selected.append(case_obj)
    if args.ids:
        unknown = set(args.ids) - {c.id for c in selected}
        if unknown:
            print(f"Unknown case ids: {sorted(unknown)}", file=sys.stderr)
            return 2

    scores = load_scores()
    OUT_DIR.mkdir(exist_ok=True)
    records = []
    with tempfile.TemporaryDirectory(prefix="pls-evals-") as tmp:
        ctx = CaseCtx(tmp=Path(tmp), cache=CACHE_DIR)
        for case_obj in selected:
            record = run_case(case_obj, ctx)
            annotate(record, scores)
            records.append(record)

    env = {
        "python": platform.python_version(),
        "platform": platform.platform(),
        "git_sha": git_sha(),
        "installed_extras": installed_extras(),
        "selection": {"ids": args.ids or None, "tags": args.tags or None},
    }
    RUN_JSON.write_text(json.dumps({"env": env, "cases": records}, indent=1))
    write_digest(records, env)

    counts = _counts(records)
    print(
        f"ran {len(records)} cases: {counts['ok']} ok, {counts['skip']} skip, "
        f"{counts['error']} error | goldens: {counts['golden_fail']} mismatched | "
        f"scores: {counts['stale']} stale, {counts['unscored']} unscored"
    )
    print(f"wrote {RUN_JSON} and {DIGEST_MD}")
    return 0


def _counts(records: list[dict[str, Any]]) -> dict[str, int]:
    return {
        "ok": sum(r["status"] == "ok" for r in records),
        "skip": sum(r["status"] == "skip" for r in records),
        "error": sum(r["status"] == "error" for r in records),
        "golden_fail": sum(r.get("golden_match") is False for r in records),
        "stale": sum(r.get("score_state") == "stale" for r in records),
        "unscored": sum(
            r["status"] == "ok" and r.get("score_state") == "unscored" for r in records
        ),
    }


def write_digest(records: list[dict[str, Any]], env: dict[str, Any]) -> None:
    counts = _counts(records)
    lines = [
        "# Eval digest",
        "",
        f"git {env['git_sha']} | python {env['python']} | "
        f"{len(env['installed_extras'])} optional libs installed",
        "",
        f"- {counts['ok']} ok / {counts['skip']} skip / {counts['error']} **error**",
        f"- {counts['golden_fail']} golden regressions",
        f"- {counts['stale']} stale scores (output changed since judged)",
        f"- {counts['unscored']} unscored",
        "",
        "Judge each case below on the rubric in evals/LOOP.md, then record with:",
        "`python -m evals.score_tool set <id> --accuracy N --informativeness N "
        "--conciseness N --hallucination-free N --critique '...' --hash <hash>`",
        "",
    ]

    def emit(record: dict[str, Any], flag: str) -> None:
        lines.append(f"## {record['id']}   [{flag}]  tags: {','.join(record['tags'])}")
        if record.get("describe_kwargs"):
            lines.append(f"KWARGS: {record['describe_kwargs']}")
        lines.append(f"INPUT: {record['display_input'] or '(see case source)'}")
        if record.get("notes"):
            lines.append(f"NOTES: {record['notes']}")
        if record["status"] == "error":
            lines.append("TRACEBACK:")
            lines.append("```")
            lines.append(record["traceback"].rstrip())
            lines.append("```")
        elif record["status"] == "skip":
            lines.append(f"SKIPPED: {record['reason']}")
        else:
            lines.append(f"OUTPUT (hash {record['output_hash']}):")
            lines.append("> " + record["content"].replace("\n", "\n> "))
            lines.append(f"META: {record['meta_excerpt']}")
            prior = record.get("prior_score")
            if prior:
                lines.append(
                    f"PRIOR SCORE: overall {prior.get('overall')} — "
                    f"{prior.get('critique', '')}"
                )
        lines.append("")

    sections = [
        ("errors", [r for r in records if r["status"] == "error"], "ERROR"),
        (
            "golden regressions",
            [r for r in records if r.get("golden_match") is False],
            "GOLDEN MISMATCH",
        ),
        (
            "stale (re-judge)",
            [r for r in records if r.get("score_state") == "stale"],
            "STALE",
        ),
        (
            "unscored (judge)",
            [
                r
                for r in records
                if r["status"] == "ok" and r.get("score_state") == "unscored"
            ],
            "UNSCORED",
        ),
    ]
    emitted = set()
    for title, group, flag in sections:
        group = [r for r in group if r["id"] not in emitted]
        if not group:
            continue
        lines.append(f"# {title} ({len(group)})")
        lines.append("")
        for record in group:
            emit(record, flag)
            emitted.add(record["id"])
    if not emitted:
        lines.append("Nothing needs attention: no errors, regressions, or unscored cases.")
    DIGEST_MD.write_text("\n".join(lines) + "\n")


# ---------------------------------------------------------------------------
# goldens


def cmd_bless(args: argparse.Namespace) -> int:
    if not RUN_JSON.exists():
        print("No run.json — run `python -m evals.runner run` first.", file=sys.stderr)
        return 2
    run = json.loads(RUN_JSON.read_text())
    by_id = {r["id"]: r for r in run["cases"]}
    scores = load_scores()

    if args.all_passing:
        targets = [
            r["id"]
            for r in run["cases"]
            if r["status"] == "ok"
            and r.get("score_state") == "fresh"
            and r.get("prior_score", {}).get("overall", 0) >= BLESS_THRESHOLD
        ]
    else:
        targets = args.ids

    GOLDENS_DIR.mkdir(exist_ok=True)
    blessed = 0
    for case_id in targets:
        record = by_id.get(case_id)
        if record is None or record["status"] != "ok":
            print(f"skip {case_id}: not an ok case in last run", file=sys.stderr)
            continue
        entry = scores.get("cases", {}).get(case_id)
        if entry is None or entry.get("output_hash") != record["output_hash"]:
            print(
                f"skip {case_id}: current output has no fresh score "
                "(judge it first, then bless)",
                file=sys.stderr,
            )
            continue
        if entry.get("overall", 0) < BLESS_THRESHOLD:
            print(
                f"skip {case_id}: overall {entry.get('overall')} < {BLESS_THRESHOLD}",
                file=sys.stderr,
            )
            continue
        (GOLDENS_DIR / golden_filename(case_id)).write_text(record["content"])
        blessed += 1
        print(f"blessed {case_id}")
    print(f"{blessed} golden(s) written")
    return 0


def iter_golden_case_ids() -> list[str]:
    if not GOLDENS_DIR.exists():
        return []
    ids = []
    for path in sorted(GOLDENS_DIR.glob("*.txt")):
        ids.append(path.stem.replace("__", "/"))
    return ids


def check_goldens(case_ids: list[str] | None = None) -> list[tuple[str, str]]:
    """Re-run golden cases; return list of (case_id, problem) mismatches."""
    cases = load_all_cases()
    failures: list[tuple[str, str]] = []
    targets = case_ids if case_ids is not None else iter_golden_case_ids()
    with tempfile.TemporaryDirectory(prefix="pls-evals-") as tmp:
        ctx = CaseCtx(tmp=Path(tmp), cache=CACHE_DIR)
        for case_id in targets:
            case_obj = cases.get(case_id)
            golden = GOLDENS_DIR / golden_filename(case_id)
            if case_obj is None:
                failures.append((case_id, "golden exists but case is gone"))
                continue
            if case_obj.missing_requirement():
                continue  # skip, same policy as run
            record = run_case(case_obj, ctx)
            if record["status"] != "ok":
                failures.append((case_id, f"case now {record['status']}"))
            elif record["content"] != golden.read_text():
                failures.append((case_id, "output differs from golden"))
    return failures


def cmd_check_goldens(args: argparse.Namespace) -> int:
    failures = check_goldens()
    total = len(iter_golden_case_ids())
    if failures:
        for case_id, problem in failures:
            print(f"FAIL {case_id}: {problem}")
        print(f"{len(failures)}/{total} golden(s) failed")
        return 1
    print(f"all {total} golden(s) match")
    return 0


# ---------------------------------------------------------------------------
# fetch


def cmd_fetch(args: argparse.Namespace) -> int:
    if not MANIFEST_PATH.exists():
        print("no manifest.json; nothing to fetch")
        return 0
    manifest = json.loads(MANIFEST_PATH.read_text())
    CACHE_DIR.mkdir(exist_ok=True)
    for entry in manifest.get("datasets", []):
        dest = CACHE_DIR / entry["filename"]
        if dest.exists() and _sha256(dest) == entry["sha256"]:
            print(f"cached  {entry['filename']}")
            continue
        print(f"fetch   {entry['filename']} <- {entry['url']}")
        try:
            with urllib.request.urlopen(entry["url"], timeout=60) as resp:
                data = resp.read()
        except Exception as exc:
            print(f"  FAILED: {exc}", file=sys.stderr)
            continue
        digest = hashlib.sha256(data).hexdigest()
        if entry.get("sha256") and digest != entry["sha256"]:
            print(
                f"  FAILED: sha256 mismatch (got {digest[:16]}..., "
                f"expected {entry['sha256'][:16]}...)",
                file=sys.stderr,
            )
            continue
        dest.write_bytes(data)
        print(f"  ok ({len(data):,} bytes)")
    return 0


def _sha256(path: Path) -> str:
    h = hashlib.sha256()
    with path.open("rb") as f:
        for chunk in iter(lambda: f.read(1 << 20), b""):
            h.update(chunk)
    return h.hexdigest()


# ---------------------------------------------------------------------------
# main


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(prog="evals.runner")
    sub = parser.add_subparsers(dest="command", required=True)

    p_run = sub.add_parser("run", help="run the corpus and emit run.json + digest.md")
    p_run.add_argument("--ids", nargs="*", default=[])
    p_run.add_argument("--tags", nargs="*", default=[])
    p_run.add_argument("--fetch", action="store_true", help="fetch manifest datasets first")
    p_run.set_defaults(func=cmd_run)

    p_bless = sub.add_parser("bless", help="write golden snapshots for judged cases")
    p_bless.add_argument("ids", nargs="*")
    p_bless.add_argument("--all-passing", action="store_true")
    p_bless.set_defaults(func=cmd_bless)

    p_check = sub.add_parser("check-goldens", help="re-run golden cases and diff")
    p_check.set_defaults(func=cmd_check_goldens)

    p_fetch = sub.add_parser("fetch", help="download manifest datasets to evals/cache")
    p_fetch.set_defaults(func=cmd_fetch)

    args = parser.parse_args(argv)
    return args.func(args)


if __name__ == "__main__":
    raise SystemExit(main())
