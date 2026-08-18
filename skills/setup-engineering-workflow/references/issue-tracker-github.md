# Issue tracker: GitHub

Store specifications and implementation tickets as GitHub issues.

## Operations

Prefer an authenticated GitHub connector or API when available. Otherwise use the authenticated `gh` CLI from inside the repository.

- Create, read, list, comment on, label, and close issues through the selected GitHub capability.
- Read an issue's complete body, labels, and relevant comments when it is a source.
- Infer the repository from the current Git remote; do not guess a different owner or repository.
- Create blockers before blocked issues so real identifiers can be referenced.
- Prefer GitHub's native issue dependencies and sub-issues. If unavailable, write a visible `Blocked by: #<number>` section.
- Apply only labels already configured in `docs/agents/triage-labels.md`; do not create labels implicitly.

When a skill says to publish to the issue tracker, create a GitHub issue and return its URL.

