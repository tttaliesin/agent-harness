---
name: project-pr-followup
description: Process authorized follow-up events for one specified PR with event deduplication, candidate checks and one writer. Use for a registered PR follow-up or an explicit PR update request; not for discovering unrelated tasks.
---

# Project PR Follow-up

Start from an explicit repository, PR, branch/worktree, change ID, allowed writes and authorized delivery endpoint.
Read actual CI/review state through github-operations and bind work to the observed head and event identity.
Use the Harness followup record to claim the event before writing.
An already processed event is a no-op; a different active writer prevents concurrent modification.

Handle only actionable CI failures or review findings using their owning skills.
Re-read the current head before applying a result, and rerun required checks after a changed candidate.
Record completion, failure or a recoverable pending owner state; do not treat a stale claim as permission to steal another task.
Honor the configured repair limit and stop on required human review, permissions, completion or user cancellation.

Use the supported Codex scheduling tool only when scheduled execution is authorized.
Record NOT_CONFIGURED until registration is actually confirmed; no scheduler database edits or new persistent service.
Repeated events, absent credentials or stopped Desktop execution are not successful follow-up evidence.
