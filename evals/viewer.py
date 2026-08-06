"""Static HTML viewer for eval results.

    python -m evals.viewer [--open]

Reads evals/out/run.json (run `python -m evals.runner run` first) plus
evals/scores.json and evals/goldens/, and injects the run data into
docs/eval-report-template.html (markup/CSS/JS lives there, not here) to
produce a single self-contained report — no server, no build step, no
third-party JS. Data is embedded as a JSON blob; the template's vanilla-JS
handles search/filter and row expansion client-side.
"""

from __future__ import annotations

import argparse
import json
import sys
import webbrowser
from pathlib import Path

from evals.cases import GOLDENS_DIR, SCORES_PATH, golden_filename
from evals.runner import RUN_JSON

REPORT_HTML = RUN_JSON.parent / "report.html"
TEMPLATE_HTML = Path(__file__).resolve().parents[1] / "docs" / "eval-report-template.html"


def _row_data(records: list[dict], scores: dict) -> list[dict]:
    rows = []
    for r in records:
        entry = scores.get("cases", {}).get(r["id"])
        golden_exists = (GOLDENS_DIR / golden_filename(r["id"])).exists()
        rows.append(
            {
                "id": r["id"],
                "status": r["status"],
                "tags": list(r.get("tags", [])),
                "display_input": r.get("display_input") or "",
                "notes": r.get("notes") or "",
                "describe_kwargs": r.get("describe_kwargs") or {},
                "content": r.get("content"),
                "meta_excerpt": r.get("meta_excerpt"),
                "traceback": r.get("traceback"),
                "reason": r.get("reason"),
                "duration_ms": r.get("duration_ms"),
                "thumbnail": r.get("thumbnail"),
                "source_url": r.get("source_url") or "",
                "golden_exists": golden_exists,
                "golden_match": r.get("golden_match"),
                "score_state": r.get("score_state"),
                "overall": entry.get("overall") if entry else None,
                "scores": entry.get("scores") if entry else None,
                "critique": entry.get("critique") if entry else None,
                "judged_at": entry.get("judged_at") if entry else None,
            }
        )
    return rows


def build_report(out_path: Path | None = None) -> Path:
    if not RUN_JSON.exists():
        print("No run.json — run `python -m evals.runner run` first.", file=sys.stderr)
        raise SystemExit(2)
    if not TEMPLATE_HTML.exists():
        print(f"No template at {TEMPLATE_HTML}.", file=sys.stderr)
        raise SystemExit(2)
    run = json.loads(RUN_JSON.read_text())
    scores = json.loads(SCORES_PATH.read_text()) if SCORES_PATH.exists() else {"cases": {}}
    payload = {"env": run["env"], "rows": _row_data(run["cases"], scores)}
    data_json = json.dumps(payload).replace("</script>", "<\\/script>")
    dest = out_path or REPORT_HTML
    dest.parent.mkdir(parents=True, exist_ok=True)
    dest.write_text(TEMPLATE_HTML.read_text().replace("__DATA__", data_json))
    return dest


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(prog="evals.viewer")
    parser.add_argument("--open", action="store_true", help="open the report in a browser")
    parser.add_argument("--out", type=Path, default=None, help="write report to this path instead of evals/out/report.html")
    args = parser.parse_args(argv)
    dest = build_report(args.out)
    print(f"wrote {dest}")
    if args.open:
        webbrowser.open(dest.as_uri())
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
