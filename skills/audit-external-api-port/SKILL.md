---
name: audit-external-api-port
description: Perform an independent, read-only audit of a GitHub-issue-led TagMango external API port for legacy/core-api behavioral parity, resolved public-contract decisions, backend enforcement of frontend rules, security and field exposure, capability-complete business logic in libs/services, shared data access in libs/repository, external plus current/future core reuse, core-replacement readiness, documentation/runtime agreement, and test evidence. Use when asked to review, audit, validate, certify, or find gaps in an external endpoint or port. Do not implement fixes unless the user separately approves them after reviewing findings.
---

# Audit External API Port

Reconstruct the expected behavior and public contract independently. Treat the implementation's port packet, comments, docs, and tests as claims to verify, not authority.

Keep the audit read-only and findings-first. Do not edit code, resolve threads, stage, commit, push, or publish anything unless the user explicitly asks after seeing the findings.

## 1. Lock scope and evidence

Read repository instructions, coding standards, testing rules, architecture maps, and working-tree state. Determine the exact base-to-head or user-specified diff; report unrelated dirty files and keep them out of scope.

Pin:

- the initiating GitHub issue, current body/comments, captured `I-###` requirements, and accepted contract decisions;
- target branch/commit and external surface;
- authoritative `apps/api` and/or `apps/core-api` source commit;
- user-designated `tagmango-web-platform` commit;
- accepted specification/decisions;
- port packet path, if any;
- claimed `M-###` capability mappings and core migration readiness;
- generated OpenAPI and runtime evidence available for the target.

If source authority is ambiguous, investigate repository/branch evidence first. Ask only when the ambiguity would change a material conclusion.

Read [audit-rubric.md](references/audit-rubric.md) before reviewing the diff.

## 2. Reconstruct behavior independently

Trace route, middleware/guards, validation, controller, service, repositories, schema defaults/hooks, transactions, external calls, queues, notifications, analytics, quotas, response transformation, and error mapping in the authoritative source.

Trace frontend initialization, conditional gates, submit validation, payload assembly/deletion/defaulting, and caller success/failure behavior. Classify each frontend restriction as a business invariant, entitlement gate, normalization/default, UI convenience, or ambiguity.

Build a reviewer ledger of externally meaningful scenarios. Include negative combinations, lifecycle states, permissions, ownership, tenant/host binding, side effects, ordering, idempotency, retries, and absent/null/false/zero/empty semantics.

Define the scoped business capability independently of the external contract. If the legacy route bundles several capabilities, verify the declared decomposition. Trace all behavior required for the capability a future core route will replace, including modes or domain results the external API intentionally omits.

Compare this ledger with the target and the port packet. Do not downgrade an independently discovered rule because the packet omitted it.

Verify that the issue was treated as the starting brief rather than unquestioned runtime truth. Check that every required `G-###` contract dimension was resolved by the developer or explicitly justified as not applicable, and that the implementation matches those resolutions.

## 3. Audit the actual wire contract

Inspect the generated OpenAPI document and, where feasible, representative runtime HTTP responses. Do not infer the public URL from a controller fragment or the response shape from Swagger DTO metadata.

Judge the endpoint from an unfamiliar integrator's perspective:

- Is the complete versioned URL intuitive and consistent?
- Are method and resource boundaries honest?
- Are path, query, headers, and body used deliberately?
- Does every public field have a clear name, type, format, unit, requiredness, default, null/empty meaning, and realistic example?
- Are conditional fields representable and backend-enforced?
- Is the response grouped around the consumer's next action and explicitly allowlisted?
- Are errors stable, actionable, documented, and consistent with runtime?
- Are retry, idempotency, concurrency, pagination, and compatibility semantics defined where material?

Write the smallest valid request, an important optional combination, and an invalid combination from the docs alone. If that is impossible, record a contract finding.

## 4. Audit validation and enforcement

Create a decision table from all discriminators and dependent fields. Send or reason through combinations that the first-party frontend never emits; external callers are not constrained by UI controls.

Verify:

- conditionally required and forbidden fields;
- contradictory values and normalization policy;
- actor-, tenant-, currency-, entitlement-, ownership-, and state-dependent rules;
- boundaries, formats, precision, unknown fields, and array encoding;
- create versus patch absent/null semantics;
- database-enforced uniqueness/integrity under races;
- frontend business rules promoted to backend enforcement;
- UI-only constraints not accidentally promoted.

