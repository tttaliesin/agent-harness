# Upstream attribution and local modifications

Adapted from [SpillwaveSolutions/design-doc-mermaid](https://github.com/spillwavesolutions/design-doc-mermaid) at `c36d83503d2ba9c1e51638dc2d8a34758a377dea`.
The plugin identifies its author as Rick Hightower, https://github.com/RichardHightower.
Upstream README declares: “Part of Claude Code Skills - MIT License”.
The upstream plugin declares `"license": "MIT"`.
There is no standalone license text in that revision; [LICENSE.txt](LICENSE.txt) supplies the standard declared terms without inventing a copyright year.
The original declarations can be found at the upstream revision linked above.

Local modifications on 2026-09-05 implement task-scoped output/publication, evidence and review gates, host-independent tool selection, and safer local rendering and Markdown conversion.
Python helper implementations were replaced; their supported CLI interface is documented in the local workflow.
Upstream presentation discretion was not expanded: semantic Unicode requirements and PlantUML opt-in remain.
Local changes on 2026-09-12 make human review and successful rendering prerequisites conditional on explicit user or repository requirements; unavailable rendering is disclosed when completing authorized local Markdown work.
Local changes are maintained in Git history.
