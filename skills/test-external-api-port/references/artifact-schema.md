# Test Run Artifact Schema

## Contents

1. Run directory
2. manifest.json
3. Case folders
4. Per-case files
5. Redaction rules
6. summary.md

## 1. Run directory

```text
<artifacts-dir>/<operation-slug>/test-runs/<run-id>/
  manifest.json
  summary.md
  T-001-<case-slug>/
  T-002-<case-slug>/
  ...
```

`run-id` is `date -u +%Y%m%dT%H%M%SZ`. Never overwrite an existing run directory; a re-run is a new run. Case folders are named by `T-###` plus a lowercase kebab-case slug of the case name.

## 2. manifest.json

Record everything needed to interpret and reproduce the run:

- run id, UTC start/end, operation slug, packet path and its status at run start;
- config snapshot with secret values replaced by `<redacted>`;
- server identities: each host URL plus deployed version/commit when discoverable from health or docs endpoints, otherwise the URL and date;
- tenant identifier and disposability, write posture, side-effect posture, and the testing Mongo MCP connection actually used;
- coverage totals: planned, executed, passed, divergent, unexpected, blocked, excluded.

## 3. Case folders

```text
T-014-duplicate-slug-conflict/
  case.json           # identity, intent, ledger refs, seed, mode
  request.json        # the external API call as sent
  response.json       # the external API response as received
  legacy/
    request.json      # same intent against the legacy or core route
    response.json
  db.json             # only when persisted state is the expected outcome
  side-effects.json   # only when the case bears side effects
  verdict.json        # the judgment, with citations
```

`legacy/` is present for differential cases and absent for new-path-only cases (`S-###`, external-only contract rules). `db.json` and `side-effects.json` appear only when relevant — an absent file means "not applicable," never "forgot."

## 4. Per-case files

**case.json** — `id`, `name`, `intent` (one sentence), `ledger_refs` (the `B/V/E/S-###` rows this case verifies, or `["EXPLORATORY"]`), `mode` (`LEDGER` | `EXPLORATORY`), `write` (boolean), `seed` (the preconditions and how they were established), `oracle` (which comparison this case uses).

**request.json** — `method`, full `url`, `path_params`, `query`, `headers` (values redacted per §5), `body` (exact JSON sent), `sent_at`, and a `curl` string with credential values as `<api-key>`/`<token>` placeholders so a human can replay the case by hand after substituting from the local config.

**response.json** — `status`, response headers worth keeping (content type, rate-limit, request id), `body` exactly as received (no reformatting beyond pretty-printing), `latency_ms`. On retry after a flake, keep both attempts as `attempts: [...]`.

**legacy/request.json, legacy/response.json** — same schema, plus `server` (`legacy-api` | `core-api`) and the route called. The request expresses the *same intent* in that route's shape, translated via the packet's `C-###` domain-mapping column.

**db.json** — `connection` (testing MCP id), `database`, and per check: `collection`, the exact `query` used, `before` and `after` document arrays. Targeted queries only — never collection dumps.

**side-effects.json** — each expected effect from the ledger with `observed` (`true` | `false` | `NOT_OBSERVABLE`), how it was observed (queue collection, log, provider sandbox), payload when captured, and order. `NOT_OBSERVABLE` requires a reason and surfaces as a residual risk; it never counts as verified.

**verdict.json** — `verdict` (`PASS` | `DIVERGENCE` | `UNEXPECTED` | `BLOCKED`), `compared_against` (the specific files/oracles cited), `ledger_refs`, `reasoning` (what matched or differed, field by field where it matters), `normalized` (any fields excluded from the diff — timestamps, generated ids — each with a reason; never silent), and for divergences: `triage` (`IMPLEMENTATION_BUG` | `LEDGER_ERROR` | `MISSING_DECISION`) and `follow_up`.

## 5. Redaction rules

- API keys, bearer tokens, cookies, and signatures never appear anywhere in artifacts — header and config values become `<redacted>`; the only place the external API key lives is the gitignored config file.
- Fields the `X-###` ledger marks `secret` are redacted in `db.json` while preserving presence/absence.
- Raw PII may remain in local artifacts (they are uncommitted evidence) but never gets copied into the packet, `summary.md` findings, or the handoff report.
- Artifacts stay in the scratch location and are never staged or committed.

## 6. summary.md

Human-first, in this order:

1. One header block: operation, run id, servers, tenant, write posture, coverage totals.
2. The verdict table: `T-###` | case name | ledger refs | verdict | one-line reason. Every row links to its case folder.
3. Divergences in full: what was compared, what differed, triage bucket, follow-up owner.
4. Residual risks: `NOT_OBSERVABLE` effects, blocked cases, environment drift.
5. A short "what to eyeball" list for the human audit pass — typically the exposure-sensitive responses (confirm absent fields are absent) and the error-shape responses.
