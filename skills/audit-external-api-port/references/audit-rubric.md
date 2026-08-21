# External API Port Audit Rubric

## Contents

1. Evidence quality
2. Behavioral parity
3. Public endpoint and request contract
4. Validation and lifecycle enforcement
5. Response and error contract
6. Security and exposure
7. Architecture and maintainability
8. Tests and documentation
9. Certification bar

## 1. Evidence quality

Require:

- initiating GitHub issue URL, current issue/comment evidence, and traceable `I-###` requirements;
- exact repository, branch, and commit for every authority;
- base-to-head target diff and current working-tree state;
- source anchors for each material behavior;
- frontend evidence for claimed UI-enforced rules;
- runtime/generated-contract evidence for the public surface;
- explicit separation of verified facts, inference, and product decisions.
- resolved or justified `G-001` through `G-008` contract decisions with developer confirmation.
- complete `M-###` legacy/shared/external/core capability mappings and the claimed core migration readiness state.

Block certification when the review mixes checkouts, follows an untrusted plan instead of source, or cannot establish the target diff.

## 2. Behavioral parity

Review the entire decision path:

| Area | Questions |
|---|---|
| Defaults | Are schema, service, and frontend-derived defaults preserved? Does the server expose/appply them intentionally? |
| Gates | Are feature access, tier, permission, quota, status, ownership, and tenant gates preserved? |
| Validation | Are scalar, cross-field, related-resource, and state-dependent rules preserved and backend-enforced? |
| Persistence | Are stored fields, omissions, clearing semantics, timestamps, indexes, and hooks equivalent? |
| Lifecycle | Do create, update, retry, delete/revoke, already-exists, and stale-state paths match? |
| Side effects | Are queues, notifications, analytics, external calls, and quota settlement triggered under the same conditions and order? |
| Failure | Are rollback, partial failure, retryability, and public error classification correct? |
| Values | Are absent, `null`, false, zero, empty string/list/object, order, rounding, timezone, and bytes handled correctly? |

Representation may differ only when the semantic outcome remains the same or an approved decision records the change.

## 3. Public endpoint and request contract

### Endpoint

- Confirm the complete generated URL, including prefix and version.
- Check plural resource naming, kebab-case, hierarchy, method semantics, action modeling, and consistency with intentional external precedents.
- Check dynamic/static route conflicts and operation-ID uniqueness.
- Check safety/idempotency expectations for the chosen HTTP method.

### Request placement

- Path identifies the addressed resource and does not duplicate authenticated context.
- Query expresses filters/search/sort/pagination/view controls, with encoding and limits documented.
- Headers carry protocol context only.
- Body models the command/domain input rather than frontend component state or persistence shape.

### Field quality

For every field, require:

- intuitive public name;
- type and concrete format;
- required/optional/conditional/forbidden status;
- allowed values/range/length/precision/units;
- default and normalization owner;
- absent/null/empty semantics;
- mutability;
- realistic valid example;
- domain mapping and consumer need.

Prefer discriminated shapes where they prevent impossible combinations. Flag loosely optional “bag of fields” contracts that require prose to discover validity.

## 4. Validation and lifecycle enforcement

Create a rule matrix and check:

- every conditionally required field missing;
- every conditionally forbidden field present;
- contradictions across discriminators/settings;
- false/zero values not treated as absent;
- unknown-field behavior;
- array encoding, duplicate IDs, ordering, and maximum sizes;
- actor/host/permission/entitlement/currency/resource state;
- related resource existence and ownership;
- uniqueness and race behavior;
- create versus partial-update semantics;
- delete/revoke/retry idempotency;
- frontend-only business restrictions now enforced by the backend;
- UI conveniences not turned into arbitrary restrictions.

Check enforcement at the correct layer. DTO/schema validation cannot establish database ownership or current entitlement. Pre-checks without atomic database protection may still race.

## 5. Response and error contract

### Response

- Verify the real global envelope and status, not only the documented DTO.
- Verify explicit allowlisting at runtime.
- Trace every field to a stable source and consumer need.
- Check grouping, naming, identifiers, units, timestamp format, null policy, arrays, pagination metadata, and deterministic ordering.
- Check calculated/estimated/pending/partial states are distinguishable.
- Check create/update responses support the consumer's next action.
- Check file, stream, redirect, and 204 paths bypass wrapping only as intended.

### Errors

- Map every reachable failure scenario to status, stable code, message/field, and retryability.
- Compare documented examples with runtime envelope.
- Check uniqueness/state conflicts, semantic validation, auth, permission, not-found/non-enumeration, rate/quota, external dependency, and server failure.
- Flag raw internal exception messages, stack/provider leakage, inconsistent codes, or different errors that enumerate other tenants' resources.

## 6. Security and exposure

Review independently:

- API-key validity and revocation;
- API-key scope and allowed hosts;
- tenant/custom-host binding;
- actor permission/entitlement;
- resource ownership;
- rate and quota policy;
- request size and unbounded lists;
- caller-controlled URLs/assets/callbacks traced through redirects, DNS/IP checks, worker fetches, byte limits, and privileged provider calls;
- response field allowlist;
- logs and errors for secrets/PII;
- duplicate/retry side effects;
- cross-tenant references and populated data;
- mass assignment through spreads or internal DTO reuse.

