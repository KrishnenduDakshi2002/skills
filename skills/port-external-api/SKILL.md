---
name: port-external-api
description: Start from a linked GitHub issue, grill and resolve the consumer-facing contract, then research, design, implement, document, and hand off a TagMango external API port from apps/api or apps/core-api. Preserve business behavior, promote confirmed frontend rules into backend validation, place capability-complete business logic in libs/services and data access in libs/repository, and make external plus current or future core controllers thin adapters over the same use case so core-api can later replace legacy routes without reimplementing domain logic. Use when asked to port, migrate, expose, create, or redesign an external endpoint or prepare its parity and contract packet. Do not create or modify test cases as part of this skill; preserve implementation traceability for a separate testing workflow. Do not use for review-only requests; use audit-external-api-port.
---

# Port External API

Port behavior, not legacy representation. Preserve the complete business decision path while designing a deliberate public contract that an unfamiliar integrator can understand and use safely.

## Non-negotiable outcomes

Satisfy and document all five outcomes independently:

1. **Behavioral fidelity:** preserve confirmed defaults, eligibility rules, validation, state transitions, persistence, side effects, error cases, ordering, transaction boundaries, and absent/null/false/zero/empty semantics from the authoritative sources.
2. **Public-contract quality:** deliberately design the URL, method, authentication, parameters, request body, response, errors, examples, naming, and documentation for external consumers. Do not expose an internal DTO or database document merely because it already exists.
3. **Shared domain ownership:** place ported business rules and use-case orchestration in `libs/services`; place new typed persistence/query code in `libs/repository`. Keep app modules as transport, authentication, wiring, and contract adapters.
4. **No duplicated capability:** route external plus every equivalent current core/internal API through the same transport-independent shared use case and repositories. Preserve each transport's request/response contract with adapters and mappers.
5. **Future core replacement readiness:** make the shared use case complete for the scoped legacy business capability, even when the external contract intentionally exposes only a subset. A future core replacement may add authentication, DTOs, mapping, and controller wiring, but must not need another business-logic or data-access port.

Promote confirmed business restrictions enforced only by the frontend into backend enforcement. Do not promote UI convenience, stale UI behavior, or accidental legacy behavior without evidence and a recorded decision. Treat "generic" as transport-neutral, capability-complete domain behavior with explicit dependencies—not speculative TypeScript generics, one oversized catch-all service, or configuration for imagined consumers.

## Select the requested stopping point

- Require a GitHub issue for every port. If it is missing or unreadable, request it and keep the packet `BLOCKED`.
- For research or design requests, complete the issue intake, contract grill, and designed `M-###` core-migration mapping, then stop before product-code edits.
- For full port requests, pause for the developer's contract confirmation. Continue only when the packet is `READY` and no material decisions remain open.
- For implementation from an existing approved packet, verify that its source pins and assumptions are still current before editing.
- For review-only requests, remain read-only and use `audit-external-api-port` instead.

## Scale across many endpoints

For a batch, create a lightweight inventory with GitHub issue, operation, source route, target resource, consumer, source pins, shared service/repository dependencies, current/future core mapping, migration readiness, risk, packet path, and status. Group work by domain behavior rather than legacy controller file.

- Research shared authentication, tenant, error, pagination, and domain policies once per pinned source snapshot; cite that evidence from each operation packet.
- Keep one packet and implementation result per operation even when several endpoints share an implementation PR.
- Order shared domain extraction before endpoint wiring, and foundational writes before dependent reads/actions.
- Parallelize independent read-only discovery lanes when the active agent supports it, then make one owner reconcile evidence and decisions. Do not let parallel agents implement competing versions of the same domain rule.
- Limit work in progress: finish the design gate for an operation before implementing it, and finish the implementation handoff before starting the next similar endpoint.
- Promote only independently audited conventions into reusable templates. Do not multiply an unreviewed first port across the batch.

## Workflow

### 1. Ingest the GitHub issue and establish authority

Read repository instructions, coding standards, architecture maps, and the working-tree diff before searching broadly or editing. Preserve unrelated changes.

Read [issue-contract-grill.md](references/issue-contract-grill.md). Read the linked GitHub issue and its current comments before broad source research. Treat it as the initial scope and product brief; verify its code and frontend pointers rather than treating them as runtime truth.

Resolve and record:

- the exact operation and consumer use case;
- every `I-###` issue requirement, source pointer, frontend pointer, proposed contract, accepted decision, and exclusion;
- the target branch and target external-API surface;
- every source repository, checkout, branch, and commit;
- whether `apps/api`, `apps/core-api`, or both contain authoritative behavior;
- the user-designated `tagmango-web-platform` checkout for frontend gates, validation, defaults, and payload assembly;
- the nearest existing external endpoints whose conventions are current and intentional.

If multiple checkouts or branches exist, do not choose by name alone. Inspect their state and ask only when the authority cannot be established from repository or issue evidence.

