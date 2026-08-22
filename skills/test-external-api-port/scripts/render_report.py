#!/usr/bin/env python3
"""Render a static HTML view over a test run's JSON artifacts.

The JSON artifacts are the evidence and stay exactly as written by the run.
This script is a derived, regenerable view: it reads a run directory
(<artifacts-dir>/<operation>/test-runs/<run-id>/), embeds the artifact data
into a self-contained report.html next to manifest.json, and refreshes two
static indexes (one per operation, one across operations). It never writes
into any artifact file and never reads the environment config.

Usage:
    python3 render_report.py <run-dir>

stdlib only. Safe to re-run any number of times.
"""

from __future__ import annotations

import argparse
import json
import re
import sys
from datetime import datetime, timezone
from html import escape
from pathlib import Path

SENSITIVE_KEY = re.compile(
    r"authorization|cookie|set-cookie|api[-_]?key|secret|signature|(?<![a-z])token",
    re.IGNORECASE,
)

CASE_FILES = {
    "case": "case.json",
    "request": "request.json",
    "response": "response.json",
    "legacy_request": "legacy/request.json",
    "legacy_response": "legacy/response.json",
    "db": "db.json",
    "side_effects": "side-effects.json",
    "verdict": "verdict.json",
}

VERDICTS = ["PASS", "DIVERGENCE", "UNEXPECTED", "BLOCKED"]


def load_json(path: Path):
    """Return (data, error). Missing file -> (None, None)."""
    if not path.is_file():
        return None, None
    try:
        return json.loads(path.read_text(encoding="utf-8")), None
    except Exception as exc:  # malformed evidence is a finding, not a crash
        return None, f"{type(exc).__name__}: {exc}"


def scrub(value):
    """Belt-and-suspenders redaction on top of the artifact-layer rules."""
    if isinstance(value, dict):
        out = {}
        for key, val in value.items():
            if SENSITIVE_KEY.search(str(key)) and isinstance(val, (str, int, float)):
                out[key] = "<redacted>"
            else:
                out[key] = scrub(val)
        return out
    if isinstance(value, list):
        return [scrub(item) for item in value]
    return value


def collect_case(folder: Path):
    files, errors = {}, {}
    for key, rel in CASE_FILES.items():
        data, err = load_json(folder / rel)
        files[key] = scrub(data) if data is not None else None
        if err:
            errors[key] = err
    return {"folder": folder.name, "files": files, "errors": errors}


def collect_run(run_dir: Path):
    manifest, manifest_error = load_json(run_dir / "manifest.json")
    summary_path = run_dir / "summary.md"
    summary_md = summary_path.read_text(encoding="utf-8") if summary_path.is_file() else None

    case_dirs = sorted(
        p for p in run_dir.iterdir() if p.is_dir() and re.match(r"^T-\d{3}", p.name)
    )
    cases = [collect_case(p) for p in case_dirs]

    counts = {v: 0 for v in VERDICTS}
    counts["UNKNOWN"] = 0
    for case in cases:
        verdict = (case["files"].get("verdict") or {}).get("verdict")
        counts[verdict if verdict in counts else "UNKNOWN"] += 1

    operation = run_dir.parent.parent.name if run_dir.parent.name == "test-runs" else None
    if not operation and isinstance(manifest, dict):
        operation = manifest.get("operation") or manifest.get("operation_slug")

    return {
        "generated_at": datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ"),
        "run_id": run_dir.name,
        "operation": operation or "unknown-operation",
        "manifest": scrub(manifest) if manifest is not None else None,
        "manifest_error": manifest_error,
        "summary_md": summary_md,
        "counts": counts,
        "cases": cases,
    }


def render_report(run_dir: Path) -> Path:
    data = collect_run(run_dir)
    payload = json.dumps(data, indent=None, ensure_ascii=False).replace("</", "<\\/")
    html = TEMPLATE.replace("__TITLE__", escape(f"{data['operation']} · {data['run_id']}"))
    html = html.replace("__DATA__", payload)
    out = run_dir / "report.html"
    out.write_text(html, encoding="utf-8")
    return out


