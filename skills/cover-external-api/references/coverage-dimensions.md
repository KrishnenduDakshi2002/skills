# Coverage dimensions

Read while tracing selected endpoints and reviewing their outlines. Apply every relevant dimension; derive expectations from the actual contract and behavior. Record a brief reason in the handoff for material exclusions. Do not invent unsupported features or promises of exhaustive permutation coverage.

## Derive behavioral invariants

An invariant is an observable guarantee that must hold across its stated inputs, actors, states, or operation sequences. Derive these guarantees before outlining cases so tests protect API behavior beyond the branches present in the newer implementation.

Inspect the selected use case across available sources, recording the checkout/revision and relevant file/symbol anchors. Trace corresponding operations even when route or field names differ; do not assume similarly named endpoints have equivalent contracts.

| Source | Evidence to extract |
|---|---|
| Legacy implementation and API | Actual guards, validation, defaults, errors, tenant boundaries, state transitions, persisted outcomes, response omissions, side effects, and ordering, including observable quirks. Use existing trustworthy runtime artifacts when available; this skill does not execute live comparisons. |
| Relevant legacy/current frontend consumers | Requests actually constructed, omitted vs explicit fields, response fields and states relied upon, retries, pagination, and sequences of API calls. Trace shared client helpers and adapters as needed. UI restrictions show consumer assumptions; they do not prove backend enforcement or define the full API input domain. |
| Newer implementation | Current policy/service/repository/schema/adapter behavior, deliberate contract changes, and possible gaps against legacy guarantees and consumer expectations. A current code path or passing test alone does not make its behavior authoritative. |

Reconcile the sources rather than taking their intersection or a majority vote. Preserve established legacy behavior where parity is required, subject to explicit approved contract changes. Frontend expectations can expose compatibility gaps but cannot silently override the API contract; newer code can reveal additional guarantees but must not validate itself as the sole oracle. Treat comments, OpenAPI, and existing tests as supporting evidence to check. Mark disagreements or unsupported candidate guarantees with `CONTRACT QUESTION`; resolve their intended behavior before implementation. If a source is unavailable, state the gap and outline supported cases without claiming cross-source confirmation.

Turn each supported invariant into reviewable cases:

1. State its preconditions, operation, observable guarantee, and scope. For related APIs, capture a shared state or relationship guarantee only when supported by their actual contracts and within the selected endpoint scope; report any required scope expansion.
2. Vary conditions that could violate it: actor/tenant, relevant state, omitted vs explicit update fields, boundary values, repeated requests, concurrent work, or dependency failure where supported. Include meaningful negative and interacting cases, not an arbitrary product of inputs. Do not assume idempotency, atomicity, or order independence without evidence.
3. Include relational checks when warranted: adding an unrelated tenant's record must not affect a tenant-scoped result; an update omitting a field must retain it if sparse-update semantics are promised; a create/read sequence must preserve the agreed representation. Derive actual names and expectations from the sources, not these examples.
4. Declare concrete `it.todo` or pending parameterized cases in stage 1. Keep a concise invariant statement and source anchors beside its cases when the relationship is not obvious; use the specs as the review artifact, not a separate invariant ledger. Apply [claim-based layer assignment and evidence rules](test-layers.md#assign-cases-from-their-claims), including real-Mongo reads for persisted-state guarantees.
5. In stage 2, implement the reviewed cases with independently specified expectations. For each invariant, identify a plausible behavioral regression and verify that its assertions would detect it; do not derive expected values by replaying the implementation under test. Report unproven guarantees separately from passing examples or line coverage.

## Enumerate relevant dimensions

| Dimension | Cases to derive where applicable |
|---|---|
| Inputs and transformation | Required/optional fields; omitted vs undefined/null/empty/zero/false; scalar/array/object mismatch; string coercion; whitespace/case; IDs; enums; nested validation; unknown fields; list tokens; size, date, and numeric boundaries immediately below/at/above limits. |
| Authentication and scope | Endpoint-specific permission/scope; wrong host/tenant/creator; foreign resource IDs and nested references; no data leakage or state change on rejection. Reuse generic missing/invalid/revoked credential coverage from the middleware/guard owner under [authorization evidence](test-layers.md#authorization-evidence); exercise actual guards when claiming their behavior. |
| Business states | Allowed and forbidden transitions; inactive/deleted/expired/pending/completed states; ownership and eligibility; merged-state update validation; mutually dependent fields; policy interactions; observable legacy quirks. |
| Reads and queries | Empty/single/multiple results; filters separately and in meaningful combinations; sorting and ties; pagination/defaults/limits/counts/cursors; missing relations; soft deletion; joins/aggregations; tenant isolation. Use real repository queries for these outcomes. |
| Writes | Persisted values/defaults/references; create vs sparse update vs explicit clearing; unchanged field preservation; no-op updates; duplicate keys; repeated request behavior; idempotency; bulk partial success/failure; delete semantics and cascades. |
| Public success contract | Status and headers where specified; exact envelope and nested key sets; full vs summary resource; types/formats/units/enum values; IDs/dates/URLs; ordering; pagination metadata; omission vs null vs empty; explicit absence of internal fields/secrets. |
| Failure contract | Validation/auth/not-found/conflict/domain failures; provider/database failure mapping; stable error code/message/details; sanitized errors; failure after partial work; rollback/compensation and preserved state. Avoid binding tests to incidental stack traces. |
| Side effects | Queue/webhook/email/payment/cache payloads and destination/scope; exactly-once/duplicate/suppressed effects as the contract specifies; cache invalidation/expiry; effects absent on failure; observable ordering when it matters. Use fakes, never real providers. |
| Time and money | Inclusive/exclusive date boundaries, expiry and time zones, rounding/precision/currency, zero/negative amounts, discounts/tax/installments; controlled clock and explicit values. |
| Consistency | Concurrent requests, uniqueness races, transaction rollback, stale state, retries, repeated delivery, atomic state transitions. Cover actual guarantees and known risks with a memory replica set if required. |

Place each claim at the boundary that can prove it. For example, mapper unit tests establish a projection but cannot establish that the response pipeline actually uses it. Repository integration can establish tenant filtering but a mocked repository returning only the right tenant cannot.

Make negative cases observable: check both the rejection and absence of unintended persisted changes/side effects. Test the public response independently of schema defaults so adding an internal schema field cannot silently update the expected response.

Do not enumerate an arbitrary Cartesian product. Explicitly cover rule interactions that change outcomes, including invalid input combined with foreign ownership, update fields combined with retained state, and dependency failure after an earlier write when those paths exist.
