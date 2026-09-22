---
name: project-review
description: Connect independent Spec and Standards reviews to one clean candidate, current specification and actual verification evidence. Use for a change acceptance review; not for unrelated routine edits.
---

# Project Review

Freeze the repository, base, candidate, OpenSpec inputs, policy/package hashes and verification evidence before review.
Reject missing specification, dirty candidate, failed required checks and stale or missing evidence.
Use the package CLI to validate the inputs; do not accept a manually written PASS or a claimed CI run ID as verified provenance.

Delegate separately to the product's `spec_reviewer` and `standards_reviewer` native roles.
The Spec reviewer assesses the stated requirements and acceptance criteria.
The Standards reviewer assesses correctness, interfaces and the product's approved engineering rules.
Use existing code-review or differential-review where appropriate; do not copy their review procedure here.
Add a domain reviewer only when a concrete domain contract needs it.

Provide identical frozen inputs to each reviewer and preserve independent findings and outcomes.
Verify the runtime's actual read-only permission and unchanged implementation tree; a TOML declaration or reviewer assertion alone is insufficient.
If the host cannot establish that boundary, report the affected acceptance check as BLOCKED.
The implementation owner fixes findings and refreshes evidence if the candidate or its inputs change.
Reviewer approval does not grant permission to publish, merge or deploy.
