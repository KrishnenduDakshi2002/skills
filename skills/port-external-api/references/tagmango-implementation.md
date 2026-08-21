# TagMango External API Implementation

## Contents

1. Read the repository correctly
2. Know the surfaces
3. Navigate the current external framework
4. Select the implementation boundary
5. Implement validation and mapping
6. Wire documentation and modules
7. Run implementation checks and hand off

## 1. Read the repository correctly

In `tagmango-backend-monorepo`, read these before editing:

- `AGENTS.md`;
- `BEST_PRACTICES.md`;
- `graphify-out/GRAPH_REPORT.md` when present, then compare its recorded commit with `git rev-parse HEAD` before relying on graph communities;
- the working-tree status and diff.

Treat `BEST_PRACTICES.md` as the target for every touched file even when nearby external modules contain legacy debt. Do not copy casts, shallow wrappers, raw response spreads, or mixed responsibilities merely because an older external endpoint does so.

Pin the source and target branch before editing. Feature ports can depend on services or schemas present on `testing` but absent from `main`; verify prerequisites instead of assuming a clean cherry-pick.

## 2. Know the surfaces

Do not conflate these surfaces:

- `apps/api`: legacy API routes, validators, controllers, services, models, side effects, and historical behavior.
- `apps/core-api/src/api-modules/<feature>` plus shared/libs: current internal/core behavior.
- `apps/core-api/src/api-modules/external`: consumer-facing external APIs targeted by this skill.
- integration APIs generated separately under `apps/core-api/src/webhook-docs/integration-apis.generator.ts`: a different auth and documentation surface.
- `tagmango-web-platform`: designated legacy frontend evidence for gates, defaults, cross-field validation, and payload assembly.

When more than one frontend checkout exists, use the one explicitly named by the user and record its commit. Do not combine a clean legacy snapshot with a newer worktree silently.

## 3. Navigate the current external framework

Inspect these current seams rather than assuming their behavior:

- `apps/core-api/src/api-modules/external/external.module.ts` for module registration;
- `apps/core-api/src/api-modules/external/base.controller.ts` for shared headers, rate limiting, and guard metadata;
- `apps/core-api/src/utils/decorator/genericApi.decorator.ts` for `ExternalApi` and documentation behavior;
- `apps/core-api/src/api-modules/external/external-api-operation-ids.ts` for stable operation IDs;
- `apps/core-api/src/shared/middleware/externalAuth.middleware.ts` for API-key, host, and tenant binding;
- `apps/core-api/src/swagger/external-api-document.ts` and `apps/core-api/src/main.ts` for generated docs, envelope descriptions, prefixes, and URI versioning — `buildExternalApiDocumentOptions` is also the tag registry: every tag a controller uses must be `.addTag(...)`-registered there;
- response and DTO interceptors/services for the actual runtime envelope and projection behavior;
- the nearest external controller, DTO, mapper, module, service, and integration tests for current conventions.

The controller path is only a fragment. Resolve the actual path after the global `api` prefix and URI version. Confirm it from the generated OpenAPI document.

Add every new operation ID to the central registry. Verify uniqueness in the generated document, not only in the TypeScript object.

Do not assume `@ExternalApi({ doc: { ... type } })` transforms runtime output. Trace active interceptors and use an explicit response-mapping seam.

Do not assume the overview prose in Swagger matches the runtime response envelope. Compare docs, interceptor/service code, and a real integration response; fix in-scope drift or report it as a blocker.

## 4. Build the shared implementation boundary

Require this shape for every new port:

```text
legacy route during transition ----\
current/future core controller -----+-> libs/services canonical use case
external controller ----------------/       -> libs/repository
        |                                    -> provider/queue/file adapters
        -> explicit external mapper / DTO
```

Place new or extracted business logic in `libs/services/src/lib/<domain>/`. Place new repositories, repository interfaces, and query/pipeline mechanics in `libs/repository/src/repositories/<domain>/`. Export them through the established library indexes and wire them through the current dependency-injection modules.

Do not introduce new repositories under `apps/core-api/src/shared/repository/` or business services under an app module. Existing app-local code is source material to characterize and extract, not the destination architecture for a port.

The canonical use case is defined by a business capability, not by any one controller. It must contain the complete source-backed behavior for the scoped legacy capability. If a legacy handler mixes unrelated capabilities, decompose it and record the boundary; do not turn it into one giant "generic" service.

Readability bar: an engineer who has never opened the legacy controller must be able to understand the shared use case from its code plus the packet — the legacy file is not documentation. Where a preserved quirk looks intentionally wrong, add one comment stating the business reason, not its legacy origin.

Current or future core and external controllers should parse their own validated DTOs, authenticate and bind transport context, call the same meaningful shared use case, and map the domain result into their own response contracts. Pass actor/tenant context into the use case so shared policies enforce business authorization consistently. When an equivalent core route already exists, rewire it to the canonical shared use case as part of the port and prove that its observable contract remains compatible. When no equivalent core route exists, the shared implementation must still be complete enough that adding one later requires only authentication, DTOs, mapping, and controller/module wiring.

