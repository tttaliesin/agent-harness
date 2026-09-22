# Follow-up and resumption

When github-operations is available, read its followup-and-handoff reference and use that established delivery workflow.
For an isolated installation without it, apply the minimum contract below using the product's existing Git tooling and task records.

## One specified PR

Read the named PR's current head, review state and CI; identify the authorized action and writer.
Before writing, requery the head and the finding's resolution state, and compare its event/run identity with the existing change record.
An already handled event or resolved finding is a no-op; a different head invalidates an old action plan.
Record the event or review identifier, evaluated head, disposition, resulting candidate and next condition in that record.
If another task owns the same write scope, coordinate before changing it; a note alone is not a concurrent execution lock.
Stop on success, out-of-scope failure, user cancellation or a required decision/permission. Schedule future checks only when requested, using the available native automation facility.
External comments require existing communication authorization.

## Handoff record

Use the existing OpenSpec change or requested durable task record, keeping one owner for its updates.
Include repository/worktree/branch, base and candidate, specification paths and authorization, changed files, check commands/results, unresolved findings, environmental blockers and the next concrete action.
Record verified and unverified requirements separately, including pending delivery and installation.
On resume, inspect the actual Git state and required inputs first; retain matching evidence and rerun invalidated checks.
Have another task use only this record and linked files to identify the correct next action; missing context is a handoff defect to fix before calling it resumable.
