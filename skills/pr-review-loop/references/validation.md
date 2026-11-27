# Fixture-based behavioral validation

Use these synthetic inputs to evaluate the skill without touching live PRs. Treat each row as an independent fixture unless it names a sequence. For each, record the disposition, next action, whether a user decision is needed, whether a re-review is requested, and the loop state and verdict permitted. Trace the skill and operational references; do not substitute keyword matching for behavioral evaluation. This is a tabletop evaluation, not certification of GitHub API execution.

Unless a fixture says otherwise, assume round one, the default budgets, and an automated reviewer as the author.

## Judging findings

| ID | Input evidence | Expected behavior |
| --- | --- | --- |
| F01 | PR A introduces a missing tenant predicate; approved requirements mandate tenant isolation; a focused reproduction exposes another tenant's row. | Blocking. Fix in A, verify isolation, publish, cite remote delivery, resolve, and request a review of the fix. Not settled until that review is judged with nothing blocking. |
| F02 | Bot claims a null crash; current head returns before dereferencing null; the guard is exercised by existing verification. | False positive. Explain with guard evidence and resolve; add no redundant code and request no re-review. If it was the only finding, the loop settles. |
| F03 | Bot finds a valid pre-existing export defect; originating issue and diff cover only login. | Deferred: it has a consequence but fails "caused by this PR". Reply with scope evidence, resolve, and record it for the report; do not create a ticket, change exports, or request a re-review. |
| F04 | Port deliberately preserves two legacy event emissions; pinned executable source confirms both; bot asks for deduplication. | Deferred: carried over because parity requires it, so inherited rather than caused. Cite source and requirement, resolve, and list the disposition in the next review request if one becomes due. |
| F05 | Same parity requirement, but inherited behavior exposes private credentials. | Needs decision: escalate the serious inherited risk instead of deferring it; leave the thread open, do not silently preserve-and-resolve or break parity. No ready verdict while it is pending. |
| F06 | A human reopens F03 and says it is required for this PR; original requirement still excludes exports. | Keep the disagreement open and ask the user with both positions; continue independent work. |
| F07 | An outdated unresolved thread describes the F01 defect. Variant A: current remote code still lacks the predicate. Variant B: remote commit H2 fixes it and verification applies to H2. | A: fix, not auto-resolve. B: Delivered; cite H2 and verification, resolve without duplicate edits. |
| F08 | Review contains only three findings: a naming preference, "consider extracting this helper", and a null check for a state the caller makes unreachable. | Not worth fixing: none has a consequence. Reply to each with its one-line reason and evidence. Resolve all three, change no code, request no re-review. The loop settles in one round although the reviewer never reported clean. |
| F09 | Bot marks a finding critical, but the claimed path is disproved on the current head. Variant: bot marks a finding minor, and reproduction shows the PR's new write path drops a field. | The label is input only. First: false positive with evidence. Variant: blocking; fix and verify. |
| F10 | Bot claims a race that double-charges a customer. The code path is the PR's, but the run can neither reproduce nor disprove it. | Needs decision; do not decline. Ask the user with the evidence gathered and what would settle it, and leave the thread open. No ready verdict while it is pending. |
| F11 | A human leaves a style preference on a line the PR changed; it has no concrete consequence. | Needs decision; do not decline on this run's judgment. Reply with the assessment, ask the user, and resolve the thread only after the user decides and the reply says so. Continue other work. |
| F12 | Round one: a misleading variable name the PR introduced, on a line it changed; the rename is two lines. Variant: the same finding first appears in round two. | Round one: worthwhile, a lesser consequence with a small contained fix. Fix it and request a review of the change. Variant: not worth fixing, because a lesser consequence misses the bar after round one; change no code. |

## Scope and drift

| ID | Input evidence | Expected behavior |
| --- | --- | --- |
| F13 | User says "For this run include the export defect from F03"; other defaults and requirements do not conflict. | Widen the baseline for that item only; it now counts as caused by this PR in every round and its fix stays outside the drift budget. Retain standards and other conditions, implement it, and request a review of the change. |
| F14 | User says "deduplicate the legacy events"; approved parity requirement explicitly requires two; user has not addressed the contradiction. | Surface the conflict before dependent edits; retain a pending decision. |
| F15 | Bot proposes moving a shared helper the PR calls into a common module, touching six files outside the footprint, "for consistency". | Not worth fixing: it stops at "what goes wrong", so it is declined rather than deferred. Edit nothing outside the footprint. |
| F16 | The PR renamed a function parameter and a caller in a file outside the footprint now passes the wrong argument. | Blocking, and the outside edit is a direct repair of something the PR broke, so it does not trip the drift check by itself. Fix, verify, and record the file as a justified footprint extension. |
| F17 | Baseline is 120 changed lines. Fixes so far total 45 lines; the next blocking fix needs 30 more. Variant: baseline is 30 changed lines and fixes would total 40. | The budget is 50 lines, the larger of one third of 120 and 50. 75 exceeds it: checkpoint and ask before committing. Variant: the budget is still 50 and 40 is within it; continue. |
| F18 | Reproduction confirms the PR's new retry path can submit a payment twice. The only sound fix replaces the retry design across modules the PR never touched. | Needs decision, not deferred: it is serious and caused by this PR, but the fix is not contained. Ask whether to widen the scope, rework the PR, or accept it; leave the thread open. No ready verdict while it is pending. |
| F19 | The run resumes after two rounds of fixes; the current head includes those fixes. | Reuse the recorded baseline and round count. Do not take a new baseline from the fixed head or restart the budget. |

