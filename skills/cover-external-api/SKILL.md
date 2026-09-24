---
name: cover-external-api
description: Create or extend behavior-focused unit and integration coverage for selected TagMango external API endpoints in two stages, first reviewable case-only .spec.ts declarations, then implementation of those reviewed cases. Use for external API test outlines, coverage reviews, implementing approved suites, and shared Mongo document builder migration needed by those tests. Excludes end-to-end tests and live endpoint certification.
---

# Cover External API

Protect external API business rules, public responses, persisted outcomes, and side effects through unit and integration tests. Make the case inventory readable before implementing it. Implement the reviewed declarations in the same `.spec.ts` files unless correcting their layer assignment; preserve observable intent and report any move. Never substitute a Markdown test plan.

## Select scope and stage

- Resolve the backend checkout from the user's path or current workspace. Read its `AGENTS.md`, `BEST_PRACTICES.md`, and `TESTING_GUIDELINES.md` when present; inspect git state before editing.
- Accept endpoint methods/routes, operation IDs, controller paths, or an explicit request to pick a bounded number. If asked to pick without a count, choose one cohesive endpoint and state the choice. Do not expand a batch to the entire API surface.
- Default to **stage 1: outline**. For **stage 2: implement**, require an existing reviewed outline and the user's direction to implement it. Honor approval already given in the conversation. A request for an outline review means inspect and report gaps, without implementing tests.
- Keep this separate from `test-external-api-port`, which exercises live servers. Do not invoke live verification, require credentials/a port packet, or change a packet to `VERIFIED` for unit/integration coverage.
- Apply the user's requirements where repository examples differ: memory-server-only Mongo, filtered cleanup, and shared builders for every schema/model document. Do not copy database-drop or inline-document patterns from older tests.

## Inspect before outlining

1. Trace each selected route through guards, DTO validation/transformation, controller, service/policy/utilities, repository/schema/indexes, response mapper/serializer, interceptors, and exception filters. Discover actual owners; logic may span `libs/services`, `libs/utilities`, `libs/repository`, and the app's external adapters.
2. Read existing tests and public contract documentation. Inspect relevant legacy behavior when parity is part of the contract. Treat comments, OpenAPI, and implementation as evidence to reconcile, not interchangeable truth. Surface contradictions and ambiguous expected outcomes; do not quietly bless a suspected bug with a passing expectation.
3. Review [coverage dimensions](references/coverage-dimensions.md). Map every reachable business rule, response variant, relevant failure, and side effect to a named case or existing effective test. Include meaningful interacting conditions, not just isolated branches. Avoid padding the count with duplicate or impossible scenarios.
4. Apply the [layer testing strategy](references/test-layers.md): assess DTO/validation, service, repository/schema, response adapters, and their integration separately. Assign each claim to a boundary that can prove it, including persistence, sequencing, and authorization. Add focused cross-layer cases for wiring and combined outcomes; keep external providers fake.
5. Inspect runner discovery/setup and [shared builders and Mongo isolation](references/testing-infrastructure.md). Identify migration, harness, and testability work for stage 2. Do not perform it during stage 1.

## Stage 1: case-only specs

Write new case declarations at their final source owners. Colocate unit `<source>.spec.ts` files with the source; put `<behavior>.integration.spec.ts` in that owning feature's `tests/` folder. Tests for code in `libs/services` belong under `libs/services`, including service + repository integration; an external API caller does not make them core-api external-module tests. Apply the same rule to repositories, utilities, DTOs, and adapters using [the placement rules](references/test-layers.md#place-specs-with-the-source-owner). Preserve existing implemented tests; append pending cases without blanking or skipping working coverage.

