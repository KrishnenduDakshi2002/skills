# External API Documentation Rubric

## Contents

1. The standard
2. Operation documentation
3. Request documentation
4. Response documentation
5. Error documentation
6. Examples
7. Style and voice
8. Overview vs endpoint
9. Honesty rules

## 1. The standard

An endpoint is documented when a consumer who has only the generated OpenAPI document — no dashboard, no support channel, no source access, possibly an AI agent — can:

- decide **whether this is the endpoint they need**, including against sibling endpoints;
- build the minimal valid request and every important optional variation without trial and error;
- interpret **every** response field and predict pagination, ordering, and empty-state behavior;
- anticipate every error they can trigger and know what to change when they hit one.

The bar is completeness of **consumer-relevant claims, not completeness of detail**. The document describes observable behavior the consumer must plan around — never the implementation that produces it. Every sentence must change what a correct integration looks like; a sentence that doesn't (internal computation, code structure, field-by-field logic narration) is a gap in the other direction: over-documentation buries the claims that matter under noise.

Each numbered section below is a checklist item in the endpoint's gap table: met, gap, or justified N/A.

## 2. Operation documentation

**Summary** — a short verb phrase naming the action in consumer terms, matching the surface's existing casing convention. It is the link text in the sidebar; it must distinguish this endpoint from its siblings at a glance.

**Description** — what a consumer reads before committing to the endpoint. Descriptions are markdown documents: the renderer gives them headings, side navigation, and callouts, so structure a long description with subheadings, bullet lists, and notes instead of paragraph walls — and keep a short one to a paragraph or two; structure serves length, never decoration. Content, in this order:

1. **Purpose** — what the endpoint represents, the consumer scenario it serves, and when to use a sibling endpoint instead; a named sibling is a markdown link built with the documentation-URL helper, not just a name the consumer has to hunt for.
2. **Nuances** — a bullet list, each item one sentence of observable behavior.
3. **Related endpoints** — which endpoints produce this one's inputs or consume its outputs, linked, when not already covered by field-level obtainment links.

The *nuance hunt* below is an investigation checklist, not a writing template: answer every item from code, packet, or captured runtime — never assumed — then write **only the answers that change what the consumer builds**. A nuance is stated as observable behavior ("results may lag writes by up to 10 minutes"), never as the code that produces it. Hunt, when applicable:

- **Defaults** — the actual coded default of every optional behavior the endpoint has (period selected, sort applied, scope assumed).
- **Ordering** — the guarantee including tie-breakers, or an explicit "no order is guaranteed". Silence reads as a promise of stability.
- **Pagination semantics** — how page/limit interact, bounds, and what an out-of-range page returns.
- **Filter interaction** — what include+exclude of the same value does, empty array vs absent, combination semantics (AND/OR).
- **Limits** — array caps, string lengths, size ceilings beyond the global rate limit.
- **Write semantics** — idempotency, retry safety, partial-failure behavior, and consumer-visible side effects (notifications sent, emails fired, state transitioned).
- **Freshness** — caching or staleness windows and what may trigger a refresh, when results can lag writes.
- **Tenant scoping** — what the `x-whitelabel-host` context implies for which data this endpoint can see or touch, when it is not obvious.
- **Deprecation** — `deprecated: true` never stands alone; the description names the replacement operation and the migration in one sentence.

Operation ID from the central registry, unique in the generated document.

## 3. Request documentation

Every parameter and body property carries a description that **adds information the name doesn't already carry**. `userId: "The user ID"` fails the bar. State:

- **meaning** — which user, which resource, in consumer terms;
- **format** — ObjectId hex string, ISO 8601 timestamp, timezone assumptions, units (or put the unit in the name: `durationSeconds`, `amountMinorUnits`);
- **obtainment** — which endpoint or flow produces this value, linked to that endpoint's reference page via the documentation-URL helper (`getExternalApiDocumentationUrl`) so the consumer can jump straight to it; an input the consumer cannot source is undocumented no matter how well described;
- **constraints** — min/max/enum/pattern mirroring the *actual validators*; prefer citing the same shared policy constants the validators use so docs cannot drift from enforcement; a documented constraint nothing enforces is a finding, not a doc;
- **requiredness truth** — required/optional as validated, defaults stated on the property, conditional and mutually-exclusive relationships cross-referenced *on both fields involved*;
- **enums** — each value's meaning when not self-evident, not just the value list.

## 4. Response documentation

