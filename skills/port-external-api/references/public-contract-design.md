# Public Contract Design

## Contents

1. Start with the consumer task
2. Design the endpoint and URL
3. Place request data deliberately
4. Define every field
5. Enforce combinations
6. Shape the response
7. Design errors
8. Address security and retries
9. Handle compatibility and versioning
10. Run the consumer simulation

## 1. Start with the consumer task

Write one sentence before designing:

> An external `<actor>` calls this operation to `<goal>` and needs `<result>` to decide `<next action>`.

Identify the likely caller, its available identifiers, whether it operates interactively or in bulk, how it retries, and what it can safely know. Do not make a consumer understand TagMango collections, frontend form state, or internal service boundaries.

Keep one endpoint focused on one externally meaningful operation. Split unrelated mutations even if the internal controller currently combines them.

## 2. Design the endpoint and URL

Inspect the current external API's actual generated paths and naming conventions first. Consistency is part of usability, but existing accidents are not automatically standards.

Use these decision rules:

- Name resources with clear public domain nouns, normally plural and kebab-case.
- Use path segments for stable resource identity or true containment.
- Use query parameters for filtering, searching, sorting, pagination, sparse field selection, and non-mutating presentation options.
- Use the body for mutation input and cohesive commands.
- Use headers only for cross-cutting protocol context such as authentication, version negotiation, idempotency, tenant/host, locale, or tracing.
- Prefer standard HTTP methods and their safety/idempotency semantics.
- Use an action subresource only when the operation is not honest CRUD, such as `:refund`, `:publish`, or `:revoke`; use the existing external convention for action syntax.
- Avoid controller names, implementation versions, redundant nesting, and verbs such as `get`, `create`, or `update` in ordinary resource paths.

Check route ambiguity and registration order. A dynamic `/:id` route must not swallow a static route such as `/reporting/summary` or `/subscriptions/count`.

Record the complete wire URL after global prefixes and URI versioning. A controller decorator fragment is not the public URL.

## 3. Place request data deliberately

### Path parameters

Use path parameters for the resource being addressed. Document identifier format and ownership/tenant scoping. Do not require a creator ID when authentication already binds the creator unless the caller genuinely selects among creators.

### Query parameters

Define pagination defaults and maximums, sort fields and tie-breakers, filter combination semantics, date inclusivity, timezone interpretation, empty-result behavior, and array encoding. Avoid an unbounded list endpoint.

### Request body

Group related fields only when the group has a meaningful name and lifecycle. Do not reproduce frontend component nesting. Prefer a discriminated union when valid fields depend on a mode/type; it makes impossible combinations unrepresentable in generated clients.

For partial updates, state whether the operation uses patch semantics and define absent versus `null` per field. Do not model a patch by making every create field optional without clear semantics.

### Headers

Document required authentication and host/tenant headers in one canonical place and show them in examples. Do not move business data into a custom header to avoid designing a body.

## 4. Define every field

For each public field, document:

- consumer-facing name and description;
- JSON type and concrete format;
- required, optional, conditionally required, or forbidden conditions;
- default and who applies it;
- allowed values, range, length, precision, units, and timezone;
- absent, `null`, empty, false, and zero semantics;
- normalization such as trimming or case handling;
- whether it is immutable after creation;
- a realistic example that satisfies all rules;
- sensitivity and reason for exposure.

Use names that communicate the unit (`durationSeconds`, `amountMinorUnits`) or document the unit unambiguously. Avoid internal abbreviations, schema field names, double negatives, and names whose meaning changes by mode.

Do not leak Mongo/Mongoose types, storage field names, populated-document shapes, provider secrets, internal flags, raw entitlement maps, or fields included “for completeness.” Every response field needs a consumer use case.

## 5. Enforce combinations

Documentation alone is not validation.

Represent conditional contracts with one or more of:

- a discriminated DTO/union for shape-level alternatives;
- a named pure validator/policy for cross-field rules;
- service-layer checks for rules requiring authenticated actor, database state, entitlement, currency, or related resources;
- schema/database constraints for atomic uniqueness and integrity.

Create a decision table covering valid and invalid combinations. Include contradictory fields, fields that are conditionally forbidden, and boundary values. Reject unknown fields when the current external policy requires it; otherwise document that they are ignored and verify the behavior.

Return one stable, actionable error per violated contract. Do not silently discard contradictory caller intent unless the packet explicitly approves normalization.

## 6. Shape the response

Follow the current external envelope only after verifying its runtime form. Keep the endpoint payload inside that envelope stable and deliberately grouped.

Design from the caller's next decision:

- return the created/updated resource identity and meaningful state;
- group related metrics or lifecycle data under clear names;
- include pagination metadata with list data;
- distinguish calculated, estimated, pending, partial, and final values;
- expose timestamps in ISO 8601 and state timezone assumptions;
- use consistent identifier and relationship representations;
- choose one policy for optional output: omit or return `null`, then document it;
- return empty lists as arrays, not alternate object/null shapes;
- preserve deterministic ordering or document that none is guaranteed.

### Keep one canonical representation per resource concept

A public resource concept has exactly one named representation per tier — typically a compact summary tier for lists and embedding, and a detail tier for the resource's own endpoints. Each tier is one DTO plus one pure mapper, defined once under the external surface and reused by every endpoint that returns the resource.

When a response embeds another resource (badges inside a user, plans inside a subscription), compose the embedded resource's canonical summary representation through its mapper. Never hand-pick the embedded resource's fields inline: two endpoints shaping the same concept independently will drift in naming, grouping, and null semantics.

Before designing a response, inventory the external surface for existing representations of every resource concept the response returns or embeds — including concepts that do not have their own endpoint yet. Reuse the tier that fits; if none fits, either evolve the canonical tier (the change appears everywhere it is used — check every consumer) or introduce a new named tier with a recorded decision. An endpoint that has no badges API yet still defines `BadgeSummary` as a canonical, reusable representation, so the future badges port composes it instead of inventing a second shape.

Build the response through an explicit allowlisted DTO/mapper. Verify that the runtime serializer actually applies it. Swagger `type` metadata alone does not filter returned objects.

Do not return raw database documents, internal exceptions, stack traces, opaque provider responses, or fields merely because the source endpoint returned them.

## 7. Design errors

List errors by scenario rather than status code alone. Define:

- HTTP status;
- stable machine-readable error code;
- human-readable message and whether callers may display it;
- field/path when applicable;
- retryability;
- whether the response intentionally hides resource existence;
- example matching the real runtime envelope.

Use distinctions consistently:

- `400` for malformed/shape/contract input;
- `401` for missing or invalid authentication;
- `403` for authenticated but disallowed operations when disclosure is safe;
- `404` for missing resources or ownership-hiding semantics;
- `409` for state/uniqueness conflicts;
- `422` for semantic input the server understands but cannot process under domain rules, if consistent with the current surface;
- `429` for rate/quota limits with retry guidance;
- `5xx` only for server failures, without leaking internals.

Match the repository's established error policy when it is intentional. Record any necessary compatibility deviation.

## 8. Address security and retries

Specify authentication, API-key scope, tenant/host binding, permission, ownership, rate limit, and exposure separately. Authentication does not prove ownership.

For mutations, decide:

- whether the operation is naturally idempotent;
- whether to accept an idempotency key;
- what happens when the same key has a different body;
- duplicate submission behavior without a key;
- transaction/rollback behavior;
- safe retry guidance after timeout or partial external failure;
- concurrency behavior for stale updates or uniqueness races.

Prefer opaque, tenant-owned asset IDs issued by a controlled upload flow over arbitrary remote URLs. When remote URLs are a real requirement, define allowed schemes/hosts, DNS and private-address policy, redirect handling, fetch-time revalidation, timeouts, byte limits, content-type verification, and per-request item limits. Validation only at request time is insufficient when a later worker performs the fetch.

Avoid user/resource enumeration through different timing or error messages when the source policy hides existence.

## 9. Handle compatibility and versioning

Classify a proposed change as:

- behavior-preserving representation design for a new endpoint;
- backward-compatible addition;
- behavior change requiring explicit approval;
- breaking public-contract change requiring the repository's versioning strategy.

Do not create a new version merely to avoid making a decision. Do not reuse an existing operation ID for a semantically different contract. Check generated clients and docs when renaming fields or operation IDs.

## 10. Run the consumer simulation

Write and inspect:

1. one minimal valid cURL/request and response;
2. one important conditional/optional request and response;
3. one invalid combination and exact error;
4. one retry or duplicate-request example for risky mutations;
5. one list pagination example when applicable.

Ask:

- Can a developer choose the endpoint without knowing internal route names?
- Could an agent consuming only the generated OpenAPI document — with no dashboard, no intuition, no support channel — build a correct request and interpret every response field?
- Can they build the request without reading frontend code?
- Can generated types represent only valid states where practical?
- Can they tell which defaults the server applied?
- Can they distinguish retryable from permanent failures?
- Does the response contain exactly what their next step needs?
- Would a field or error reveal another tenant's data?

Redesign before implementation when any answer is no.