# ---------------------------------------------------------------- indexes


def manifest_coverage(manifest):
    if not isinstance(manifest, dict):
        return {}
    for key in ("coverage", "coverage_totals", "totals"):
        if isinstance(manifest.get(key), dict):
            return manifest[key]
    return {}


def run_row(run_dir: Path) -> dict:
    manifest, _ = load_json(run_dir / "manifest.json")
    cov = manifest_coverage(manifest)
    counts = {v: 0 for v in VERDICTS}
    executed = 0
    for folder in run_dir.iterdir():
        if folder.is_dir() and re.match(r"^T-\d{3}", folder.name):
            executed += 1
            verdict = (load_json(folder / "verdict.json")[0] or {}).get("verdict")
            if verdict in counts:
                counts[verdict] += 1
    started = ""
    if isinstance(manifest, dict):
        started = str(manifest.get("started_at") or manifest.get("start") or "")
    return {
        "run_id": run_dir.name,
        "started": started,
        "planned": cov.get("planned", ""),
        "excluded": cov.get("excluded", ""),
        "executed": executed,
        "counts": counts,
        "has_report": (run_dir / "report.html").is_file(),
    }


def badge_cells(counts) -> str:
    cells = []
    for verdict in VERDICTS:
        n = counts.get(verdict, 0)
        cls = "zero" if not n else VERDICT_CLASS[verdict]
        cells.append(f'<td class="num {cls}">{n}</td>')
    return "".join(cells)


VERDICT_CLASS = {
    "PASS": "v-pass",
    "DIVERGENCE": "v-div",
    "UNEXPECTED": "v-unexp",
    "BLOCKED": "v-block",
}


def render_operation_index(test_runs_dir: Path) -> Path:
    operation = test_runs_dir.parent.name
    runs = sorted(
        (p for p in test_runs_dir.iterdir() if p.is_dir()),
        key=lambda p: p.name,
        reverse=True,
    )
    rows = []
    for run in runs:
        row = run_row(run)
        link = (
            f'<a href="{escape(run.name)}/report.html">{escape(row["run_id"])}</a>'
            if row["has_report"]
            else escape(row["run_id"])
        )
        rows.append(
            "<tr>"
            f"<td>{link}</td>"
            f'<td>{escape(row["started"])}</td>'
            f'<td class="num">{row["planned"]}</td>'
            f'<td class="num">{row["executed"]}</td>'
            f"{badge_cells(row['counts'])}"
            f'<td class="num">{row["excluded"]}</td>'
            "</tr>"
        )
    body = INDEX_TEMPLATE.replace("__TITLE__", escape(f"{operation} · test runs"))
    body = body.replace("__HEADING__", escape(operation))
    body = body.replace("__SUBHEADING__", f"{len(runs)} test run{'s' if len(runs) != 1 else ''}")
    body = body.replace(
        "__THEAD__",
        "<th>Run</th><th>Started</th><th>Planned</th><th>Executed</th>"
        "<th>Pass</th><th>Divergence</th><th>Unexpected</th><th>Blocked</th><th>Excluded</th>",
    )
    body = body.replace("__ROWS__", "\n".join(rows) or '<tr><td colspan="9">No runs yet</td></tr>')
    out = test_runs_dir / "index.html"
    out.write_text(body, encoding="utf-8")
    return out


