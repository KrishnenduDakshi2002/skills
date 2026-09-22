# Coverage dimensions

Read while tracing selected endpoints and reviewing their outlines. Apply every relevant dimension; derive expectations from the actual contract and behavior. Record a brief reason in the handoff for material exclusions. Do not invent unsupported features or promises of exhaustive permutation coverage.

| Dimension | Cases to derive where applicable |
|---|---|
| Inputs and transformation | Required/optional fields; omitted vs undefined/null/empty/zero/false; scalar/array/object mismatch; string coercion; whitespace/case; IDs; enums; nested validation; unknown fields; list tokens; size, date, and numeric boundaries immediately below/at/above limits. |
| Authentication and scope | Missing/invalid/revoked credentials; insufficient permission/scope; wrong host/tenant/creator; foreign resource IDs and nested references; no data leakage or state change on rejection. Exercise guards themselves when guarding behavior is in scope. |
| Business states | Allowed and forbidden transitions; inactive/deleted/expired/pending/completed states; ownership and eligibility; merged-state update validation; mutually dependent fields; policy interactions; observable legacy quirks. |
| Reads and queries | Empty/single/multiple results; filters separately and in meaningful combinations; sorting and ties; pagination/defaults/limits/counts/cursors; missing relations; soft deletion; joins/aggregations; tenant isolation. Use real repository queries for these outcomes. |
| Writes | Persisted values/defaults/references; create vs sparse update vs explicit clearing; unchanged field preservation; no-op updates; duplicate keys; repeated request behavior; idempotency; bulk partial success/failure; delete semantics and cascades. |
| Public success contract | Status and headers where specified; exact envelope and nested key sets; full vs summary resource; types/formats/units/enum values; IDs/dates/URLs; ordering; pagination metadata; omission vs null vs empty; explicit absence of internal fields/secrets. |
| Failure contract | Validation/auth/not-found/conflict/domain failures; provider/database failure mapping; stable error code/message/details; sanitized errors; failure after partial work; rollback/compensation and preserved state. Avoid binding tests to incidental stack traces. |
| Side effects | Queue/webhook/email/payment/cache payloads and destination/scope; exactly-once/duplicate/suppressed effects as the contract specifies; cache invalidation/expiry; effects absent on failure; observable ordering when it matters. Use fakes, never real providers. |
| Time and money | Inclusive/exclusive date boundaries, expiry and time zones, rounding/precision/currency, zero/negative amounts, discounts/tax/installments; controlled clock and explicit values. |
| Consistency | Concurrent requests, uniqueness races, transaction rollback, stale state, retries, repeated delivery, atomic state transitions. Cover actual guarantees and known risks with a memory replica set if required. |

Place each claim at the boundary that can prove it. For example, mapper unit tests establish a projection but cannot establish that the response pipeline actually uses it. Repository integration can establish tenant filtering but a mocked repository returning only the right tenant cannot.

Make negative cases observable: check both the rejection and absence of unintended persisted changes/side effects. Test the public response independently of schema defaults so adding an internal schema field cannot silently update the expected response.

Do not enumerate an arbitrary Cartesian product. Explicitly cover rule interactions that change outcomes, including invalid input combined with foreign ownership, update fields combined with retained state, and dependency failure after an earlier write when those paths exist.
