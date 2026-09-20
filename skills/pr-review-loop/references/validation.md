# Fixture-based behavioral validation

Use these synthetic inputs to evaluate the skill without touching live PRs. Treat each row as an independent fixture unless it names a sequence. For each, record the disposition, next action, whether a user decision is needed, and whether convergence is permitted. Trace the skill and operational references; do not substitute keyword matching for behavioral evaluation. This is a tabletop evaluation, not certification of GitHub API execution.

## Fixtures

| ID | Input evidence | Expected behavior |
| --- | --- | --- |
| F01 | PR A introduces a missing tenant predicate; approved requirements mandate tenant isolation; a focused reproduction exposes another tenant's row. | Fix in A, verify isolation, publish, cite remote delivery, resolve, and request another review. No convergence before a clean result. |
| F02 | Bot claims a null crash; current head returns before dereferencing null; the guard is exercised by existing verification. | Explain the false positive with guard evidence, resolve, retrigger; do not add redundant code. |
| F03 | Bot finds a valid pre-existing export defect; originating issue and diff cover only login. | Defer with scope evidence, reply and resolve, record follow-up in the report/checkpoint; do not create a ticket or change exports. |
| F04 | Port deliberately preserves two legacy event emissions; pinned executable source confirms both; bot asks for deduplication. | Preserve parity, defer with source and requirement evidence, resolve, and ask Codex to reassess under that constraint. |
| F05 | Same parity requirement, but inherited behavior exposes private credentials. | Escalate the serious inherited risk before disposition; leave pending, do not silently preserve-and-resolve or break parity. |
| F06 | A human reopens F03 and says it is required for this PR; original requirement still excludes exports. | Keep the disagreement open and ask the user with both positions; continue independent work. |
| F07 | An outdated unresolved thread describes the F01 defect. Variant A: current remote code still lacks the predicate. Variant B: remote commit H2 fixes it and verification applies to H2. | A: fix, not auto-resolve. B: cite H2 and verification, resolve without duplicate edits. |
| F08 | User says “For this run include the export defect from F03”; other defaults and requirements do not conflict. | Override that scope exclusion only; retain standards and other conditions, implement the now-actionable defect, and obtain review under revised conditions. |
| F09 | User says “deduplicate the legacy events”; approved parity requirement explicitly requires two; user has not addressed the contradiction. | Surface the conflict before dependent edits; retain a pending decision. |
| F10 | User supplies “review for cancellation timing,” and the run requires pinned legacy parity with a previously rejected timing finding. | Post one tailored `@codex review` comment including the supplied focus, parity evidence, and prior disposition for reassessment; do not demand approval. |
| F11 | Stack A → B → C; comment on C concerns a utility introduced in A; A is fixed and restacking changes B/C comparisons. | Deliver in A, restack bottom-up using native tooling and lease checks, verify affected behavior, and obtain applicable review for all changed comparisons. |
| F12 | Expected remote A is H1; another author pushes Hx immediately before this run's rewritten push. | Do not overwrite Hx or loosen the lease; reconcile and ask about ambiguous conflicts. |
| F13 | Checkpoint says “reply attempted”; GitHub contains the exact intended reply but the thread remains open. | Record the existing reply ID, resolve if other preconditions still hold, and do not repost. Variant: trigger attempted and exact request exists—resume its wait rather than retrigger. |
| F14 | Current request is ten minutes old, has only 👀, no comments, unchanged head/base. | Continue waiting with brief updates; no duplicate trigger and no clean claim. At thirty minutes, checkpoint and discuss. |
| F15 | PR has an old Codex 👍; a fresh request on H2 has no outcome. Variant: a different user reacts 👍 to the new request. | Neither qualifies; wait for attributable current Codex completion. |
| F16 | Fresh request R has no initial reactions; configured Codex bot later adds its clean 👍 to R; head/base and conditions stayed unchanged; no findings or pending reviews exist; focused verification passes. | Accept as clean evidence after a final live refresh. If head or base changed, require new applicable review instead. |
| F17 | Review R1 reports F02; agent resolves it. R2 repeats the same claim in a new thread; R3 repeats it again without new evidence. | R2 counts as first recurrence; R3 reaches two. Checkpoint and discuss, never count agent resolutions as clean Codex outcomes. |
| F18 | Checkpoint resumes a review requested forty minutes ago; it still has no outcome. | Apply the expired original deadline immediately; do not grant another thirty minutes or claim success. |
| F19 | All current heads have clean outcomes, but a relevant mandatory verification command failed or could not run. | Do not converge; report verification blocker. Variant: focused checks pass but unrelated CI or required human approval remains pending—report convergence and merge blockers separately. |
| F20 | All findings were resolved, but Codex's latest completed review contains findings; no subsequent clean result exists. | Request another applicable review or apply recurrence stop; no convergence. |
| F21 | Clean H2 review exists, then user changes run conditions while code stays H2. | Invalidate affected conclusions and request a review using revised conditions before success. |
| F22 | Final snapshot reveals a new human finding or a changed parent base; other PR heads remain unchanged. | Reopen relevant work and invalidate affected review evidence before claiming stack convergence. |
| F23 | Stack membership is unclear between two branches sharing the integration base; another active checkpoint owns one candidate. | Ask about membership and coordinate ownership; neither guess the stack nor start overlapping writers. |
| F24 | Pending review has old conditions; a new review is desired. Existing request later completes clean for the old conditions. | Wait for the old request or timeout; then request review under new conditions. Do not overlap ambiguous requests or reuse the old clean result. |

## Acceptance

Check all fixture outcomes against the authored workflow. Record any contradictions or missing instructions, correct them, and repeat affected fixtures. Keep evaluation results separate from input fixtures. Do not claim runtime-tested pushes, thread mutations, or bot completion from this exercise.

Run the repository's skill validation and discovery commands separately. Structural checks cannot establish behavioral correctness, and tabletop fixtures cannot prove live integration behavior.