Documentation without enforcement is a defect. A DTO decorator alone is insufficient for rules requiring authenticated/database context.

## 5. Audit exposure and security

Trace every response field to its source. Flag raw document spreads, broad projections, internal DTO reuse, populated objects, unstable schema fields, secrets, private user data, internal flags, provider payloads, and cross-tenant relationships.

Verify authentication separately from API-key scope, host/tenant binding, permission, resource ownership, rate/quota policy, and non-enumeration behavior. Test or inspect revoked keys, wrong hosts, other-owner resources, and failure messages.

For mutations, inspect atomicity, duplicate submission, timeout/retry behavior, and whether side effects can double-run.

## 6. Audit architecture and tests

Confirm the target preserves business behavior through maintainable current architecture:

- controller owns HTTP parsing/auth and delegates one meaningful use case;
- shared domain service under `libs/services` owns rules, transactions, state transitions, and side-effect orchestration;
- shared repository under `libs/repository` owns typed persistence and queries;
- equivalent core and external controllers call the same shared use case rather than duplicate policy branches;
- the shared use case is complete for the scoped legacy capability rather than shaped around the external subset;
- transport DTOs, HTTP errors, envelopes, and public exposure mapping remain outside the shared service;
- domain commands, results, actor/tenant context, and errors are transport-neutral and do not branch on `external` versus `core`;
- public mapper/DTO owns response shaping;
- shared canonical services/utilities are reused;
- legacy controllers are not called or copied wholesale;
- every file added by the port has a lowercase kebab-case descriptive base with established dot-delimited role suffixes; untouched legacy names are out of scope, and any repository-, framework-, or generator-mandated exception is documented;
- no shallow facade, response-shaped domain service, cast-heavy boundary, or duplicated error mapping was added.

Verify that every scoped `B-###` and `V-###` rule appears in an `M-###` row, then trace each row independently from legacy behavior into shared service/repository code, external adapter policy, the current or future core mapping, and tests. When no core route exists, verify that adding it would require only authentication, DTO/mapping, and controller/module wiring. If it would require a new business rule, repository query, state transition, side-effect path, or response-shaped rewrite of the shared model, the readiness claim fails.

Treat new app-local business services/repositories, failure to rewire an equivalent core caller, an external-shaped partial domain model, or a future core replacement that still needs business/data reimplementation as blocking architecture findings. Do not accept speculative generics or a catch-all service as a substitute for a concrete, capability-complete shared use case.

Map reviewer rules to tests. Reject construction-only, handler-existence, broad snapshot, mock-choreography, and happy-path-only tests as parity evidence. Require behavior-focused tests at the correct unit/integration/HTTP seams, real Mongo where persistence matters, and faked external infrastructure.

Verify generated docs against runtime. Typecheck, lint, build, and coverage are supporting signals, not behavior certification.

## 7. Report findings

Order findings by severity and confidence. Use this format:

```text
[P1] <concise violated promise> — <target file:line>

Scenario: <concrete request/state/actor>
Expected: <source-backed behavior or public contract, with evidence>
Actual: <what target does, with evidence>
Impact: <consumer, data, security, compatibility, or operability consequence>
Remediation: <smallest sound direction; do not patch>
Missing test: <observable test that would catch it>
```

Use:

- `P0` for exploitable security/privacy, cross-tenant access, irreversible corruption, or catastrophic side effects;
- `P1` for broken business parity, auth/ownership, public compatibility, data integrity, required shared-layer reuse, or common unusable contract behavior;
- `P2` for important edge cases, misleading docs/examples, response exposure, maintainability, or material test gaps;
- `P3` for low-risk clarity/consistency issues worth fixing.

Do not flood the report with style nits while behavioral or contract risks remain. Do not state speculative findings as facts; label hypotheses and name the missing evidence.

## 8. Give a certification result

Conclude with exactly one:

- `APPROVED` — no blocking findings; behavior, contract, enforcement, exposure, core-replacement readiness, docs, runtime, and tests are adequately evidenced.
- `CHANGES REQUIRED` — one or more valid findings block approval.
- `BLOCKED BY DECISION` — source-backed behaviors conflict and a product decision is required.
- `NOT CERTIFIED` — required source/runtime/test evidence was unavailable.

List the source pins, checks actually run, core migration readiness result, unverified areas, and residual risks. Never convert a partial static review into a parity certification.
