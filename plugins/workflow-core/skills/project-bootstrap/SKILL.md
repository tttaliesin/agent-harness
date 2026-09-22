---
name: project-bootstrap
description: Connect an existing product to the shared Harness using an explicit package version, existing commands and OpenSpec. Use for first binding or binding updates; not routine feature work or host provisioning.
---

# Project Bootstrap

Identify the product Git root, current branch, existing changes, native commands and accepted requirements.
Read its README and existing repository AGENTS; do not create an instruction file above the repository.
Use development-tooling for runtime and package-manager decisions, and workspace-governance only for cross-repository ownership.

Run `harnesskit --root <product> doctor` and inspect the actual missing requirements.
Select the package revision and product checks explicitly; preserve native scripts and dependency managers.
The package's `harness-sync` operation uses a reviewed template manifest and ownership hashes.
Run it once, review the diff, then repeat and confirm no changes.
If a generated file has a user edit, preserve it and resolve that conflict before updating the binding.

Generate OpenSpec skills with the pinned OpenSpec CLI and required profile.
Do not copy them into this plugin or create a second requirements/task store.
The product adapter contains paths and check inputs; the implementation remains in the product's commands.
Resolve `harnesskit ... --help` from the installed version before running an operation.

Report schema/package checks, binding conflict tests and actual skill discovery separately.
Native role permissions, hook trust, CI and deployment require their own actual evidence.
