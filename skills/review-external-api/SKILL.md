---
name: review-external-api
description: Code-owner review of any TagMango external API change — a PR, branch, or working tree — against the established external-API rules; contract design, request↔response vocabulary symmetry, canonical representation tiers, exposure and mapper enforcement, shared libs/services + libs/repository architecture, naming, and the documentation bar. Works with or without a port packet; read-only P0–P3 findings with optional inline PR comments after explicit confirmation. For full behavioral certification of a packet-driven port, use audit-external-api-port.
argument-hint: "[pr-number | branch | path] [--comment]"
disable-model-invocation: true
---

# Review External API — Owner Review

You review on behalf of the external API surface's code owner. The contributor may not have used the port pipeline — no GitHub-issue grill, no port packet, no ledgers. **The rules still bind the code**; pipeline artifacts are evidence when present, never a precondition for review. Judge the diff against the established rulebook, not against what the contributor knew.

This is not `audit-external-api-port`. The audit skill certifies a packet-driven port end-to-end, including behavioral parity against pinned legacy sources, and correctly refuses to certify without that evidence. This skill answers the owner's question — *does this change conform to how we build the external surface?* — for any external-API-touching change, and never claims parity certification. When the change is a legacy port whose behavior matters, this review still runs, and the verdict escalates.

Stay read-only and findings-first: no edits, no staging, no commits, no PR state changes. The only write this skill ever performs is posting review comments, and only after the user confirms the findings in-session.

## 1. Resolve the target and scope

- A PR number → resolve the base-to-head diff with `gh pr view` / `gh pr diff`; never trust the PR description as evidence.
- A branch → diff against its merge-base with the repository's integration branch (`testing` unless the user says otherwise).
- No argument → the working tree diff.

In scope: everything the diff touches on or reachable from the external surface — `apps/core-api/src/api-modules/external/**`, the canonical DTO files under `apps/core-api/src/shared/dto/examples/` and `shared/dto/external/`, the swagger/tag/operation-id registries, and any `libs/services` / `libs/repository` code an external controller reaches. Unrelated changes riding in the same PR are listed as out of scope, not reviewed deeply, and flagged if they widen the PR.

Then locate pipeline artifacts for the touched operations: a port packet under the established scratch location, test-run evidence, grill decisions. Present → treat them as claims to verify and use their `D-###` decisions as recorded authority. Absent for a new or changed public endpoint → record one process finding (normally `P2`: contract decisions unrecorded, behavior unverified by the testing workflow) and continue; absence never blocks the review.

## 2. Walk the owner's checklist

Read [review-checklist.md](references/review-checklist.md) and walk every dimension against the diff. It is the distillation of the rules the four pipeline skills enforce; each finding cites the checklist item it violates so the contributor can trace the rule, not just the complaint.

Ground every wire-contract judgment correctly:

- Prefer the generated OpenAPI document (the repository's external preview script, temporary output path) when it can be produced cheaply; a controller decorator fragment is not the public URL and Swagger metadata is not the runtime shape.
- Remember the serialization seam: `@ExternalApi` does not attach `RespondWithDto`, so no `plainToInstance` allowlisting runs on external routes — the feature's `*.mapper.ts` is the only exposure enforcement. Trace what the service actually returns; a DTO the response bypasses protects nothing.
- Read the repository's own standards (`BEST_PRACTICES.md`, `AGENTS.md`) for anything the checklist doesn't settle; the checklist adds external-surface rules, it does not replace repo standards.

## 3. Verify, then report

Verify every candidate finding against the code before reporting it — open the file, trace the call path, confirm the failure scenario is reachable. Drop what you cannot confirm or label it explicitly as a hypothesis with the missing evidence named.

Report findings ordered by severity, in the shared format:

```text
[P1] <concise violated rule> — <file:line>

Rule: <checklist item / skill rule violated>
Scenario: <concrete request/state that exposes it>
Expected: <what the rule requires>
Actual: <what the diff does, with evidence>
Impact: <consumer, exposure, drift, or maintainability consequence>
Remediation: <smallest sound direction; do not patch>
```

- `P0` — exploitable exposure or security: cross-tenant data, unallowlisted fields reaching the wire, auth/host binding gaps.
- `P1` — contract or architecture violations that ship debt: vocabulary asymmetry, a second public shape for an owned concept, app-local business logic, raw documents passed through, an unregistered tag breaking docs.
- `P2` — important conformance gaps: hand-restated DTO fields, missing policy objects, docs below the bar, missing pipeline artifacts, naming violations.
- `P3` — low-risk consistency and clarity issues.

Do not flood the report with `P3` nits while `P0`–`P1` risks remain. Conclude with exactly one recommendation:

- `APPROVE` — no `P0`/`P1` findings; `P2`/`P3` items listed for follow-up.
- `CHANGES REQUIRED` — one or more `P0`/`P1` findings block merge.
- `ESCALATE TO FULL AUDIT` — the change ports or rewrites legacy behavior whose parity cannot be judged from the diff; route to `audit-external-api-port` (and the pipeline) after the conformance findings are fixed.

## 4. Post comments — only on confirmation

With `--comment`, or when the user asks after seeing the report: show the complete findings first, get explicit in-session confirmation of which findings to post, then post each as an inline PR review comment (`gh api` review with per-finding path/line), severity-tagged and citing the rule. Submit as a `COMMENT` review; use `REQUEST_CHANGES` only when the user explicitly says so. Never post without the confirmation, never edit or resolve threads, and never approve the PR on the user's behalf.

## Ground rules

- Every finding cites its rule and its evidence (`file:line`); a finding without both is not reportable.
- Pipeline absence is a finding, never a reason to review less rigorously — the rules bind the code either way.
- Never describe this review as parity or runtime certification; that authority belongs to `audit-external-api-port` and `test-external-api-port`.
- Never stage, commit, push, or change PR state unless the user explicitly asks.
