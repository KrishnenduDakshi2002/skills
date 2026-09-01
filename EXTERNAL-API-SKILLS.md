# External API Skills — Usage Guide

Four skills cover the lifecycle of moving a TagMango backend endpoint (`apps/api` / `apps/core-api`) onto the external API surface. Each is independently invocable, but they are designed as a pipeline with hard handoff gates:

| Stage | Skill | Invoke with | Writes | Ends at |
|---|---|---|---|---|
| 1. Implement | `port-external-api` | `<github-issue-url>` | product code + port packet | packet `IMPLEMENTED` |
| 2. Review | `audit-external-api-port` | `[pr-number \| branch \| packet-path]` | nothing (read-only) | P0–P3 findings + one verdict |
| 3. Verify | `test-external-api-port` | `<packet-path \| operation-slug> [--report [run-id]]` | test-run artifacts + HTML reports | packet `VERIFIED` (or findings) |
| 4. Document | `document-external-api` | `<operation-id \| tag \| controller-path \| --all>` | docs-only code changes | consumer-ready OpenAPI docs |

## Install

Each skill is a plain folder (`SKILL.md` + `references/` + `scripts/`, Python 3 stdlib only). Install and update them with the skills CLI:

```sh
npx skills@latest add KrishnenduDakshi2002/skills
npx skills@latest update
```

Agents load skill text at session start — after installing or updating a skill, **start a fresh session**.

## Shared concepts

