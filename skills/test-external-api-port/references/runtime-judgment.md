# Runtime Judgment and Triage

## Contents

1. Oracle precedence
2. Translate before comparing
3. Compare value semantics exactly
4. Write scenarios and state equivalence
5. Persisted-state checks
6. Side effects
7. Verdicts
8. Triage buckets
9. Flakes and environment noise
10. Exploratory findings

## 1. Oracle precedence

Judge each case against the strongest available oracle:

1. A live legacy/core capture of the same intent under equivalent state.
2. Persisted documents before and after each path.
3. The packet's pinned rule rows (`B/V/E/S-###`) with their concrete expected values.
4. The generated OpenAPI document, for shape conformance only.

Every verdict cites at least one. When oracles disagree with *each other* — the live legacy response contradicts the packet's `B-###` row — that is itself a finding (usually a ledger error the runtime just exposed), never a free choice of the more convenient oracle.

## 2. Translate before comparing

The external response legitimately differs from legacy in envelope, field names, and grouping. Before diffing, translate the public response back to domain fields through the packet's `X-###` exposure mapping; the canonical representation tiers define embedded-resource shapes. After translation:

- a value difference is a divergence;
- a public field with no `X-###` row is a divergence (undeclared exposure);
- a mapped field missing from the response is a divergence unless its row declares conditional omission;
- fields the exposure ledger intentionally omits are verified as *absent*, not ignored.

An approved representation change passes only when its decision or exposure row exists. "The new shape is nicer" is not an approval.

## 3. Compare value semantics exactly

Treat absent, `null`, `false`, `0`, empty string, empty array, and empty object as distinct on both wire and persisted comparisons. Check ordering wherever the ledger or legacy capture shows a deterministic order; check rounding, precision, timezone rendering, and units against the equivalence notes' named dimensions. Pagination cases compare metadata and page stability, not just the first page's items.

## 4. Write scenarios and state equivalence

A differential write case is meaningful only when both paths start from equivalent state:

- seed through existing APIs where a route exists (authentic documents); record documented direct inserts as the fallback;
- run legacy and new from a reset or twin-seeded state — never run the new path against state the legacy call just mutated;
- record the seed in `case.json` precisely enough to reproduce it;
- clean up only data this run created, only in a disposable tenant, and record every cleanup action in the artifacts.

When write scenarios are blocked by config or tenant posture, they are reported as `BLOCKED` coverage gaps — a run without them cannot flip the packet to `VERIFIED` unless the packet's write behavior was excluded with a recorded justification.

## 5. Persisted-state checks

Use the testing Mongo MCP connection for targeted before/after reads whenever a rule's expected outcome is persisted state: the exact documents, the fields written, the fields *not* written, timestamps' presence, and clearing semantics (`null` vs removed). Query narrowly by the ids the case created or addressed; never dump collections. The Mongo connection is read-only in spirit — the only permissible mutation is §4 cleanup.

## 6. Side effects

Where the ledger records side effects, attempt observation: queue/outbox collections, notification records, provider sandboxes, logs the environment exposes. Compare presence, payload, and order against the `B-###` rows. What cannot be observed is recorded `NOT_OBSERVABLE` with a reason and carried as a residual risk in the summary and handoff — an unobserved effect is undetermined, not passed.

## 7. Verdicts

- `PASS` — the cited comparison matched; the verdict names the oracle files and any normalized fields.
- `DIVERGENCE` — evidence on both sides captured, difference stated field-by-field, triage bucket assigned.
- `UNEXPECTED` — an observation no ledger row predicted (an extra field, an unlisted error shape, a surprising success). Always a finding: either a ledger gap or an implementation surprise.
- `BLOCKED` — the environment prevented execution (auth failure, missing endpoint, write posture). Never silently converted to a skip.

There is no bare "skipped": a case not run is `BLOCKED` with a reason, or `EXCLUDED` in the plan with a justification.

## 8. Triage buckets

Every `DIVERGENCE` lands in exactly one bucket, with the artifact folder as proof:

| Bucket | Meaning | Action |
|---|---|---|
| `IMPLEMENTATION_BUG` | The new path breaks a source-backed rule | Route to `port-external-api`; packet stays `IMPLEMENTED` |
| `LEDGER_ERROR` | Runtime proved the packet row wrong | Update the row citing the run id as runtime evidence; re-judge dependent cases |
| `MISSING_DECISION` | Behavior changed on purpose but no `D-###` records it | The decision is owed; packet stays `IMPLEMENTED` until recorded |

Never fix product code in this workflow, and never edit a packet row to match the implementation without runtime evidence that legacy actually behaves that way.

## 9. Flakes and environment noise

On a timeout or transport error, retry once after a delay and keep both attempts in the artifacts. Normalize only inherently unstable fields — server timestamps, generated ids, request ids — and list each normalized field with a reason in `verdict.json`; an undeclared normalization is a falsified comparison. If the two paths hit differently-versioned deployments of the same behavior, record the drift in the manifest and treat affected comparisons as reduced-confidence, not as failures.

## 10. Exploratory findings

Beyond the ledger, probe what no row predicted: boundary values, OpenAPI-derived field combinations, unknown fields, oversized arrays, and a consumer walkthrough driving the API from the generated docs alone (the posture of a real MCP agent consumer). Everything surprising becomes an `UNEXPECTED` case folder feeding a ledger or contract finding. Exploratory results never substitute for ledger coverage — they extend it.