- Use at most two `describe` levels: subject/feature, then business context. Let each `it` name state the observable outcome. Name the endpoint and test boundary clearly enough to find the suite.
- Separate specs by the layer and behavior they protect using [claim-based assignment](references/test-layers.md#assign-cases-from-their-claims). Enumerate relevant cases for every owning layer during this stage, including repository-owned business rules. Do not postpone lower-layer case discovery until implementation or hide the whole inventory in one endpoint suite.
- Use `it.todo('...')` for individual pending cases. For a parameterized family use `it.skip.each` with an empty callback; use `describe.each` with pending leaves when multiple behaviors share a context. Never use an active empty `it` callback, which would falsely pass. Do not invent `it.todo.each`.
- Keep all new test bodies unimplemented. Do not add assertions, hooks, dependency mocks, production imports, model instances, fixture builders, DB setup, or refactors. Permit only suite/case declarations, inert parameter tables describing conditions/expected outcomes, and concise comments needed to resolve a contract question.
- Keep parameter rows readable and name each row distinctly. Model meaningful equivalent inputs with `.each`; keep different behavior/setup/side effects as separate cases. Never manually loop to register tests.
- Make case names/tables concrete: named response fields and omissions, exact status/error semantics where established, relevant persisted changes, and emitted or suppressed side effects. Avoid vague cases such as “returns correct shape” or “handles errors.”
- Do not create document-shaped fixtures in outline tables. Describe the domain state in words or scalar parameters; instantiate it through shared builders in stage 2.
- Mark uncertain cases with a concise `CONTRACT QUESTION` comment and a pending name. Resolve their expected behavior before implementing them. Keep any lightweight source anchors next to the cases rather than creating a parallel case ledger.

Example structure (illustrative only; derive actual rules from the selected endpoint):

```ts
describe('External certificate listing (integration)', () => {
  describe('when the user belongs to another tenant', () => {
    it.todo('returns an empty items array without exposing certificate links');
  });

  describe('when filtering by type', () => {
    it.skip.each([
      { input: 'unknown', reason: 'unsupported type' },
      { input: 'mango,,course', reason: 'empty type token' },
    ])('rejects $reason with HTTP 400 for "$input"', () => {});
  });
});
```

Review the outline against the traced code, layer strategy, and coverage dimensions before handing it off. Report selected endpoints, spec paths and pending case counts by layer (expand parameter rows), existing coverage reused, reasons any layer needs no separate suite, unresolved questions, and stage-2 infrastructure needs. Keep the case inventory in the specs. Do not report pending cases as implemented, passing, or measured coverage. Avoid running integration setup just to enumerate declarations.

**Stop here for review.** Ask the user to review the concrete spec files and authorize implementation; explain that this skill's two-stage workflow requires the handoff. Do not interpret silence or a successful syntax check as approval. Another reviewer agent may assess completeness, but its feedback alone does not authorize stage 2 unless the user delegated that decision.

## Stage 2: implement the reviewed cases

1. Re-read the reviewed specs, current source, and review feedback. Reconcile drift before implementation. Preserve case intent; correct layer assignments under [the assignment rules](references/test-layers.md#assign-cases-from-their-claims). Turn `todo` into `it` and remove pending modifiers as bodies are completed. Do not delete, merge away, weaken, or leave approved cases skipped just to produce a green run. Make newly discovered gaps visible as additional declarations; seek a decision only where contract or scope materially changes.
2. Follow [testing infrastructure](references/testing-infrastructure.md) before executing any integration suite, including old consumer tests. Apply its domain-ownership and dependency checks before adding or moving test support. Limit builder work to the selected coverage and make the harness safe before importing code that could connect to infrastructure.
3. Build all Mongo/schema document fixtures through shared builders, including objects returned by unit dependency mocks. Pin values important to expectations. Keep request DTOs, external payloads, and explicitly authored expected public responses readable; those are not document fixtures.
4. Implement independent, deterministic cases at their assigned layers. Use real rules and collaborators material to the behavior; control unit dependencies and fake external providers under [the assertion ownership rules](references/test-layers.md#assert-behavior-and-persisted-outcomes). Never stub the behavior under test or reconstruct the expected value by calling its production mapper/calculator.
5. Assert outputs, full public contract boundaries, database state, and externally meaningful side effects. Use exact response keys/shape and explicit negative exposure checks where contract safety matters; a broad `objectContaining` assertion alone does not establish a public response shape. Pin time/IDs as needed rather than accepting arbitrary values everywhere.
6. Exercise production validation, mapping, serialization, and error handling at the boundary that owns them. A direct controller/service invocation cannot prove HTTP status/envelope or decorator/pipe behavior. Use a focused in-process adapter/module integration with the actual relevant pipeline when required; do not boot the full app, contact a deployed server, or turn this into E2E coverage. State any unexercised boundary.
7. Apply [persistence and sequencing evidence](references/test-layers.md#assert-behavior-and-persisted-outcomes) and [authorization evidence](references/test-layers.md#authorization-evidence). Match each claim to an observable assertion at the exercised boundary.
8. When code is hard to test, explain the blocker and make only the behavior-preserving refactor authorized by this workflow/user direction: expose an appropriate dependency seam, extract an existing pure rule, or separate orchestration from I/O. Characterize behavior before changing it where possible. Preserve errors, omissions, timing, ordering, and side effects; validate before/after. Do not redesign the API, export private internals solely to spy on them, or fix product behavior under the label of refactoring. Escalate ambiguous behavior or broader product changes.

## Validate and hand off

- Complete the mandatory [final assertion audit](references/test-layers.md#mandatory-final-assertion-audit) and [test-support ownership audit](references/testing-infrastructure.md#test-support-ownership-audit).
- Run focused unit and integration targets separately after verifying their setup is safe and checking [runner discovery](references/testing-infrastructure.md#discover-and-consolidate-builders). Do not disable safety guards to work around a runner failure.
- Run affected shared-builder/harness checks and existing core-api consumer suites after migration, subject to the same Mongo/cleanup requirements. Typecheck and lint touched projects as appropriate. Use the repository's installed runner/version and commands, not a newly downloaded test runner.
- Inspect statement/branch coverage for the selected behavior and dependencies by owning layer; include relevant unexecuted source files so percentages are not inflated by imports alone. Reconcile uncovered meaningful paths against the inventory. Service coverage cannot stand in for DTO/repository/response coverage. Coverage percentages do not prove assertion quality or completeness.
- For critical assertions, check that a plausible defect (wrong tenant, extra response field, duplicate side effect, missing write) would fail the test. Avoid count targets, snapshot dumps, and assertions that merely echo mocks.
- Report implemented/passing/failing/pending counts, commands actually run, remaining behavioral/boundary gaps, case moves, and infrastructure/refactor changes. State whether authentication was exercised or bypassed and which guarantees that establishes. Separate outline completeness from runtime results; report blocked execution honestly. Do not claim all external APIs are covered from one batch or claim E2E/live certification.
- Leave changes unstaged and uncommitted unless the user explicitly authorizes those actions.
