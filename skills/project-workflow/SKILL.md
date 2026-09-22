---
name: project-workflow
description: Carry an authorized OpenSpec change from repository setup or resumption through implementation, product checks, independent review and handoff. Use for an end-to-end change in a product using OpenSpec, not isolated edits or planning-only requests.
---

# Project workflow

Connect the selected tools to the current change; execute the product's existing commands directly.
The product owns its requirements, runtime, tests and CI; this skill supplies the working procedure.

## Establish the change

1. Read the product's AGENTS.md, existing documentation and actual commands; identify the Git root, current changes, requested result and authorized delivery endpoint.
2. Recover decisions from the task and the current OpenSpec change before asking questions. Preserve existing user changes and one writer per worktree.
3. If first setup is authorized, use development-tooling's OpenSpec setup procedure when available. Otherwise inspect the installed CLI and select the seven workflows in [workflow routing](references/workflow-routing.md); preserve existing instructions and local modifications.
4. Read the generated openspec-explore or openspec-propose skill for investigation/planning, or select an existing change with `openspec list --json` and `openspec status --change <name> --json`.
5. Record acceptance criteria, specification paths, required checks, write scope and existing approval in the change. Use the current user request as authority; reuse explicit implementation authorization for the same scope. A planning-only request ends with the proposal.

Read only the generated skill for the current stage. OpenSpec owns the proposal, design, delta specs and tasks; link them from tracking records instead of duplicating the task list.
Material scope changes or external actions outside the authorization require a decision; routine implementation choices do not.

## Implement and verify

Use openspec-apply-change and the relevant implementation skills; use openspec-update-change when the agreed change evolves.
When installed, use test-driven-development for meaningful behavior changes and systematic-debugging for uncertain failures; otherwise follow the product's existing equivalent procedure.
Load only the affected domain guidance: webapp-testing, python-testing or streaming-testing when available.
Discover actual commands and expected reports from the product, run them, and retain command, exit, case count, report path and candidate/input context in its existing change record or CI.
Treat a missing required tool, browser or GPU as BLOCKED, failed checks as FAIL, and skipped or unexecuted work as incomplete.
Zero tests, missing required reports and an exit code without the expected result cannot establish acceptance.
Apply the existing task/product limits for repair rounds, tool retries and budget. If none are stated, retry transient tools at most twice and stop after two repair rounds without new evidence or progress. Record the failure, attempted fixes and next required input in a handoff; do not loop indefinitely or weaken checks to finish.

## Review the same candidate

Read openspec-verify-change and compare each requirement and scenario with implementation and observed checks.
For formal acceptance, use a clean committed candidate, a fixed base and required specification; otherwise report WIP or BLOCKED.
Run code-review's independent Spec and Standards passes when available. Supply both with the same candidate, specification, product rules, common skill revision and required-check evidence.
If that skill is absent, perform those two named passes directly, preserve both results and disclose the independence limitation.
Missing required specifications, stale results, an unresolved failing axis or unavailable required review permissions block final acceptance.
Record each finding's disposition, justification and subsequent check; assess feedback before applying it rather than accepting every suggestion.
After a candidate or relevant input changes, rerun the affected checks and review.

## Deliver and resume

Use the authorized Git workflow for the established destination; query the actual CI run's repository, head and artifacts.
For PR follow-up or handoff, read [follow-up and resumption](references/followup-and-resumption.md).
Before final delivery, establish whether canonical specification updates and archival belong in the same PR/commit. For that policy, finish checks and review, use openspec-sync-specs and openspec-archive-change, then commit the resulting files, fix the new candidate and rerun affected checks/review before delivery. Otherwise perform them at the product's documented post-delivery stage and deliver those changes through the authorized Git workflow.
An incomplete implementation task or blocked required check remains open. Record pending delivery explicitly even when the product requires pre-merge archival; archiving a specification is not proof of delivery or deployment.
Report implemented behavior, actual validation and remaining conditions separately from installation success.
