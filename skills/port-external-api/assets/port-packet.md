# External API Port Packet: {{OPERATION}}

Status: DISCOVERY
Operation: {{OPERATION}}
Source kind: {{SOURCE_KIND}}
GitHub issue: {{ISSUE_URL}}
Generated: {{GENERATED_AT}}

## Scope

<!-- Replace with the exact operation, target surface, authorized stopping point, and explicit exclusions. -->

Consumer goal: <!-- Replace with: An external ACTOR calls this to GOAL and needs RESULT for NEXT ACTION. -->

Target branch/base: <!-- Replace -->

Target external surface: <!-- Replace -->

Out of scope: <!-- Replace -->

## GitHub Issue Intake

Issue URL: {{ISSUE_URL}}

Retrieved at: {{GENERATED_AT}}

| ID | Requirement, pointer, decision, or exclusion | Issue/comment permalink | Classification | Evidence or resolution |
|---|---|---|---|---|
| I-001 | <!-- Replace --> | <!-- Replace --> | <!-- consumer/source-pointer/frontend-pointer/proposal/accepted/open/exclusion --> | <!-- Replace --> |

Referenced backend operation(s): <!-- Replace -->

Referenced frontend page/flow: <!-- Replace -->

Issue contradictions or missing context: <!-- Replace or None -->

## Source Authorities

| Source | Pin | Role | Why authoritative |
|---|---|---|---|
| <!-- repository --> | <!-- commit SHA --> | <!-- backend/frontend/contract --> | <!-- reason --> |

Use evidence anchors in the form `repository@commit:path:line` throughout this packet.

## Consumer and Existing Conventions

### Consumer context

<!-- Replace with caller, identifiers available to it, retry model, volume, and next action. -->

### Current external conventions inspected

| Concern | Current convention and evidence | Adopt or deviate | Rationale |
|---|---|---|---|
| URL/versioning | <!-- Replace --> | <!-- Replace --> | <!-- Replace --> |
| Authentication/tenant | <!-- Replace --> | <!-- Replace --> | <!-- Replace --> |
| Request naming | <!-- Replace --> | <!-- Replace --> | <!-- Replace --> |
| Response envelope | <!-- Replace with runtime evidence --> | <!-- Replace --> | <!-- Replace --> |
| Errors | <!-- Replace --> | <!-- Replace --> | <!-- Replace --> |

## Behavior Ledger

| ID | Scenario and preconditions | Authoritative behavior | Persistence/side effects/order | Evidence | Classification | Target decision |
|---|---|---|---|---|---|---|
| B-001 | <!-- Replace --> | <!-- Replace --> | <!-- Replace --> | <!-- repository@commit:path:line --> | <!-- preserve/approved-change/needs-decision --> | <!-- Replace --> |

## Frontend Rule Classification

| ID | Frontend observation | Evidence | Classification | Backend target behavior | Related behavior |
|---|---|---|---|---|---|
| F-001 | <!-- Replace --> | <!-- repository@commit:path:line --> | <!-- invariant/entitlement/default/UI-only/ambiguous --> | <!-- Replace --> | B-001 |

## Validation Matrix

| ID | Preconditions | Valid input | Invalid input | Current enforcement/evidence | Target layer | Public error |
|---|---|---|---|---|---|---|
| V-001 | <!-- Replace --> | <!-- Replace --> | <!-- Replace --> | <!-- repository@commit:path:line --> | <!-- DTO/policy/service/database --> | <!-- E-001 --> |

Explicitly cover absent, `null`, false, zero, empty string, empty list, and empty object where their meanings differ.

## Contract Design Grill

| ID | Dimension | Issue/source constraints | Viable options and consequences | Recommendation | Status | Developer resolution and evidence |
|---|---|---|---|---|---|---|
| G-001 | Consumer goal, operation boundary, and public terminology | <!-- Replace --> | <!-- Replace --> | <!-- Replace --> | OPEN | <!-- Replace --> |
| G-002 | Method, complete versioned URL, resource naming, and containment | <!-- Replace --> | <!-- Replace --> | <!-- Replace --> | OPEN | <!-- Replace --> |
| G-003 | Path/query/header/body placement | <!-- Replace --> | <!-- Replace --> | <!-- Replace --> | OPEN | <!-- Replace --> |
| G-004 | Request fields, types, defaults, normalization, and conditional semantics | <!-- Replace --> | <!-- Replace --> | <!-- Replace --> | OPEN | <!-- Replace --> |
| G-005 | Response envelope, grouping, exposure, relationships, and next action | <!-- Replace --> | <!-- Replace --> | <!-- Replace --> | OPEN | <!-- Replace --> |
| G-006 | Pagination, filtering, sorting, limits, ordering, and empty results | <!-- Replace or justify N/A --> | <!-- Replace --> | <!-- Replace --> | OPEN | <!-- Replace --> |
| G-007 | Errors, compatibility, versioning, idempotency, retries, concurrency, and quotas | <!-- Replace --> | <!-- Replace --> | <!-- Replace --> | OPEN | <!-- Replace --> |
| G-008 | Canonical capability boundary, shared ownership, external subset, and current/future core reuse | <!-- Replace --> | <!-- Replace --> | <!-- Replace --> | OPEN | <!-- Replace --> |