Read [behavior-parity.md](references/behavior-parity.md) before tracing the source. For TagMango work, also read [tagmango-implementation.md](references/tagmango-implementation.md) before selecting target files.

### 2. Create the durable port packet

Use the repository's established scratch/spec location. Otherwise default to `.scratch/external-api-ports/<operation-slug>/port-packet.md`; keep it uncommitted unless the user explicitly requests publication.

Initialize from the bundled template:

```sh
python3 <skill-directory>/scripts/port_packet.py init \
  --operation <operation-slug> \
  --source <legacy|core-api|both> \
  --issue <github-issue-url> \
  --output <packet-path>
```

The script copies [port-packet.md](assets/port-packet.md). Maintain the packet while researching and implementing; do not reconstruct it at the end from memory.

### 3. Reconstruct the complete behavior

Trace every reachable layer, not only the controller:

- route registration, middleware, authentication, tenant/host resolution, permissions, and ownership;
- request validation and normalization;
- controller, service, repository/query, schema defaults, hooks, and shared utilities;
- feature flags, entitlements, quotas, idempotency, concurrency, transactions, external calls, queues, notifications, analytics, and other side effects;
- frontend field initialization, conditional visibility, gates, cross-field validation, payload assembly, omitted/deleted fields, and success/failure handling;
- existing tests, production-facing documentation, and sibling callers.

Trace every caller-controlled URL, file reference, webhook destination, redirect, or provider identifier through downstream consumers. A value that looks like harmless metadata at the API boundary may become a server-side fetch, queue job, or privileged provider operation later.

Work breadth-first, then risk-first: map all layers and fields once, then deepen public fields plus every cross-field rule, permission, persistence effect, and side effect in the scoped canonical capability. Research converges when every public input/output and every material capability behavior has pinned evidence or a `D-###` decision; do not keep expanding into unrelated domain behavior.

Record source evidence as `repository@commit:path:line` and assign every confirmed rule a stable `B-###` identifier. Distinguish verified facts from hypotheses.

Classify frontend observations as one of:

- business invariant to enforce on the backend;
- product/entitlement gate to enforce on the backend;
- normalization or default required for parity;
- UI-only convenience that must not become an API restriction;
- suspected bug or ambiguous behavior requiring a decision.

### 4. Draft the external contract from the consumer inward

Read [public-contract-design.md](references/public-contract-design.md). Design the wire contract before choosing implementation shapes.

Specify the actual versioned wire URL, HTTP method, auth and tenant context, idempotency/retry behavior, path/query/header/body fields, response groups, error codes, pagination, units, timestamp formats, nullability, defaults, examples, and compatibility strategy.

For every request and response field, record:

- public name and type;
- precise meaning, units/format, requiredness, default, and absent/null/empty behavior;
- source/domain mapping;
- why an external consumer needs it;
- sensitivity and exposure decision;
- applicable `B-###` and `V-###` rules.

Add an `S-###` threat/abuse entry for each caller-controlled value that reaches a fetcher, queue, file/media processor, redirect, provider, bulk query, or cross-tenant lookup. Record the implemented controls and the risk that a later testing workflow must verify, not only a proposed validation decorator.

Draft three consumer examples before coding: the smallest valid request, one important optional combination, and one invalid combination with its exact error. If these examples require internal knowledge to interpret, redesign the contract.

### 5. Grill and confirm the contract decisions

Use the bounded `grill-with-docs` composition in [issue-contract-grill.md](references/issue-contract-grill.md). Discover facts first, construct a dependency-aware frontier from the draft, and ask all currently independent questions with evidence, realistic options, a recommendation, and concrete request/response examples.

When the host supports composing installed skills, load `grill-with-docs` for this bounded phase; invoking `port-external-api` grants the required consent to be grilled, so do not require the developer to invoke both skills. Use the bundled reference as the complete fallback when composition is unavailable.

Resolve or justify every `G-###` dimension: operation/resource boundary, complete URL and method, parameter placement, request fields, response shape/exposure, pagination and collection semantics, errors/retries/versioning, and capability-complete shared ownership for external plus current or future core adapters. Preserve settled issue decisions, but surface contradictions instead of silently overriding them.

Before presenting each question round, checkpoint the issue intake, source pins, discovered behavior, draft contract options, and shared architecture plan in the packet; set its status to `BLOCKED`. Do not ask from private working notes while the durable packet still contains untouched template rows.

Do not implement after merely proposing a reasonable contract. Wait for the developer to confirm the frontier is empty, record every resolution, and keep the packet `BLOCKED` while a material question remains.

### 6. Resolve remaining behavioral decisions

Investigate discoverable facts instead of asking the developer. In addition to the required public-contract grill, ask when two plausible answers would materially change business behavior, security, data exposure, or implementation scope.

Use this format:

```text
Q<D-###> — <decision>
Evidence: <what each source currently does, with anchors>
Why unresolved: <the contradiction or missing product rule>
Recommended: <one option and rationale>
Impact: <wire or behavior consequence of each plausible option>
```

