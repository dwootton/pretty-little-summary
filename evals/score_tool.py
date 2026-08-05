"""Upsert judge scores into evals/scores.json.

    python -m evals.score_tool set <case_id> \
        --accuracy 5 --informativeness 4 --conciseness 5 --hallucination-free 5 \
        --critique "..." --hash <output_hash>

The --hash must match the case's output_hash in the latest run.json — this
guarantees a score always refers to the output it judged. A lock file
serializes the read-modify-write so parallel judge agents cannot clobber
each other's entries.
"""

from __future__ import annotations

import argparse
import contextlib
import datetime
import json
import os
import sys
import time

from evals.cases import SCORES_PATH
from evals.runner import RUN_JSON

LOCK_PATH = SCORES_PATH.with_suffix(".lock")


@contextlib.contextmanager
def _scores_lock(timeout: float = 30.0):
    deadline = time.monotonic() + timeout
    while True:
        try:
            fd = os.open(LOCK_PATH, os.O_CREAT | os.O_EXCL | os.O_WRONLY)
            break
        except FileExistsError:
            if time.monotonic() > deadline:
                raise TimeoutError(f"could not acquire {LOCK_PATH}")
            time.sleep(0.05)
    try:
        yield
    finally:
        os.close(fd)
        with contextlib.suppress(FileNotFoundError):
            os.unlink(LOCK_PATH)

DIMENSIONS = ("accuracy", "informativeness", "conciseness", "hallucination_free")


def cmd_set(args: argparse.Namespace) -> int:
    if not RUN_JSON.exists():
        print("No run.json — run `python -m evals.runner run` first.", file=sys.stderr)
        return 2
    run = json.loads(RUN_JSON.read_text())
    record = next((r for r in run["cases"] if r["id"] == args.case_id), None)
    if record is None:
        print(f"Case {args.case_id!r} not in latest run.", file=sys.stderr)
        return 2
    if record["status"] != "ok":
        print(f"Case {args.case_id!r} was {record['status']}, not scorable.", file=sys.stderr)
        return 2
    if record["output_hash"] != args.hash:
        print(
            f"Hash mismatch: latest run has {record['output_hash']}, you judged "
            f"{args.hash}. Re-read the current output before scoring.",
            file=sys.stderr,
        )
        return 2

    scores = {
        "accuracy": args.accuracy,
        "informativeness": args.informativeness,
        "conciseness": args.conciseness,
        "hallucination_free": args.hallucination_free,
    }
    for dim, value in scores.items():
        if not 1 <= value <= 5:
            print(f"{dim} must be 1-5, got {value}", file=sys.stderr)
            return 2

    with _scores_lock():
        data = (
            json.loads(SCORES_PATH.read_text())
            if SCORES_PATH.exists()
            else {"rubric_version": 1, "cases": {}}
        )
        data["cases"][args.case_id] = {
            "output_hash": args.hash,
            "scores": scores,
            "overall": round(sum(scores.values()) / len(scores), 2),
            "critique": args.critique,
            "judged_at": datetime.datetime.now(datetime.timezone.utc)
            .replace(microsecond=0)
            .isoformat(),
        }
        data["cases"] = dict(sorted(data["cases"].items()))
        SCORES_PATH.write_text(json.dumps(data, indent=1) + "\n")
    entry = data["cases"][args.case_id]
    print(f"{args.case_id}: overall {entry['overall']}")
    return 0


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(prog="evals.score_tool")
    sub = parser.add_subparsers(dest="command", required=True)
    p_set = sub.add_parser("set", help="record scores for one case")
    p_set.add_argument("case_id")
    p_set.add_argument("--accuracy", type=int, required=True)
    p_set.add_argument("--informativeness", type=int, required=True)
    p_set.add_argument("--conciseness", type=int, required=True)
    p_set.add_argument("--hallucination-free", type=int, required=True, dest="hallucination_free")
    p_set.add_argument("--critique", required=True)
    p_set.add_argument("--hash", required=True)
    p_set.set_defaults(func=cmd_set)
    args = parser.parse_args(argv)
    return args.func(args)


if __name__ == "__main__":
    raise SystemExit(main())
