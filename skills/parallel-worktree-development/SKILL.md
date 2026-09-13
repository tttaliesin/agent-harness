---
name: parallel-worktree-development
description: Coordinate a substantive local implementation across two or more genuinely independent Git worktrees after github-operations has classified any GitHub Issue lifecycle. Use for parallel slice decomposition, agent-to-worktree assignment, file ownership, local integration, conflict handling, and integrated verification. Do not create or resolve Issues, push, create or merge pull requests, publish releases, dispatch workflows, or delete remote refs; route those operations to github-operations.
---

# Parallel worktree development

Use this skill only for a substantive local implementation with at least two genuinely independent
slices whose throughput benefit exceeds worktree and integration cost. It owns local decomposition,
worker worktrees, local commits, integration, and integrated verification—not the GitHub lifecycle.

## Apply the invariant contract

- Fix the exact repository, base revision, integration branch, final destination worktree, and one
  named integration owner before dispatch. Only that owner may mutate the integration destination.
- Give each worker an observable slice with explicit owned files, directories, or symbols. A file
  or generated artifact has exactly one mutation owner.
- Preserve tracked, staged, untracked, ignored, and user-owned files. Never stash, reset, discard,
  overwrite, or carry unrelated changes into a branch or worktree.
- Use unique worker branches and absent or empty worktree paths. Workers operate only in their
  assigned worktrees and return local commits with evidence.
- Workers never push, merge, rewrite the integration branch, create or resolve Issues, create or
  merge PRs, publish releases, dispatch workflows, delete refs, or clean branches and worktrees.
- A worker result, passing worker check, merge, or cherry-pick is not integrated proof. The named
  owner remains responsible until the agreed destination and acceptance criteria are verified.

Apply the target repository's workspace policy and preserve the approved scope through handoff.
Load the available `github-operations` skill when Issue classification, remote effects or final
branch cleanup may be involved. If it is unavailable, continue independently authorized local
work and identify any unresolved operation contract before the dependent action.

## Route by current phase

- **Planning, worktree creation, or worker dispatch:** read
  [planning and workers](references/planning-and-workers.md). Use it to decide whether parallelism is
  justified, record contracts, create isolated worktrees, and dispatch workers.
- **Local integration or verification:** read
  [integration and verification](references/integration-and-verification.md). Use it to inspect
  worker commits, integrate under one owner, resolve conflicts, and prove the combined result at the
  final local destination.
- **Handoff, cleanup, or a blocked parallel path:** read
  [handoff and cleanup](references/handoff-and-cleanup.md). Use it to return control to the Git owner,
  preserve reachable work, and record pending state without destructive cleanup.

For a full new parallel run, read the phase references in lifecycle order. For an existing run,
start at the current phase and load an earlier reference only when its contract evidence is missing.

## Stop overlap before it spreads

If workers overlap, consume unfinished sibling output, or discover an unfixed shared interface,
stop only the affected parallel path and serialize that boundary under the integration owner.
Continue independent authorized work when safe. Do not turn a coordination problem into remote
mutation, forced integration, or destructive cleanup.