- Every response field described with its consumer meaning — what they can do with it, where it can be used as an input.
- Null/omission policy stated per optional field: is it `null`, absent, or an empty collection, and what does each mean.
- Enum and status fields explain each value a consumer must branch on.
- Collection responses state their ordering (or disclaim it) and their empty shape.
- The success description on `doc.ok` says what "success" delivered, not "Operation successful".
- A field you cannot give a consumer use case for is a **possible exposure defect**: raise the finding to `audit-external-api-port` and pause on that field — neither advertise it with prose nor quietly hide it; whether it stays in the contract is a contract decision, not a documentation one.

## 5. Error documentation

- Every scenario in `errors: [...]` traces to a reachable throw path; every reachable externally-visible error code appears in `errors: [...]`. Both directions are checked — an unreachable documented error and an undocumented reachable error are each gaps.
- Descriptions are consumer-actionable: what condition produced it and what to change — "One or more badge IDs do not belong to this creator; fetch valid IDs from List Badges" beats "Invalid badge filter".
- Definitions come from the central error registry (`getErrDefinition`), never inline literals.
- Validation-shaped 400s from DTO constraints don't need one scenario per field, but the endpoint documents that constraint violations return the standard validation error shape when it has a body worth noting.

## 6. Examples

- Realistic platform data — plausible names, titles, amounts, ObjectId-shaped IDs — never `"string"`, `"foo"`, `"test"`. The one exception: credentials are always placeholders (`<your-api-key>`).
- One operation's examples tell **one coherent story**: the IDs in the request appear in the response, counts match array lengths, timestamps are ordered sensibly. Captured runtime evidence from test runs (redacted) is the best source.
- Examples exercise the documented semantics: a filter example shows a filter actually filtering; a pagination example is not page 1 of 1.

## 7. Style and voice

- Consumer language throughout. Platform terms a consumer meets in the product (mango, creator, custom host) are fine; internal vocabulary is not — no Mongo/Mongoose/schema field names, module or function names, frontend labels, or "same as the old API" references. Legacy provenance is packet material, never contract material.
- Active voice, present tense, sentences over fragments. Descriptions are markdown: structure a long one with subheadings, bullet lists, and note callouts — headings feed the reader's side navigation — but keep heading depth shallow (one level of subheadings) and give a short description no structure it doesn't need.
- Concise by selection, not compression: cover purpose, nuances, and related endpoints in the fewest sentences that carry them, and cut the sentence that changes nothing for the consumer rather than shortening every sentence into fragments.
- Observable behavior only. How a value is computed, which module produces it, what the code checks in what order — implementation is never contract material. A field's description says what the value means and how to use it, not how it is derived; derivation enters the docs only when it surfaces as behavior the consumer must plan around (staleness, ordering, side effects).
- Emphasis sparingly and by meaning: call out destructive, irreversible, or security-relevant behavior prominently; a non-obvious but safe nuance is a plain sentence. A warning on every endpoint means none of them read as important.
- The description never restates what the spec already encodes (method, path, status codes) — it spends its words on what the schema cannot say.

## 8. Overview vs endpoint

The overview description in `external-api-document.ts` owns the once-only facts: authentication headers, tenant header, response envelope, global rate limits, general error shape. Endpoint docs:

- never repeat an overview fact except where the endpoint deviates from it — and a deviation is stated explicitly *as* a deviation;
- never contradict the overview; if the overview itself is wrong or stale against runtime, that is a finding on the overview, fixed there once, not compensated per endpoint;
- new cross-cutting facts discovered while documenting (a shared pagination convention, a shared freshness rule) get proposed for the overview or a shared DTO rather than duplicated into each endpoint.

Tags are part of this layer: every tag a controller uses is registered in `buildExternalApiDocumentOptions` with a consumer-facing description of the domain, not a restatement of the tag name.

## 9. Honesty rules

- **Trace or flag.** Every claim of behavior (default, order, limit, side effect, error condition) has a trace anchor in the working notes — code location, packet row, or captured run. No anchor → the claim is not written; the gap is reported instead.
- **Existing prose is a claim.** Verify every sentence you keep with the same rigor as one you write. Stale prose that survives a documentation pass is worse than absent prose — it now carries this pass's authority.
- **The code wins on "is".** When docs, packet, and code disagree, the docs must describe what the code does now; the disagreement itself is routed as a finding (packet correction, or bug to `port-external-api`).
- **Never document aspiration.** Behavior that "will be fixed", "should" hold, or exists only in an unmerged branch does not enter the contract.
- **Undocumentable is reportable.** Behavior too erratic, accidental, or exposure-laden to describe honestly is exactly the material for a finding; leaving it vague in prose converts a defect into a promise.
