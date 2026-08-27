---
name: document-external-api
description: Raise the generated OpenAPI documentation of TagMango external API endpoints to a consumer-ready bar — purpose, nuances, field semantics, defaults, errors, and realistic examples — through docs-only code changes (Swagger decorators, DTO metadata, error scenarios). Never changes runtime behavior. Documents one operation, a tag, or backfills the whole external surface.
argument-hint: <operation-id | tag | controller-path | --all>
disable-model-invocation: true
---

# Document External API

The reader is an integrator — increasingly an AI agent — with no dashboard access, no support channel, and no TagMango insider vocabulary. The generated OpenAPI document is everything they get. Every endpoint must let that reader build a correct request, interpret every response field, and predict every error from the document alone — in the fewest words that do it. The document is a contract, not a code walkthrough: it carries observable behavior the consumer must plan around, never the implementation that produces it, and never a sentence that doesn't change what the consumer builds.

**Documentation is a set of claims about runtime behavior, and every claim needs a source.** A claim traces to code (controller → DTO validators → shared use case → repository), to a port packet ledger row, or to a captured runtime response from a test run. Existing prose is a claim to verify, never authority to carry forward. A claim you cannot trace is a doubt, and a doubt becomes a finding — never confident prose.

**Docs-only boundary.** This workflow may touch: `@ExternalApi` doc/error metadata, `@ApiProperty`/`@ApiPropertyOptional` options, the central operation ID registry, tag registrations and descriptions in `buildExternalApiDocumentOptions`, description strings, and examples. It never touches validation rules, mappers, guards, response shaping, or any control flow. When honest documentation would require a behavior change — a documented error no code path can throw, a documented constraint no validator enforces, a response field with no defensible consumer use case — that is a finding routed out (implementation bugs to `port-external-api`, contract and exposure questions to `audit-external-api-port`), never a fix smuggled into this workflow and never prose that papers over it.

## The pipeline you are editing

Decorators are the source: `@ExternalApi({ doc, response, errors })` on each handler plus `@ApiProperty` metadata on DTOs. The repository's preview script (`apps/core-api/src/scripts/preview-external-swagger.ts`) generates the external OpenAPI document, which downstream documentation tooling renders. Consequences:

- Judge everything in the **generated document**, not in the TypeScript — that is what the consumer sees. Descriptions are markdown and render as doc pages with headings, side navigation, and callouts — structure them accordingly.
- `errors: [...]` scenarios render as named examples per status code — one entry per reachable `errorCode`, via the central `getErrDefinition` registry.
- Operation IDs come from the central registry and become page slugs and client method names; never inline a string.
- When naming another endpoint would make a description correct and complete — where an input value comes from, which sibling to use instead — link it: a markdown link whose URL is built with `getExternalApiDocumentationUrl(tagSlug, operationId)` from `apps/core-api/src/api-modules/external/external-api-documentation-url.ts`, never a hardcoded docs URL. The helper keeps links valid across environments and origin changes.
- Convention-level facts (auth headers, response envelope, global rate limit) live once in the overview description in `external-api-document.ts`. Per-endpoint docs state only what is endpoint-specific and must never contradict the overview.
- The preview script's default output path targets a sibling `tagmango-documentation` checkout. **Always pass an explicit temporary output path**; publishing a spec to the documentation repo is the user's call, never a side effect.

## Workflow

### 1. Scope and baseline

Resolve the argument to a concrete set of operations: one operation ID, every operation under a tag or controller, or the full external surface. Generate the current document to a temporary path (discover the invocation from the repository — Nx target, package script, or ts-node — never assume), then take the mechanical baseline:

```sh
python3 <skill-directory>/scripts/doc_coverage.py <spec-path> --repo <repo-root> [--operation <id> ...]
```

Keep its output verbatim; it is the before-evidence for the handoff. The script measures presence — missing summaries, thin descriptions, undescribed fields, absent error responses, placeholder examples. Presence is the floor. The rubric is the bar.

