# Issue tracker: GitLab

Store specifications and implementation tickets as GitLab issues.

## Operations

Prefer an authenticated GitLab connector or API when available. Otherwise use the authenticated `glab` CLI from inside the repository.

- Create, read, list, comment on, label, and close issues through the selected GitLab capability.
- Read an issue's complete description, labels, and relevant notes when it is a source.
- Infer the project from the current Git remote; do not guess another namespace or project.
- Create blockers before blocked issues so real identifiers can be referenced.
- Prefer native blocking links when the GitLab tier supports them. Otherwise write a visible `Blocked by: #<number>` section.
- Apply only labels already configured in `docs/agents/triage-labels.md`; do not create labels implicitly.

When a skill says to publish to the issue tracker, create a GitLab issue and return its URL.

