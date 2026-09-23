# Shared builders and Mongo isolation

Read during discovery and before stage-2 setup, migration, or execution. These requirements apply to new suites and any existing suites executed for regression validation.

## Discover and consolidate builders

The inspected backend checkout contains these starting points; verify them in the active checkout rather than assuming migration is complete:

- Shared test-only code: `libs/testing`, with `builders`, `mongo`, `env`, and `fakes` subpaths under `@tagmango-backend-monorepo/testing`.
- Historical builders: `apps/core-api/src/utils/test/mock-data-builders`. Both old definitions/imports and shared builders can coexist.
- Runner/setup: root and per-project Jest configs, `apps/core-api/jest-integration.config.ts`, app global setup/teardown, `libs/services/jest.config.ts`, TypeScript aliases, and Nx targets.

Keep runner discovery aligned with [source ownership](test-layers.md#place-specs-with-the-source-owner). If a library lacks an integration target or its config mixes unit and integration discovery, record the gap in stage 1 and configure the owning library's runner in stage 2. Reuse shared `libs/testing` infrastructure; do not move library specs into core-api or import app-owned setup to obtain a working harness. Verify the intended specs are discovered and integration setup does not run for unit suites.

Inspect builder implementations and all their consumers before migration. Compare defaults, methods, inheritance, types, date behavior, and build/mutation semantics; identical names do not prove interchangeable behavior.

- Prefer the existing `libs/testing/src/builders` owner. If absent in that checkout, establish the equivalent shared test-only library using the repository's conventions. Do not place test builders in production utilities or make a library import an app.
- Consolidate duplicates and preserve existing core-api fixture behavior. Update all consumers of each migrated builder, exports, aliases, test resolution, and dependency boundaries. A temporary old-path re-export is acceptable for a demonstrated compatibility need; it must contain no duplicate implementation. Report any unmigrated builders explicitly.
- Use shared builders for **all** schema/model document objects, persisted or mocked. Add/extend the shared model builder when missing; do not introduce local document literals, local model factories, or casts as a shortcut. Represent invalid/legacy document variants through explicit builder overrides too.
- Derive builder types from existing schema/domain owners. Keep builders independent of app bootstrapping, database connections, and persistence. Keep setup/scenario persistence explicit through the suite's models/repositories.
- Feature-local scenario helpers may compose shared builders. They must not become a parallel document-construction layer. Plain API request bodies, expected public responses, and provider payloads are not Mongo documents and may be inline.
- Preserve deterministic relevant values and fresh per-case data. Avoid introducing broad builder redesign during migration; remove real duplication and verify affected consumers.

## Prove memory-server provenance before connecting

Unit tests start no Mongo, Redis, queue workers, schedulers, HTTP server, or real external SDK. Integration uses real Mongo only through `mongodb-memory-server`; use its replica-set mode for transaction-dependent behavior.

1. Inspect imports, config factories, Jest setup files, global setup, and every named/default/analytics connection reachable by the selected suite. Avoid importing the production root app or infrastructure modules that auto-connect.
2. Reuse the shared environment hardening before production imports, in every worker as needed. Block inherited application Mongo credentials and later dotenv reloads. Disable schedulers and fake other infrastructure. `NODE_ENV=test` alone is not isolation.
3. Start a memory server owned by this test invocation. Obtain connection details from that instance's `getUri()` or a trusted handoff created by this run's global setup. Replace stale test URI values; never fall back to an inherited URI, `.env`, developer server, Docker Mongo, MCP connection, or staging/testing/production cluster.
4. Validate parsed host/port and the run-owned URI against that provenance before any connection. Localhost, a `test_` database prefix, or a protected-name denylist alone cannot prove that Mongo belongs to this run. An arbitrary `MONGO_TEST_URI` is not trusted just because its name says test.
5. Allocate unique suite/worker databases on that server. Bind all models/repositories to the explicit suite connection; preserve needed schemas/indexes and await index readiness for index-dependent tests. Override every required connection provider so no ambient/default connection remains.
6. Fail before connecting if provenance is missing or mismatched. If memory-server startup/download fails, report blocked integration execution; never switch to an actual environment cluster to get tests running.

Do not assume an existing “safe” helper satisfies these requirements. The inspected `createIsolatedMongoConnection` accepts an environment base URI, and its `dropAndClose` path drops the database. Audit/adapt the smallest shared seam needed; use connection-only close after filtered cleanup.

## Targeted cleanup only

This workflow intentionally overrides repository examples that recommend dropping an isolated suite database. Isolation reduces risk but does not waive the user's filtered-deletion requirement.

- Track documents created by builders **and** by the code under test, per collection. Prefer recorded `_id` sets; also constrain by run-owned tenant/parent IDs when needed. Register ownership before risky operations so partial writes after a thrown error remain identifiable.
- For generated IDs not returned on failure, find them through the suite's uniquely owned parent/tenant relationship. Never discover cleanup candidates with an unscoped query. Do not add test markers to production schemas merely for cleanup.
- Delete only with positively bounded filters such as `{ _id: { $in: createdIds } }`. A run-unique ownership filter must identify only this run's documents, not all data for a real/shared tenant. Skip an empty ownership set; never replace it with `{}` or a broad fallback.
- Prohibit `deleteMany()` without a filter, `deleteMany({})`, match-all filters, `drop()`, `dropCollection`, `dropDatabase`, and wrappers that perform those operations. Inspect before/after hooks, reset helpers, model middleware, and global teardown for hidden broad deletion.
- Perform targeted cleanup after cases or suites as appropriate, including failed assertions and partial setup. Await it before closing the connection. Surface cleanup failures; still close opened resources in `finally` and stop only the run-owned memory server at global teardown. Stopping that disposable process is permitted; do not issue database/collection drops as cleanup.
- Verify cleanup cannot remove unrelated records in the same collection and handles an empty tracked set. Use shared builders for those verification records too, and remove them later through their own tracked IDs.

For migration regression suites that currently use broad cleanup, make the relevant setup comply before execution or report those checks blocked. Do not silently run unsafe legacy suites just to claim a migration passed.
