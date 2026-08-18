---
name: to-spec
description: Synthesize the current conversation and codebase context into a detailed, implementation-light specification, then publish it to the configured issue tracker or a local Markdown fallback. Use only when the user explicitly asks to create, write, or publish a spec from requirements already discussed; do not use when a full requirements interview is still needed.
disable-model-invocation: true
---

# To Spec

Turn existing context into a specification. Do not reopen requirements discovery or conduct a broad interview; synthesize what is already known and expose assumptions honestly.

## Process

### 1. Gather established context

Read the current conversation, any referenced plan or prototype, repository instructions, relevant code, `docs/agents/domain.md` when present, the applicable `CONTEXT.md`, and relevant ADRs. Use canonical project vocabulary and respect recorded decisions.

If sources contradict one another, identify the conflict in the draft instead of silently choosing. Ask only when the contradiction makes a responsible specification impossible.

### 2. Choose testing seams

Identify the highest existing public seams through which the requested behavior can be verified. Prefer fewer, higher seams over new or internal ones. Propose new seams only when existing public interfaces cannot express the behavior.

Before publication, ask the user to confirm the proposed seams unless they were already agreed in the conversation or source material. This is a focused confirmation, not another requirements interview.

### 3. Resolve the publication destination

Read `docs/agents/issue-tracker.md` and `docs/agents/triage-labels.md` when present. If no destination was supplied and the tracker configuration is missing, ask the user to invoke `setup-engineering-workflow` before external publication. If that skill is unavailable or the user prefers a one-off local artifact, use the local fallback.

Use this precedence:

1. A destination explicitly supplied by the user.
2. Repository instructions or `docs/agents/issue-tracker.md`.
3. An issue tracker unambiguously established by the repository remote and available tools.
4. A local fallback at `.scratch/<feature-slug>/spec.md`.

Do not guess credentials or publish to an external tracker whose ownership is ambiguous. When using the local fallback, clearly report that no external issue was created.

Use the configured ready-for-agent label when one exists. Otherwise use `ready-for-agent` only if that label already exists; do not create labels implicitly.

### 4. Write the specification

Use this structure:

```markdown
## Problem Statement

Describe the user's problem from the user's perspective.

## Solution

Describe the intended solution from the user's perspective.

## User Stories

1. As a <actor>, I want <capability>, so that <benefit>.

Provide a complete numbered set covering primary flows, important alternatives, failures, permissions, and lifecycle behavior relevant to the feature.

## Implementation Decisions

- Modules or boundaries that will change
- Public interfaces and contracts
- Technical clarifications and architectural decisions
- Schema, API, and interaction decisions

## Testing Decisions

- The external behavior tests must verify
- The confirmed seams and modules under test
- Relevant testing prior art in the repository

## Out of Scope

State explicit exclusions and nearby work that is not part of this specification.

## Further Notes

Record assumptions, source references, unresolved contradictions, and useful context.
```

Avoid specific file paths and working code snippets because they become stale. If a prototype produced a compact state machine, reducer, schema, or type shape that records a decision more precisely than prose, include only that decision-rich excerpt and identify it as prototype-derived.

### 5. Publish and report

Create one specification in the resolved destination. Apply the configured ready label when available. Return the created issue link or local path, note any label that could not be applied, and list assumptions that remain visible in the spec.