The shared service should own business decisions, named cross-field policies, transactions, state transitions, and side-effect orchestration. Define transport-neutral input, result, actor/tenant context, and domain-error types; do not import an external/core request DTO, HTTP exception, Swagger type, or response envelope into `libs/services`. Do not branch on a transport label such as `external` or `core`; represent genuine permission or capability differences through domain context and injected policies.

Repositories should own typed persistence/query mechanics, not business decisions. Return typed domain/persistence data rather than an external or core response DTO. Reuse `BaseRepository` operations and current library repositories before adding methods. Add a custom method only for meaningful query, atomicity, invariant-default, or domain-mapping behavior; do not wrap a base method solely to rename it.

Keep provider/queue/file clients behind injectable service dependencies so the capability remains reusable and independently observable by the later testing workflow. Keep public exposure policy in an explicit external mapper/DTO under the external API surface; a shared service result may contain domain data that one transport intentionally omits.

Define each canonical public representation (summary and detail tiers) once, in the owning resource concept's module under the external surface, and export it for composition. An endpoint that embeds another concept imports that concept's summary DTO and mapper rather than shaping its fields locally — even when the embedded concept has no standalone endpoint yet. `libs/services` results stay domain-shaped; representation tiers are an external-surface concern. An external-only request restriction must stay in the external adapter unless it is a real domain invariant that core must also enforce.

An external adapter/facade earns its existence only when it maps a public contract, applies external-only policy, or coordinates a meaningful boundary. Do not add a service that merely forwards one method.

### Prove the pattern before building it (P-001–P-010)

"Check existing patterns" means inspecting recent intentional external ports — not merely nearby files, which may carry legacy debt. Resolve each packet conformity row against a pinned exemplar before implementing that concern:

- **Validation and transformation (P-001):** when a DTO decorator transforms values (e.g., ObjectId arrays), the DTO declares the transformed type (`Types.ObjectId[]`) and controllers never transform again; reuse shared validators instead of endpoint-local pipes.
- **Representations (P-002):** returned or embedded resources compose the canonical summary/detail DTOs (see §4 representation rules); derive tiers from existing DTOs rather than restating fields.
- **Envelope and serialization (P-003):** Swagger declares the result DTO directly; the global layer owns the runtime envelope — do not re-wrap or re-document it per endpoint.
- **Errors (P-004):** reuse the shared error registry and definition helpers (`AppErrorMap`, `getErrDefinition(...)`) and the single established controller mapping boundary.
- **Dependency injection (P-005):** `LibServicesModule` and `LibRepositoriesModule` own shared construction and exports; feature modules consume, never reconstruct.
- **Clients and shared state (P-006):** cache reuse means keys, TTL units, and serialization format — not just a matching method signature; reuse shared Redis/provider/queue/file clients and preserve their conventions.
- **Schemas (P-007):** schema ownership is architectural — repository registrations use the established schema library (`legacy-schemas`); a missing schema is migrated with fidelity (fields, indexes, timestamps, model identity), never redefined ad hoc.
- **Type derivation (P-008):** derive projections from existing domain/persistence types with `Pick`/`Omit` instead of restating fields that will drift.
- **Terminology (P-009):** public naming follows product terminology (e.g., `mangoes`), regardless of legacy storage names; storage terminology survives only inside persistence mechanics.
- **Limits as policy (P-010):** numeric limits, defaults, and intervals are policies, not constants sprinkled through decorators — one reusable owner with a semantic name, units, and rationale.

A new wrapper, adapter, parser, pipe, interface, or factory is presumed unnecessary until repository inspection proves no existing primitive covers the concern; record the proof in the P-### row.

The gate points both ways: you are building the exemplar the next port will pin. Every primitive this port creates — policy, representation tier, repository method, error definition — goes to the shared module or registry that owns its concern, named for the domain rather than the endpoint, so the next port's P-### inspection adopts it unchanged instead of duplicating it.

### Name every new file in kebab case

Every file created by the port must use a lowercase kebab-case descriptive base. Keep established dot-delimited role suffixes, so names such as `create-mango.service.ts`, `create-mango-request.dto.ts`, `external-mango.controller.ts`, and `mango.repository.ts` comply. A conventional single lowercase token such as `index.ts` also complies. Do not introduce snake_case, camelCase, PascalCase, spaces, or ad hoc abbreviations in new filenames.

Do not rename an untouched legacy file merely to satisfy this rule. A repository-, framework-, or generator-mandated filename may be retained only when the exact constraint and path are recorded as an exception in the port packet. Before handoff, inspect every added path in the scoped diff and every scoped untracked path; record the result in the `New-file naming audit` implementation check.

When porting from `apps/api`:

