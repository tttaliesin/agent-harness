---
name: markdown-authoring
description: Create, edit, or review Markdown artifacts, including `.md` files and Markdown content in MDX. Apply repository-aware rules for structure, portability, accessibility, examples, links, tables, and diagrams. Do not use for Markdown-formatted chat responses, read-only document lookup, or non-Markdown implementation work.
---

# Markdown Authoring

Create accurate, accessible, and maintainable Markdown that serves the reader's task. Apply explicit repository instructions and renderer or build constraints before this skill. Do not treat accumulated repository patterns as writing rules.

## Start with the document context

- Read the applicable `AGENTS.md` and repository documentation instructions before editing. Then inspect documentation framework, build, lint, and renderer configuration. Use nearby maintained documents only to verify facts, terminology, links, or supported syntax; do not derive prose style, list endings, or source wrapping policy from them.
- For an existing document, preserve its purpose, correct facts, terminology, front matter, anchors, and required custom syntax. Naming a target file does not authorize whole-file style normalization. A local link, path, number, or typo correction does not require rewriting surrounding prose or source wrapping. Apply writing defaults to newly authored or substantively rewritten explanatory prose; normalize the whole document only when that scope is requested.
- Use portable CommonMark when support for an extension remains unknown.
- Identify whether the reader needs a tutorial, how-to, reference, explanation, README, or decision document. Put the outcome and prerequisites where that reader expects them.

## Apply the writing defaults

- Put each complete prose sentence on its own source line without fixed-column wrapping. Use blank lines only for semantic paragraph breaks.
- Throughout Korean Markdown documents, use concise `개조식`, including ordinary explanatory paragraphs, list items, numbered procedures, task lists, and table prose. End authored statements with noun phrases or action expressions without sentence-final punctuation, such as `설정 파일에서 실행 환경 선택` or `변경 이력은 Git으로 관리`; avoid `-다.`, `-합니다`, `-습니다`, and mechanical `-함` endings. Ordinary paragraphs are not an exception. Preserve reasoning, conditions, and qualifications in concise connected statements; retain useful paragraph structure instead of forcing every statement into a bullet. Keep item-specific explanations with their item and apply the same style to continuation paragraphs. Preserve literal quotations, code, commands, identifiers, and required syntax. Use narrative sentence endings only when the user explicitly requests them or a controlling document requirement needs them.
- Do not override these defaults with patterns inferred from existing repository documents.

## Match the requested operation

- For creation, identify the audience, purpose, renderer, and required outcome, then create the smallest complete document that serves them.
- For editing, preserve correct content and stable interfaces and make a targeted diff. When file access is available, modify the target instead of returning only an outline.
- For review, keep the task read-only unless the user also requests a change, including selecting checks that do not modify files. Complete the review by reporting findings, evidence, and verification limits; fixing findings or making checks pass is not a review completion requirement. Lead with consequential findings, cite the file and line when available, and separate correctness or compatibility problems from optional improvements.
- Do not invoke this skill merely because an ordinary chat response uses Markdown formatting or because a document is read to answer a factual question.

Before editing a generated Markdown artifact, find repository evidence for its canonical input or generator. Change that source when it is available and in scope. Do not guess a generation path, and warn when an explicitly requested output-only edit may be overwritten.

## Use the relevant writing rules

For creation, structural rewrites, or a broad review, read [the common Markdown authoring rules](references/markdown-authoring-rules.md).
For a local link, path, number, typo, or similarly narrow change or review, use this entrypoint and only the reference needed to resolve the affected rule; do not reload unrelated guidance.
Then load only the conditional reference required by the artifact or change:

- For lists, procedures, tables, code, commands, emphasis, links, and navigation, read
  [Text and navigation](references/markdown-authoring/text-and-navigation.md).
- For images, accessibility, alerts, collapsed sections, footnotes, Mermaid, math, front matter,
  HTML, and MDX, read
  [Media and extensions](references/markdown-authoring/media-and-extensions.md).
- For generated artifacts, existing-document edits, validation, and completion review, read
  [Editing and validation](references/markdown-authoring/editing-and-validation.md).

For AGENTS.md or similar agent instructions, read [writing for agents](references/writing-for-agents.md).

## Finish deliberately

- Keep commands copyable, code fences balanced, links descriptive, and technical identifiers canonical.
- Validate with the repository-provided checks relevant to the changed content. When they do not
  cover portable structure, run `scripts/check-markdown.py <FILE>...` from this skill package. Do
  not add dependencies or alter validation configuration solely to check the document.
- Triage bundled-checker diagnostics against explicit repository requirements and renderer evidence. Document false positives or non-applicable rules rather than changing correct content to silence them. This does not waive actual defects or required repository checks.
- Report material changes, checks that ran and their results, and checks that could not run with the remaining unverified scope.
