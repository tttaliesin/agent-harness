---
name: github-operations
description: Establish the delivery endpoint and authorized Git workflow for repository development, independently decide whether GitHub Issue tracking is useful, and safely operate repositories, Issues, pull requests, releases, workflows, pushes, and branches with gh and git. Apply authentication, mutation-scope, retry, and verification rules. Do not use for editing GitHub Actions YAML.
---

# GitHub Operations

Establish the user's delivery endpoint before selecting implementation or tracking steps. Load only
the policy section and command recipe needed for the current route, while applying the common
invariants below throughout the task.

## Apply common invariants

- Identify the exact repository and requested resource from evidence. Resolve base, head, branch
  and expected commit SHA when they affect the selected operation. Ask only when a wrong choice
  could materially affect another resource.
- Name the integration owner and final destination before delegating work. A worker result is not
  final delivery, and a handoff does not shrink the established endpoint.
- Preserve tracked, staged, untracked, ignored, and user-owned work. Never stash, reset, discard,
  overwrite, or include unrelated changes to make an operation proceed.
- Reuse approval for the same target, action, environment, and validity conditions. Do not use an
  earlier approval for a materially different repository, mutation, or production effect.
- Decide whether Issue tracking is useful independently of delivery. An Issue neither authorizes a
  remote mutation nor changes a local, branch, PR, or merge endpoint.
- Do not run `gh auth status` as routine preflight. Use the narrow requested command or inspection;
  diagnose authentication only after relevant evidence or an explicit request.
- Never expose credentials, switch accounts to bypass a failure, bypass required checks or reviews,
  use `--admin`, or infer authorization for visibility, deployment, release, or unrelated changes.
- Before retrying a mutation with an uncertain outcome, inspect whether the resource was already
  created or changed. Report partial state instead of treating an unknown outcome as failure or
  success.

## Choose the narrow route

Read only the material listed for the current route:

- **Read-only inspection:** apply the common invariants and run a targeted `git` or `gh` query. Do
  not preload the long policy or command references unless the evidence creates a specific need.
- **Implementation or local integration:** read
  [completion endpoint](references/github-operations.md#완료-지점을-먼저-정한다) and
  [local completion](references/github-operations.md#로컬-통합과-완료를-확인한다).
- **Issue intake:** read
  [Issue selection](references/github-operations.md#issue로-추적할-과제를-판정한다) and the
  [Issue delivery recipe](references/github-issue-delivery-recipes.md).
- **Issue resolution:** read
  [authorization lifecycle](references/github-operations.md#요청한-작업을-권한의-경계로-삼는다),
  [local completion](references/github-operations.md#로컬-통합과-완료를-확인한다), the
  [Issue delivery recipe](references/github-issue-delivery-recipes.md), and the relevant merge and
  cleanup sections in the [repository and PR recipe](references/github-repository-pr-recipes.md).
- **Repository creation, push, PR, checks, or merge:** read the
  [repository and PR recipe](references/github-repository-pr-recipes.md). A PR-only request does not
  authorize merge.
- **Release or workflow run:** read the
  [release and workflow recipe](references/github-release-workflow-recipes.md). Editing workflow
  YAML belongs to `github-actions-workflows`.
- **Branch or worktree mutation and cleanup:** first read the relevant sections of the
  [common command rules](references/github-operation-recipes.md). Do the same before a GitHub
  resource mutation, raw API call, or uncertain mutation retry.
- **Parallel local implementation:** after the route and endpoint are fixed, use
  `parallel-worktree-development` only for two or more genuinely independent substantive slices.
  Read [parallel handoff policy](references/github-operations.md#병렬-local-구현은-별도-skill로-handoff한다)
  and retain ownership of Issue and remote operations.

For authorized PR follow-up or handing repository work to another task, read
[follow-up and handoff](references/followup-and-handoff.md). Preserve the established endpoint;
check the current candidate before writing or reusing evidence.

## Protect branch and worktree state

For branch switching, worktree removal, and local or remote branch cleanup, use the bundled
`scripts/git-safety.py` helper after verifying the repository remote, branch ownership, worktree
state including ignored files, and expected SHA. Never substitute `git branch -D`, an unconditional
remote deletion, or `gh issue develop --checkout`.

The helper cannot establish exclusive ownership against unrelated local processes. If ownership is
uncertain, preserve the branch and worktree and report cleanup as pending. A worker becoming idle is
not evidence that cleanup is safe.

## Finish at the established endpoint

Verify each relevant state separately: local commit, remote commit, PR base and head, required
checks, actual merge rather than queue registration, Issue closure, and branch or worktree cleanup.
If an installed package is also part of delivery, verify both the canonical repository state and
the authorized installed copy. Do not claim full completion while integration, installation, or
cleanup remains pending.

After an accepted merge or direct integration, clean only the exact temporary branch owned by this
delivery. Immediately before deletion, compare its local and remote SHA with the verified job or PR
head. Preserve a branch that advanced, remains the delivery artifact, has an explicit retention
purpose, or cannot be safely attributed. Record local-ref, remote-ref, and worktree dispositions
separately, with the owner and resumption condition for anything pending.
