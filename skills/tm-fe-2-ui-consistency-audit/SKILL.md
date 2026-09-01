---
name: tm-fe-2-ui-consistency-audit
description: Audit and fix UI and utils consistency issues in the current branch or PR changes of the tagmango-frontend-2.0 repo. Use when asked to audit UI consistency, enforce shared components (Card, Badge, Input, Field, DataTable, button presets), reduce forceful className overrides, trim verbose comments, or check version-1 (tagmango-web-platform) behavioral parity in frontend-2.0 changes.
disable-model-invocation: true
---

# TagMango Frontend 2.0 UI Consistency Audit

Audit the current PR's changed files for UI and utils consistency, then fix the confirmed findings. Work findings-first: list everything before editing anything.

## Ground rules

- Read `AGENTS.md`, `CONTRIBUTING.md`, and `architecture.md` first, if present in the repo.
- Locate and read `CATALOG.md` — it documents the shared components and utils; treat it as the source of truth for what already exists.
- Inspect the actual changed files and nearby shared components before editing.
- Do not stage or commit anything unless the user explicitly asks.
- Keep changes tightly scoped to the touched UI.
- Preserve the current visual output unless the user explicitly asks for a redesign.

## Scope lock

- Capture the initial PR file list with `git diff --name-only <base>...HEAD` before doing anything else.
- Only edit files from that list.
- Nearby and shared files may be inspected but remain read-only.
- If a fix requires editing a file outside the PR diff, report it and ask first.
- Ignore unrelated pre-existing staged or unstaged changes.
- Classify every finding as **PR-scoped**, **adjacent**, or **out-of-scope**.

## Focus areas

### 1. Replace raw HTML UI patterns with existing shared components

Where a shared component already exists, use it:

- Card/surface wrappers → `Card` or the existing surface component
- Status/count labels → `Badge`
- Inputs/search groups → `Input` / `InputGroup`
- Label/description/control rows → `Field` / `FieldLabel` / `FieldDescription`
- Dropdowns, menus, buttons, dialogs → existing UI primitives
- Tables/lists → the governed `DataTable` when applicable

### 2. Reduce forceful className overrides

- Avoid hard-coded theme-sensitive colors, shadows, borders, radii, spacing, and state styles.
- Prefer component variants, props, slots, or small shared-component extensions.
- Keep local `className` only for layout or feature-specific structure.
- Do not make broad changes to shared components unless the need is real and reusable; if extending one, keep the API small and backward-compatible.
- Treat `rounded-full` overrides as wrong by default — they break under theme changes. Replace them with the themed radius the component system provides.

### 3. Maintain the existing UX

- Keep grouping and interaction patterns that already work; do not flatten useful grouped controls.
- Preserve responsive behavior.
- Avoid unrelated refactors.
- Check `button-presets` for call sites where an existing preset can replace a bespoke button. If nothing comes close, create a new preset — generic enough for other use cases — and use it.

### 4. Trim unnecessary comments

- Keep comments only for code that is genuinely ambiguous and cannot be made clear by the code itself.
- Comments should answer *why*, and record nuances other devs need to know — minimal, not verbose.
- Delete comments that restate what the code already says.

### 5. Maintainability and scalability of code architecture

- Any new code architecture introduced by the changes must be scalable, maintainable, and intuitive to discover.
- Prefer simplification: if an existing structure can be made simpler, propose that.
- Before changing or deciding on architecture, ask the user with the proposed architecture and its pros and cons versus the existing one.
- Flag any architectural pattern likely to drift and become hard to maintain as soon as you spot it.

### 6. Correctness and version-1 parity

- These changes are version 2, based on version 1 (the `tagmango-web-platform` project). UI/UX may be improved in v2, but be very careful about behavioral differences.
- Flag every behavioral change from version 1 to the user; only proceed with it once they agree.

### 7. Code cleanness

- Keep types as strict as possible wherever possible, clean and organized.

### 8. Reusability, efficiency, and de-duplication

- Review from a reusability, efficiency, de-duplication, and stale-comment-removal angle.
- Verify no new code blocks, variables, functions, or files were created where existing ones could have been used.

## Process

1. List all findings first, with file references, each classified PR-scoped / adjacent / out-of-scope.
2. Fix PR-scoped findings one by one, choosing the smallest change that improves consistency. Pause and ask before anything requiring architecture decisions, out-of-diff edits, or behavioral changes from version 1.
3. After edits, run the repo's format, lint, and typecheck commands when feasible.
4. Report exactly what changed, what checks passed or failed, and confirm nothing was staged or committed.
