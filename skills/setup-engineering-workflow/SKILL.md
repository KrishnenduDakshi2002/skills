---
name: setup-engineering-workflow
description: Configure a repository's persistent issue-tracker workflow, triage-label vocabulary, domain-document layout, and agent-instruction pointers for the to-spec, to-tickets, grill-with-docs, and implement skills. Use only when the user explicitly asks to set up or reconfigure these engineering workflows for a repository.
disable-model-invocation: true
---

# Setup Engineering Workflow

Configure a repository once so the other engineering skills do not repeatedly infer where work and domain documentation belong. Explore first, show the proposed configuration, obtain confirmation, then write.

## Process

### 1. Explore

Inspect without changing files:

- Git remotes and repository host
- Existing `AGENTS.md` and `CLAUDE.md`, especially workflow-related blocks
- `docs/agents/` from any previous setup
- Root `CONTEXT.md` or `CONTEXT-MAP.md`
- Root and context-specific ADR directories
- `.scratch/` conventions
- Monorepo signals such as workspace configuration and multiple substantial packages
- Available authenticated issue-tracker capabilities

Present what exists, what is missing, and what can be inferred confidently.

### 2. Choose the issue tracker

Recommend the tracker established by the repository remote and authenticated tooling. Otherwise recommend local Markdown. Offer:

- GitHub Issues
- GitLab Issues
- Local Markdown under `.scratch/`
- Another tracker such as Jira or Linear, described by the user

Read the matching reference before drafting:

- [issue-tracker-github.md](references/issue-tracker-github.md)
- [issue-tracker-gitlab.md](references/issue-tracker-gitlab.md)
- [issue-tracker-local.md](references/issue-tracker-local.md)

For another tracker, record the user's workflow precisely rather than inventing commands or capabilities.

### 3. Choose the label vocabulary

Recommend the defaults in [triage-labels.md](references/triage-labels.md). Ask whether the project already uses different label strings. Record mappings rather than creating duplicate labels.

Do not create or modify labels in an external tracker during setup unless the user explicitly requests it.

### 4. Choose the domain-document layout

Recommend one root `CONTEXT.md` and `docs/adr/` for most repositories. Offer a root `CONTEXT-MAP.md` with per-context glossaries and ADRs only when exploration found genuine multiple-domain or large-monorepo signals.

Read [domain.md](references/domain.md) before drafting the configuration.

### 5. Choose agent instruction entrypoints

Use shared files under `docs/agents/` as the source of truth. Add only concise pointers to agent instruction files:

- Update existing `AGENTS.md` for Codex and other compatible agents.
- Update existing `CLAUDE.md` for Claude Code.
- If only one exists, preserve it and ask whether the other should be created for cross-agent use.
- If neither exists, recommend creating both for a Claude Code plus Codex repository, but let the user decide.

Never replace surrounding instructions or append a duplicate workflow block.

### 6. Confirm the draft

Show the user:

- The proposed instruction-file pointer blocks
- `docs/agents/issue-tracker.md`
- `docs/agents/triage-labels.md`
- `docs/agents/domain.md`

Wait for approval or edits before writing.

### 7. Write

Create or update the three shared configuration files and the approved instruction-file blocks. Use this block shape:

```markdown
## Agent workflow

### Issue tracker

<One-line summary>. See `docs/agents/issue-tracker.md`.

### Triage labels

<One-line summary>. See `docs/agents/triage-labels.md`.

### Domain docs

<One-line summary>. See `docs/agents/domain.md`.
```

Update existing blocks in place. Preserve all unrelated content.

### 8. Report

List the created or updated files, summarize the configured tracker and layout, and explain that the user may edit `docs/agents/*.md` directly later.

