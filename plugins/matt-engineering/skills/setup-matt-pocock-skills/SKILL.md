---
name: setup-matt-pocock-skills
description: Inspect how the selected engineering skills fit a repository's existing OpenSpec, Core policy, domain documents, and work tracker. Use when the user requests setup.
---

# Set up the selected engineering skills

Map these skills onto the repository's existing workflow.
Keep OpenSpec as the change specification and Core as the workflow authority.

## Inspect the current configuration

Read the applicable AGENTS.md, existing Core routing and product binding, OpenSpec configuration and current change, and any established tracker guidance.
Locate the domain glossary, context map, and architectural decisions through those pointers.
Read [domain documentation guidance](domain.md) for the consumer behavior.

Identify the selected supplies: domain-modeling, grill-with-docs, grilling, codebase-design, code-review, and writing-for-agents from this plugin; the existing systematic-debugging skill; and the selected Superpowers execution skills.
Report any missing supply using its name and the observed catalog.
Do not infer installation from the presence of files.

## Reuse existing decisions

Summarize which existing documents supply specifications, terms, decisions, verification commands, and delivery rules.
Derive answers from the repository and current task before asking the user.
Ask only when an unresolved choice would materially change the requested result.

Use the current tracker when tracking is needed and authorized.
The presence of a GitHub remote does not select a tracker or authorize creating issues, labels, pull requests, or messages.
This selected package does not require triage roles, a .scratch tracker, to-spec, to-tickets, or a second planning lifecycle.

## Apply the requested setup

When setup edits are requested, add only the missing pointers in the repository's established documentation location.
Preserve generated Core bindings and existing AGENTS.md ownership; update their canonical source through the owning workflow if needed.
Do not replace AGENTS.md or prefer CLAUDE.md as a competing authority.
If configuration is already sufficient, report that result without creating another config file.

Create a glossary or ADR only when a resolved term or consequential decision needs one and document creation is in scope.
Use the established location, including OpenSpec design documentation when it already owns the decision.
The sibling [domain-modeling skill](../domain-modeling/SKILL.md) supplies glossary and ADR formats when no repository format exists.

## Verify the result

Check the edited pointers and the actual available skill catalog.
Report what changed, which existing configuration it uses, and any unavailable skill or required user decision.
Local static package checks do not demonstrate native Codex installation, loading, or enforcement.
