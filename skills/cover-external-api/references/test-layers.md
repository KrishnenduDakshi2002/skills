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

Test guards/authorization policy at their owning boundary too. Do not consider authorization covered because service tests pass a pre-authorized actor.

## Split depth from composition

- Exhaust the meaningful rule/input variants at the layer that owns each rule. Add integration cases wherever combining layers introduces a distinct failure mode; do not copy the entire same case matrix into every layer.
- Keep repository-owned business behavior visible even if it would ideally belong elsewhere. Test its current public entry point; do not relocate it solely to fit a testing diagram.
- Give each assertion the right scope. A service unit test can prove the decision for a returned record; it cannot prove that the repository selected the right record. A repository test can prove tenant filtering; it cannot prove that the adapter supplied the authenticated tenant.
- Allow deliberate overlap for separate guarantees. For example, test invalid pagination values in the DTO suite, ordering and page boundaries in the repository suite, and the selected page's public envelope in adapter integration.
- Do not mandate a new test file for every class or layer. Reuse effective existing suites; omit isolated tests for a trivial forwarding layer if integration already proves its contract. Explain the omission in the handoff. Never omit a substantive rule merely because it lives below the service.
- Distinguish architectural layer coverage from line coverage. Report which contracts were actually exercised, including boundary gaps left by mocks.

## Keep the two-stage review legible

Organize case-only specs at their final owners, for example:

```text
<external-feature>/dto/list-items.dto.spec.ts
<service-feature>/list-items.service.spec.ts
<service-feature>/tests/list-items.integration.spec.ts
<repository-feature>/tests/list-items.repository.integration.spec.ts
<external-feature>/mappers/item.mapper.spec.ts
<external-feature>/tests/list-items-response.integration.spec.ts
```

These are ownership examples, not a requirement to create six files. Follow actual source names and repository conventions. Use suite names to distinguish unit decisions, repository integration, and response integration; keep existing two-level `describe` depth. Review all relevant layer outlines together before implementing the same files in stage 2.
