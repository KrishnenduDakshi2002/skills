# External API Documentation Rubric

## 1. The standard

Aim for the shortest clear, complete reference. Simplify wording and structure without dropping integration facts or compressing them into cryptic fragments.

Document enough for a third-party developer to choose the endpoint, build a valid request, interpret its response, and handle relevant errors. Evaluate the generated OpenAPI document as a whole, including schemas and the overview. Completeness does not require repeating each fact in operation prose.

Publish a fact only when it changes a consumer's request, interpretation, or next action. Keep source traces, database queries, implementation branches, module names, and legacy comparisons in working notes. Translate relevant implementation behavior into its public consequence: “Results may take up to 10 minutes to appear,” without explaining the cache or worker behind it. Explain calculations only when needed to interpret a public metric, such as its denominator or included population.

Audit each section below as met, gap, or justified N/A. Removing noise and duplication is part of closing a gap.

## 2. Operation documentation

Use a short action summary that distinguishes the operation from its siblings. Add a description only for integration facts the summary and schema do not express. A short paragraph is usually enough; add bullets or headings only when the necessary content warrants them. Do not require a purpose/nuances/related-endpoints template.

Investigate these behaviors when applicable, then document only relevant findings in their owning location (§8):

- Ordering, tie-breakers, pagination, and empty results.
- Defaults, filter combinations, absent versus empty inputs, and conditional requirements.
- Retry safety, idempotency, partial failures, and visible side effects such as notifications.
- Freshness guarantees and endpoint-specific access or tenant scope.
- Deprecation and the replacement operation.

Do not turn an incidental code path into a public guarantee. If ordering or freshness matters but has no guarantee, state the limitation. Keep field-specific defaults, bounds, enum options, and obtainment links on the field rather than recapping them here. Link a sibling operation only when it helps the reader choose or complete a flow, using `getExternalApiDocumentationUrl`.

Use the central operation ID registry and verify uniqueness in the generated document.

## 3. Request documentation and schema metadata

Let Swagger/OpenAPI express facts it supports: type, format, enum, default, requiredness, nullability, numeric bounds, string lengths, array limits, and patterns. Match actual validation and behavior. Do not repeat these facts as sentences or option lists in descriptions.

- Reuse the canonical enum, allowed-value array, or constant map used by the public contract. Select keys or values according to the actual wire representation; include only the supported public subset. Do not blindly export an internal map or numeric enum's reverse mappings.
- Pass those values through the Swagger decorator's `enum` metadata. Reuse existing policy constants for defaults and bounds. Do not create a documentation-only copy of a value list or a helper for a single trivial expression.
- When individual options need explanation beyond their names, derive those explanations from an existing consumer-safe value/label or value/meaning map. A dynamic list that merely repeats the enum is still duplication. If no suitable mapping exists, explain only the non-obvious semantics needed; do not invent meanings from internal labels or introduce a second exhaustive catalog.
- Keep examples representative, not exhaustive. Verify that they remain valid members of the generated schema.

Write field prose only for information the name and metadata leave unclear: which resource an ID identifies, where to obtain it, units or timezone assumptions, the meaning of omission, or which response field a filter targets. Link obtainment endpoints on the relevant field. For a relationship between fields, explain the rule once on the containing schema or operation; use a short cross-reference only where needed to make it discoverable.

For example, a status field's description can say “Filter by payment status.” Its `enum` metadata supplies the allowed values from the existing contract constant; the description must not append “Possible values: …”. A page-size limit belongs in schema bounds, not another sentence in the controller description.

If the field name and schema are sufficient, omit redundant prose and justify the coverage warning. A documented constraint without runtime enforcement is a finding, not permission to change validation.

## 4. Response documentation

Make every field interpretable using its name, schema, and only the additional prose it needs. Explain non-obvious business meaning, units, or how to use an output in a later request. Apply §3's rules to response enums and other metadata too.

Encode nullability and optionality in the schema; explain what null or absence means only when needed. State collection ordering and empty-state behavior once at the relevant collection or operation. Explain status values that require different consumer actions without reproducing the full option list.

Make `doc.ok` say what was returned or completed in a short sentence. Do not use it to repeat the operation description or enumerate response fields.

If a field has no defensible consumer use, report a possible exposure defect to `audit-external-api-port`; do not hide the field or invent a use for it.

## 5. Error documentation

Match `errors: [...]` to reachable, externally visible operation-specific error codes in both directions. Use central definitions through `getErrDefinition`. Keep shared authentication and validation behavior in the overview or shared error documentation rather than repeating it per operation.

Explain the condition and useful recovery action in the error scenario itself: “One or more badge IDs are unavailable. Fetch valid IDs from List Badges.” Link the named operation when appropriate. Do not repeat the error catalog in the operation description or narrate internal validation order. DTO validation does not need a scenario for every field constraint.

## 6. Examples

Use realistic, redacted platform data; credentials remain placeholders such as `<your-api-key>`. Avoid generic values such as `"string"` or `"foo"`.

Keep request and response examples coherent: related IDs agree, counts and timestamps make sense. Prefer captured runtime evidence when available. Add an example when it clarifies a meaningful combination or response shape; do not duplicate schema-generated examples or enumerate every possible option.

## 7. Style and voice

Write like a developer explaining an API to another developer: direct verbs, familiar words, present tense, and short complete sentences. Address the reader as “you” when giving an action. Use public domain terms consistently.

- Prefer “Returns certificates issued to this learner” to “This endpoint enables consumers to retrieve the set of certificate resources associated with the specified learner.”
- Prefer “Omit this field to include all courses” to “It is important to note that omission of this parameter results in the absence of course-based filtering.”
- Cut introductions such as “This endpoint allows you to,” repeated “Please note,” and generic claims of seamless, robust, or comprehensive behavior.
- Avoid formulaic headings, repeated caveats, and warnings for ordinary behavior. Highlight destructive effects when the reader must act on them.
- Read the page as one document. Delete sentences that repeat its schema, another description, or the overview. Do not add prose to satisfy a character count or make every field look equally documented.

## 8. One authoritative home per fact

| Fact | Owning location |
| --- | --- |
| Authentication, tenant header, envelope, global rate limit, common error shape | Overview in `external-api-document.ts` |
| Allowed values, defaults, formats, bounds, requiredness, nullability | Swagger/OpenAPI schema metadata |
| Field meaning, units, source of an identifier, non-obvious value semantics | Relevant DTO property or parameter description |
| Shared pagination or other reusable field semantics | Existing shared DTO/schema |
| Endpoint purpose, interactions across fields, retry behavior, side effects | Operation description or containing schema, whichever owns the rule |
| Error condition and recovery | Error scenario |
| Domain orientation | Tag description in `buildExternalApiDocumentOptions` |

Reference the owning location instead of copying its text. Reuse shared DTO metadata where semantics match; do not generalize an endpoint-specific rule into a shared schema. An endpoint deviation from a global convention belongs on that endpoint, stated explicitly. Correct stale shared documentation at its source within scope, and account for affected consumers.

## 9. Honesty and final review

Trace claims to current code, packet rows, or captured responses in working notes. Verify existing prose too. When sources disagree, describe verified current behavior and report the discrepancy; never document an aspiration or silently fix runtime behavior.

Inspect the regenerated document for missing integration facts, duplicate explanations, internal details, and enum/default/constraint drift. A clean coverage report cannot establish these qualities. A justified missing description is preferable to filler. Report unresolved behavior or exposure questions instead of turning them into confident prose.
