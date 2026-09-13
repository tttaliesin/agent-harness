# Media and extensions

Use these rules when a Markdown artifact contains images, alerts, collapsed sections, footnotes,
diagrams, math, front matter, HTML, MDX, or another renderer-specific extension.

## Images and accessibility

- Add an image only when it contributes information or materially reduces explanation effort.
- Give informative images concise alt text that communicates purpose in context. Use empty alt text
  for purely decorative images when supported.
- Do not repeat a nearby caption word-for-word in alt text. Explain essential information from
  charts, complex screenshots, and diagrams in nearby prose.
- Do not put required instructions or critical facts only in images or diagrams.
- Do not rely on color, position, shape, icons, or typography alone.
- Crop screenshots to relevant content and remove secrets, personal data, and irrelevant UI. Keep
  screenshots current with the documented interface.
- Use semantic headings, lists, links, tables, and code blocks instead of visual approximations.
- Make headings, links, and table headers meaningful when read independently. Avoid culture-specific
  idioms and language that assumes reader ability, experience, identity, or environment.
- Use neutral, non-sensitive placeholder data.

## Blockquotes, alerts, collapsed sections, and footnotes

Use normal blockquotes for quotations and attribute them when needed. Use project-specific alert
syntax only when the renderer supports it.

- **Note:** useful supplemental information.
- **Tip:** an optional improvement.
- **Important:** a condition required for success.
- **Warning:** urgent action needed to avoid a problem.
- **Caution:** risk of data loss, security exposure, irreversible change, or another negative
  outcome.

State the concrete consequence and safe action. Avoid consecutive alerts and reserve them for
exceptional information, generally no more than one or two per article. Never hide a warning in a
collapsed section. If alerts are unsupported, use a short labeled blockquote or descriptive
heading.

Use collapsed sections only for optional advanced examples, long diagnostics, generated data, or
supplementary detail. Never collapse prerequisites, required steps, warnings, decisions, or the only
explanation of a result. Use a specific summary label and avoid nesting.

Use footnotes only when supported and only for brief, nonessential qualifications or source details.
Keep required explanation and warnings in the main text. Put sources near the claims they support
and prefer primary sources.

## Mermaid and other diagrams

Use Mermaid only when support is established and a diagram reduces the effort required to
understand structure or behavior.

For substantive Mermaid modeling, code-to-diagram evidence, rendering, or image conversion, use the available `design-doc-mermaid` skill within the same task.
Keep document structure, language, links, and accessibility under these Markdown rules; the diagram skill owns diagram-specific evidence and validation.
Carry existing valid scope and approvals into that routing, and apply source and available syntax/render checks.
Require successful rendering or human approval before integration only when explicitly required by the user or repository; otherwise complete authorized local Markdown work and disclose unavailable rendering.
If the diagram skill is unavailable, continue the authorized work with these rules and report missing validation rather than installing it implicitly.

- Use `flowchart` for a process, branching flow, pipeline, or dependency.
- Use `sequenceDiagram` for time-ordered interaction between actors or components.
- Use `stateDiagram-v2` for states and allowed transitions.
- Use `erDiagram` for data entities and relationships.
- Use `classDiagram` for static classes, types, interfaces, and relationships.
- Use `gantt` or `timeline` for time and dependencies; use `gitGraph` for a small focused Git
  history.
- Use `mindmap` only for a supported concept hierarchy.

Prefer a numbered list for a short linear procedure, a table for precise comparison, a `text` tree
for a small hierarchy, and prose for rationale or trade-offs.

For every diagram:

- Make it answer one clear question and introduce what readers should learn from it.
- Use short, descriptive labels and a direction that matches the mental model.
- Split dense diagrams rather than shrinking labels or adding crossing edges.
- Avoid experimental syntax and unnecessary custom colors. Support light and dark themes and never
  encode meaning only by color.
- Provide a nearby text summary without duplicating every detail in prose.
- Validate with repository or Mermaid tooling when available.

Use GeoJSON, TopoJSON, or STL only for genuine geographic or 3D information on a known supporting
platform.

## Math, front matter, HTML, and MDX

- Use math only when it is clearer than prose and supported by the renderer. Define variables,
  units, assumptions, and ranges nearby; explain practical meaning in prose.
- Use code formatting, not math, for program expressions and configuration syntax.
- Add front matter only when an evidenced consumer or schema requires it, including a publishing system, agent harness, or knowledge-management tool. Preserve its schema and delimiters.
  Do not invent metadata or reorder it solely for appearance.
- Preserve MDX imports, exports, JSX components, and expression syntax.
- Use raw HTML only for a necessary, supported feature ordinary Markdown cannot express clearly.
  Never use HTML tables for layout.
- Use HTML comments only for maintainer notes; remove stale comments and do not hide user
  requirements in them.
- Prefer paragraphs over trailing-space line breaks or repeated `<br>` elements.