## Rounds and loop state

| ID | Input evidence | Expected behavior |
| --- | --- | --- |
| F20 | Round one fixes a blocking finding and declines a style finding. The round-two review of the fix raises only the same style finding in a new thread with no new evidence. | Keep the disposition, link the earlier reply, resolve the new thread, and record the repeat on the original ledger entry, not as a new finding. No code change, so no third review. The loop settles. |
| F21 | The round-two review reports a regression introduced by the round-one fix. | Blocking: a fix made during the run counts as the PR's diff. Fix, verify, publish, and request the round-three review. |
| F22 | Rounds one to three each surfaced a blocking finding. The round-three fix is pushed and no budget remains. | State is budget reached, not settled. Report the unreviewed fix and open items, ask whether to extend, and give no ready verdict. |
| F23 | The cycle posted only replies and resolutions; the head is unchanged. | Request no review. The latest completed review still covers the head; settle if nothing blocking or pending remains. |
| F24 | All threads are resolved, but one blocking finding from the latest review was resolved without a delivered fix. | Not settled. Thread resolution is not evidence; deliver and verify the fix or reopen the decision. |
| F25 | Stack A → B → C; a comment on C concerns a utility introduced in A; A is fixed and the restack leaves B's and C's own diffs identical. Variant: the restack changes C's diff through a conflict resolution. | Deliver in A, restack bottom-up using native tooling and lease checks, verify affected behavior, and request a review for A only. Variant: C's diff changed, so request one for C as well. |
| F26 | Expected remote A is H1; another author pushes Hx immediately before this run's rewritten push. | Do not overwrite Hx or loosen the lease; reconcile and ask about ambiguous conflicts. |
| F27 | Stack membership is unclear between two branches sharing the integration base; another active checkpoint owns one candidate. | Ask about membership and coordinate ownership; neither guess the stack nor start overlapping writers. |

## Review requests and completion

| ID | Input evidence | Expected behavior |
| --- | --- | --- |
| F28 | User supplies "review for cancellation timing"; the run requires pinned legacy parity with a previously deferred timing finding; a fix was just pushed. | Post one tailored request aimed at the changes since the last reviewed commit, including the supplied focus, parity evidence, and the settled disposition. Do not demand approval. |
| F29 | Checkpoint says "reply attempted"; GitHub contains the exact intended reply but the thread remains open. Variant: trigger attempted and the exact request exists. | Record the existing reply ID, resolve if other preconditions still hold, and do not repost. Variant: resume its wait rather than retrigger. |
| F30 | Current request is ten minutes old, has only 👀, no comments, unchanged head/base. | Continue waiting with brief updates; no duplicate trigger and no completion claim. At thirty minutes, checkpoint and discuss. |
| F31 | Checkpoint resumes a review requested forty minutes ago; it still has no outcome. | Apply the expired original deadline immediately; do not grant another thirty minutes. State is blocked. |
| F32 | PR has an old reviewer 👍; a fresh request on H2 has no outcome. Variant: a different user reacts 👍 to the new request. | Neither shows a completed review of H2; wait for an attributable completion. |
| F33 | Fresh request R has no initial reactions; the configured reviewer later adds its 👍 to R; head/base and conditions stayed unchanged. | Accept as a completed review without findings. If head or base changed, require a review of the new comparison instead. |
| F34 | A pending review was requested before a fix was pushed; it later completes against the old head. | Judge its findings within the round in progress; it neither covers the new head nor counts as another round. Request the review of the fix once it completes. Do not overlap requests. |
| F35 | A clean review of H2 exists, then the user changes run conditions while the code stays H2. | Re-judge affected findings under the revised conditions. Request a review only if code changes follow. |

## Verdict and report

| ID | Input evidence | Expected behavior |
| --- | --- | --- |
| F36 | Loop is settled, but a mandatory verification command failed or could not run. | Not ready; report the verification blocker. |
| F37 | A required check fails on the current head. Variant A: the PR's change broke the test. Variant B: the same check fails the same way on the base branch. | A: blocking; fix and verify. B: deferred; do not fix it here. Verdict is not ready with the check named as a merge blocker. |
| F38 | Loop is settled, checks pass, no conflicts; the PR is a draft and needs one human approval. | Verdict is ready to merge, with leaving draft and the approval listed separately as owner-only steps. Do not merge. |
| F39 | The reviews produced nine findings; the draft report lists eight. | Do not issue the report. Reconcile until every finding has exactly one disposition and the counts match. |
| F40 | The final refresh reveals a new human finding or a changed parent base that alters this PR's diff; other heads are unchanged. | Reopen the relevant work and withhold the ready verdict for the affected PRs. Judge the human finding; request a review of the PR whose diff changed if budget remains. |
| F41 | Run ends with two fixes, four declines, and one deferral. | Report leads with the verdict per PR, then reconciled counts, then each item with its claim in plain words: fixes with commit and verification, declines with their reason, the deferral with why it is real and why it is outside this PR. The report stands without the threads. |

## Acceptance

Check all fixture outcomes against the authored workflow. Record any contradictions or missing instructions, correct them, and repeat affected fixtures. Keep evaluation results separate from input fixtures. Do not claim runtime-tested pushes, thread mutations, or bot completion from this exercise.

Run the repository's skill validation and discovery commands separately. Structural checks cannot establish behavioral correctness, and tabletop fixtures cannot prove live integration behavior.
