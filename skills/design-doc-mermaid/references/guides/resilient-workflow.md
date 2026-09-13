# Local validation and artifact workflow

The package entrypoint owns scope, review gates and source truth.
This workflow replaces the upstream unconditional image/export/search loop.
Commands below run from the installed package; substitute absolute paths to the task's authorized files.
Use `python3` and inspect `--help` when adapting arguments.

## Inspect or validate Markdown

```bash
python3 scripts/extract_mermaid.py document.md --list-only
python3 scripts/extract_mermaid.py document.md --validate
```

The extractor handles unindented top-level backtick and tilde fences, including longer outer fences that contain examples.
It preserves distinct duplicate occurrences and rejects an unclosed Mermaid fence.
It rejects indented Mermaid fences and does not transform blockquote/list containers; report this coverage instead of claiming all diagrams were checked.
A zero-diagram validation fails rather than claiming a pass.
Validate container diagrams separately from their extracted source through the repository's appropriate parser/workflow.

## Extract editable sources

```bash
python3 scripts/extract_mermaid.py document.md --output-dir diagrams
```

Outputs are occurrence- and content-addressed and refuse existing paths.
Existing authorized document content remains untouched.
Use a new task-owned directory when extracting again; do not delete an unrelated directory to make the command pass.

## Render one source

```bash
python3 scripts/mermaid_to_image.py diagram.mmd diagram.svg
```

PNG and PDF are selected by the output extension.
Image exports default to an opaque white background to preserve readability on dark document surfaces.
For an explicitly selected dark variant, use `--theme dark --background "#1f2937"` and inspect the result; transparent output requires checking the destination background.
The compatibility entrypoint `resilient_diagram.py` accepts the same two positional paths.
The previous string/naming/batch flags are intentionally replaced by explicit input/output paths.
For a batch, enumerate only the requested inputs and call the renderer for each identified output.
The helper stages output beside the destination and publishes only a nonempty successful render.
Use `--overwrite` only when modification of that exact output is authorized; it is not itself permission.
Input/output aliasing and symlink output are rejected.

## Build an image-based review candidate

```bash
python3 scripts/extract_mermaid.py source.md --replace-with-images \
  --output-markdown review-candidate.md --image-dir diagrams --image-format svg
```

Every supported block must render before any replacement is published.
Links are built from each occurrence and actual generated artifacts, with preserved `.mmd` sources.
Assets use content hashes and are not overwritten; the input Markdown is never the output path.
The helper preserves old files on render failure and refuses conflicting output unless the exact candidate overwrite was authorized.
Check the candidate's content and links before using it in the requested final document.
Require separate user/team approval only when the user or repository explicitly requires it; rendering does not satisfy that human review.

## Runtime and failure classification

For an authorized runtime installation or package regression checks, use [runtime setup](../runtime-setup.md).
Resolve a repository-established renderer first by passing `--mmdc` and, if needed, `--puppeteer-config`.
Otherwise use the existing approved installation discovered by the helper.
Host configuration is `$XDG_CONFIG_HOME/developer-skills/mermaid-runtime.json`, defaulting to `~/.config/developer-skills/mermaid-runtime.json`.
It contains local `mmdc` and optional `puppeteer_config` paths; do not put personal runtime paths into the skill source.
Record the renderer version using that executable's `--version`.
Do not change browser sandbox flags or download dependencies to make a check pass without authorization for that change.

| Error | Response |
| --- | --- |
| TOOL_MISSING | Report missing executable; preserve draft and complete independent work |
| CONFIG_ERROR / BROWSER_ERROR | Diagnose configured runtime/browser; do not alter Mermaid syntax |
| TIMEOUT | Report bounded timeout and inspect complexity/runtime evidence |
| SYNTAX_ERROR | Use local type/version-specific syntax guidance |
| OUTPUT_ERROR / OUTPUT_CONFLICT / IO_ERROR | Preserve old artifact and fix only authorized output scope |
| RENDER_ERROR | Preserve diagnostic as unclassified; do not invent a syntax explanation |

No helper searches externally.
If external research is needed within the authorized task, use an available tool and a sanitized minimal reproduction with renderer version and error category.
Never automatically transmit repository source, full diagram content, raw error text containing internal identifiers, credentials or tokens.
Unavailable named providers are not installation requirements.
Retry only when new evidence supports a correction; stop repeated identical failures without a new hypothesis.
