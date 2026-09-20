# Agent Review Workflows

These terms describe the review-feedback workflow provided by this skill collection.

## Language

**Review run**:
One explicitly requested effort to bring a selected PR stack to review convergence under a set of run conditions.
_Avoid_: Background watcher

**Run conditions**:
The criteria used to judge whether a finding is valid and actionable, including scope, acceptance requirements, and applicable compatibility constraints.
_Avoid_: Custom finish line

**Review instructions**:
Guidance supplied to the reviewer for a particular review, informed by the run conditions and relevant evidence.
_Avoid_: Approval instructions

**Review cycle**:
One round of assessing feedback, addressing or explaining findings, and obtaining another review outcome.
_Avoid_: Poll

**Finding disposition**:
An evidence-backed decision about how a reported issue is handled, including fixing, deferring, rejecting, or requesting clarification.
_Avoid_: Automatic fix

**Review convergence**:
A positive clean Codex outcome for every current PR comparison under the effective conditions, with observed feedback accounted for, required focused verification passing, and no pending decisions.
_Avoid_: Merge readiness

**Deferred finding**:
A valid issue left unchanged because an established scope or compatibility constraint excludes its correction from the review run.
_Avoid_: False positive
