# Viewer-specific delivery

GitHub and compatible Markdown viewers can render supported fenced Mermaid syntax.
Check the target's actual Mermaid version and syntax rather than assuming every C4 or experimental diagram works everywhere.
Prefer the requested supported form among flowchart, sequenceDiagram, classDiagram, erDiagram and stateDiagram-v2.
Use a supported flowchart representation if an unsupported architecture syntax must be replaced, preserving its meaning.
A local renderer pass does not prove the remote viewer's compatibility.

For image-based destinations, prepare the required PNG/SVG beside the editable source.
Upload or publish only to the user-authorized destination through the owning integration.
Preparation is not authorization to post a Wiki, Confluence, Notion or other external page.
Apply any human review or approval explicitly required by the user or repository before the affected integration.
Follow repository Markdown language and structure rules; do not impose STE100 or an unavailable document-specialist skill.

## PlantUML remains opt-in

Invoke PlantUML only when explicitly selected and relevant to Salt wireframes, use case, timing, ArchiMate, nwdiag, WBS, JSON/YAML trees, or an existing `.puml` source for a Confluence/Word image.
Do not switch class, ER, state or ordinary component diagrams to PlantUML merely because Mermaid failed.
Render selected PlantUML to PNG/SVG and link the actual image; publishing remains a separate authorized action.

## Documentation delivery

Derive existing-system nodes and edges from actual code, configuration or events.
Keep scope omissions explicit and do not invent services.
Retain semantic Unicode and high-contrast custom text styling as specified by SKILL.md.
Run available syntax/render checks and retain editable source at the repository-established location.
If a renderer is unavailable, complete authorized local Markdown integration with source checks and disclose the unverified rendering scope, unless a successful render is an explicit acceptance requirement.
Reuse matching approval; do not add a human review gate solely because a diagram describes code.