def render_root_index(root: Path) -> Path:
    rows = []
    for op_dir in sorted(p for p in root.iterdir() if (p / "test-runs").is_dir()):
        runs_dir = op_dir / "test-runs"
        runs = sorted((p for p in runs_dir.iterdir() if p.is_dir()), key=lambda p: p.name)
        latest = runs[-1] if runs else None
        counts = run_row(latest)["counts"] if latest else {}
        latest_cell = escape(latest.name) if latest else "—"
        rows.append(
            "<tr>"
            f'<td><a href="{escape(op_dir.name)}/test-runs/index.html">{escape(op_dir.name)}</a></td>'
            f'<td class="num">{len(runs)}</td>'
            f"<td>{latest_cell}</td>"
            f"{badge_cells(counts)}"
            "</tr>"
        )
    body = INDEX_TEMPLATE.replace("__TITLE__", "External API port · test runs")
    body = body.replace("__HEADING__", "External API port test runs")
    body = body.replace("__SUBHEADING__", "Latest-run verdicts per operation")
    body = body.replace(
        "__THEAD__",
        "<th>Operation</th><th>Runs</th><th>Latest run</th>"
        "<th>Pass</th><th>Divergence</th><th>Unexpected</th><th>Blocked</th>",
    )
    body = body.replace("__ROWS__", "\n".join(rows) or '<tr><td colspan="7">No runs yet</td></tr>')
    out = root / "index.html"
    out.write_text(body, encoding="utf-8")
    return out


# ---------------------------------------------------------------- templates

# Tokens follow the validated reference palette: status colors are fixed
# (good/warning/serious/critical), text always wears ink tokens, verdicts
# carry icon + label so color never works alone, dark mode is selected steps.
BASE_CSS = """
:root {
  color-scheme: light;
  --page: #f9f9f7; --surface: #fcfcfb;
  --ink: #0b0b0b; --ink-2: #52514e; --muted: #898781;
  --hairline: #e1e0d9; --ring: rgba(11,11,11,0.10);
  --good: #0ca30c; --warning: #fab219; --serious: #ec835a; --critical: #d03b3b;
  --accent: #2a78d6;
}
@media (prefers-color-scheme: dark) {
  :root {
    color-scheme: dark;
    --page: #0d0d0d; --surface: #1a1a19;
    --ink: #ffffff; --ink-2: #c3c2b7; --muted: #898781;
    --hairline: #2c2c2a; --ring: rgba(255,255,255,0.10);
    --accent: #3987e5;
  }
}
* { box-sizing: border-box; }
body {
  margin: 0; background: var(--page); color: var(--ink);
  font: 14px/1.5 system-ui, -apple-system, "Segoe UI", sans-serif;
}
a { color: var(--accent); text-decoration: none; }
a:hover { text-decoration: underline; }
.wrap { max-width: 1200px; margin: 0 auto; padding: 24px 20px 64px; }
h1 { font-size: 20px; font-weight: 600; margin: 0 0 2px; }
.sub { color: var(--ink-2); margin: 0 0 20px; }
.card {
  background: var(--surface); border: 1px solid var(--ring);
  border-radius: 8px; padding: 16px; margin-bottom: 16px;
}
table { border-collapse: collapse; width: 100%; }
th {
  text-align: left; font-weight: 600; color: var(--ink-2); font-size: 12px;
  padding: 6px 10px; border-bottom: 1px solid var(--hairline); white-space: nowrap;
}
td { padding: 7px 10px; border-bottom: 1px solid var(--hairline); vertical-align: top; }
tr:last-child td { border-bottom: none; }
.num { font-variant-numeric: tabular-nums; text-align: right; }
.zero { color: var(--muted); }
.v-pass { color: var(--ink); } .v-div, .v-unexp, .v-block { font-weight: 600; }
.dot { display: inline-block; width: 9px; height: 9px; border-radius: 50%;
       margin-right: 6px; vertical-align: baseline; }
.badge { display: inline-flex; align-items: center; gap: 6px; white-space: nowrap; }
.badge .icon {
  display: inline-flex; align-items: center; justify-content: center;
  width: 15px; height: 15px; border-radius: 50%; color: #fff;
  font-size: 10px; font-weight: 700; line-height: 1;
}
"""

