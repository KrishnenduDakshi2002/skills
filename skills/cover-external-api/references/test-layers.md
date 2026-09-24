# Testing by layer

Read before drafting or reviewing endpoint outlines and when implementing their cases. A layer is an ownership boundary, not a test type: a service can need both unit and integration tests, while a repository usually needs integration tests.

## Assign observable contracts

| Layer | Prove | Test boundary and dependencies |
|---|---|---|
| Request DTO / validation | Accepted/rejected input, coercion, defaults, optional/null semantics, nested validation, unknown-field handling, and cross-field constraints owned here. | Focused tests using the real DTO and production validation/transformation configuration. No Mongo. Exercise runtime validation; constructing a DTO or checking TypeScript types does not validate a request. Use component integration when a pipe and transformer must work together. |
| Service / business rules | Eligibility, calculations, state transitions, merged-state decisions, domain errors, returned results, and externally meaningful side effects or their suppression. | Unit-test pure rules and service decisions with controlled direct dependencies. Use service + real repository + memory Mongo integration for CRUD outcomes, persistence-dependent decisions, transactions, and multi-step changes. Fake external providers. |
| Repository / data access | Returned records and projections, tenant/ownership boundaries, soft-delete rules, filters/joins/aggregations, sorting/pagination/counts, atomic writes, duplicates, and any business rule enforced here. | Call the real repository against actual schemas/indexes on memory Mongo. Seed through shared builders; assert returned values and persisted state. Mocked Mongoose chains or query-shape assertions do not prove query semantics. Independently exported pure repository rules may also have unit tests when those tests add distinct value. |
| Schema / persistence constraints | Application-defined defaults, casting/validation, middleware, unique/compound indexes, and persistence invariants that affect the selected endpoint. | Focused memory Mongo integration, often within the repository suite. Await indexes. Use a memory replica set where transactions are involved. Test the application's configuration and invariants, not Mongoose/Mongo's generic functionality. |
| Response mapper / controller adapter | Public field allowlists, renaming, nested shapes, missing/null fields, serialization, error translation, status/envelope/headers, and contextual information passed across the boundary. | Unit-test meaningful mapping/error-conversion logic. Use focused in-process adapter integration with actual relevant pipes, guards, serializers, interceptors, and filters to establish the wire contract. A mocked service result only proves the adapter's handling of that result. |
| Cross-layer behavior | Correct composition: validated inputs reach the use case, repository rules affect outcomes, writes feed the returned representation, and domain failures become the intended public response without unintended effects. | Focused module/component integration for representative success, rejection, and failure interactions. Keep material services/repositories real and external infrastructure fake; use memory Mongo whenever persistence is involved. Do not start the full application or use live servers. |

## Assign cases from their claims

During stage 1, normally assign cases containing “persists,” “retains,” “leaves unchanged,” “before,” “after,” or “atomic” to real-Mongo integration. Assign by the observable claim rather than the word alone. Unit tests cover pure decisions, domain errors, failure propagation/policy, and genuine external contracts; repository mocks cannot support persistence claims.

If implementation reveals that an approved case belongs at another layer, move its declaration and implementation to the correct source-owned suite. Preserve its observable intent and report the old/new paths and reason. Do not keep an implementation-detail test merely to preserve the original file assignment; seek a decision only for a material contract or scope change.

## Assert behavior and persisted outcomes

Prove application behavior, not Mongo or repository implementation. Never assert exact repository filters, update objects, Mongo operators, `bulkWrite` operations, private calls, or internal repository call order/counts. An assertion such as `toHaveBeenCalledWith({ ... }, { $set: ... })` is not persistence evidence. A mocked repository call never proves database behavior.

- Any claim that data was persisted, changed, retained, left unchanged, written atomically, or written before/after another effect requires the real persistence path on MongoMemoryServer and targeted reads of the affected documents through the suite connection. Select by known IDs or run-owned relationships; compare relevant values/absence against the seeded state where needed.
- Repository/Mongoose spies may only inject a controlled failure. Assert the resulting output, persisted state, or external side effects, never the injected method's arguments, count, or order. Unit dependency fakes may supply records or errors for decisions; they remain evidence only for those decisions.
- Assert mock calls only for a genuine external observable contract, such as a queue, provider, or cache interaction. Verify payload, multiplicity, and suppression where those are contract requirements. Do not treat an internal collaborator as external merely because it is mocked.
- For atomicity, exercise the relevant failure or concurrency condition and query all affected documents for the promised invariant. A successful final-state read alone does not prove atomicity, nor does observing a transaction or bulk-write call.

### Prove sequencing observably

| Claim | Evidence |
|---|---|
| External operation precedes persistence | Hold the external fake with a deferred promise. Await a signal that the fake was entered, query Mongo while it is pending, then release it, await completion, and query the final state. Settle deferred work in teardown even when an assertion fails. |
| Persistence precedes an event | Have the event fake query the stored document when invoked and assert the state it observed at that moment. Await the observation; a read only after the whole operation cannot prove this ordering. |
| Partial failure preserves or changes specific state | Inject the controlled failure, await the operation's outcome, and query the resulting documents, including any partial writes and unaffected records relevant to the claim. |

