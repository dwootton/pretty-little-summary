"""Static HTML viewer for eval results.

    python -m evals.viewer [--open]

Reads evals/out/run.json (run `python -m evals.runner run` first) plus
evals/scores.json and evals/goldens/, and writes a single self-contained
evals/out/report.html — no server, no build step, no third-party JS. Data is
embedded as a JSON blob; a small vanilla-JS snippet handles search/filter and
row expansion client-side.
"""

from __future__ import annotations

import argparse
import html
import json
import sys
import webbrowser

from evals.cases import GOLDENS_DIR, SCORES_PATH, golden_filename
from evals.runner import RUN_JSON

REPORT_HTML = RUN_JSON.parent / "report.html"


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


_PAGE = """<!doctype html>
<html>
<head>
<meta charset="utf-8">
<title>pls eval results</title>
<style>
  :root {
    --ink: #1a1d23; --dim: #6b7280; --line: #e5e7eb; --panel: #f8f9fb;
    --accent: #5b5bd6; --ok: #1e7e34; --ok-bg: #e6f4ea;
    --bad: #b3261e; --bad-bg: #fbe9e8; --warn: #8a6100; --warn-bg: #fff4d6;
  }
  * { box-sizing: border-box; }
  body {
    font: 14px/1.45 -apple-system, BlinkMacSystemFont, "Segoe UI", sans-serif;
    margin: 0; padding: 0; color: var(--ink); background: #fff;
  }
  code, .mono { font: 12.5px/1.4 ui-monospace, SFMono-Regular, Menlo, Consolas, monospace; }
  header {
    padding: 16px 24px; border-bottom: 1px solid var(--line); position: sticky; top: 0;
    background: rgba(255,255,255,.96); backdrop-filter: blur(6px); z-index: 2;
  }
  header h1 { font-size: 17px; margin: 0 0 2px; letter-spacing: -0.01em; }
  header h1 .accent { color: var(--accent); }
  .meta { color: var(--dim); font-size: 12px; margin-bottom: 12px; }
  .meta .mono { color: var(--dim); }

  .stats { display: flex; gap: 10px; flex-wrap: wrap; margin-bottom: 12px; }
  .stat {
    background: var(--panel); border: 1px solid var(--line); border-radius: 8px;
    padding: 7px 12px; min-width: 88px;
  }
  .stat .n { font-size: 17px; font-weight: 650; line-height: 1.1; }
  .stat .l { font-size: 10.5px; text-transform: uppercase; letter-spacing: .04em; color: var(--dim); }
  .stat.warn .n { color: var(--warn); }
  .stat.bad .n { color: var(--bad); }
  .stat.ok .n { color: var(--ok); }

  .controls { display: flex; gap: 8px; flex-wrap: wrap; align-items: center; }
  input[type=text] {
    flex: 1; min-width: 220px; padding: 6px 10px; font: inherit; border: 1px solid var(--line);
    border-radius: 6px; outline: none;
  }
  input[type=text]:focus { border-color: var(--accent); box-shadow: 0 0 0 3px rgba(91,91,214,.12); }
  select {
    padding: 6px 8px; font: inherit; border: 1px solid var(--line); border-radius: 6px;
    background: #fff; color: var(--ink);
  }
  #count { color: var(--dim); font-size: 12px; white-space: nowrap; }

  table { width: 100%; border-collapse: collapse; }
  th, td { text-align: left; padding: 7px 10px; border-bottom: 1px solid var(--line); vertical-align: top; }
  th {
    position: sticky; top: 113px; background: var(--panel); font-size: 11px; color: var(--dim);
    text-transform: uppercase; letter-spacing: .03em; z-index: 1; user-select: none;
  }
  th.sortable { cursor: pointer; }
  th.sortable:hover { color: var(--ink); }
  th .arrow { opacity: .4; margin-left: 2px; }
  th.sorted .arrow { opacity: 1; color: var(--accent); }
  td.num, th.num { text-align: right; }
  tr.row { cursor: pointer; }
  tr.row:hover { background: #f5f6fa; }
  tr.row.error-row { background: #fef7f6; }
  tr.row.error-row:hover { background: #fcecec; }
  tr.detail { display: none; }
  tr.detail.open { display: table-row; }
  tr.detail td { background: var(--panel); padding: 12px 22px 18px; }

  .tag {
    display: inline-block; background: #ecebfb; color: #4c3fb3; border-radius: 999px;
    padding: 1px 8px; margin: 1px 2px 1px 0; font-size: 10.5px; font-weight: 550;
  }
  .badge {
    display: inline-block; border-radius: 5px; padding: 2px 7px; font-size: 11px; font-weight: 650;
  }
  .badge.ok { background: var(--ok-bg); color: var(--ok); }
  .badge.error { background: var(--bad-bg); color: var(--bad); }
  .badge.skip { background: #eee; color: #777; }
  .badge.mismatch { background: var(--bad-bg); color: var(--bad); }
  .badge.match { background: var(--ok-bg); color: var(--ok); }
  .badge.stale { background: var(--warn-bg); color: var(--warn); }
  .badge.unscored { background: #eee; color: #777; }
  .badge.fresh { background: var(--ok-bg); color: var(--ok); }

  .dur-cell { display: flex; align-items: center; gap: 7px; justify-content: flex-end; }
  .dur-bar-track { width: 46px; height: 5px; border-radius: 3px; background: #edeef2; overflow: hidden; }
  .dur-bar-fill { height: 100%; background: linear-gradient(90deg, #8b8bf0, var(--accent)); border-radius: 3px; }
  .dur-val { font-variant-numeric: tabular-nums; min-width: 52px; text-align: right; }
  .dur-val.slow { color: var(--warn); font-weight: 650; }

  pre {
    white-space: pre-wrap; word-break: break-word; background: #fff; border: 1px solid var(--line);
    padding: 10px; border-radius: 6px; margin: 4px 0 12px; font: 12.5px/1.5 ui-monospace, Menlo, Consolas, monospace;
  }
  .field-label {
    font-size: 10.5px; text-transform: uppercase; letter-spacing: .04em; color: var(--dim);
    margin-top: 10px; font-weight: 650;
  }
  .score-grid { display: flex; gap: 16px; margin: 8px 0; }
  .score-grid div { font-size: 12px; color: var(--dim); }
  .score-grid b { font-size: 16px; color: var(--ink); }
  .toggle-cell { color: var(--dim); width: 18px; }
</style>
</head>
<body>
<header>
  <h1>pls <span class="accent">eval</span> results</h1>
  <div class="meta mono" id="env-meta"></div>
  <div class="stats" id="stats"></div>
  <div class="controls">
    <input type="text" id="search" placeholder="search id / tags / input / notes / critique...">
    <select id="status-filter">
      <option value="">status: any</option>
      <option value="ok">ok</option>
      <option value="error">error</option>
      <option value="skip">skip</option>
    </select>
    <select id="golden-filter">
      <option value="">golden: any</option>
      <option value="mismatch">mismatch</option>
      <option value="match">match</option>
      <option value="none">no golden</option>
    </select>
    <select id="score-filter">
      <option value="">score: any</option>
      <option value="stale">stale</option>
      <option value="unscored">unscored</option>
      <option value="fresh">fresh</option>
      <option value="low">overall &lt; 4</option>
    </select>
    <span id="count"></span>
  </div>
</header>
<table>
  <thead>
    <tr>
      <th></th>
      <th class="sortable" data-key="id">id <span class="arrow">↕</span></th>
      <th class="sortable" data-key="status">status <span class="arrow">↕</span></th>
      <th>tags</th>
      <th class="sortable" data-key="golden_match">golden <span class="arrow">↕</span></th>
      <th class="sortable" data-key="score_state">score <span class="arrow">↕</span></th>
      <th class="sortable num" data-key="overall">overall <span class="arrow">↕</span></th>
      <th class="sortable num" data-key="duration_ms">time <span class="arrow">↕</span></th>
    </tr>
  </thead>
  <tbody id="tbody"></tbody>
</table>
<script id="data" type="application/json">__DATA__</script>
<script>
const payload = JSON.parse(document.getElementById('data').textContent);
const rows = payload.rows;

function esc(s) {
  const d = document.createElement('div');
  d.textContent = s == null ? '' : String(s);
  return d.innerHTML;
}

function fmtMs(ms) {
  if (ms == null) return '-';
  if (ms >= 1000) return (ms / 1000).toFixed(2) + 's';
  if (ms >= 1) return ms.toFixed(1) + 'ms';
  return ms.toFixed(2) + 'ms';
}

const durations = rows.map(r => r.duration_ms).filter(d => d != null);
const totalMs = durations.reduce((a, b) => a + b, 0);
const maxMs = durations.length ? Math.max(...durations) : 0;
const slowest = rows.filter(r => r.duration_ms != null)
  .sort((a, b) => b.duration_ms - a.duration_ms)[0];

document.getElementById('env-meta').textContent =
  `git ${payload.env.git_sha} | python ${payload.env.python} | ` +
  `${payload.env.installed_extras.length} optional libs installed`;

function renderStats() {
  const okN = rows.filter(r => r.status === 'ok').length;
  const errN = rows.filter(r => r.status === 'error').length;
  const skipN = rows.filter(r => r.status === 'skip').length;
  const mismatchN = rows.filter(r => r.golden_match === false).length;
  const cards = [
    {l: 'cases', n: rows.length},
    {l: 'ok', n: okN, cls: 'ok'},
    {l: 'error', n: errN, cls: errN ? 'bad' : ''},
    {l: 'skip', n: skipN},
    {l: 'golden mismatch', n: mismatchN, cls: mismatchN ? 'bad' : ''},
    {l: 'total runtime', n: fmtMs(totalMs)},
    {l: 'slowest case', n: slowest ? fmtMs(slowest.duration_ms) : '-'},
  ];
  document.getElementById('stats').innerHTML = cards.map(c =>
    `<div class="stat ${c.cls || ''}"><div class="n">${c.n}</div><div class="l">${c.l}</div></div>`
  ).join('');
}
renderStats();

function goldenBadge(r) {
  if (!r.golden_exists) return '<span class="badge">-</span>';
  return r.golden_match
    ? '<span class="badge match">match</span>'
    : '<span class="badge mismatch">mismatch</span>';
}

function scoreBadge(r) {
  if (!r.score_state || r.score_state === 'n/a') return '<span class="badge">-</span>';
  return `<span class="badge ${r.score_state}">${r.score_state}</span>`;
}

function durationCell(r) {
  if (r.duration_ms == null) return '<span class="dur-val">-</span>';
  const pct = maxMs > 0 ? Math.max(3, Math.round((Math.log10(r.duration_ms + 1) / Math.log10(maxMs + 1)) * 100)) : 0;
  const slow = maxMs > 0 && r.duration_ms >= maxMs * 0.5 && r.duration_ms > 20;
  return `
    <div class="dur-cell">
      <span class="dur-val ${slow ? 'slow' : ''}">${fmtMs(r.duration_ms)}</span>
      <span class="dur-bar-track"><span class="dur-bar-fill" style="width:${pct}%"></span></span>
    </div>`;
}

function detailHtml(r) {
  let parts = [];
  if (Object.keys(r.describe_kwargs).length) {
    parts.push(`<div class="field-label">kwargs</div><pre>${esc(JSON.stringify(r.describe_kwargs))}</pre>`);
  }
  parts.push(`<div class="field-label">input</div><pre>${esc(r.display_input || '(see case source)')}</pre>`);
  if (r.notes) parts.push(`<div class="field-label">notes</div><pre>${esc(r.notes)}</pre>`);
  if (r.duration_ms != null) {
    parts.push(`<div class="field-label">duration</div><pre>${esc(fmtMs(r.duration_ms))}</pre>`);
  }
  if (r.status === 'error') {
    parts.push(`<div class="field-label">traceback</div><pre>${esc(r.traceback)}</pre>`);
  } else if (r.status === 'skip') {
    parts.push(`<div class="field-label">skip reason</div><pre>${esc(r.reason)}</pre>`);
  } else {
    parts.push(`<div class="field-label">output</div><pre>${esc(r.content)}</pre>`);
    parts.push(`<div class="field-label">meta excerpt</div><pre>${esc(r.meta_excerpt)}</pre>`);
  }
  if (r.scores) {
    const s = r.scores;
    parts.push(`<div class="field-label">judged ${esc(r.judged_at || '')}</div>`);
    parts.push(`<div class="score-grid">
      <div><b>${r.overall}</b><br>overall</div>
      <div><b>${s.accuracy}</b><br>accuracy</div>
      <div><b>${s.informativeness}</b><br>informativeness</div>
      <div><b>${s.conciseness}</b><br>conciseness</div>
      <div><b>${s.hallucination_free}</b><br>hallucination-free</div>
    </div>`);
    if (r.critique) parts.push(`<div class="field-label">critique</div><pre>${esc(r.critique)}</pre>`);
  }
  return parts.join('');
}

const tbody = document.getElementById('tbody');
const countEl = document.getElementById('count');
let sortKey = null;
let sortDir = 1;

function sortValue(r, key) {
  if (key === 'golden_match') return r.golden_match === false ? 0 : r.golden_match === true ? 1 : 2;
  if (key === 'score_state') return ({stale: 0, unscored: 1, fresh: 2})[r.score_state] ?? 3;
  return r[key];
}

function applySort(list) {
  if (!sortKey) return list;
  const withVal = list.map(r => [sortValue(r, sortKey), r]);
  withVal.sort((a, b) => {
    const [av, bv] = [a[0], b[0]];
    if (av == null && bv == null) return 0;
    if (av == null) return 1;
    if (bv == null) return -1;
    if (av < bv) return -1 * sortDir;
    if (av > bv) return 1 * sortDir;
    return 0;
  });
  return withVal.map(([, r]) => r);
}

function render() {
  const q = document.getElementById('search').value.toLowerCase();
  const statusF = document.getElementById('status-filter').value;
  const goldenF = document.getElementById('golden-filter').value;
  const scoreF = document.getElementById('score-filter').value;

  let filtered = rows.filter(r => {
    if (statusF && r.status !== statusF) return false;
    if (goldenF === 'mismatch' && r.golden_match !== false) return false;
    if (goldenF === 'match' && r.golden_match !== true) return false;
    if (goldenF === 'none' && r.golden_exists) return false;
    if (scoreF === 'stale' && r.score_state !== 'stale') return false;
    if (scoreF === 'unscored' && r.score_state !== 'unscored') return false;
    if (scoreF === 'fresh' && r.score_state !== 'fresh') return false;
    if (scoreF === 'low' && !(r.overall != null && r.overall < 4)) return false;
    if (q) {
      const hay = [r.id, r.tags.join(' '), r.display_input, r.notes, r.critique]
        .join(' ').toLowerCase();
      if (!hay.includes(q)) return false;
    }
    return true;
  });
  filtered = applySort(filtered);

  countEl.textContent = `${filtered.length} / ${rows.length} shown`;
  tbody.innerHTML = '';
  for (const r of filtered) {
    const tr = document.createElement('tr');
    tr.className = 'row' + (r.status === 'error' ? ' error-row' : '');
    const tags = r.tags.map(t => `<span class="tag">${esc(t)}</span>`).join('');
    tr.innerHTML = `
      <td class="toggle-cell">&#9656;</td>
      <td class="mono">${esc(r.id)}</td>
      <td><span class="badge ${r.status}">${esc(r.status)}</span></td>
      <td>${tags}</td>
      <td>${goldenBadge(r)}</td>
      <td>${scoreBadge(r)}</td>
      <td class="num">${r.overall != null ? r.overall : '-'}</td>
      <td class="num">${durationCell(r)}</td>
    `;
    const detailTr = document.createElement('tr');
    detailTr.className = 'detail';
    const detailTd = document.createElement('td');
    detailTd.colSpan = 8;
    detailTd.innerHTML = detailHtml(r);
    detailTr.appendChild(detailTd);

    tr.addEventListener('click', () => {
      detailTr.classList.toggle('open');
      tr.firstElementChild.innerHTML = detailTr.classList.contains('open') ? '&#9662;' : '&#9656;';
    });

    tbody.appendChild(tr);
    tbody.appendChild(detailTr);
  }
}

for (const id of ['search', 'status-filter', 'golden-filter', 'score-filter']) {
  document.getElementById(id).addEventListener('input', render);
}
for (const th of document.querySelectorAll('th.sortable')) {
  th.addEventListener('click', () => {
    const key = th.dataset.key;
    if (sortKey === key) {
      sortDir *= -1;
    } else {
      sortKey = key;
      sortDir = 1;
    }
    for (const other of document.querySelectorAll('th.sortable')) {
      other.classList.toggle('sorted', other === th);
      other.querySelector('.arrow').textContent = other === th ? (sortDir > 0 ? '↑' : '↓') : '↕';
    }
    render();
  });
}
render();
</script>
</body>
</html>
"""


def build_report() -> None:
    if not RUN_JSON.exists():
        print("No run.json — run `python -m evals.runner run` first.", file=sys.stderr)
        raise SystemExit(2)
    run = json.loads(RUN_JSON.read_text())
    scores = json.loads(SCORES_PATH.read_text()) if SCORES_PATH.exists() else {"cases": {}}
    payload = {"env": run["env"], "rows": _row_data(run["cases"], scores)}
    data_json = json.dumps(payload).replace("</script>", "<\\/script>")
    REPORT_HTML.write_text(_PAGE.replace("__DATA__", data_json))


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(prog="evals.viewer")
    parser.add_argument("--open", action="store_true", help="open the report in a browser")
    args = parser.parse_args(argv)
    build_report()
    print(f"wrote {REPORT_HTML}")
    if args.open:
        webbrowser.open(REPORT_HTML.as_uri())
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