**The port packet** is the single source of truth for one operation, at `.scratch/external-api-ports/<operation-slug>/port-packet.md` (or the repo's established scratch location). Everything the pipeline knows lives in its lettered ledgers: `I` (issue requirements), `B` (behavior rules with source anchors), `V` (validation matrix), `E` (errors), `S` (security threats), `X` (exposure mapping), `C` (contract fields), `G` (contract-grill dimensions), `D` (recorded decisions), `P` (pattern conformity), `M` (core-migration mapping), `H` (implementation traceability), `T` (test cases).

**Statuses are a closed set**: `DISCOVERY`, `BLOCKED`, `READY`, `IMPLEMENTING`, `IMPLEMENTED`, `VERIFIED`. Nothing else exists (`VERIFYING`, `TESTING`, `IN_PROGRESS` are invalid). Only `test-external-api-port` may write `VERIFIED`, and only at its final gate. `port_packet.py check <packet> --stage <design|implementation|testing>` validates the gates mechanically.

**Git posture**: packets and diffs stay uncommitted unless the user explicitly asks. Test-run JSON evidence is committed with the port; everything under `.reports/` is regenerable and never committed (the tree gitignores itself).

## 1. `port-external-api` — implement the port

Give it the GitHub issue URL; a port without a readable issue stays `BLOCKED`. It reconstructs the complete legacy behavior with source anchors, designs the public contract consumer-first, then grills that contract through `AskUserQuestion` rounds (`G-001`–`G-008`) — **invoking the skill is consent to be grilled**. Implementation starts only after the developer confirms the contract and the packet is `READY`.

What it enforces:

- **Same-outcome rule** — same request, actor, and state produce the same persisted state, responses, side effects (in order), and errors as the pinned legacy source. Suspected legacy bugs are preserved and escalated as a `D-###` decision, never silently fixed.
- **Shared-capability rule** — one transport-neutral use case in `libs/services`, typed data access in `libs/repository`; external and core controllers are thin adapters. A future core route must need only auth, DTOs, mapping, and wiring.
- **One public vocabulary** — request and response share names and grouping: write DTOs derive from the resource's canonical representation so a write-then-read round-trips, internal-field renames apply identically in both directions, and filters name the response field they operate on. Every resource concept has exactly two canonical tiers — a verbose `Ext<Resource>Dto` and an `Ext<Resource>SummaryDto` composed wherever the resource is embedded — with specialized shapes derived from them (`PickType`/`OmitType`), never restated.
- **Never writes or runs tests.** It stops at `IMPLEMENTED` — traceability shows where behavior was placed, not that it executes correctly.

Use it for: new ports, research/design-only requests (stops after the grill), and retrofitting packets for already-committed code. Not for reviews — that's the audit skill.

## 2. `audit-external-api-port` — independent review

Read-only, findings-first. It reconstructs expected behavior and the contract **independently** — the packet, comments, docs, and tests are claims to verify, not authority. It audits behavioral parity, wire-contract quality (from the generated OpenAPI document, never inferred from controller fragments), request↔response symmetry and canonical representation-tier reuse, validation enforcement by layer, exposure/security (allowlist tracing, tenant binding, key scope), shared-architecture and core-replacement readiness, and test honesty.

Output: `P0`–`P3` findings (severity-ordered, each with scenario/expected/actual/impact/remediation/missing-test) and exactly one verdict: `APPROVED`, `CHANGES REQUIRED`, `BLOCKED BY DECISION`, or `NOT CERTIFIED`. It never edits code.

Use it for: PR reviews, pre-merge certification, and any "is this port sound?" question. Confirmed contract-design findings from other skills also route here.

## 3. `test-external-api-port` — runtime verification

Executes the packet's scenarios against **live external, legacy, and core servers** and diffs outcomes against the legacy oracle and persisted state. The only skill allowed to flip a packet to `VERIFIED`.

Expect the environment gate first: `scripts/testing_env.py` owns `.external-api-testing.toml` and will ask you for server URLs, the custom host (the tenant), and the API key. **Answers come only from you in-session** — the agent may not remember, infer, or default them — and you confirm the complete READY table before any request is sent. Mongo access is the pre-connected testing MCP connection, read-only; production connections are forbidden.

What a run produces, under `<artifacts-dir>/<operation>/test-runs/<run-id>/`:

- one JSON file per `T-###` case (request, response, legacy capture, db before/after, side effects, verdict with citations), plus `manifest.json` and a human-first `summary.md` — this tree is the durable, commit-worthy evidence;
- HTML reports under `<artifacts-dir>/.reports/` (per-run report, per-operation index, root index) — regenerable views, never committed, never evidence.

Verdicts are comparisons, never opinions: `PASS`, `DIVERGENCE` (triaged to implementation bug / ledger error / missing decision), `UNEXPECTED`, `BLOCKED`. A red case is never fixed by weakening the expectation.

Extras:

- `--report [run-id]` — pure re-rendering of HTML reports from existing artifacts; executes nothing, asks nothing.
- `scripts/consolidate_run.py <run-dir>` — migrates a legacy folder-per-case run to the current file-per-case format, with per-case verification; keeps anything it doesn't recognize.
- Superseded runs (named on the packet's `Test run:` line) may be deleted; the pinned run never is.

## 4. `document-external-api` — consumer-ready OpenAPI docs

Raises endpoint documentation to the bar where a consumer — increasingly an AI agent — can integrate from the generated document alone: purpose, nuances (defaults, ordering, filter interaction, limits, freshness, side effects), field semantics with **where each input value is obtained** (linked via `getExternalApiDocumentationUrl`), reachable errors with actionable descriptions, and realistic coherent examples.

Descriptions are structured markdown — purpose and use case first, then nuances as a list, then related endpoints, with subheadings and callouts on long pages — and written at the contract level: observable behavior only, never the implementation that produces it. Concision is part of the bar; a sentence that doesn't change what the consumer builds is over-documentation, not thoroughness.

Hard boundary: **docs-only diffs** — decorator metadata, DTO `@ApiProperty` options, error scenarios, registries, prose. Every claim traces to code, a packet ledger, or a captured test run; a claim that can't be traced becomes a finding (implementation bugs → `port-external-api`, contract/exposure questions → `audit-external-api-port`), never confident prose. `scripts/doc_coverage.py <spec> --repo <root>` gives the mechanical before/after gap report.

Use it for: one operation after it's verified, a tag, or a full-surface backfill sweep (`--all`).

## Common flows

- **Full lifecycle**: `port-external-api <issue-url>` → fix findings from `audit-external-api-port` → `test-external-api-port <packet>` until `VERIFIED` → `document-external-api <operation-id>`.
- **Review someone's PR**: `audit-external-api-port <pr-number>` — nothing else runs.
- **Re-render test reports** (after pruning, on a new machine, after a renderer update): `test-external-api-port --report`.
- **Docs backfill** on endpoints that predate the pipeline: `document-external-api <tag>` per domain, or `--all`.

## Ground rules for agents (all four skills)

- Never stage, commit, push, or publish unless the user explicitly asks.
- Never invent environment values, statuses, ledger rows, or evidence. Every fact is sourced: config file, user answer in-session, pinned source commit, or captured artifact.
- The generated OpenAPI document and live runtime are the contract's reality — TypeScript fragments and Swagger metadata are not.
- A suspected legacy bug is a `D-###` decision, never a silent fix or a silent keep.
- Findings route to the owning skill; no skill fixes what another skill owns.
