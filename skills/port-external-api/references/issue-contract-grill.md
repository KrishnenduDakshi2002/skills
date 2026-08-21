# GitHub Issue Intake and Contract Grill

Use this workflow at the start of every port. It composes the decision-tree discipline of `grill-with-docs` into the external-API workflow while keeping this skill usable when installed by itself.

## 1. Capture the issue as the starting brief

Require a GitHub issue URL. Read the live title, body, current comments, linked artifacts, labels, and edit state with available read-only GitHub capabilities. Record the URL, repository, issue number, retrieval time, and stable comment permalinks in the port packet. Do not edit the issue.

Classify each externally meaningful statement as an `I-###` entry:

- consumer requirement or acceptance criterion;
- source endpoint or behavior pointer;
- frontend page, component, or flow pointer;
- proposed public contract;
- accepted decision;
- open question or explicit exclusion.

Treat the issue as scope and product intent, not proof of current runtime behavior. Verify every source pointer against pinned code. Surface contradictions between the issue, backend, frontend, and existing external conventions.

If the issue cannot be read, set the packet to `BLOCKED` and request access or a current body-and-comments export. Do not infer a mutable issue from its title or URL.

## 2. Discover facts before questioning

Resolve facts with repository and GitHub evidence:

- the actual source route and full backend decision path;
- the exact frontend route/page, form initialization, validation, payload assembly, and response handling referenced by the issue;
- existing core and external endpoints for the same capability;
- current public URL, auth, request, response, pagination, error, and versioning conventions;
- current shared service and repository ownership.

Ask the developer for decisions, not for facts the agent can discover. Record unresolved contradictions as `D-###` decisions.

## 3. Build the contract decision tree

Represent choices and their prerequisites. The frontier contains every unresolved choice whose prerequisites are settled. Recompute it after each answer; do not ask a field-shape question while the operation boundary or consumer goal is still unresolved.

When the host can compose installed skills, load `grill-with-docs` and apply its frontier, recommendation, terminology, and edge-case discipline as this bounded design phase. Invoking `port-external-api` is explicit consent for this grill; do not require a second invocation. Its no-implementation rule applies until this frontier closes. The `port-external-api` workflow may resume only after the developer confirms the resulting contract decisions. When skill composition is unavailable, follow this reference directly as the self-contained fallback.

Track these required dimensions in the packet:

- `G-001` — consumer goal, operation boundary, and public resource terminology;
- `G-002` — HTTP method, complete versioned URL, resource naming, and containment;
- `G-003` — placement across path, query, headers, and request body;
- `G-004` — request field names, types, formats, defaults, normalization, conditional rules, and absent/null/empty semantics;
- `G-005` — response envelope, grouping, field exposure, relationship representation, and consumer next action;
- `G-006` — pagination, filtering, sorting, limits, ordering, and empty-page behavior for collection operations, or an explicit not-applicable rationale;
- `G-007` — errors, compatibility, versioning, idempotency, retries, concurrency, and rate/quota behavior;
- `G-008` — the canonical shared capability boundary, `libs/services` and `libs/repository` ownership, external exposure subset, current core callers to rewire, and future core replacement path. Resolve whether future core work is transport-only or identify the missing domain behavior as a blocker.

An issue may settle a dimension only when its wording is explicit. Record the issue or comment permalink as the resolution evidence. Otherwise present realistic alternatives.

## 4. Ask the frontier efficiently

Ask all currently independent questions in one round. Use a structured question interface when available; otherwise use concise numbered text. For each question include:

```text
Q<G-### or D-###> — <decision title>
Evidence: <issue and pinned source facts>
Options: <two or more viable choices and their wire/behavior consequences>
Recommended: <one choice and why it best serves an unfamiliar integrator>
Required answer: <what must be selected or confirmed>
```

Do not overwhelm the developer with every field before presenting a coherent proposal. Group fields with the same lifecycle, show a proposed request/response example, then ask the developer to confirm or change it. Invent boundary and invalid-combination scenarios that expose hidden assumptions.

Do not ask irrelevant questions merely to complete a checklist. Mark a dimension `N/A` with evidence and rationale—for example, pagination on a single-resource mutation.

Before sending the round, write the evidence, options, recommendation, and current status into the matching packet rows; fill the issue/source/behavior and shared-architecture sections reached by the research; and set the packet status to `BLOCKED`. After every answer, update the packet before recomputing the frontier. Never leave the durable packet as an untouched `DISCOVERY` template while presenting developed recommendations to the user.

## 5. Record and close the grill

Keep every resolution in the packet, including rejected options and consequences. Use the packet as the primary durable record. Update a repository glossary only for accepted domain terminology and offer an ADR only for an accepted, hard-to-reverse trade-off when repository documentation changes are in scope.

Close the grill only when:

- every `G-###` dimension is `RESOLVED` or justified `N/A`;
- every material `D-###` decision is resolved;
- consumer examples reflect the selected contract;
- the developer explicitly confirms the contract frontier is complete.

Keep the packet `BLOCKED` and do not edit product code before that confirmation.