Use synchronization signals rather than timing sleeps or mock invocation-order metadata.

## Authorization evidence

- Sending an `Authorization` header through the production header extractor and guard can prove header wiring when token verification is controlled safely. State that controlled verification does not establish real token validation.
- Overriding the guard or injecting authenticated request context bypasses authentication; it proves neither Authorization-header parsing nor token validation. Such setup may still exercise downstream endpoint-specific authorization and access policy.
- Put generic authentication-header behavior and its matrix in the middleware/guard owner's suite. Endpoint suites cover endpoint-specific authorization and access-policy effects, with focused wiring cases where needed; do not duplicate the complete authentication matrix.
- In the handoff, identify the real extractor/guard/verifier boundaries exercised and any bypass or fake. Distinguish header wiring, token validation, and endpoint authorization rather than reporting a single undifferentiated “auth covered.”

## Mandatory final assertion audit

Before handing off stage 2:

1. Inspect every mock-call assertion and confirm it represents an external observable contract.
2. For every persistence or sequencing claim, identify the targeted Mongo read that proves it, including the moment of observation for ordering. Correct the layer or evidence when that read is missing.
3. Search all selected specs for Mongo operators inside expectations and manually inspect every match. Include multiline expectations and helper-based assertions; reject assertions of query/update syntax rather than observable results.
4. Search for repository/Mongoose methods inside `toHaveBeenCalled*` assertions and inspect every match, including aliases and separately named spies. Remove implementation-detail assertions; keep failure injection only with outcome evidence.

Searches locate candidates; they do not replace reading assertions and their helpers. Complete the separate [test-support ownership audit](testing-infrastructure.md#test-support-ownership-audit) and verify the correct runner discovers each suite.

## Split depth from composition

- Exhaust the meaningful rule/input variants at the layer that owns each rule. Add integration cases wherever combining layers introduces a distinct failure mode; do not copy the entire same case matrix into every layer.
- Keep repository-owned business behavior visible even if it would ideally belong elsewhere. Test its current public entry point; do not relocate it solely to fit a testing diagram.
- Give each assertion the right scope. A service unit test can prove the decision for a returned record; it cannot prove that the repository selected the right record. A repository test can prove tenant filtering; it cannot prove that the adapter supplied the authenticated tenant.
- Allow deliberate overlap for separate guarantees. For example, test invalid pagination values in the DTO suite, ordering and page boundaries in the repository suite, and the selected page's public envelope in adapter integration.
- Do not mandate a new test file for every class or layer. Reuse effective existing suites; omit isolated tests for a trivial forwarding layer if integration already proves its contract. Explain the omission in the handoff. Never omit a substantive rule merely because it lives below the service.
- Distinguish architectural layer coverage from line coverage. Report which contracts were actually exercised, including boundary gaps left by mocks.

## Place specs with the source owner

Choose the location from the code or behavior under test, not the endpoint that calls it. Keep unit specs beside their source and integration specs in the owning feature's `tests/` folder, within the same app or library.

- Service/business-rule tests for `libs/services` stay in `libs/services`, including service + real repository + memory Mongo integration. Do not place them under `apps/core-api/src/api-modules/external` merely because an external route uses the service.
- Keep repository/schema and utility tests with their actual source owners, such as `libs/repository`, `libs/schemas`, or `libs/utilities`. A repository suite may cover its schemas' persistence constraints without requiring a separate schema suite.
- Keep external DTO, controller, mapper, and response-pipeline tests beside the corresponding external adapter. Focused adapter integration may exercise library services; its distinct purpose is to prove the adapter contract and wiring, not to house the service's full business-rule matrix.
- Use an app-level `src/tests/` only for app composition spanning features when no single feature owns the behavior. Calling several repositories from one service does not remove that service's ownership.
- Follow local naming and folder conventions within the source owner; older misplaced specs or a convenient app runner are not precedents for placing library tests in an app.

Organize case-only specs at these final owners from stage 1, for example:

```text
libs/services/src/lib/<feature>/<feature>.service.spec.ts
libs/services/src/lib/<feature>/tests/list-items.integration.spec.ts
libs/repository/src/lib/<feature>/tests/list-items.repository.integration.spec.ts
apps/core-api/src/api-modules/external/<feature>/dto/list-items.dto.spec.ts
apps/core-api/src/api-modules/external/<feature>/mappers/item.mapper.spec.ts
apps/core-api/src/api-modules/external/<feature>/tests/list-items-response.integration.spec.ts
```

These are ownership examples, not a requirement to create six files. Derive actual paths and filenames from the source. Use suite names to distinguish unit decisions, repository integration, and response integration; keep existing two-level `describe` depth. Review all relevant layer outlines together before implementing the reviewed cases in stage 2.