Keep the packet `BLOCKED` until every row is `RESOLVED` or justified `N/A` and the developer confirms the frontier is complete.

## Contract Proposal

### Wire operation

`<!-- Replace with METHOD /api/vN/external/resources -->`

Operation ID: <!-- Replace -->

Compatibility/version decision: <!-- Replace -->

### Authentication, tenant, permission, and ownership

<!-- Replace each concern separately. -->

### Path parameters

| ID | Name | Type/format | Meaning and ownership | Evidence/rule |
|---|---|---|---|---|
| C-001 | <!-- Replace or write None --> | <!-- Replace --> | <!-- Replace --> | <!-- B/V IDs --> |

### Query parameters

| ID | Name | Type/format | Required/default | Semantics, limits, and encoding | Evidence/rule |
|---|---|---|---|---|---|
| C-002 | <!-- Replace or write None --> | <!-- Replace --> | <!-- Replace --> | <!-- Replace --> | <!-- B/V IDs --> |

### Headers

| ID | Name | Type/format | Required/default | Purpose | Evidence/rule |
|---|---|---|---|---|---|
| C-003 | <!-- Replace --> | <!-- Replace --> | <!-- Replace --> | <!-- Replace --> | <!-- B/V IDs --> |

### Request body

| ID | Public field | Type/format | Required/forbidden conditions | Default and absent/null/empty semantics | Domain mapping | Evidence/rule |
|---|---|---|---|---|---|---|
| C-004 | <!-- Replace --> | <!-- Replace --> | <!-- Replace --> | <!-- Replace --> | <!-- Replace --> | <!-- B/V IDs --> |

### Response

Envelope: <!-- Replace with exact runtime shape -->

| ID | Public field | Type/format | Meaning and units | Optional/null/empty semantics | Source mapping | Consumer need | Evidence/rule |
|---|---|---|---|---|---|---|---|
| C-005 | <!-- Replace --> | <!-- Replace --> | <!-- Replace --> | <!-- Replace --> | <!-- Replace --> | <!-- Replace --> | <!-- B/V IDs --> |

### Errors

| ID | Scenario | HTTP status | Machine code | Message/field | Retryable | Disclosure policy | Evidence/rule |
|---|---|---|---|---|---|---|---|
| E-001 | <!-- Replace --> | <!-- Replace --> | <!-- Replace --> | <!-- Replace --> | <!-- yes/no --> | <!-- Replace --> | <!-- B/V IDs --> |

### Idempotency, retries, concurrency, and atomicity

<!-- Replace with explicit behavior, even when not applicable. -->

## Field Exposure Ledger

| ID | Internal/domain field | Public field or omitted | Sensitivity | Consumer need | Exposure rationale | Mapping owner |
|---|---|---|---|---|---|---|
| X-001 | <!-- Replace --> | <!-- Replace --> | <!-- public/private/secret/internal --> | <!-- Replace --> | <!-- Replace --> | <!-- mapper/DTO --> |

## Threat and Abuse Cases

| ID | Caller-controlled input or capability | Downstream action/data | Abuse or failure mode | Required controls and limits | Deferred verification concern |
|---|---|---|---|---|---|
| S-001 | <!-- Replace --> | <!-- Replace, including worker/provider consumers --> | <!-- Replace --> | <!-- Replace --> | <!-- Replace for later testing workflow --> |

## Mapping and Implementation Plan

### Request to domain

<!-- Replace with explicit mapping, defaults, normalizers, and policy boundary. -->

### Domain to response

<!-- Replace with explicit allowlist/projection and serializer boundary. -->

### Architecture slices

1. <!-- Replace -->

## Shared Architecture Plan

