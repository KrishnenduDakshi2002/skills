# External API Owner Review Checklist

The distilled rulebook the pipeline skills (`port-external-api`, `audit-external-api-port`, `test-external-api-port`, `document-external-api`) enforce, applied as a conformance review. Each numbered dimension is walked against the diff; a finding cites its item as `§N`.

## Contents

1. Endpoint and URL
2. Request placement and field quality
3. One public vocabulary — request↔response symmetry
4. Canonical representation tiers
5. Exposure and serialization
6. Validation by layer
7. Shared-capability architecture
8. Reuse and primitives
9. Legacy behavior signals
10. Errors
11. Documentation bar
12. Naming and hygiene
13. Process artifacts

## 1. Endpoint and URL

- The complete wire URL (after global prefix and URI versioning) is confirmed from the generated document, not a controller fragment.
- Plural kebab-case public domain nouns; path segments for identity/containment, query for filtering/sorting/pagination/presentation, body for mutation input, headers for protocol context only.
- HTTP method matches safety/idempotency semantics; action subresources only for non-CRUD operations, in the existing convention.
- No dynamic `/:id` route shadowing a static sibling; operation ID from the central registry (`external-api-operation-ids.ts`), unique in the generated document.
- Controller extends `BaseExternalController` and the module is registered in the external module tree; every tag the controller uses is registered with a description in `buildExternalApiDocumentOptions` — an unregistered tag breaks documentation construction (`P1`).

## 2. Request placement and field quality

- No unbounded list endpoint: pagination extends the shared `PaginationDto`, with per-endpoint bounds `override`-declared from a named policy object in `libs/utilities` (e.g. `TransactionQueryPolicy`), never bare literals.
- Path params reuse the shared ID param DTOs (`CourseIdDto` etc.) carrying `@IsTransformedObjectId`; controllers never re-parse.
- Every public field has an expressive consumer-facing name (unit in the name or documented: `durationSeconds`), a concrete format, requiredness truth, defaults with an owner, and defined absent/`null`/empty/false/zero semantics. No internal abbreviations, storage names, or Mongo/Mongoose leakage.
- Optional public filters use `@IsOptionalNotNull()` so an explicit `null` is rejected, not silently treated as absent.
- Mode-dependent shapes use discriminated DTOs/unions, not a loose bag of optionals whose validity lives in prose.

## 3. One public vocabulary — request↔response symmetry

What a caller sends is what they get back.

