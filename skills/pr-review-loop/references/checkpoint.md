# Checkpoint and recovery

Store local state outside committed source. Resolve the absolute Git common directory using `git rev-parse --path-format=absolute --git-common-dir`; place each run at `pr-review-loop/<run-id>.json` beneath it. Use a filesystem-safe timestamp or generated identifier for the run ID. This shares discovery across worktrees without assuming `.git` is a directory.

Do not commit the checkpoint, copy credentials into it, or modify ignore rules. If Git metadata is not writable, report the persistence limitation and obtain an allowed local location rather than silently claiming durable recovery.

## Record only what recovery needs

Use a compact versioned JSON record with these groups:

| Group | Required content |
| --- | --- |
| Run | ID, format version, repository identity, start/update times, active session owner, status, authorization scope and any narrowed instructions |
| Stack | Ordered PR URLs/IDs, branch and worktree ownership, dependencies, current and previously observed head/base SHAs |
| Conditions | Original user conditions and review instructions, effective conditions, pinned requirement and legacy references, revision of these conditions |
| Findings | Stable thread/comment IDs and URLs, underlying claim, evidence revisions, disposition, owning layer, pending user decisions, recurrence count and last counted review ID |
| Delivery | Local commits, published equivalents after restack, verification commands/results and applicable SHAs, deferred defects |
| Reviews | Per-PR request ID/body/time, conditions revision, head/base, baseline reactions, pending/completed state, completion evidence and last poll |
| Actions | Intended publication/reply/resolution, target and expected head, attempted time, confirmed remote IDs/results, uncertain outcomes needing reconciliation |

Use statuses `active`, `waiting-review`, `waiting-user`, `blocked`, `interrupted`, and `converged`. These describe the checkpoint, not a host-specific goal API. If a host goal facility is available and explicitly requested, keep it consistent without depending on it for portability.

Persist before external mutations and immediately after confirmed results or user decisions. Write a temporary sibling then rename it to avoid a truncated record. Before starting, inspect records for overlapping active PR ownership. Do not run concurrent writers over the same stack; coordinate or discuss an apparently abandoned owner before taking over.

## Resume from live truth

1. Match the checkpoint to the selected repository and stack. An explicit resume continues the documented run scope unless the user changes it; a checkpoint alone does not authorize a new run.
2. Refresh heads, bases, threads, review results, checks, and local worktree state. Reconcile interrupted commits/pushes by inspecting history and remote ancestry, not merely branch names.
3. For an action marked attempted but unconfirmed, inspect the target thread, request comments, or remote branch. Record success if the intended action already occurred; retry only after determining it did not. Discuss outcomes that cannot be established safely.
4. Reuse a disposition only while its source evidence, subsequent discussion, and conditions remain applicable. Reopened human disagreement requires discussion. Changed code or conditions invalidate affected verification and review evidence.
5. Continue the original review wait deadline and count each completed review at most once for recurrence. Do not reset a timeout because the session restarted. Preserve unresolved decisions until an actual answer arrives.

Checkpoint closed or merged PRs as no longer actionable and report their state; do not modify or claim a clean outcome for them unless qualifying evidence exists. Ask about changed stack membership before expanding the originally recorded run to new PRs. On interruption, report the checkpoint path and exact pending work.