| Concern | Required ownership | Planned implementation and consumers |
|---|---|---|
| Capability-complete business use case and policies | `libs/services/src/lib/<domain>/` | <!-- Replace with the exact scoped legacy capability and every transport consumer --> |
| Typed persistence and queries | `libs/repository/src/repositories/<domain>/` | <!-- Replace --> |
| Current/future core transport adapter | `apps/core-api` controller/DTO/mapper only | <!-- Replace with existing callers rewired or the future transport-only mapping --> |
| External transport adapter | `apps/core-api/src/api-modules/external` controller/DTO/mapper only | <!-- Replace --> |
| Provider/queue/file adapters | Shared injectable service dependencies | <!-- Replace or None --> |

Transport-neutral domain input/result/errors: <!-- Replace -->

App-local business/repository duplication removed or explicitly blocked: <!-- Replace -->

Library exports, model registration, and dependency-injection wiring: <!-- Replace -->

## Core Migration Readiness

Core migration readiness: DISCOVERY

Canonical capability: <!-- Replace with the precise business capability, not a controller name -->

Legacy replacement scope: <!-- Replace with the legacy route paths/branches covered and explicit exclusions -->

Core replacement implementation delta: UNASSESSED

Future core business/repository reimplementation required: UNASSESSED

| ID | Legacy capability path and behavior IDs | Canonical shared service/repository mapping | External adapter and exposure decision | Current or future core adapter mapping | Implementation evidence and deferred runtime risk | Status |
|---|---|---|---|---|---|---|
| M-001 | <!-- Replace with B/V IDs and source path --> | <!-- Replace --> | <!-- Replace, including intentional omissions --> | <!-- Replace; transport/auth/DTO/mapper/wiring only --> | <!-- H-### and remaining runtime risk --> | OPEN |

Use `DESIGNED` at the design gate and `IMPLEMENTED` after the complete shared capability exists. Set `Core replacement implementation delta` to `TRANSPORT_ONLY` and future business/repository reimplementation to `NO` only when every row supports those implementation claims; otherwise keep the packet `BLOCKED`. Runtime certification belongs to the separate testing workflow.

Shared domain contract remains complete when the external contract omits fields or modes: <!-- Replace -->

Known migration blockers or approved capability exclusions: <!-- Replace or None -->

## Consumer Examples

### Minimal valid request and response

```http
<!-- Replace -->
```

### Important optional/conditional request and response

```http
<!-- Replace -->
```

### Invalid combination and exact error

```http
<!-- Replace -->
```

### Retry/duplicate example

```http
<!-- Replace or explain why not applicable -->
```

## Decisions and Questions

| ID | Status | Decision/question | Evidence and options | Recommendation | Resolution and owner |
|---|---|---|---|---|---|
| D-001 | OPEN | <!-- Replace or remove row when no decision exists --> | <!-- Replace --> | <!-- Replace --> | <!-- Replace --> |

Set packet status to `BLOCKED` while any material decision is open.

## Implementation Traceability

| ID | Behavior/validation/grill/migration/threat IDs | Planned or implemented files and symbols | Planned or actual representation of the rule | Deferred runtime uncertainty or later-testing context |
|---|---|---|---|---|
| H-001 | B-001, V-001, G-001, M-001, S-001 | <!-- Replace --> | <!-- Replace --> | <!-- Replace or None --> |

## Implementation Checks

| Check | Scope/command | Outcome | Evidence or limitation |
|---|---|---|---|
| Formatting/lint | <!-- Replace --> | <!-- PASS/FAIL/SKIPPED --> | <!-- Replace --> |
| Typecheck | <!-- Replace --> | <!-- PASS/FAIL/SKIPPED --> | <!-- Replace --> |
| Build | <!-- Replace --> | <!-- PASS/FAIL/SKIPPED --> | <!-- Replace --> |
| Generated OpenAPI static inspection | <!-- Replace --> | <!-- PASS/FAIL/SKIPPED --> | <!-- Replace --> |
| New-file naming audit | Added paths in scoped diff and scoped untracked paths | <!-- PASS/FAIL/SKIPPED --> | <!-- Replace with exceptions or None --> |
| Final diff and architecture review | <!-- Replace --> | <!-- PASS/FAIL/SKIPPED --> | <!-- Replace --> |

## Handoff

Preserved behavior: <!-- Replace -->

New backend enforcement promoted from frontend: <!-- Replace -->

Approved deviations: <!-- Replace or None -->

Residual risks and unverified areas: <!-- Replace or None -->

Core migration readiness and remaining future adapter work: <!-- Replace -->

Drift watchlist (legacy routes keeping a live duplicated implementation until core replacement): <!-- Replace or None -->

Optimization equivalence notes: <!-- Replace with outcome-equality arguments per affected B-###, or None -->

Testing status: DEFERRED TO SEPARATE WORKFLOW

Deferred behavioral/runtime verification scope and risks: <!-- Replace -->

Test files added or modified by this port: None
