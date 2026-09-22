# Shared Harness development

This repository owns common skills, their policy references, selected upstream packages,
and the small `harnesskit` runtime that connects product commands to evidence.
Product behavior and deployment remain with their owning repositories.

## Locate and route

- Start with `README.md`, `docs/implementation/layout-map.md`, and the affected skill.
- Common policy source: `skills/workspace-governance/references/workspace-rules/`.
- Tool selection: `skills/development-tooling/`.
- GitHub operations: `skills/github-operations/`; workflows: `skills/github-actions-workflows/`.
- Parallel implementation: `skills/parallel-worktree-development/` with native worktrees and delegation.
- Runtime: `src/harnesskit/`; strict contracts: `schemas/`; behavioral tests: `tests/`.

## Change and verify

Reuse existing skills and native product commands before adding behavior.
Keep one active supply for each skill name; OpenSpec-generated skills belong to the product.
Use selected tools from `mise.toml`, explicit `just sync`, then `just check`.
Checks must propagate failures and must not install dependencies, update locks, or publish.
Review changes to `upstream.lock.json` with the actual selected source and patch content.
Binding owns only paths listed in its manifest; user modifications must be preserved.
Local evidence is not authoritative CI evidence.
Keep unsupported external CI or native permission enforcement visible as `BLOCKED`.

## Handoff

Report the candidate revision, actual checks, remaining blockers, and next command.
Do not create instructions above the repository root or duplicate the policy body here.