1. Characterize observable behavior before restructuring.
2. Identify the semantic decisions and side-effect ordering embedded in the legacy function.
3. Reuse or create the canonical typed domain service in `libs/services` and persistence in `libs/repository`, covering the complete scoped capability rather than only the public subset.
4. Keep transport quirks out of the domain model.
5. Route the new external behavior and every equivalent current core/internal caller through the canonical implementation.
6. Complete the `M-###` legacy/shared/external/core mapping. If a future core replacement still needs domain or repository work, record the blocker and stop instead of calling the port migration-ready.

When porting from core-api, reuse the canonical service directly when it already owns the full behavior. Do not call an internal controller or make an HTTP loopback.

### Core migration readiness gate

Treat a port as core-migration-ready only when all are true for the scoped capability:

- every legacy `B-###` rule, validation, persistence effect, state transition, domain error, and side effect maps to shared code or an approved exclusion;
- external omissions are explicit adapter/exposure decisions, not missing shared behavior;
- shared commands/results/errors have no controller DTO, HTTP, Swagger, envelope, or transport-label dependency;
- repositories expose the typed queries and atomic operations the capability needs;
- an existing core caller uses the shared use case, or the future core mapping shows only authentication, DTO/mapping, and wiring work;
- implementation traceability accounts for the complete capability independently of the external controller and exposes stable seams for later testing.

Do not create speculative core endpoints or catch-all abstractions merely to satisfy this gate. If the port intentionally covers only part of the capability required to replace a legacy route, say so and keep readiness blocked until the missing capability slices are implemented and mapped.

## 5. Implement validation and mapping

Use validation layers deliberately:

- DTO decorators or schema validation for scalar shape, format, and simple conditional structure;
- discriminated DTOs/unions when valid fields differ by operation mode;
- a named pure policy/validator for cross-field business combinations;
- the domain service for actor, tenant, entitlement, related-resource, currency, uniqueness, and state-dependent rules;
- database constraints/transactions for race-safe integrity.

The global `ValidationPipe` currently uses whitelist/transform behavior; determine whether unknown fields are stripped or rejected for the target contract. If strict rejection is required, implement and document it intentionally rather than assuming it.

Preserve the difference between create defaults and patch semantics. Never use truthiness for fields where `false`, `0`, empty, and absent differ. Avoid `value || default` when zero/false is valid.

Map public requests into a named domain input. Map domain results into a dedicated external response DTO using an explicit allowlist. Prefer class-transformer or a focused pure mapper consistent with current standards. Record the exact allowlist and any runtime serialization uncertainty for the later testing workflow.

Use stable domain errors and one HTTP mapping boundary. Document every externally reachable error code. Do not duplicate the same `try/catch` mapping across controller methods when a current exception filter/mapper can own it.

## 6. Wire documentation and modules

For each endpoint:

- register the controller/module in the external module tree;
- apply external auth middleware/guards consistently;
- use the central operation ID registry;
- when the port introduces a new external module or tag, register the tag with a consumer-facing description in `buildExternalApiDocumentOptions` (`apps/core-api/src/swagger/external-api-document.ts`) — a controller tag missing from this registry breaks documentation construction;
- document summaries, detailed semantics, defaults, restrictions, errors, and realistic examples;
- annotate every request/response property with correct types and formats;
- ensure static routes cannot be shadowed by dynamic parameters;
- verify response status and no-content/file-stream behavior through the runtime response interceptor;
- confirm the endpoint appears only in the intended OpenAPI surface.

Keep documentation aligned with the packet. Do not paste an internal function description or frontend labels as the API contract.

## 7. Run implementation checks and hand off

Inspect configured Nx targets before choosing commands:

```sh
npx nx show project core-api
```

Do not create or modify tests and do not run test suites in this workflow. Existing tests may be read as source evidence only. Run the repository's proportionate non-test targets such as formatting, lint, typecheck, and build. If a configured command necessarily includes tests, skip it and record the limitation for the separate testing workflow.

Generate the external OpenAPI document with the repository's preview/generation script using a temporary output path. Inspect the YAML/JSON for:

- actual path and method;
- operation ID;
- every controller tag present in the document's registered tag list with its description;
- security and required headers;
- parameter location and encoding;
- request requiredness and conditional rules;
- response schema/envelope;
- error scenarios and examples;
- duplicate or missing operations;
- accidental internal fields.

Do not turn this phase into runtime or behavioral certification. Record the Nest validation, auth/tenant, response-mapping, and global-interceptor seams that the later testing workflow must exercise, together with any runtime assumptions that remain unverified.

Run `git diff --check`, inspect every added and scoped untracked filename, and review the final target diff against the port packet. The `New-file naming audit` must be `PASS`; list any justified mandated exceptions in its evidence cell, or write `None`. Complete the `H-###` implementation traceability and implementation-check results, mark the packet `IMPLEMENTED`, and leave changes unstaged unless the user explicitly asks to stage or commit.