Batch only independent questions. Record the answer in the packet. Set the packet to `BLOCKED` and stop before product-code edits when any `G-###` or material `D-###` decision remains open. Do not label a missing fact as a product decision.

### 7. Implement one shared semantic model

Read [tagmango-implementation.md](references/tagmango-implementation.md) before editing.

- Reuse an existing canonical domain service in `libs/services` when it already owns the behavior.
- Put every new or extracted business use case in `libs/services/src/lib/<domain>/` and every new typed data-access implementation in `libs/repository/src/repositories/<domain>/`, following their public exports and dependency wiring conventions.
- Define the canonical capability boundary independently of the legacy route and the public endpoint. When one legacy handler bundles several capabilities, separate them deliberately; for the capability in scope, capture every source-backed rule, state transition, persistence effect, and side effect in the shared implementation.
- When behavior exists only in an app, characterize it first, then extract the complete scoped decision model into these shared libraries. Do not call a legacy/internal controller, copy its architecture wholesale, or add new app-local business/repository code.
- Model transport-neutral commands, results, domain errors, actor/tenant context, and injected policies. Do not branch on `external` versus `core` inside the domain service; express real permission or capability differences through domain inputs and policies.
- Keep the shared result rich enough for the complete scoped capability. Enforce the narrower external request and exposure contract in its DTOs and mapper rather than deleting core-relevant behavior or fields from the domain model.
- When a matching core API exists, rewire its controller to the shared use case in the same port. Keep core and external contract adapters separate, preserve both observable contracts in their mappers, and record the implementation mapping. If safe rewiring is materially blocked, stop and record a decision instead of duplicating logic.
- When no matching core API exists yet, complete the packet's `M-###` mapping and show from source and implementation traceability that a future core route needs only transport authentication, DTO/mapping, and wiring. If any business rule, repository query, state transition, or side-effect orchestration would still have to be implemented during the core migration, keep core migration readiness `BLOCKED` and do not call the port complete.
- Keep HTTP parsing and authorization in the controller, business rules in the domain service, persistence in repositories, and public response shaping in an explicit mapper/DTO boundary.
- Put confirmed cross-field rules in a named validator or policy with a stable seam for the later testing workflow. Keep database-dependent rules in the service/domain layer.
- Use explicit allowlists for public responses. Never spread a database document or internal DTO into an external response.
- Preserve side-effect order, retry safety, atomicity, and legacy failure semantics unless the packet records an approved change.
- Follow current repository standards for every touched file even when the source is legacy debt.

Implement in narrow behavior slices. Do not stage, commit, push, publish docs, or mutate trackers unless the user explicitly requests that action.

### 8. Complete implementation traceability and defer testing

Do not create or modify test files and do not run test suites under this skill. Do not design or execute a test-certification phase; a separate testing skill will own that process. Existing tests may be read as source evidence during research, but they are not changed or executed here.

Map every `B-###`, `V-###`, `G-###`, `M-###`, and `S-###` rule to an `H-###` implementation-handoff row containing:

- the exact implemented files and symbols;
- how the rule is represented in the service, repository, adapter, mapper, DTO, or documentation;
- any behavior that remains runtime-unverified;
- the source evidence and risk context the later testing workflow will need.

Run proportionate non-test implementation checks such as formatting, lint, typecheck, build, generated OpenAPI inspection, and final diff/architecture review. Choose commands that do not invoke test targets; when such a command is unavailable, record the limitation instead of broadening this workflow.

Set the packet to `IMPLEMENTED`, not `VERIFIED`. State clearly that behavioral and runtime certification is deferred. Implementation traceability demonstrates where the intended behavior was placed; it does not prove that behavior through execution.

### 9. Validate the implementation handoff

Validate the packet at each gate:

```sh
python3 <skill-directory>/scripts/port_packet.py check <packet-path> --stage design
python3 <skill-directory>/scripts/port_packet.py check <packet-path> --stage implementation
```

Stop at `IMPLEMENTED`. Preserve the packet, source pins, ledgers, consumer examples, implementation mapping, check results, and unresolved runtime risks so a later testing or audit skill can continue without reconstructing the port from scratch. Do not invoke those later workflows automatically.

## Handoff

Report:

- endpoint and consumer goal;
- GitHub issue URL, captured requirements, and resolved grill decisions;
- authoritative source pins;
- packet path and status;
- public contract summary;
- preserved behavior and newly backend-enforced frontend rules;
- implementation files changed;
- shared service/repository paths and every core/external consumer rewired to them;
- canonical capability scope, `M-###` coverage, core migration readiness, and the exact work a future core adapter still requires;
- non-test implementation checks and exact outcomes;
- explicit deferred-testing status and runtime risks handed to the later workflow;
- unresolved decisions, known deviations, and residual risks.

Separate confirmed parity from inferred or unverified behavior. Never describe a partial port as complete.