Treat response exposure as an allowlist exercise. “Already present in the model” is not a reason to publish a field.

## 7. Architecture and maintainability

Require clear ownership:

```text
legacy route during transition ----\
current/future core controller -----+-> libs/services canonical use case -> libs/repository
external controller ----------------/                                  -> provider adapters
        |-> explicit external mapper
```

Require new or extracted business logic under `libs/services/src/lib/<domain>/` and new data access under `libs/repository/src/repositories/<domain>/`. The use case must be complete for the scoped legacy capability even when the external API exposes only a subset. Equivalent current core/internal and external endpoints must call it while keeping their DTOs and response mappers separate.

Audit core replacement readiness explicitly:

- every legacy behavior, validation, persistence effect, state transition, domain error, and side effect in scope maps to the shared implementation or an approved exclusion;
- external-only restrictions and exposure omissions stay in its adapter rather than truncating the shared model;
- shared inputs, results, errors, and policies do not depend on an external/core DTO, HTTP/Swagger/envelope type, or transport-name branch;
- existing core callers are rewired, or the documented future core adapter needs only authentication, DTO/mapping, and wiring;
- service/repository tests cover the complete capability independently of the external route;
- each `M-###` claim has source and test evidence.

If future core implementation still needs new domain or repository behavior, record a `P1` architecture finding and reject the readiness claim. Do not require a speculative core endpoint when none exists; require a complete shared capability and an evidence-backed transport-only mapping.

Inspect every file added in the actual base-to-head diff, plus any scoped untracked file included in a local audit. Its descriptive base must be lowercase kebab case, with established dot-delimited role suffixes permitted: `create-mango.service.ts`, `create-mango-request.dto.ts`, and `mango.repository.ts` comply, as does a conventional single lowercase token such as `index.ts`. Flag snake_case, camelCase, PascalCase, spaces, and unexplained naming exceptions. Do not flag untouched legacy filenames. Accept a repository-, framework-, or generator-mandated exception only when the exact path and constraint are documented in the port packet.

Flag:

- controller business logic or direct DB access;
- internal/legacy controller calls;
- copied legacy function with mixed responsibilities;
- external service that only forwards;
- domain service that shapes one HTTP response;
- repository methods that return an external/core DTO or public projection instead of reusable typed domain/persistence data;
- hand-spread raw documents;
- duplicated public error mapping;
- casts/non-null assertions hiding boundary uncertainty;
- repeated business policy instead of canonical reuse;
- new app-local business services or repositories;
- an equivalent core route left on a duplicated decision path;
- a shared service that implements only the external subset of the scoped legacy capability;
- future core replacement that still requires business rules, repository queries, transitions, or side-effect orchestration;
- branching on `external` versus `core` inside domain logic instead of modeling real actor/capability policy;
- HTTP DTOs, exceptions, envelopes, or external exposure policy imported into the shared service;
- non-atomic multi-write behavior;
- a newly added filename that violates the kebab-case rule or has an undocumented exception;
- unrelated cleanup widening the port;
- invented abstraction with one call site and no real behavior.

Clean architecture must not alter the source-backed business outcome. A refactor is not a license to “improve” legacy semantics silently.

## 8. Tests and documentation

### Test adequacy

Require observable tests for:

- minimal valid request and alternate modes;
- validation decision matrix and boundary values;
- auth, wrong host, permission, entitlement, ownership, and hidden-resource behavior;
- real persistence/query/default/index semantics;
- side effects and failure/rollback order;
- idempotency, duplicate, retry, and concurrency where risky;
- exact public projection/envelope and sensitive-field absence;
- stable errors;
- generated OpenAPI and valid examples.

Reject as primary evidence:

- `service is defined`;
- `handler exists`;
- operation-ID constant equals a string;
- assertions only on internal mock calls;
- broad snapshots;
- direct controller/service tests presented as full wire-contract proof;
- typecheck/lint/build presented as parity proof.

Use real Mongo/repositories when DB behavior matters and fake external infrastructure. Verify tests would fail if the protected rule were removed.

### Documentation adequacy

- Operation and property docs agree.
- Examples validate and match the real response.
- Conditional rules and defaults are explicit.
- Pagination, units, timezones, retry, idempotency, and errors are documented where relevant.
- Overview envelope/auth/rate information matches runtime.
- The endpoint appears in the intended docs surface only.

## 9. Certification bar

Approve only when all are true:

- authoritative source and target scope are pinned;
- the initiating issue and contract-grill resolutions are traceable and implemented;
- all material behavior paths are accounted for;
- public contract is deliberate and consumer-usable;
- frontend business rules are correctly classified and enforced server-side;
- auth, tenant, ownership, and exposure are safe;
- architecture preserves behavior through shared `libs/services` and `libs/repository` ownership with core/external reuse and no duplicated policy path;
- the `M-###` ledger and tests prove that future core replacement is transport-only for the scoped capability;
- tests cover the risk matrix through appropriate seams;
- generated docs and representative runtime responses agree;
- no material decision or unexplained divergence remains.

When evidence is missing, return `NOT CERTIFIED`; when sources conflict, return `BLOCKED BY DECISION`; when findings are valid, return `CHANGES REQUIRED`.