INDEX_TEMPLATE = (
    "<!doctype html>\n<html lang=\"en\">\n<head>\n<meta charset=\"utf-8\">\n"
    "<meta name=\"viewport\" content=\"width=device-width, initial-scale=1\">\n"
    "<title>__TITLE__</title>\n<style>" + BASE_CSS + "</style>\n</head>\n<body>\n"
    '<div class="wrap">\n<h1>__HEADING__</h1>\n<p class="sub">__SUBHEADING__</p>\n'
    '<div class="card"><table><thead><tr>__THEAD__</tr></thead>\n'
    "<tbody>\n__ROWS__\n</tbody></table></div>\n"
    "</div>\n</body>\n</html>\n"
)

TEMPLATE = (
    "<!doctype html>\n<html lang=\"en\">\n<head>\n<meta charset=\"utf-8\">\n"
    "<meta name=\"viewport\" content=\"width=device-width, initial-scale=1\">\n"
    "<title>__TITLE__ · test run report</title>\n<style>"
    + BASE_CSS
    + """
.tiles { display: grid; grid-template-columns: repeat(auto-fit, minmax(120px, 1fr));
         gap: 12px; margin-bottom: 16px; }
.tile { background: var(--surface); border: 1px solid var(--ring); border-radius: 8px;
        padding: 12px 14px; }
.tile .label { font-size: 12px; color: var(--ink-2); display: flex;
               align-items: center; gap: 6px; }
.tile .value { font-size: 26px; font-weight: 600; margin-top: 2px; }
.meta { display: grid; grid-template-columns: repeat(auto-fit, minmax(240px, 1fr));
        gap: 4px 24px; }
.meta div { min-width: 0; overflow-wrap: anywhere; }
.meta b { color: var(--ink-2); font-weight: 600; font-size: 12px; display: block; }
.filters { display: flex; flex-wrap: wrap; gap: 8px; align-items: center;
           margin-bottom: 12px; }
.chip { border: 1px solid var(--hairline); background: var(--surface); color: var(--ink);
        border-radius: 999px; padding: 4px 12px; cursor: pointer; font: inherit;
        font-size: 13px; }
.chip[aria-pressed="true"] { border-color: var(--ink); font-weight: 600; }
.chip .n { color: var(--ink-2); margin-left: 4px; font-variant-numeric: tabular-nums; }
#search { margin-left: auto; border: 1px solid var(--hairline); border-radius: 6px;
          background: var(--surface); color: var(--ink); padding: 5px 10px;
          font: inherit; min-width: 220px; }
tr.case-row { cursor: pointer; }
tr.case-row td:first-child { white-space: nowrap; }
tr.case-row:hover td { background: var(--ring); }
tr.detail-row > td { background: var(--page); padding: 12px 16px; }
.reason { color: var(--ink-2); }
.mode-tag, .triage-tag { font-size: 11px; border: 1px solid var(--hairline);
        border-radius: 4px; padding: 1px 6px; color: var(--ink-2); white-space: nowrap; }
details { border: 1px solid var(--hairline); border-radius: 6px; margin-bottom: 8px;
          background: var(--surface); }
details > summary { cursor: pointer; padding: 7px 12px; font-weight: 600;
                    font-size: 13px; list-style: none; display: flex; gap: 8px;
                    align-items: center; }
details > summary::before { content: "▸"; color: var(--muted); font-size: 11px; }
details[open] > summary::before { content: "▾"; }
details .body { padding: 0 12px 10px; }
pre { background: var(--page); border: 1px solid var(--hairline); border-radius: 6px;
      padding: 10px 12px; overflow: auto; max-height: 420px; margin: 0;
      font: 12px/1.5 ui-monospace, SFMono-Regular, Menlo, monospace; }
.copy { float: right; font-size: 12px; border: 1px solid var(--hairline);
        border-radius: 6px; background: var(--surface); color: var(--ink);
        padding: 2px 10px; cursor: pointer; }
.warn-line { color: var(--ink-2); font-size: 13px; margin: 8px 0 0; }
.risk li { margin-bottom: 4px; }
.footer { color: var(--muted); font-size: 12px; margin-top: 24px; }
</style>\n</head>\n<body>\n<div class="wrap" id="app"></div>\n
<script id="run-data" type="application/json">__DATA__</script>\n<script>
"use strict";
const DATA = JSON.parse(document.getElementById("run-data").textContent);
const STATUS = {
  PASS:       { color: "var(--good)",     icon: "\\u2713" },
  DIVERGENCE: { color: "var(--critical)", icon: "\\u2715" },
  UNEXPECTED: { color: "var(--warning)",  icon: "!" },
  BLOCKED:    { color: "var(--serious)",  icon: "\\u2298" },
  UNKNOWN:    { color: "var(--muted)",    icon: "?" },
};
function el(tag, attrs, ...children) {
  const node = document.createElement(tag);
  for (const [k, v] of Object.entries(attrs || {})) {
    if (k === "text") node.textContent = v;
    else if (k.startsWith("on")) node.addEventListener(k.slice(2), v);
    else node.setAttribute(k, v);
  }
  for (const child of children) if (child != null) node.append(child);
  return node;
}
function badge(verdict) {
  const s = STATUS[verdict] || STATUS.UNKNOWN;
  return el("span", { class: "badge" },
    el("span", { class: "icon", style: "background:" + s.color, text: s.icon }),
    el("span", { text: verdict || "NO VERDICT" }));
}
function jsonBlock(title, value, extra) {
  if (value == null && !extra) return null;
  const body = el("div", { class: "body" });
  if (extra) body.append(extra);
  if (value != null) body.append(el("pre", { text: JSON.stringify(value, null, 2) }));
  return el("details", null, el("summary", { text: title }), body);
}
function caseMeta(c) {
  const f = c.files, v = f.verdict || {}, meta = f.case || {};
  return {
    id: c.folder.slice(0, 5),
    name: meta.name || c.folder.slice(6).replace(/-/g, " "),
    refs: (meta.ledger_refs || v.ledger_refs || []).join(", "),
    mode: meta.mode || "",
    verdict: v.verdict || "UNKNOWN",
    triage: v.triage || "",
    reason: v.reasoning || "",
  };
}
const state = { verdicts: new Set(), q: "" };
function matches(m) {
  if (state.verdicts.size && !state.verdicts.has(m.verdict)) return false;
  if (!state.q) return true;
  return (m.id + " " + m.name + " " + m.refs + " " + m.triage)
    .toLowerCase().includes(state.q);
}
function detailFor(c) {
  const f = c.files, wrap = el("div");
  for (const [key, msg] of Object.entries(c.errors || {}))
    wrap.append(el("p", { class: "warn-line", text: "\\u26a0 " + key + ".json failed to parse: " + msg }));
  let curlExtra = null;
  if (f.request && f.request.curl) {
    const btn = el("button", { class: "copy", text: "Copy curl", onclick: () => {
      navigator.clipboard.writeText(f.request.curl);
      btn.textContent = "Copied"; setTimeout(() => (btn.textContent = "Copy curl"), 1200);
    }});
    curlExtra = el("div", null, btn, el("pre", { text: f.request.curl, style: "margin-bottom:8px" }));
  }
  const sections = [
    jsonBlock("Verdict", f.verdict),
    jsonBlock("Case", f.case),
    jsonBlock("Request \\u2014 external", f.request, curlExtra),
    jsonBlock("Response \\u2014 external", f.response),
    jsonBlock("Request \\u2014 legacy/core", f.legacy_request),
    jsonBlock("Response \\u2014 legacy/core", f.legacy_response),
    jsonBlock("DB before/after", f.db),
    jsonBlock("Side effects", f.side_effects),
  ].filter(Boolean);
  if (!sections.length) wrap.append(el("p", { class: "warn-line", text: "No artifact files found in this folder." }));
  sections.forEach((s) => wrap.append(s));
  return wrap;
}
function renderTable(tbody) {
  tbody.replaceChildren();
  let shown = 0;
  for (const c of DATA.cases) {
    const m = caseMeta(c);
    if (!matches(m)) continue;
    shown++;
    const cells = [
      el("td", { text: m.id }),
      el("td", null, el("div", { text: m.name }),
        m.mode === "EXPLORATORY" ? el("span", { class: "mode-tag", text: "EXPLORATORY" }) : null),
      el("td", { text: m.refs }),
      el("td", null, badge(m.verdict),
        m.triage ? el("div", null, el("span", { class: "triage-tag", text: m.triage })) : null),
      el("td", { class: "reason", text: m.reason.length > 160 ? m.reason.slice(0, 157) + "\\u2026" : m.reason }),
    ];
    const row = el("tr", { class: "case-row" }, ...cells);
    const detail = el("tr", { class: "detail-row", hidden: "" },
      el("td", { colspan: "5" }, detailFor(c)));
    row.addEventListener("click", () => detail.toggleAttribute("hidden"));
    tbody.append(row, detail);
  }
  if (!shown) tbody.append(el("tr", null, el("td", { colspan: "5", class: "reason", text: "No cases match the current filter." })));
}
function build() {
  const app = document.getElementById("app");
  const man = DATA.manifest || {};
  app.append(
    el("h1", { text: DATA.operation }),
    el("p", { class: "sub", text: "Test run " + DATA.run_id +
      (man.packet_status ? " \\u00b7 packet " + man.packet_status + " at run start" : "") }));

  // Environment / manifest header
  const meta = el("div", { class: "meta" });
  const addMeta = (label, value) => {
    if (value == null || value === "") return;
    meta.append(el("div", null, el("b", { text: label }),
      el("span", { text: typeof value === "string" ? value : JSON.stringify(value) })));
  };
  addMeta("Packet", man.packet_path || man.packet);
  addMeta("Started (UTC)", man.started_at || man.start);
  addMeta("Ended (UTC)", man.ended_at || man.end);
  addMeta("Tenant (custom host)", man.custom_host || (man.tenant && man.tenant.custom_host));
  const hosts = man.hosts || man.servers || {};
  for (const [name, value] of Object.entries(hosts)) addMeta("Host \\u00b7 " + name, value);
  addMeta("Side-effect posture", man.side_effect_posture);
  app.append(el("div", { class: "card" }, meta,
    DATA.manifest_error ? el("p", { class: "warn-line", text: "\\u26a0 manifest.json failed to parse: " + DATA.manifest_error }) : null));

  // Stat tiles — counts computed from the case folders themselves
  const cov = man.coverage || man.coverage_totals || man.totals || {};
  const tiles = el("div", { class: "tiles" });
  const tile = (label, value, color) => tiles.append(
    el("div", { class: "tile" },
      el("div", { class: "label" },
        color ? el("span", { class: "dot", style: "background:" + color }) : null,
        el("span", { text: label })),
      el("div", { class: "value", text: String(value) })));
  tile("Planned", cov.planned != null ? cov.planned : DATA.cases.length);
  tile("Executed", DATA.cases.length);
  for (const v of ["PASS", "DIVERGENCE", "UNEXPECTED", "BLOCKED"])
    tile(v.charAt(0) + v.slice(1).toLowerCase(), DATA.counts[v] || 0, STATUS[v].color);
  tile("Excluded", cov.excluded != null ? cov.excluded : "\\u2014");
  app.append(tiles);

  // Integrity note if the manifest disagrees with the folders on disk
  const pairs = [["passed", "PASS"], ["divergent", "DIVERGENCE"], ["unexpected", "UNEXPECTED"], ["blocked", "BLOCKED"]];
  const drift = pairs.filter(([k, v]) => cov[k] != null && cov[k] !== (DATA.counts[v] || 0));
  if (drift.length) app.append(el("p", { class: "warn-line",
    text: "\\u26a0 manifest coverage disagrees with the case folders on disk (" +
      drift.map(([k, v]) => k + ": manifest " + cov[k] + " vs folders " + (DATA.counts[v] || 0)).join("; ") +
      ") \\u2014 trust the folders; the manifest needs correcting." }));

  // Filters + verdict table
  const filters = el("div", { class: "filters" });
  for (const v of ["PASS", "DIVERGENCE", "UNEXPECTED", "BLOCKED", "UNKNOWN"]) {
    if (!DATA.counts[v]) continue;
    const chip = el("button", { class: "chip", "aria-pressed": "false", onclick: () => {
      state.verdicts.has(v) ? state.verdicts.delete(v) : state.verdicts.add(v);
      chip.setAttribute("aria-pressed", state.verdicts.has(v) ? "true" : "false");
      renderTable(tbody);
    }}, el("span", { text: v }), el("span", { class: "n", text: String(DATA.counts[v]) }));
    filters.append(chip);
  }
  filters.append(el("input", { id: "search", type: "search",
    placeholder: "Filter by id, name, ledger ref\\u2026",
    oninput: (e) => { state.q = e.target.value.trim().toLowerCase(); renderTable(tbody); } }));
  const tbody = el("tbody");
  app.append(el("div", { class: "card" }, filters,
    el("table", null,
      el("thead", null, el("tr", null,
        el("th", { text: "Case" }), el("th", { text: "Name" }),
        el("th", { text: "Ledger refs" }), el("th", { text: "Verdict" }),
        el("th", { text: "Reason" }))),
      tbody)));
  renderTable(tbody);

  // Residual risks
  const risks = [];
  for (const c of DATA.cases) {
    const m = caseMeta(c);
    if (m.verdict === "BLOCKED") risks.push(m.id + " blocked: " + (m.reason || "see verdict.json"));
    const walk = (node) => {
      if (Array.isArray(node)) node.forEach(walk);
      else if (node && typeof node === "object") {
        if (node.observed === "NOT_OBSERVABLE")
          risks.push(m.id + " side effect not observable: " + (node.reason || JSON.stringify(node).slice(0, 120)));
        else Object.values(node).forEach(walk);
      }
    };
    walk(c.files.side_effects);
  }
  if (risks.length) app.append(el("div", { class: "card" },
    el("h2", { text: "Residual risks", style: "font-size:15px;margin:0 0 8px" }),
    el("ul", { class: "risk" }, ...risks.map((r) => el("li", { text: r })))));

  // The written summary, verbatim
  if (DATA.summary_md) app.append(
    el("details", null, el("summary", { text: "summary.md (verbatim)" }),
      el("div", { class: "body" }, el("pre", { text: DATA.summary_md }))));

  app.append(el("p", { class: "footer",
    text: "Derived view generated " + DATA.generated_at +
      " by render_report.py \\u2014 the JSON artifact files are the evidence; regenerate this page after any artifact change." }));
}
build();
</script>\n</body>\n</html>\n"""
)


def main(argv=None) -> int:
    parser = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    parser.add_argument("run_dir", help="path to <artifacts-dir>/<operation>/test-runs/<run-id>/")
    args = parser.parse_args(argv)

    run_dir = Path(args.run_dir).resolve()
    if not run_dir.is_dir():
        print(f"ERROR: not a directory: {run_dir}", file=sys.stderr)
        return 2

    report = render_report(run_dir)
    print(f"report: {report}")

    if run_dir.parent.name == "test-runs":
        op_index = render_operation_index(run_dir.parent)
        print(f"operation index: {op_index}")
        root = run_dir.parent.parent.parent
        root_index = render_root_index(root)
        print(f"root index: {root_index}")
    else:
        print("note: run dir is not under <operation>/test-runs/ — indexes skipped")
    return 0


if __name__ == "__main__":
    sys.exit(main())
