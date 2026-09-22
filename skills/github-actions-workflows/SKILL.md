---
name: github-actions-workflows
description: Design, create, edit, review, or diagnose generic GitHub Actions workflows and Product CI for this workspace. Do not use for GitHub resource operations that do not concern workflow behavior or YAML.
---

# GitHub Actions Workflows

Use this skill for generic GitHub Actions/YAML mechanics and Product CI. It prescribes no workflow
outside Product CI: derive routed workflow behavior from the owning skill and target-repository
evidence. It does not own deployment promotion, runner lifecycle, or Komodo management-plane/service
lifecycle.

## Select the relevant policy

For an ordinary workflow change, use the generic rules below and the actual repository evidence.
Read only the policy sections and recipes relevant to the affected behavior; a generic YAML edit does not require the full Product or Infra runbook.
Preserve any applicable policy already established for a continued task.

| Affected behavior | Reference |
| --- | --- |
| Product module build, image publication, immutable identity or moving channel | [Product publication](references/github-actions-workflows.md#product-ci-build-only-계약), [event semantics](references/github-actions-workflows.md#event와-상태-전이), and relevant [verification cases](references/github-actions-workflow-recipes.md) |
| Product installation release or test coverage | [Installation release](references/github-actions-workflows.md#제품-설치-릴리스) and the actual consumer interface |
| Infra trust or cross-repository access | [Infra boundaries](https://github.com/tttaliesin/developer-skills/blob/main/skills/workspace-governance/references/workspace-rules/docs/categories/infra.md) |
| Unresolved prerequisite or handoff | [Evidence applicability](references/github-actions-workflows.md#evidence-discovery-and-operation-applicability) |

For deployment use the available `deployment-promotion` skill; for host preparation use
`target-host-management`; for runner operations use `self-hosted-runner-management`; for the
Komodo management use `target-host-management`. Read the target repository's contract when the
relevant skill is unavailable. Do not infer its workflow, supported operations or readiness
requirements from this skill.

## Generic workflow and security rules

- Start with the target repository's `AGENTS.md`, existing workflows, actual build/test/publish
  entrypoints, event and branch conventions, runner evidence, and action-pinning convention.
  Reuse established commands and shapes; do not synthesize a workflow from policy prose.
- Use precise events and refs. Treat `pull_request`/`merge_group` revisions as validation inputs
  and a `main` push as the merged source only when the Product CI contract says so. Do not infer
  a trigger, release condition, or reusable workflow that the repository does not evidence.
- Declare workflow or job `permissions` at the minimum required scope. Default to no permissions
  where possible, grant only the read/write access used by a step, and avoid unverified
  `secrets: inherit` or broad long-lived credentials.
- Pin every third-party action and external reusable workflow to a reviewed immutable commit SHA,
  following the repository's established convention. Do not replace an evidence-backed pin with a
  floating tag or invent a revision.
- Treat all pull-request code, including fork code, as untrusted. Do not run it with privileged
  secrets, publication credentials, or on a persistent trusted self-hosted runner. Never use
  `pull_request_target` to check out or execute the PR head. Do not restore untrusted caches or
  artifacts in a privileged job.
- Keep credentials step-scoped, prevent checkout credentials from persisting when they are not
  needed, and avoid copying secrets into logs, outputs, summaries, artifacts, or repository files.
- Distinguish controls expressed in YAML from repository, organization, identity, secret-store,
  and runner settings configured elsewhere. An observed successful run does not prove those
  external settings exist.

## Evidence-based implementation and review

Inspect event filters, checked-out refs, expressions, `needs` and output wiring, permissions,
concurrency, secret references, action pins, and the boundary between untrusted validation and
trusted Product CI. For each Product module publication, confirm that its source revision, GHCR image, full digest and source/run provenance match that module’s evidence-backed run and attempt.

Use the target repository's existing checks and validation procedure when the task calls for
verification. If no validator exists, statically inspect the workflow structure and security
boundaries. Diagnose a failed run from its event, commit, job, step, and logs before proposing a
change. When GitHub run or pull-request operations are required and the `github-operations` skill
is installed, apply its authorization, mutation, retry, and verification rules. Do not use
`gh auth status` as a routine workflow preflight.
