# GitHub review operations

Use available authenticated GitHub APIs or CLI and native stack tooling. Discover capabilities rather than assuming a particular connector. Keep GitHub IDs, review requests, and source revisions in the checkpoint.

## Snapshot the whole comparison

Read PR head/base refs and SHAs, state, draft state, reviews, checks, and thread conversations. With GraphQL, use `reviewThreads` and include `id`, `isResolved`, `isOutdated`, anchors, and each comment's author, body, URL, timestamps, and commit association. Paginate both the outer threads and nested comments. Read review bodies and issue comments separately: not all findings are inline threads.

Record review IDs, reviewed commit SHAs, submission times, and whether each author is a bot or a human. Identify the actual configured automated reviewers from the repository's integrations and history; do not accept an arbitrary author's comment or reaction as a reviewer's outcome. Read subsequent human discussion before acting on a previously resolved finding.

Record the scope baseline from the same snapshot: the PR's stated intent, the files changed against its base, and the changed-line count. Use the merge-base comparison GitHub shows for the PR, so a parent layer's changes are not counted in a child.

Pin the base as well as the head. A changed parent layer can alter a child's diff without changing the child's head. After a restack or retarget, compare each PR's own diff before and after, for example with a range diff. A PR whose diff is unchanged keeps its review evidence; one whose diff changed needs a review of the new comparison. Do not carry a top-layer review across the rest of the stack.

## Publish without duplication

Before every external write, recheck relevant heads and discussion. If they changed, refresh the evidence and intended action first. After a successful write, record its returned ID/URL and verify the remote result. On an ambiguous network error, inspect GitHub before retrying.

Reply in the original inline thread where possible. State the disposition first, then the evidence:

- **Fixed:** the commit and the verification that covers it.
- **False positive:** the code path that disproves the claim.
- **Not worth fixing:** why no consequence follows, or why a lesser one misses the bar for this round.
- **Deferred:** why the defect is real and what places it outside this PR.
- **Repeat:** a link to the earlier reply that settled the same claim.

Include enough source evidence to audit the decision without rereading the code. Use structured body arguments or a body file for multiline CLI comments; never interpolate review text into shell code.

Resolve by the actual thread ID after the reply succeeds, then re-query. Resolve a human's thread only after the fix it asked for is delivered or the user has decided the outcome and the reply says so. Do not dismiss a formal review, remove feedback, or fabricate approval. If permissions prevent a required action, record the blocker and continue independent work without reporting the action as completed.

## Compose a tailored request

Request a review only when the loop rules call for one. Use the reviewer's documented trigger. For Codex, that is a PR comment containing `@codex review` followed by the instructions, not a separate instruction message. For example:

```text
@codex review the changes since <last reviewed commit> on this PR.
Check whether those changes introduce a regression or leave an acceptance criterion unmet.
PR intent: <one-line scope from the baseline>.
Settled findings: <thread links with their dispositions and evidence>.
Raise a settled finding again only with new evidence that the disposition is wrong.
```

Replace placeholders with actual relevant references. Include the effective custom conditions and explicit user guidance. Keep requests focused on this PR's layer while providing needed stack context. Link evidence accessible to the reviewer; a local-only filesystem path is not a usable remote reference. If source is unavailable remotely, describe the relevant verified behavior honestly and state the limitation.

Do not instruct the reviewer to approve, hide genuine findings, or assume prior dispositions are correct. Do not use a fix-task mention: this session owns implementation. Do not change repository-wide review configuration to silence feedback.

Reuse a pending review only when it can be associated with the current head/base and effective instructions. If an older review remains pending after a change, wait for it before requesting the review of the new head; do not create overlapping requests that make outcomes ambiguous. At the timeout, checkpoint and discuss rather than requesting a replacement. Judge the older review's findings when it completes, but do not treat it as covering the new head.

## Establish that a review completed

A round needs a completed review that can be tied to the current head and comparison. A review completes in one of two ways:

- **With findings:** an identifiable review or comment set from the configured reviewer, associated with the reviewed commit. Judge every finding in it.
- **Without findings:** an explicit completion message or review reporting none, associated with the reviewed commit. A completed review with an empty body is insufficient without another positive signal.

A reviewer's 👍 reaction can count as completion without findings only when the integration uses it that way and it is demonstrably associated with this review request and comparison. Record the request comment ID, bot identity, baseline reactions, head/base at request time, conditions, and observed outcome. For reactions without commit metadata, require a fresh request with no prior qualifying reaction, a newly observed bot reaction on that request, and an unchanged head/base since the request. If attribution is ambiguous, do not infer completion; await explicit evidence or discuss the missing signal.

An 👀 reaction acknowledges processing; it is not completion. A historical PR-level 👍, elapsed time, no comments, resolved threads, passing CI, or human approval does not show that a review of the current head completed.

A completed review with findings does not keep the loop open by itself. The loop settles when judging those findings leaves nothing blocking and nothing pending, even though the reviewer never reported a clean result.

Take a final snapshot across all selected PRs. New feedback, changed comparisons, or contradictory outstanding requests reopen the relevant work. Read required checks and mergeability from the same snapshot for the verdict.

Official reference: [Review GitHub pull requests with Codex](https://learn.chatgpt.com/docs/third-party/github). It documents tailored `@codex review` comments and review outcomes; verify integration-specific signals when the observed behavior differs. Do not assume every custom Codex GitHub Action or other reviewer exposes the same signals.
