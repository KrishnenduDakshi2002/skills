# Behavior Parity Research

## Contents

1. Define authority
2. Trace the full execution path
3. Build the behavior ledger
4. Interpret frontend behavior
5. Preserve value semantics
6. Resolve contradictions and outliers
7. Capture parity evidence for implementation
8. Avoid common failure modes

## 1. Define authority

Pin every source before drawing conclusions. Record the repository, checkout, branch, commit, and why it is authoritative.

Use this precedence unless the user provides a different one:

1. Explicit user designation of a repository/branch/commit.
2. Accepted product specification or durable decision record.
3. Runtime backend behavior and persisted invariants.
4. Tests that assert observable behavior.
5. Frontend gates, validation, defaults, and payload assembly.
6. Existing external APIs and documentation as public-contract precedent.
7. Comments, tickets, and names as supporting evidence only.

Do not treat the current target diff, an agent-authored plan, or a nearby refactor as source truth. Do not mix files from different commits without recording the mixed provenance.

## 2. Trace the full execution path

Start at the registered route rather than a method name found by search. Follow:

```text
route
  -> middleware / guards / tenant resolution
  -> request validator / parser / normalizer
  -> controller
  -> service and policy decisions
  -> repositories / models / schema defaults / hooks
  -> external calls / queues / notifications / analytics
  -> response and error transformation
```

Then trace every known caller, especially the designated legacy frontend:

```text
initial state / hydrated edit state
  -> field visibility and entitlement gates
  -> on-change normalization
  -> submit validation
  -> payload assembly, field deletion, and defaulting
  -> backend call
  -> success, retry, and failure behavior
```

Search by route, controller/service symbol, persisted field names, error strings, analytics/queue names, and frontend payload keys. A field can be renamed several times across these boundaries.

For every caller-controlled URL, asset reference, redirect target, callback, provider identifier, or filename, trace the downstream consumer. Record whether the server fetches it, follows redirects, derives storage keys from it, queues it, logs it, or passes it to a privileged third party. Treat the downstream action—not the input's superficial string type—as the behavior and security boundary.

Inspect sibling create/update/read/delete flows when they share rules. Creation defaults often differ from edit patch semantics; never infer one from the other.

## 3. Build the behavior ledger

Assign one `B-###` identifier to each externally meaningful behavior. Keep rules atomic enough that each rule maps to one clear implementation decision and can later be verified independently. Record scenarios with concrete executable values — real field names, sample payloads, expected persisted fields — not abstractions.

Define the canonical capability before letting the external contract narrow the research. A legacy route may bundle several independent capabilities; split those deliberately, then trace the complete behavior of the capability in scope. The external adapter may accept or return fewer fields, but that exposure choice must not erase legacy rules that a future core replacement will need.

For every rule, record:

- scenario and preconditions;
- accepted input and rejected input;
- defaulting and normalization;
- persisted state;
- returned value or error;
- side effects and their order;
- evidence anchor;
- confidence and classification;
- target behavior and implementation-handoff mapping.

Include negative and lifecycle rules, not only happy-path transformations:

- permissions, ownership, tenant/host scoping, and feature access;
- already-exists, already-deleted, stale-state, and duplicate-request behavior;
- partial failure and rollback behavior;
- idempotency and retry behavior;
- ordering and pagination stability;
- time, timezone, currency, units, and rounding;
- external provider calls, queues, notifications, analytics, and quotas.

Separate the invariant from its current implementation. For example, record “a free product cannot carry paid pricing” rather than “the frontend deletes `price` on line X.” The deletion is evidence; the invariant is the portable behavior.

Create one `M-###` mapping per capability slice. Map the legacy behavior IDs to the canonical shared use case/repository, external adapter behavior, current or future core adapter, and implementation evidence. If a future core route would still require new business logic, data access, state transitions, or side-effect orchestration, the port is not core-migration-ready.

## 4. Interpret frontend behavior

Do not blindly copy every disabled control into backend validation. Classify each observation:

