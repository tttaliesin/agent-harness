---
name: project-workflow
description: Carry an OpenSpec change through existing implementation skills and product checks with candidate-bound Harness evidence. Use for work in a bound product; not as a replacement for its implementation or Git workflow.
---

# Project Workflow

Read the selected OpenSpec change, its acceptance criteria, `harness/project.yaml` and the change's `harness.yaml`.
Keep requirements and task status in OpenSpec and execution inputs in the adapter.
Identify the candidate/base and one owner of the change's writable paths.

Use the existing skill that owns the work: selected domain/design skills for decisions, test-driven-development for a test-driven change, systematic-debugging for a fault, and github-operations for Git delivery.
Use parallel-worktree-development when independent implementation slices justify parallel work; do not implement a second worktree manager.
Internal delegation uses native Codex subagents and inherits the task's authorization.

Run the product's shared just commands, which call its existing native checks.
Do not register a composite check together with all of its descendants.
Use explicit change IDs and a trusted base; union required checks across the requested changes.
Local verification records local evidence, and cannot authorize a CI/release claim.

After changes, verify the current candidate and run project-review when required by the change.
If a required resource is absent, preserve BLOCKED and continue independent authorized work.
When interrupted or handing over, use project-handoff with the next concrete command and durable references.
