# GitHub review operations

Use available authenticated GitHub APIs or CLI and native stack tooling. Discover capabilities rather than assuming a particular connector. Keep GitHub IDs, review requests, and source revisions in the checkpoint.

## Snapshot the whole comparison

Read PR head/base refs and SHAs, state, draft state, reviews, checks, and thread conversations. With GraphQL, use `reviewThreads` and include `id`, `isResolved`, `isOutdated`, anchors, and each comment's author, body, URL, timestamps, and commit association. Paginate both the outer threads and nested comments. Read review bodies and issue comments separately: not all findings are inline threads.

Record review IDs, reviewed commit SHAs, submission times, and bot identity. Identify the actual configured Codex reviewer from the repository's integration and history; do not accept an arbitrary author's thumbs-up as Codex approval. Read subsequent human discussion before acting on a previously resolved finding.

Pin the base as well as the head. A changed parent layer can invalidate a child's reviewed diff without changing the child's head. Restacking, retargeting, or materially changing conditions requires renewed applicable review evidence. Do not carry a top-layer review across the rest of the stack.

## Publish without duplication

Before every external write, recheck relevant heads and discussion. If they changed, refresh the evidence and intended action first. After a successful write, record its returned ID/URL and verify the remote result. On an ambiguous network error, inspect GitHub before retrying.

Reply in the original inline thread where possible. Distinguish “fixed in <commit>” from “deferred because <scope/parity evidence>.” Include enough source evidence to audit the decision. Use structured body arguments or a body file for multiline CLI comments; never interpolate review text into shell code.

Resolve by the actual thread ID after the reply succeeds, then re-query. Do not dismiss a formal review, remove feedback, or fabricate approval. If permissions prevent a required action, record the blocker and continue independent work without reporting the action as completed.

## Compose a tailored request

Use a PR comment containing `@codex review` followed by the instructions, not a separate instruction message. For example:

```text
@codex review this PR against the approved legacy-parity requirements.
Check the current diff for introduced regressions and unmet acceptance criteria.
Legacy evidence: <repository-accessible permalink and relevant behavior>.
Prior disposition: <thread link and source-backed explanation>.
Reassess that explanation against current code and flag any remaining valid issues.
```

Replace placeholders with actual relevant references. Include the effective custom conditions and explicit user guidance. Keep requests focused on this PR's layer while providing needed stack context. Link evidence accessible to Codex; a local-only filesystem path is not a usable remote reference. If source is unavailable remotely, describe the relevant verified behavior honestly and state the limitation.

Do not instruct Codex to approve, hide genuine findings, or assume prior resolutions are correct. Do not use a fix-task mention: this session owns implementation. Do not change repository-wide review configuration to silence feedback.

Reuse a pending review only when it can be associated with the current head/base and effective instructions. If an older review remains pending after a change, wait for it or reach the timeout before requesting a replacement; do not create overlapping requests that make outcomes ambiguous. Once it completes, request review for the new comparison. Do not count the old outcome toward completion.

## Establish a positive clean outcome

Prefer an identifiable Codex review or completion message explicitly reporting no findings, associated with the current reviewed commit and comparison. A completed review with an empty body is insufficient without another positive clean signal.

A Codex 👍 can count only when the integration uses it as a clean outcome and it is demonstrably associated with this review request/comparison. Record the request comment ID, bot identity, baseline reactions, head/base at request time, conditions, and observed outcome. For reactions without commit metadata, require a fresh request with no prior qualifying reaction, a newly observed bot clean reaction on that request, and an unchanged head/base since the request. If attribution is ambiguous, do not infer success; await explicit evidence or discuss the missing signal.

An 👀 reaction acknowledges processing; it is not completion. A historical PR-level 👍, elapsed time, no comments, resolved threads, passing CI, or human approval does not substitute for a current clean Codex result. A review containing findings remains non-clean even after this agent resolves them. Require a subsequent clean outcome.

Take a final snapshot across all selected PRs. New feedback, changed comparisons, or contradictory outstanding requests reopen the relevant work. Record merge requirements separately from this review gate.

Official reference: [Review GitHub pull requests with Codex](https://learn.chatgpt.com/docs/third-party/github). It documents tailored `@codex review` comments and review outcomes; verify integration-specific signals when the observed behavior differs. Do not assume every custom Codex GitHub Action exposes the same signals.