### 2. Gather the evidence

For each in-scope operation, collect what documentation claims must be traced against, in this order of preference:

- the port packet when one exists (`.scratch/external-api-ports/<slug>/port-packet.md` or the repository's established scratch location): its `B/V/E/X-###` ledgers and consumer examples are pre-traced evidence — reuse them; when current code contradicts the packet, the code wins for what the docs say and the contradiction is a finding;
- captured runtime evidence from `test-external-api-port` runs (`<artifacts-dir>/<operation>/test-runs/`): real request/response pairs are the best source of realistic examples;
- the code itself: controller, DTO validators, shared use case, repository — the only source that can answer the nuance hunt in rubric §2 (defaults, ordering, limits, filter interaction, side effects, staleness, where identifiers come from).

### 3. Audit against the rubric

Read [documentation-rubric.md](references/documentation-rubric.md) and walk every in-scope endpoint through it. Record a gap table per endpoint — rubric item, current state, evidence needed — before writing anything. An endpoint whose docs already meet the bar is recorded as such and left untouched; churn on adequate docs is noise in the diff.

### 4. Write the documentation

Work endpoint by endpoint, rubric in hand. A description is a structured markdown document — purpose and use case first, then nuances as a bullet list, then related endpoints, with subheadings and note callouts on long descriptions rather than paragraph walls. Write at the contract level: each nuance is one sentence of observable behavior, never the code logic behind it, and a hunted nuance that changes nothing for the consumer stays in the working notes, not the docs. Every optional field states its coded default; every collection states its ordering or explicitly disclaims one; every input identifier names the endpoint that produces it; every reachable error code appears with a consumer-actionable description; examples are realistic platform data telling one coherent story. Register new tags and operation IDs centrally. Prefer constants already shared with validators (policy objects, enums) over retyped literals so docs cannot drift from enforcement.

### 5. Regenerate and verify

Regenerate the document to a fresh temporary path and verify mechanically:

- `doc_coverage.py` reports clean for the scoped operations, or every remaining gap has a recorded justification;
- diff the before/after specs: only in-scope operations and their reachable schemas changed;
- `git diff` shows docs-only edits — decorator metadata, DTO option objects, registries, prose — and nothing else;
- run the repository's format, lint, typecheck, and build targets (docs are code); never run test suites here.

### 6. Acid test

From the regenerated document alone — no source access — write for each documented endpoint: the minimal valid request, one important optional combination, and one invalid combination with the exact error it should produce. If writing them needs knowledge the document doesn't carry, the docs are incomplete: return to step 4. Executing these against a live environment is `test-external-api-port`'s gated territory, not this workflow's; note anything worth runtime verification in the handoff instead.

## Sweeps

For a tag-level or full-surface backfill, keep one inventory (operation, controller, packet path if any, baseline gap count, status) and process one tag at a time — evidence gathering stays coherent within a domain. Never template one endpoint's prose across siblings; shared wording for genuinely shared semantics (pagination, tenant scoping) belongs in shared DTOs or the overview, not copy-paste.

## Stopping points

- Documentation would change behavior, or a field/error/constraint cannot be honestly documented → finding, routed out; the endpoint's docs land only up to the honest line.
- The user asks for guides, tutorials, or docs-site work beyond the generated reference → out of scope; say so.
- Never stage, commit, or push; never write into a `tagmango-documentation` checkout; never edit generated YAML by hand.

## Handoff

Report: the scope and how it was resolved; per-endpoint before/after coverage (the two `doc_coverage.py` outputs); a summary of what each endpoint's docs now claim that they didn't before; the acid-test artifacts; every finding with its routing (`port-external-api` / `audit-external-api-port` / runtime questions for `test-external-api-port`); any claims left deliberately undocumented with the reason; and the untouched-because-adequate list. The diff stays uncommitted for the user's review.
