---
name: project-handoff
description: Record and validate resumable context for an OpenSpec change using candidate and durable evidence references. Use when handing work to another task or resuming interrupted bound work.
---

# Project Handoff

Use the selected change's OpenSpec files as the requirement/task source and retain the current authorized delivery endpoint.
Read native Git state, active write ownership and the CLI's evidence freshness result.
Create a handoff with repository/worktree/branch, base/candidate, completed checks, unresolved findings, constraints and the next concrete action.
Reference durable reports, CI runs and artifacts; do not paste a full conversation or duplicate requirements.

Use `harnesskit --root <product> handoff --help` for the installed argument contract.
Preserve existing user-authored handoff content on conflict and report which input needs reconciliation.
A handoff commit changes the candidate and can invalidate evidence; do not embed evidence into the candidate it purports to prove.

On resumption, compare actual Git and package/policy/spec inputs with the recorded ones before reusing results.
Reuse current valid evidence and rerun only invalidated or required checks.
A different task must be able to find the next action without access to the original conversation.
