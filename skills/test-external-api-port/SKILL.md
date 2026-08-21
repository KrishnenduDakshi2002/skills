---
name: test-external-api-port
description: Runtime-verify an IMPLEMENTED external API port by executing its packet scenarios against live external, legacy, and core servers. Captures per-case JSON artifacts for human audit, diffs outcomes against the legacy oracle and persisted state, and flips the packet to VERIFIED or reports divergences. Writes no product code and no committed test files.
argument-hint: <packet-path | operation-slug>
disable-model-invocation: true
---

# Test External API Port

Certify at runtime what `port-external-api` implemented and `audit-external-api-port` reviewed. The oracle is not your judgment — it is the live legacy route, the persisted documents, and the packet's pinned rules. Every case leaves a folder of raw wire evidence a human can audit without trusting you.

**A verdict is a comparison against captured evidence — never an opinion that a response "looks correct."** Every verdict cites what it compared: the legacy capture, the persisted documents, or the packet row.

**Never weaken an expected outcome to make a case pass.** A red case has exactly three explanations — implementation bug, ledger error, or an approved change missing its record — and gets triaged, not papered over.

**You know nothing about this environment.** Server locations, ports, tenant identifiers, custom hosts, keys — these are facts you cannot infer, remember, or default. Legacy is not "probably on localhost"; the tenant is not "the one from last time." Every environment fact comes from exactly two sources: the config file, or the user's answer in this session. Anything else — memory of another conversation, a port that's usually right, a tenant name in your training or context — is fabrication.

This workflow produces artifacts only: no product code, no committed test files, no packet edits beyond the Test Traceability section and one possible status change. Confirmed implementation bugs go back through `port-external-api`; contract-design findings through `audit-external-api-port`.

Packet statuses are a closed set — `DISCOVERY`, `BLOCKED`, `READY`, `IMPLEMENTING`, `IMPLEMENTED`, `VERIFIED` — and this workflow may write exactly one of them: `VERIFIED`, only at the §7 gate. While testing runs, the packet stays `IMPLEMENTED`. Never invent a status (`VERIFYING`, `TESTING`, `IN_PROGRESS` do not exist); the validator rejects them and the run's state lives in the run artifacts, not the packet status.

## 1. Resolve the environment — script-gated

Environment values are not your call. [testing_env.py](scripts/testing_env.py) owns `.external-api-testing.toml` (created gitignored on first run):

```sh
python3 <skill-directory>/scripts/testing_env.py check --repo <target-repo-root>
```

- `ENVIRONMENT NOT READY` — the output lists each missing value with the exact question to ask the user. Relay every question verbatim, record each answer with `testing_env.py set <section.key> "<answer>" --repo <root>` (it validates URLs, rejects garbage, and redacts the key), then re-run `check`.
- `ENVIRONMENT READY` — and only then — proceed.

Until `check` prints READY you may not send a request, build a URL, or name a tenant. `set` receives only values the user gave *in this session*: a port from serve targets, a server you noticed running, or a host/tenant remembered from another conversation is not an answer. If the user says "it's running locally," ask for the port. The custom host *is* the tenant — all scenarios and seeded data live under it; there is no separate tenant value. Timeouts, delays, artifact locations, and the oracle token env-var names (`TM_TEST_LEGACY_TOKEN`, `TM_TEST_CORE_TOKEN`) are fixed policy in the script, never asked.

**Never asked and never configured:** Mongo — the already-connected testing MCP connection is used, read-only.

## 2. Ingest the packet

Locate the packet by path or by operation slug under the established scratch location. Require status `IMPLEMENTED` with the implementation gate passing; an unimplemented packet is the port skill's job, and a code-review request is the audit skill's.

Read the ledgers this run consumes: `B-###` scenarios with their concrete payloads, the `V-###` matrix, `E-###` errors, `S-###` threats, the `X-###` exposure mapping (the translation table for diffing), `H-###` rows' runtime-unverified items, optimization equivalence notes, the drift watchlist, and deferred-testing risks from the Handoff.

## 3. Derive the case plan

Write the full `T-###` plan before executing anything. Derive cases from the ledgers, not from imagination:

- each `B-###` row → its concrete scenario against the new path, plus the same intent against the legacy/core route from the drift watchlist (entries arrive as directly callable `<apps/api | core-api> METHOD /full/path`; a prose entry you cannot call verbatim is a packet defect to report, not to re-derive silently);
- each `V-###` invalid combination → expected rejection on both paths;
- each `E-###` row → the failure scenario and equivalent error class;
- each `S-###` row → new path only (revoked key, wrong host, other-tenant, abuse limits);
- each equivalence note → targeted cases on its named dimensions (ordering, rounding, projection, null handling);
- each `H-###` runtime-unverified assumption → a case that observes it.

Coverage gate: every ledger row maps to a case or a justified `EXCLUDED` reason. Add exploratory cases beyond the ledger — boundary probing, OpenAPI-derived combinations, an agent-consumer walkthrough from docs alone — but label them `EXPLORATORY`; an exploratory surprise is a ledger gap, which is itself a finding.

## 4. Preflight the environments

Start mechanically:

```sh
python3 <skill-directory>/scripts/testing_env.py preflight --repo <root> --packet <packet-path>
```

It re-verifies readiness, requires packet status `IMPLEMENTED` (a corrupted status is reported, never repaired or invented around), extracts the wire operation, checks every host answers over HTTP, and prints the manifest seed with config provenance for every value. A preflight failure means ask or fix — never improvise a value to get past it.

Then verify yourself and add to the manifest:

- the ported endpoint exists in the external server's OpenAPI document and the API key + custom host actually authenticate — if the deployment predates the port, stop;
- deployed identity of each server (version/commit from health or docs endpoints when discoverable; otherwise URL plus date);
- data posture: this is a testing platform, so write scenarios are allowed — but everything you create must be plain, realistic platform data (sensible names, titles, descriptions, amounts), never random strings; a human auditing the tenant later should see records that look real;
- side-effect posture: deployed servers fire real queues, notifications, and provider calls — list every side-effect-bearing case and confirm the environment neuters or tolerates them before running any;
- Mongo: use the already-connected testing MCP connection for reads only; confirm with one harmless read that it is the testing environment. **Never touch a production database connection**, even read-only, and never write through Mongo at all — writes are API-only.

## 5. Execute and capture

Follow [artifact-schema.md](references/artifact-schema.md) exactly: one run directory, one folder per case, fixed file names — `case.json`, `request.json`, `response.json`, `legacy/`, `db.json`, `side-effects.json`, `verdict.json` — plus `manifest.json` and a human-first `summary.md`.

Both paths of a differential case must run against equivalent state: seed through the APIs themselves (authentic documents), giving each path its own freshly twin-seeded state, and never run the new path against state the legacy call just mutated. The Mongo MCP connection is read-only verification: capture targeted before/after documents with it whenever a rule's expected outcome is persisted state, but every write — seed and scenario — goes through the APIs only, never through Mongo. No cleanup: run-created data stays in the test tenant, listed in the artifacts — which is why it must look like real platform data, not junk. Apply the fixed inter-request delay; deployed environments are shared.

## 6. Judge and triage

Follow [runtime-judgment.md](references/runtime-judgment.md): translate public fields through the `X-###` mapping before diffing, compare absent/null/false/zero/empty exactly, and issue one of `PASS`, `DIVERGENCE`, `UNEXPECTED`, or `BLOCKED` per case with the comparison cited. Triage every divergence into one bucket — implementation bug (route to `port-external-api`), ledger error (update the packet row with the run as runtime evidence), or approved-change-missing-record (a `D-###` is owed) — with the artifact folder as proof.

## 7. Gate and verdict

Append a `## Test Traceability` section to the packet: the `T-###` table (case, ledger refs, verdict) covering every `B/V/E/S-###` row, and a `Test run:` line pinning the run directory. Only when every case is `PASS` or justified `EXCLUDED` and no divergence is unresolved, set the packet Status and `Testing status:` to `VERIFIED`, then validate:

```sh
python3 <port-skill-directory>/scripts/port_packet.py check <packet-path> --stage testing
```

Anything unresolved: the packet stays `IMPLEMENTED`, and the run report carries the findings. This workflow is the only one permitted to write `VERIFIED`, and it never does so with an open divergence, an unobservable side effect claimed as verified, or blocked cases left unaccounted.

## Handoff

Report: the run directory path; coverage (cases run / excluded / blocked per ledger prefix); the verdict table; every divergence with its triage bucket and artifact folder; ledger corrections made; residual risks (unobservable side effects, blocked cases, environment drift from pinned commits); and the resulting packet status. Point the user at `summary.md` for their own audit pass — the artifacts, not this report, are the evidence.
