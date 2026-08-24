# Test Run Artifact Schema

## Contents

1. Run directory
2. manifest.json
3. Case files
4. Case blocks
5. Redaction rules
6. summary.md
7. Derived HTML views

## 1. Run directory

```text
<artifacts-dir>/<operation-slug>/test-runs/<run-id>/
  manifest.json
  summary.md
  T-001-<case-slug>.json
  T-002-<case-slug>.json
  ...
```

This tree is the durable record — JSON evidence plus `summary.md`, trackable and meant to be committed alongside the port. Nothing generated or regenerable ever lands here; all HTML views live in the separate, git-ignored `.reports/` tree (§7).

Only the gating run is durable: the run the packet's `Test run:` line pins is the evidence for `VERIFIED` and is what gets committed. When a new run supersedes older ones, the `Test run:` line says so by id — and a run recorded as superseded may be deleted; its evidentiary role has passed to its successor. Keep in-progress runs while iterating; never prune the pinned run.

`run-id` is `date -u +%Y%m%dT%H%M%SZ`. Never overwrite an existing run directory; a re-run is a new run. Case files are named by `T-###` plus a lowercase kebab-case slug of the case name — one file holds the whole case (§3).

## 2. manifest.json

Record everything needed to interpret and reproduce the run:

- run id, UTC start/end, operation slug, packet path and its status at run start;
- config snapshot with secret values replaced by `<redacted>`;
- server identities: each host URL plus deployed version/commit when discoverable from health or docs endpoints, otherwise the URL and date;
- the custom host (the tenant everything runs under), side-effect posture, and the testing Mongo MCP connection actually used;
- coverage totals: planned, executed, passed, divergent, unexpected, blocked, excluded.

## 3. Case files

One JSON file per case, with the case's parts as fixed top-level blocks:

```jsonc
// T-014-duplicate-slug-conflict.json
{
  "case": { ... },          // identity, intent, ledger refs, seed, mode
  "request": { ... },       // the external API call as sent
  "response": { ... },      // the external API response as received
  "legacy": {               // same intent against the legacy or core route
    "request": { ... },
    "response": { ... }
  },
  "db": { ... },            // only when persisted state is the expected outcome
  "side_effects": { ... },  // only when the case bears side effects
  "verdict": { ... }        // the judgment, with citations
}
```

`legacy` is present for differential cases and absent for new-path-only cases (`S-###`, external-only contract rules). `db` and `side_effects` appear only when relevant — an absent block means "not applicable," never "forgot." (Runs recorded before this schema used one folder per case with these blocks as separate files — `case.json`, `request.json`, `legacy/request.json`, `db.json`, `side-effects.json`, … — the renderer reads both, and `scripts/consolidate_run.py <run-dir>` migrates a folder-form run with per-case verification.)

## 4. Case blocks

**`case`** — `id`, `name`, `intent` (one sentence), `ledger_refs` (the `B/V/E/S-###` rows this case verifies, or `["EXPLORATORY"]`), `mode` (`LEDGER` | `EXPLORATORY`), `write` (boolean), `seed` (the preconditions and how they were established), `oracle` (which comparison this case uses).

**`request`** — `method`, full `url`, `path_params`, `query`, `headers` (values redacted per §5), `body` (exact JSON sent), `sent_at`, and a `curl` string with credential values as `<api-key>`/`<token>` placeholders so a human can replay the case by hand after substituting from the local config.

**`response`** — `status`, response headers worth keeping (content type, rate-limit, request id), `body` exactly as received (no reformatting beyond pretty-printing), `latency_ms`. On retry after a flake, keep both attempts as `attempts: [...]`.

**`legacy.request`, `legacy.response`** — same schema, plus `server` (`legacy-api` | `core-api`) and the route called. The request expresses the *same intent* in that route's shape, translated via the packet's `C-###` domain-mapping column.

**`db`** — `connection` (testing MCP id), `database`, and per check: `collection`, the exact `query` used, `before` and `after` document arrays. Targeted queries only — never collection dumps.

**`side_effects`** — each expected effect from the ledger with `observed` (`true` | `false` | `NOT_OBSERVABLE`), how it was observed (queue collection, log, provider sandbox), payload when captured, and order. `NOT_OBSERVABLE` requires a reason and surfaces as a residual risk; it never counts as verified.

**`verdict`** — `verdict` (`PASS` | `DIVERGENCE` | `UNEXPECTED` | `BLOCKED`), `compared_against` (the specific files/oracles cited), `ledger_refs`, `reasoning` (what matched or differed, field by field where it matters), `normalized` (any fields excluded from the diff — timestamps, generated ids — each with a reason; never silent), and for divergences: `triage` (`IMPLEMENTATION_BUG` | `LEDGER_ERROR` | `MISSING_DECISION`) and `follow_up`.

## 5. Redaction rules

- API keys, bearer tokens, cookies, and signatures never appear anywhere in artifacts — header and config values become `<redacted>`; the only place the external API key lives is the gitignored config file.
- Fields the `X-###` ledger marks `secret` are redacted in the `db` block while preserving presence/absence.
- The evidence tree is written to be commit-safe: it holds only testing-tenant data (the environment gate forbids production connections), and anything that would be sensitive in a repository — credentials, signatures, `secret`-marked fields — is redacted at capture time. PII never gets copied into the packet, `summary.md` findings, or the handoff report.
- Two git postures, never mixed: the JSON evidence tree is the record to track and commit; the derived `.reports/` tree is never committed — it ignores itself (§7).

## 6. summary.md

Human-first, in this order:

1. One header block: operation, run id, servers, tenant, write posture, coverage totals.
2. The verdict table: `T-###` | case name | ledger refs | verdict | one-line reason. Every row names its case file.
3. Divergences in full: what was compared, what differed, triage bucket, follow-up owner.
4. Residual risks: `NOT_OBSERVABLE` effects, blocked cases, environment drift.
5. A short "what to eyeball" list for the human audit pass — typically the exposure-sensitive responses (confirm absent fields are absent) and the error-shape responses.

## 7. Derived HTML views — `.reports/`, never tracked

Everything HTML is derived from the evidence and regenerable at will, so it lives in a mirrored tree that keeps itself out of git — the renderer writes a `.gitignore` containing `*` inside it, so it stays ignored with no edit to the repository's own ignore rules:

```text
<artifacts-dir>/.reports/
  .gitignore                     # "*" — the tree ignores itself
  index.html                     # latest-run verdicts across all operations
  <operation-slug>/
    index.html                   # every run of the operation, newest first
    <run-id>/
      report.html                # the full run report
```

`scripts/render_report.py <run-dir>` writes all three levels. `report.html` is self-contained (no network, no external assets), openable straight from disk: stat tiles for coverage, the filterable verdict table, expandable per-case detail (request, response, legacy capture, db before/after, side effects, verdict with citations, a copyable `curl`), and computed residual risks. If the manifest's coverage totals disagree with the case files on disk, the page flags it — the files win.

Rules: regenerate after any artifact change; never edit the HTML by hand; never treat the report as evidence (the JSON files are); never write HTML into the evidence tree (the renderer also sweeps out views older versions left there). The renderer applies its own redaction pass on top of §5, but that is a backstop — secrets still must never reach the artifacts in the first place.
