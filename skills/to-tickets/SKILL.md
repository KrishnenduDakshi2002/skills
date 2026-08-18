---
name: to-tickets
description: Break an approved plan, specification, or conversation into dependency-aware tracer-bullet tickets and publish them to the configured issue tracker or local Markdown files. Use only when the user explicitly asks to create, split, draft, or publish implementation tickets and is available to approve their granularity and blocking relationships before publication.
disable-model-invocation: true
---

# To Tickets

Create narrow, complete vertical slices that each fit in a fresh agent context and declare the tickets that block them.

## Process

### 1. Gather context

Use the plan, spec, or conversation already in context. If the user supplies an issue, URL, or file, fetch and read its complete body and relevant comments. Read repository instructions, `docs/agents/domain.md` when present, applicable domain glossaries, and relevant ADRs.

### 2. Explore the codebase when useful

Inspect enough of the current implementation to make the slices realistic. Use project vocabulary in titles and acceptance criteria. Look for prefactoring that makes the requested change easier: make the change easy, then make the easy change.

### 3. Draft tracer-bullet slices

For normal feature work:

- Cut a narrow but complete path through every required layer rather than creating one ticket per layer.
- Make every completed slice independently demoable or verifiable.
- Size each slice for one fresh agent context.
- Put enabling prefactors before the work they unblock.
- Declare only genuine blocking edges. Tickets without blockers form the initial frontier.

Treat wide mechanical refactors as an exception. Use expand-contract when one change fans across many call sites and no vertical slice can land green:

1. **Expand:** introduce the new form beside the old.
2. **Migrate:** move callers in independently green batches sized by blast radius.
3. **Contract:** remove the old form after every migration completes.

If migration batches cannot remain green independently, sequence them on an integration branch and add a final integrate-and-verify ticket. State that green is promised only at that final point.

### 4. Obtain approval

Present a numbered proposal containing, for every ticket:

- **Title**
- **Blocked by**
- **What it delivers**

Ask whether the granularity is right, whether each dependency genuinely blocks the ticket, and whether anything should be merged or split. Revise until the user approves. Do not publish before approval.

### 5. Resolve the publication destination

Read `docs/agents/issue-tracker.md` and `docs/agents/triage-labels.md` when present. If no destination was supplied and the tracker configuration is missing, ask the user to invoke `setup-engineering-workflow` before external publication. If that skill is unavailable or the user prefers a one-off local artifact, use the local fallback.

Use this precedence:

1. A destination explicitly supplied by the user.
2. Repository instructions or `docs/agents/issue-tracker.md`.
3. An issue tracker unambiguously established by the repository remote and available tools.
4. Local Markdown under `.scratch/<feature-slug>/issues/`.

Publish blockers first so later tickets can reference real identifiers. Prefer native blocking or sub-issue relationships when the tracker supports them; otherwise record a visible `Blocked by` section.

Use the configured ready-for-agent label when one exists. Otherwise use `ready-for-agent` only if it already exists; do not create labels implicitly. Do not close or modify a parent issue.

### 6. Publish

For local Markdown, create one file per ticket in dependency order:

```text
.scratch/<feature-slug>/issues/01-<slug>.md
.scratch/<feature-slug>/issues/02-<slug>.md
```

Use this local template:

```markdown
# <NN> — <Ticket title>

**What to build:** <end-to-end behavior, from the user's perspective>

**Blocked by:** <ticket numbers and titles, or "None — can start immediately">

**Status:** ready-for-agent

- [ ] Acceptance criterion 1
- [ ] Acceptance criterion 2
```

Use this external issue template:

```markdown
## Parent

<Parent reference, when the source was an existing issue>

## What to build

<End-to-end behavior, not a layer-by-layer implementation list>

## Acceptance criteria

- [ ] Criterion 1
- [ ] Criterion 2

## Blocked by

- <Blocking issue reference, or "None — can start immediately">
```

Avoid specific file paths and working code snippets. A compact prototype-derived state machine, reducer, schema, or type shape may be included only when it preserves a decision more precisely than prose; trim it to the decision-rich part and identify its origin.

### 7. Report the frontier

Return links or paths for every published ticket and identify the initial frontier: every ticket whose blockers are already complete. Report any native relationship or label that the tracker could not apply.
