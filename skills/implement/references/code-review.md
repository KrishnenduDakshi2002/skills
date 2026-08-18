# Two-axis code review

Review the completed implementation independently against repository standards and the source specification. Do not let success on one axis mask failure on the other.

## 1. Pin the comparison

Resolve the fixed point established before implementation, normally the starting commit or merge-base. Record the diff command and commit list. Account for pre-existing working-tree changes so the review does not claim or rewrite unrelated work.

Fail early when the fixed point is invalid or the task produced no relevant diff.

## 2. Identify sources

For the specification axis, use the complete originating issue, specification, acceptance criteria, and relevant comments.

For the standards axis, read repository instructions, coding standards, contribution rules, domain glossaries, and applicable ADRs.

## 3. Run independent passes

When parallel subagents are supported, give one the complete standards brief and one the complete specification brief. Do not leak either pass's conclusions into the other.

Otherwise perform two sequential passes without editing between them. Keep separate notes and do not rerank findings across axes.

### Standards pass

Report documented-standard violations with the exact rule and relevant hunk. Also evaluate these heuristic smells, suppressing any that repository standards explicitly endorse:

- **Mysterious Name:** a name does not reveal its role.
- **Duplicated Code:** the same logic shape appears in multiple changed locations.
- **Feature Envy:** behavior reaches into another module's data more than its own.
- **Data Clumps:** the same fields or parameters repeatedly travel together.
- **Primitive Obsession:** a primitive substitutes for a domain concept needing its own type.
- **Repeated Switches:** repeated branching on the same kind or state.
- **Shotgun Surgery:** one behavior requires scattered edits.
- **Divergent Change:** one module changes for unrelated reasons.
- **Speculative Generality:** abstractions or hooks serve no accepted requirement.
- **Message Chains:** callers navigate a long object chain.
- **Middle Man:** a layer mostly delegates without owning policy or behavior.
- **Refused Bequest:** an implementation inherits a contract it mostly rejects.

Treat smell findings as judgment calls, not hard violations. Skip concerns that automated tooling already enforces.

### Specification pass

Report:

- Missing or partial requirements
- Unrequested behavior or scope creep
- Requirements that appear implemented incorrectly
- Acceptance criteria without verification evidence

Quote or precisely reference the source requirement for every finding.

## 4. Aggregate and fix

Present findings under separate `Standards` and `Specification` headings. State finding counts and the worst issue within each axis without choosing one overall winner.

Fix valid in-scope findings, rerun affected checks, and repeat focused review where the fixes materially changed behavior.

