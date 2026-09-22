# OpenSpec stage selection

Use the product-generated skills from its `.agents/skills/` directory.
Read their actual instructions and the pinned CLI's help; slash commands are not a portable invocation contract.

| Situation | Generated skill | Required result |
| --- | --- | --- |
| Unclear behavior or existing code | openspec-explore | Repository evidence and material unresolved decisions |
| New approved planning work | openspec-propose | Proposal, design, delta specification and tasks |
| Authorized implementation | openspec-apply-change | Changed behavior and task-specific checks |
| Agreed scope or design changes | openspec-update-change | Updated artifacts, affected checks identified |
| Candidate ready to assess | openspec-verify-change | Requirement/scenario mapping and gaps |
| Accepted delta | openspec-sync-specs | Canonical specification updated once |
| Completed change | openspec-archive-change | Validated archive and resumable result record |

Bootstrap must explicitly select explore, propose, apply, update, verify, sync and archive.
The default profile may omit verify; inspect all seven generated names and their generatedBy versions.
One upstream source owns these skills; do not install a second copy from the common skill repository.
Preserve user changes before init/update; test the pinned CLI's changes in a copy before replacing modified generated files.

During setup, locate the established tracker from the remote and repository policy, the domain glossary/ADRs, source boundaries, task commands and CI.
Add a short product AGENTS.md only when needed to locate these existing sources; preserve CLAUDE.md and link shared material rather than copy it.
Use domain-modeling for substantive glossary/ADR work when available; record decisions in the product's existing format otherwise.
Use grilling only for requested consultation or a material decision that cannot be resolved from available evidence; do not interview again before each approved implementation.