- Write-body field names, grouping, and nesting mirror the representation the API returns for the same resource, so a write-then-read round-trips on identical paths: the `settings` group accepted on create is the `settings` group every read returns.
- Write DTOs derive from the canonical representation — create body from the detail tier, update body as a partial of create (`ExtUpdateCourseBodyDto extends PartialType(ExtCreateCourseBodyDto)`) — never an independently designed input vocabulary.
- An internal field renamed for the public surface is renamed once, in the mapper, identically in both directions; a caller must never send a value under one name and read it back under another.
- Filter and sort parameters name the response field they operate on, and the description states the linkage (`signedUpAfter`/`signedUpBefore` → the response's `signedUpAt`).
- A normalized or defaulted input echoes the applied value back under the request field's name (`reportingCurrency` request → top-level `reportingCurrency` response).
- Any in-name/out-name or in-grouping/out-grouping asymmetry without a recorded decision is `P1`.

## 4. Canonical representation tiers

Every public resource concept has exactly two canonical tiers, defined once and derived, never restated:

```text
<Resource>Dto                  ← full DB shape (shared/dto/examples/<resource>.dto.ts)
   └─ Ext<Resource>Dto             ← verbose tier: PickType allowlist + renamed/grouped fields
        └─ Ext<Resource>SummaryDto     ← embedded tier: PickType of the verbose tier
```

- The verbose tier is *the* full publicly exposable field set; the summary tier is *the* amount of the resource every embedding exposes. Shared embedded field lists live in `libs/services/src/lib/embedded-summary.types.ts` (`mangoSummaryFields`, `badgeSummaryFields`).
- An endpoint that embeds another concept imports that concept's `Ext<Resource>SummaryDto` and mapper — never an inline field selection, even when the embedded concept has no standalone endpoint yet.
- A specialized shape derives from a canonical tier (`PickType`/`OmitType` plus targeted re-expansion, as `ExtCourseDetailsDto` does) — a hand-restated class whose fields can drift is `P2`; a second independent public shape for an owned concept is `P1`.
- Diff every returned or embedded shape against the concept's canonical representation elsewhere on the surface; divergence in fields, names, or null semantics without a recorded tier decision is a finding.

## 5. Exposure and serialization

Exposure is an allowlist exercise; "already on the model" is never a reason to publish a field.

- `@ExternalApi` does **not** attach `RespondWithDto`: no `plainToInstance` allowlisting runs on external routes, `@Expose()` on `Ext*` DTOs is inert there, and the feature's `*.mapper.ts` is the only enforcement. Trace what the service actually returns to the interceptor.
- A service handing repository documents straight through (a `select:` projection is not an allowlist the DTO enforces) is `P0` when it widens the wire beyond the documented shape.
- Every response field traces to a stable source and a consumer use case; no raw documents, populated internal shapes, provider payloads, secrets, internal flags, or fields "for completeness".
- Tenant/host binding, API-key scope, ownership, and non-enumeration are checked separately from authentication; caller-controlled URLs/assets/callbacks are traced to their downstream consumer.

## 6. Validation by layer

- DTO decorators for scalar shape/format; discriminated DTOs for mode-dependent shapes; named pure policies for cross-field rules; the domain service for actor/tenant/entitlement/ownership/state/uniqueness; database constraints for race-safe integrity.
- Documentation without enforcement is a defect; a DTO decorator cannot enforce a rule needing authenticated or database context — check the layer, not the presence.
- `false`, `0`, empty, and absent are distinct where the domain distinguishes them; no `value || default` over valid falsy values; create defaults and patch semantics stay distinct.
- Numeric limits, defaults, and intervals come from one named policy owner with units and rationale, shared between validator and docs.

## 7. Shared-capability architecture

```text
legacy route during transition ----\
current/future core controller -----+-> libs/services canonical use case
external controller ----------------/       -> libs/repository
        |                                    -> provider/queue/file adapters
        -> explicit external mapper / DTO
```

- Business rules, transactions, and side-effect orchestration in `libs/services/src/lib/<domain>/`; typed persistence in `libs/repository/src/repositories/<domain>/`; controllers parse, authenticate, delegate, and map — nothing else.
- No new app-local business services or repositories; no legacy-controller calls or HTTP loopbacks; no `external`-versus-`core` branching in domain code; no HTTP/Swagger/envelope types imported into `libs/services`.
- Repository methods return typed domain/persistence data, never a public DTO or projection.
- An equivalent core route left on a duplicated decision path, or a shared service implementing only the external subset of the capability, is `P1`.

## 8. Reuse and primitives

- A new wrapper, adapter, parser, pipe, interface, or factory is presumed unnecessary until inspection shows no existing primitive covers the concern — shared validators, DTO transformers, error registry (`AppErrorMap`, `getErrDefinition`), DI modules (`LibServicesModule`, `LibRepositoriesModule`), clients, schema library (`legacy-schemas`), and `Pick`/`Omit` type derivation come first.
- What the change creates — policies, representation tiers, repository methods, error definitions — lands in the shared module or registry that owns the concern, named for the domain, so the next endpoint adopts it instead of duplicating it. A domain-general primitive buried endpoint-local is `P2`.
- Public naming follows product terminology (`mangoes`), regardless of storage names; storage terminology survives only inside persistence mechanics.

## 9. Legacy behavior signals

When the diff ports or rewires legacy behavior (this review cannot certify parity — it looks for the signals that parity was respected):

- Suspected legacy bugs are preserved and surfaced as recorded decisions, never silently "fixed" or silently kept.
- Defaults, validation strictness, side-effect order, rounding/precision/timezone handling, query filters, and "useless-looking" writes are unchanged unless a decision records the change.
- Frontend-only restrictions promoted to the backend have evidence they are business rules, not UI convenience.
- Any of these changed without a recorded decision, or a legacy port with no packet at all → include `ESCALATE TO FULL AUDIT` in the verdict.

## 10. Errors

- Every reachable failure maps to a status, a stable machine-readable code from the central registry (`getErrDefinition`, never inline literals), a displayable message, and retryability; one controller-level mapping boundary, no duplicated `try/catch` mapping.
- Standard status semantics (400 shape / 401 auth / 403 permission / 404 missing-or-hidden / 409 conflict / 422 semantic / 429 limits); no internal exceptions, stack traces, or enumeration of other tenants' resources.

## 11. Documentation bar

The generated document is everything the consumer gets — increasingly an AI agent.

- Operation summary and structured description (purpose → nuances as observable-behavior bullets → related endpoints); cross-links built with `getExternalApiDocumentationUrl`, never hardcoded.
- Every parameter/property description adds what the name doesn't carry: meaning, format, obtainment (which endpoint produces the value, linked), constraints mirroring actual validators, requiredness truth.
- Filter/sort parameters state which response field they operate on; responses state null/omission policy, ordering (or disclaim it), and empty shapes.
- Examples are realistic platform data telling one coherent story; credentials are placeholders.
- Acid test: could an integrator build the minimal valid request, one optional variation, and predict one invalid combination's error from the generated document alone?

## 12. Naming and hygiene

- Every added file is lowercase kebab-case with established dot-delimited role suffixes (`create-mango.service.ts`, `list-transactions.dto.ts`); no snake_case, camelCase, or PascalCase filenames. Untouched legacy filenames are not flagged.
- DTO classes follow `<Op>BodyDto` / `<Op>QueryDto` / `<Op>ParamDto` / `<Op>ResponseDto` and the `Ext*` prefix for external shapes.
- No unrelated cleanup widening the PR; no commented-out code, no casts or non-null assertions hiding boundary uncertainty.

## 13. Process artifacts

- A new or changed public endpoint with no port packet: `P2` — contract decisions unrecorded and runtime behavior unverified by `test-external-api-port`. State what the pipeline would have produced (grill decisions, ledgers, test evidence) so the finding is actionable, not bureaucratic.
- A packet that exists but contradicts the code: the code wins on "is"; the contradiction is its own finding.
- Breaking changes to an existing public contract (renamed field, changed operation ID, changed semantics) require the repository's versioning strategy — an unversioned break is `P0`/`P1` by blast radius.