| Class | Meaning | Target action |
|---|---|---|
| Business invariant | The combination is invalid regardless of client | Enforce on the backend and document the error |
| Product/entitlement gate | The actor is not allowed to use the capability | Enforce with current server-side entitlement/permission policy |
| Normalization/default | The UI consistently derives a canonical value | Preserve when source-backed; expose or default deliberately |
| UI convenience | The UI simplifies input but the combination remains valid | Do not create an API restriction |
| Stale/accidental behavior | Sources disagree or behavior appears buggy | Record a decision; do not silently preserve or fix |

Require more than conditional visibility alone before calling something a business invariant. Look for submit validation, payload deletion/forcing, backend consumers that assume the invariant, tests, copy, or product documentation.

When the frontend forces a value instead of rejecting input, decide deliberately whether the external API should:

- reject the contradictory input;
- normalize it and disclose the normalized response;
- omit the field from the public request entirely.

Prefer rejection for contradictory caller intent. Prefer omission when the value is purely internal and callers cannot make a meaningful choice. Preserve normalization only when it is stable, safe, and clearly documented.

## 5. Preserve value semantics

Treat these as distinct until evidence proves equivalence:

- field absent;
- field present with `undefined` before serialization;
- `null`;
- `false`;
- `0`;
- empty string;
- empty array;
- empty object.

Trace each value through DTO transformation, validation, object spreading, schema defaults, update operators, persistence, and response serialization. Pay special attention to partial updates: absent usually means “leave unchanged,” while `null` may mean “clear.”

Record ordering, trimming, case folding, HTML/rich-text bytes, numeric coercion, timezone conversion, and array de-duplication explicitly. Do not add a normalizer merely because it appears cleaner.

## 6. Resolve contradictions and outliers

Use a question only when source investigation cannot resolve a material choice.

Mark a rule `needs-decision` when any of these hold:

- backend and frontend allow different combinations;
- create and edit paths disagree without a clear lifecycle reason;
- current runtime behavior contradicts accepted documentation;
- preserving a behavior would expose sensitive/internal data;
- an apparent legacy bug has real compatibility impact;
- two branches/checkouts implement different product decisions;
- target-branch prerequisites are missing.

Describe both behaviors with evidence and recommend one. Do not average them, select the easier implementation, or hide the divergence behind a permissive fallback.

If an outlier affects only an internal transport artifact, keep it out of the public contract. If it affects observable behavior, include it in the ledger even when rare.

## 7. Capture parity evidence for implementation

Prefer evidence in this order:

1. Current runtime behavior or stable captured request/persistence/response evidence when already available.
2. Existing characterization or behavior tests as source evidence; do not author new tests in this workflow.
3. Pinned controller/service/repository/schema/frontend source comparison.
4. Explicit hypotheses and deferred runtime risks when executable evidence is unavailable.

Distinguish exact parity from semantic parity. Exact parity compares bytes/values when representation matters. Semantic parity permits an approved public representation change while comparing the same business outcome, persistence, and side effects.

An optimization or restructuring claims semantic parity only with an equivalence note in the packet arguing outcome-equality against each affected `B-###` — covering ordering, rounding, projection, pagination stability, timezone, and null handling — flagged for the later testing workflow to verify.

Never broaden normalizers, add allowlists, or discard fields merely to simplify the port. Record unexplained differences for a product decision or the later testing workflow.

## 8. Avoid common failure modes

- Do not stop after finding the legacy controller.
- Do not call typecheck, build, or handler existence parity certification; this skill produces an implementation handoff, not certification.
- Do not assume a schema default matches a frontend-created document.
- Do not copy legacy request/response names into the public API by default.
- Do not use current target code as proof that its own behavior is correct.
- Do not infer a rule from one happy-path payload.
- Do not reason only from values the frontend can currently submit; external callers can send every schema-valid combination.
- Do not promise a port against a target branch before checking its prerequisite domain services and schemas.
- Do not silently turn an accidental permissive backend path into a documented external capability.
