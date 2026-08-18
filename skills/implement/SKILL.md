---
name: implement
description: Implement a defined piece of work from an approved specification, issue, or set of tickets, including focused tests, repository validation, and a final self-review. Use only when the user explicitly asks to implement or complete the referenced work; do not use for planning, ticket decomposition, or review-only requests.
disable-model-invocation: true
---

# Implement

Complete the work described by the user while preserving repository conventions, scope, and unrelated changes.

## Process

### 1. Resolve the source of truth

Read the complete specification or tickets, including relevant comments, acceptance criteria, blocking relationships, and referenced decisions. If multiple sources disagree, follow the most explicit and recent user direction and surface any material conflict before changing code.

Do not begin a blocked ticket. Report unresolved blockers and stop unless the user explicitly authorizes working ahead.

### 2. Inspect the repository

Read applicable agent instructions, coding standards, domain glossaries, ADRs, and the existing implementation around the requested behavior. Inspect the working tree and preserve unrelated user changes. Reuse established primitives, patterns, and public seams.

### 3. Establish the implementation slices

Translate the accepted work into narrow vertical slices. Use testing seams already agreed in the spec or tickets. If no seams were agreed and the choice materially affects architecture or scope, confirm them with the user before writing tests.

### 4. Implement and test incrementally

Read [tdd.md](references/tdd.md) before writing the first test and follow its seam, test-quality, mocking, and red-green rules. When a compatible TDD skill is available, it may be used instead.

Follow this loop:

1. Add one behavior-focused test through a public seam and confirm it fails for the expected reason.
2. Implement only enough production behavior to make that test pass.
3. Repeat for the next slice.

Test externally observable behavior rather than private implementation details. Avoid speculative features, broad cleanup, and horizontal batches of imagined tests. Keep changes inside the approved scope.

Run the narrowest relevant typecheck, lint, and test commands regularly. Use repository-defined commands rather than inventing replacements.

### 5. Validate the complete change

After focused checks pass, run the broadest relevant validation the repository supports, including the full test suite when its cost is reasonable. Distinguish failures caused by the change from pre-existing or environmental failures; never claim a check passed when it did not run successfully.

Exercise runtime or browser behavior when the acceptance criteria require it. Static checks alone do not certify runtime behavior.

### 6. Review against two axes

Read [code-review.md](references/code-review.md) and follow its independent two-axis review. Use parallel subagents when supported; otherwise perform two separate passes without editing between them. A compatible code-review skill may be used instead.

The two axes are:

- **Specification:** verify every acceptance criterion, identify missing or partial behavior, and remove unrequested scope.
- **Standards:** verify repository conventions, public-interface boundaries, duplication, naming, error handling, and test quality.

Fix valid in-scope findings and rerun affected checks.

### 7. Preserve user control of Git and trackers

Do not stage, commit, push, close tickets, change ticket status, or post external comments unless the user explicitly asks for that action. Leave implementation changes unstaged by default.

### 8. Hand off

Report what changed, which checks ran and their outcomes, any remaining gaps or risks, and whether the source specification or tickets appear fully satisfied.
