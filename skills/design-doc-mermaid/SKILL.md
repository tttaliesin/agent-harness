---
name: design-doc-mermaid
description: Create or review Mermaid diagrams from requirements or code, including architecture, deployment, sequence, flow, state, class and ER views; validate sources and prepare local Markdown or image artifacts. Does not authorize publication or deployment.
---

# Design Doc Mermaid

## Scope and ownership

Start from the question, requested viewer, source scope, and output action.
Use existing task decisions and valid approvals for the same target, action, environment, external effects, and validity conditions.
Preserve one-time, per-execution, expiry, credential, production, review, and unrelated-state boundaries.
A read-only review produces findings and evidence; it does not start file generation, rendering with artifact writes, dependency installation, or external publication.
Authoring permission covers the requested local artifact, not uploads, Wiki edits, commits, or live system changes outside that scope.
Route authorized external actions through their owning integration and preserve pending approval requirements.

For document language, structure, links and accessibility, use the repository's Markdown rules and the available markdown-authoring skill.
This package owns diagram modeling, source evidence, syntax/render checks and local conversion.
Do not impose STE100, a framework, or a companion skill unavailable on the host.
Load full design-document templates only when a full document was requested.

## Choose the relevant reference

| Question | Reference |
| --- | --- |
| Process, branch or business flow | [Activity](references/guides/diagrams/activity-diagrams.md) |
| Runtime resources and deployment boundaries | [Deployment](references/guides/diagrams/deployment-diagrams.md) |
| Components, layers and dependencies | [Architecture](references/guides/diagrams/architecture-diagrams.md) |
| Ordered calls and asynchronous messages | [Sequence](references/guides/diagrams/sequence-diagrams.md) |
| Class, ER, state or viewer-specific delivery | [Viewer guide](references/guides/wiki-ticket-and-github.md) |
| Existing code or configuration | [Code-to-diagram](references/guides/code-to-diagram/README.md) and [evidence](references/evidence.md) |
| Validate, render, extract or convert | [Local workflow](references/guides/resilient-workflow.md) |
| Syntax failure | [Troubleshooting](references/guides/troubleshooting.md), after classifying the failure |

Read only the selected guide and, for matching actual code, its framework example.
Examples illustrate shapes and questions, not facts or executable instructions for the target repository.
Do not infer a Go or NestJS topology from Spring Boot or Express examples.
For a full document choose one existing template under assets and retain only useful sections.
Replace sample values and completion checkmarks with actual evidence or explicitly unverified status.

## Evidence before drawing

For existing systems, support each material node and relationship with a source locator or a user-provided fact.
Distinguish observed structure, inferred relationships, and proposed design.
An import does not establish a runtime call; a port setting does not prove an active connection.
Show only supported and relevant versions, protocols, ports, retry counts and resources.
For asynchronous commands distinguish broker acceptance, execution confirmation, timeout, and unknown outcome.
Do not invent retries or live-device success to complete a sequence diagram.
Read [evidence.md](references/evidence.md) for the compact evidence table and review requirements.

## Output and validation gates

Use fenced Mermaid for a verified supporting Markdown viewer and images when requested or required by the target.
GitHub/Obsidian version support must be checked for the actual syntax; experimental C4/architecture syntax is not universally supported.
Keep the editable source in the requested document or repository-established `.mmd` location; avoid two independently edited sources of truth.
When exporting images, preserve the `.mmd` input and record the tool version and actual validation scope.

Check source meaning and syntax with the available validation tools before delivery; fix known errors.
If rendering is unavailable, inspect the source, complete the requested local Markdown integration, and report that rendering or viewer appearance remains unverified.
When the user or repository explicitly requires a successful render, human review, or approval before integration, complete source preparation and available checks first, then pause only the affected integration.
Reuse approval when its scope and validity conditions still match; an ordinary request to add a local diagram does not require another approval.
Rendering or an agent's review does not satisfy an explicitly required human review.
A helper-generated Markdown file still needs content and link checks before replacing the requested document.

Report syntax/rendering, source meaning, actual viewer appearance, and required human review as separate results.
Screenshot creation does not prove visual acceptance; a source citation does not prove live topology.
A missing optional viewer leaves its compatibility unverified and does not erase completed checks.

## Preserved invocation and presentation rules

PlantUML remains opt-in and limited to the types or existing `.puml` inputs in the viewer guide.
Do not install or invoke it merely because Mermaid rendering failed.
Preserve the reviewed upstream requirement to use semantic Unicode symbols and high-contrast styling.
Each custom `classDef` must specify text `color:` and readable foreground/background contrast.
Keep labels and relationships understandable independently of color or symbols and report missing glyphs found during visual checking.
Load the Unicode reference only when the user asks for symbols/icons, preserving its selective-loading condition.
The optional change making symbols discretionary was not accepted in this implementation.

## Local tools

For runtime setup or package maintenance, read [runtime setup](references/runtime-setup.md).
Helpers require Python 3.9+ and an existing or explicitly authorized Mermaid CLI runtime.
They discover `mmdc` on PATH, `DESIGN_DOC_MERMAID_MMDC`, or the host-local developer-skills runtime configuration.
They do not install dependencies, upload artifacts, or send error/source text to external services.
Inspect helper process/output behavior before first use or after updates; then use `--help` for exact arguments.
The local workflow documents the adapted command interface; old upstream CLI examples are not an API compatibility promise.
