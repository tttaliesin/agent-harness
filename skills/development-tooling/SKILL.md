---
name: development-tooling
description: Design, scaffold, migrate, or review repository development toolchains and repeatable task entry points under workspace policy, including mise, language package managers, version ownership, CI and Dev Container consistency. Use for tool selection or tooling changes, not ordinary application edits or host provisioning.
---

# Development tooling

Use the common defaults, ownership and execution contract in [the development tooling policy](references/development-tooling.md).
Read only the selected language profiles below; read [template usage](references/development-tooling-templates.md) when producing a configuration.
The policy owns defaults; do not reconstruct them from whatever tools a reference project happens to use.

## Decide from the purpose

Inspect the target Git root, README and available AGENTS.md, then its actual runtime declarations, manifests, lockfiles, task commands and relevant CI or Dev Container configuration.
Recover goals, operating constraints and reusable knowledge from the current task and relevant repository documentation.
Treat existing tool choices as migration inputs, not permanent canonical defaults; preserve the product's goals and observable behavior.
Identify supported OS/architecture, independent modules, native dependencies and necessary checks before selecting profiles.
Use the documented default without reopening the full tool comparison unless a concrete requirement or new upstream evidence changes the decision.

## Produce the requested result

- For review or design, complete findings, the proposed ownership table, configuration examples and verification limits within the authorized output scope.
- For local implementation, render and apply the relevant overlay, connect actual manifests and commands, and run the available checks; do not stop after a plan when implementation is requested.
- For a migration, separate runtime, dependency manager and task runner changes sufficiently to diagnose regressions; preserve a documented rollback combination.

Use `scripts/render-template.py <spec.json> <new-output-directory>` to render a reviewed specification with explicit versions.
The helper is a dependency-free Python 3 renderer; it does not select current versions, generate application code, create dependency locks, install tools or edit existing repositories.
Use only needed profiles from `assets/specs/`; these contain illustrative version pins, not a promise that those versions remain secure or preferred.
Verify supported upstream versions when adopting, fill actual module commands, then merge fragments into existing files without overwriting unrelated state.
No-op tests and unspecified required checks are not successful adoption.

Keep one selector per runtime and one root command surface.
Installing a common skill does not require replacing an existing Taskfile, justfile or native package script.
For first use, identify the actual product requirements, commands and available tools, then run only the relevant checks.
Use the installed OpenSpec CLI directly when OpenSpec setup is part of the task; avoid a second binding or configuration generator.
Before implementing or reviewing a selected language profile, read its version, lock and execution constraints:

- [Python](references/development-tooling.md#python)
- [Node and pnpm](references/development-tooling.md#node-and-pnpm)
- [Go](references/development-tooling.md#go)
- [Rust](references/development-tooling.md#rust)

For a polyglot project, read each affected profile; unrelated profiles need not be loaded.
Treat mise tasks, configuration templates and dependency install scripts as executable code and inspect them before trust or execution.
Existing user approvals continue across skill transitions; trust handling does not authorize unrelated host or production operations.

## Boundaries and completion

Governance owns policy and these declaration templates; infra owns the common image/bootstrap implementation and repositories own their actual manifests and commands.
Route CI changes to `github-actions-workflows` and infrastructure lifecycle changes to the owning skill in the same task, carrying the existing scope.
This skill does not publish packages, deploy, remove global managers or rewrite another project's canonical knowledge without that scope.

Validate selected paths and versions, installation and locked sync, actual checks, failure exit propagation and unchanged committed locks in a clean supported environment.
Check declared compatibility floors separately from the newer compiler used for development.
For polyglot projects, validate independent module commands plus relevant contract/simulator integration.
For research, runtime locks are only part of reproducibility: preserve data/model revisions, hardware, seeds and tolerances where relevant.
Report the adopted template version, changed files, validation evidence, exceptions and remaining unverified platforms.
Distinguish rendered output, validated template mechanics and an actually migrated project.
