---
name: workspace-governance
description: Apply workspace category and ownership rules and route repository work to the owning skill. Do not use for ordinary single-repository implementation work.
---

# Workspace Governance

Use this skill for repository classification and workspace-wide ownership rules.
Read [Workspace Rules](references/workspace-rules/README.md), then only the relevant category in `references/workspace-rules/docs/categories/`.
For task entry points and knowledge ownership, read [the task guide](references/workspace-rules/docs/use-cases.md).
Current host, runner, repository, or service state must come from the owning implementation repository, not a historical research snapshot.

## Route by responsibility

| Target | Owning skill |
| --- | --- |
| Repository toolchain selection, shared development tasks, tooling templates | `development-tooling` |
| Product CI or generic Actions | `github-actions-workflows` |
| Deploy automatic test refresh, selected service composition, target-scoped deployment, recovery | `deployment-promotion` |
| Deployment target host, Periphery, public-key trust and connection | `target-host-management` |
| Persistent runner IaC and lifecycle | `self-hosted-runner-management` |
| Komodo Core and Periphery configuration | `target-host-management` |
| GitHub resources and delivery lifecycle | `github-operations` |
| Independent local implementation worktrees | `parallel-worktree-development` after the repository owner |

Use the target's responsibility rather than its file format to select the owner.
If that skill is unavailable, inspect the target repository's instructions and report any unavailable contract before a dependent operation; do not invent another owner's policy.
The [Infra rules](references/workspace-rules/docs/categories/infra.md) own environment, repository, credential, socketless runner, and bootstrap boundaries.
A governance edit does not authorize changes to implementation repositories or live resources.

## Apply and finish

Inspect the target Git root, README, and available AGENTS.md before repository work.
An absent optional AGENTS.md is not itself a blocker.
Routing continues the same task with its existing scope and approvals; it neither ends the task nor expands authority.
Resolve reachable evidence and complete independent authorized work before stopping at an unavailable fact, required review, or execution permission.
Edit rules directly in the owning skill’s references; do not duplicate them in navigation pages.
State durable objectives and safety boundaries separately from replaceable implementation choices.
Do not turn one owner's current file layout, schema, workflow, or retry mechanism into a workspace-wide requirement unless the objective depends on that exact mechanism.
Keep helpers inside the skill that uses them, with tests proportionate to their behavior. Product commands, reports and resource management remain in the owning repository. Supply common instructions through installed skills; avoid a second policy copy, generic execution engine or synchronization service.
Use the current task and relevant repository documentation for working context.
