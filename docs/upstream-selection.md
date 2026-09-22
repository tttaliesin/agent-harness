# Selected upstream Codex packages

The `matt-engineering` and `superpowers-execution` plugins share compatible version `0.1.0` with the parent Core bundle.
Each has a real `.codex-plugin/plugin.json` manifest and a `skills/` tree.
They use the existing OpenSpec and Core workflow for planning, authority, review gates, and delivery.
They define no hooks, MCP service, global installation, tracker lifecycle, or competing orchestration engine.

## Pinned selection

The public repositories were inspected and fetched on 2026-09-22.
Pins are full resolved Git commit IDs, not tags or inferred release versions.

| Source | Commit | License |
| --- | --- | --- |
| [Matt Pocock skills](https://github.com/mattpocock/skills) | `c55ee46073ed923f86ce59a5eb3b6d895095d1b7` | MIT |
| [Superpowers execution](https://github.com/obra/superpowers) | `5bf4e78011075bcfc0dc295f0724994cd123ee71` | MIT |
| [Existing debugging origin](https://github.com/obra/superpowers/tree/b36e0829c6d0140e93cfef2ca599b1b07d4a7797/skills/systematic-debugging) | `b36e0829c6d0140e93cfef2ca599b1b07d4a7797` | MIT |

The actual upstream paths and active destinations are listed below.
The lock enumerates every selected file, including supporting references and metadata.

| Upstream directory | Active supply |
| --- | --- |
| `skills/engineering/setup-matt-pocock-skills` | `matt-engineering/skills/setup-matt-pocock-skills` |
| `skills/engineering/domain-modeling` | `matt-engineering/skills/domain-modeling` |
| `skills/engineering/grill-with-docs` | `matt-engineering/skills/grill-with-docs` |
| `skills/productivity/grilling` | `matt-engineering/skills/grilling` |
| `skills/engineering/codebase-design` | `matt-engineering/skills/codebase-design` |
| `skills/engineering/code-review` | `matt-engineering/skills/code-review` |
| `skills/productivity/writing-for-agents` | `matt-engineering/skills/writing-for-agents` |
| `skills/test-driven-development` | `superpowers-execution/skills/test-driven-development` |
| `skills/verification-before-completion` | `superpowers-execution/skills/verification-before-completion` |
| `skills/receiving-code-review` | `superpowers-execution/skills/receiving-code-review` |
| `skills/systematic-debugging` at the older pin | Existing root `skills/systematic-debugging` only |

## Adaptation decisions

Setup reads existing Core bindings, AGENTS.md ownership, OpenSpec, domain documents, and tracker decisions.
It writes only missing requested pointers through the established owner.
The upstream GitHub, GitLab, local tracker templates, and triage-label template are omitted because this setup no longer consumes them.
The adapted domain guidance and all required glossary/ADR/design/testing references remain available.

Grill-with-docs loads explicit sibling references through Codex facilities.
Grilling resolves material open decisions and reuses prior authorization.
Domain modeling records terms and consequential decisions in existing locations, with upstream formats as fallbacks.
Codebase design keeps the deep-module vocabulary while preserving established repository terms.
Code review keeps independent Standards and Spec passes, uses native Codex delegation when available, includes uncommitted changes when applicable, and applies existing Core readiness rules.
Writing-for-agents retains the writing discipline; its mechanics reference uses Codex metadata rather than a Claude-specific Skill tool.

Setup and grill-with-docs preserve explicit invocation through `policy.allow_implicit_invocation: false` in `agents/openai.yaml`.
Their incompatible upstream `disable-model-invocation: true` front matter is removed.
Execution skills preserve meaningful testing, technical assessment of feedback, and evidence before claims, while avoiding destructive restart rules, blanket new approval gates, and redundant verification.
External review replies remain subject to existing communication authorization.

The existing [systematic-debugging](../skills/systematic-debugging/SKILL.md) is the sole active debugging supply.
Its [correspondence note](../plugins/superpowers-execution/DEBUGGING.md) explains the independently verified older pin and retained local references.
Parent integration must not add another active skill of that name to Core or either plugin.
If the parent deliberately relocates this supply, it must review the source target mappings and patch records as well as the active-supply check before refreshing the lock.

## Lock contract and offline verification

`upstream.lock.json` uses `schema_version: 1`, a `sources` list, and an `artifacts` mapping.
Artifact keys are canonical paths relative to the repository/package root; values are SHA-256 hashes of the exact bytes on disk.
The inventory includes all files under `plugins/`, `skills/`, `policies/`, `templates/`, and `docs/`, plus the root third-party notice and both packaging commands.
Runtime caches (`__pycache__`, `node_modules`, `.git`, `.pytest_cache`, `.venv`, and Python bytecode) are excluded.
Symlinks and Windows reparse points in the managed trees are rejected, including at ignored directory boundaries.

Each source has exactly `id`, `repository`, `commit`, `license`, `selected_paths`, and `patches`.
The license record contains `spdx`, `path`, and `sha256`.
Each per-file patch record contains `upstream_path`, `target`, `upstream_sha256`, `sha256`, and `reason`; changed files also have `patch` and `patch_sha256`.
Unchanged files retain a byte-for-byte copy record without a diff.
The full original license and copyright are preserved for each source pin.

Provenance directories retain original bytes with a `.source` suffix and the exact Git commit and required ancestor tree objects.
The verifier computes Git object IDs, walks the captured trees, and verifies each selected original blob belongs to its pinned commit.
It compares adaptation diffs and both original and target SHA-256 hashes.
These files are inert evidence outside active skill discovery.
The lock and scripts are trusted, reviewed inputs; the proof cannot authenticate a remote repository against malicious replacement of the pin and all evidence.

Verification rejects absent or extra artifacts, hash changes, missing manifests or versions, unexpected schema keys, missing required skills, duplicate active names across root and plugin trees, missing provenance or licenses, unsafe paths, and unresolved required Markdown links.
It validates inline links, reference definitions and explicit reference uses outside fenced examples, and recursively follows local Markdown links from every active root skill and active plugin prose.
URL fragments and arbitrary bare code spans are not file-dependency declarations.
Use explicit relative Markdown links for mandatory support files.
It performs no network calls, invokes no Git executable, and never modifies the lock.

From the repository root, use Python 3.12 or later with the project's existing PyYAML dependency:

```text
python scripts/check-packages.py --root .
python -m unittest discover -s tests -p test_packages.py -v
```

The check command emits JSON and returns `0` for PASS, `1` for invalid packaging, or `2` when the required Python dependency is unavailable.
PASS explicitly reports `native_installation_validated: false`.

## Parent integration and explicit refresh

After integrating Core and migrated policy artifacts, preview the new artifact inventory, then explicitly write and verify it:

```text
python scripts/refresh-package-lock.py --root <integration-root>
python scripts/refresh-package-lock.py --root <integration-root> --write
python scripts/check-packages.py --root <integration-root>
```

Omit `--root` to use the directory above the invoked script.
The preview reports added, removed, and changed paths and does not write files.
`--write` preserves all reviewed source records, validates the complete candidate, checks for concurrent changes, and atomically replaces only the lock.
An invalid candidate leaves the previous lock intact.
Verification never performs a refresh implicitly.

The refresh includes new Core/plugin directories and root policies/templates automatically.
It rejects duplicate active names if migration copies a skill into a plugin while leaving the root supply active.
It cannot silently accept changes to selected upstream/adapted bytes, pins, patches, or licenses; those need explicit reviewed source records and patch updates first.
The selected plugin directories use local `.gitattributes` to preserve exact bytes.
Existing root files retain their checkout bytes; the parent owns the final repository line-ending policy and final inventory refresh.
An intentional byte change to the selected debugging adaptation requires updating its recorded adaptation evidence, even when the change is only line endings.

## Verification boundary

Local plugin schema validation and these checks establish package structure, selection, provenance consistency, references, and static integrity.
They do not establish Codex Desktop loading, catalog availability, read-only enforcement, live delegation behavior, or successful installation.
Parent integration owns the final Core release, complete locked-environment checks, native validation, and any publication decision.
No private donor policy is introduced by this packaging slice.

## Packaging slice file list

The local packaging commit adds these 121 paths relative to the repository root.
Existing root skills and parent-owned artifacts are hashed but are not edited by this slice.

```text
THIRD_PARTY_NOTICES.md
docs/upstream-selection.md
plugins/matt-engineering/.codex-plugin/plugin.json
plugins/matt-engineering/.gitattributes
plugins/matt-engineering/LICENSE.txt
plugins/matt-engineering/NOTICE.md
plugins/matt-engineering/provenance/mattpocock-skills/commit.raw
plugins/matt-engineering/provenance/mattpocock-skills/files/LICENSE.source
plugins/matt-engineering/provenance/mattpocock-skills/files/skills/engineering/code-review/SKILL.md.source
plugins/matt-engineering/provenance/mattpocock-skills/files/skills/engineering/code-review/agents/openai.yaml.source
plugins/matt-engineering/provenance/mattpocock-skills/files/skills/engineering/codebase-design/DEEPENING.md.source
plugins/matt-engineering/provenance/mattpocock-skills/files/skills/engineering/codebase-design/DESIGN-IT-TWICE.md.source
plugins/matt-engineering/provenance/mattpocock-skills/files/skills/engineering/codebase-design/SKILL.md.source
plugins/matt-engineering/provenance/mattpocock-skills/files/skills/engineering/codebase-design/agents/openai.yaml.source
plugins/matt-engineering/provenance/mattpocock-skills/files/skills/engineering/domain-modeling/ADR-FORMAT.md.source
plugins/matt-engineering/provenance/mattpocock-skills/files/skills/engineering/domain-modeling/CONTEXT-FORMAT.md.source
plugins/matt-engineering/provenance/mattpocock-skills/files/skills/engineering/domain-modeling/SKILL.md.source
plugins/matt-engineering/provenance/mattpocock-skills/files/skills/engineering/domain-modeling/agents/openai.yaml.source
plugins/matt-engineering/provenance/mattpocock-skills/files/skills/engineering/grill-with-docs/SKILL.md.source
plugins/matt-engineering/provenance/mattpocock-skills/files/skills/engineering/grill-with-docs/agents/openai.yaml.source
plugins/matt-engineering/provenance/mattpocock-skills/files/skills/engineering/setup-matt-pocock-skills/SKILL.md.source
plugins/matt-engineering/provenance/mattpocock-skills/files/skills/engineering/setup-matt-pocock-skills/agents/openai.yaml.source
plugins/matt-engineering/provenance/mattpocock-skills/files/skills/engineering/setup-matt-pocock-skills/domain.md.source
plugins/matt-engineering/provenance/mattpocock-skills/files/skills/productivity/grilling/SKILL.md.source
plugins/matt-engineering/provenance/mattpocock-skills/files/skills/productivity/grilling/agents/openai.yaml.source
plugins/matt-engineering/provenance/mattpocock-skills/files/skills/productivity/writing-for-agents/SKILL-MECHANICS.md.source
plugins/matt-engineering/provenance/mattpocock-skills/files/skills/productivity/writing-for-agents/SKILL.md.source
plugins/matt-engineering/provenance/mattpocock-skills/files/skills/productivity/writing-for-agents/agents/openai.yaml.source
plugins/matt-engineering/provenance/mattpocock-skills/patches/skills/engineering/code-review/SKILL.md.patch
plugins/matt-engineering/provenance/mattpocock-skills/patches/skills/engineering/codebase-design/DEEPENING.md.patch
plugins/matt-engineering/provenance/mattpocock-skills/patches/skills/engineering/codebase-design/DESIGN-IT-TWICE.md.patch
plugins/matt-engineering/provenance/mattpocock-skills/patches/skills/engineering/codebase-design/SKILL.md.patch
plugins/matt-engineering/provenance/mattpocock-skills/patches/skills/engineering/domain-modeling/ADR-FORMAT.md.patch
plugins/matt-engineering/provenance/mattpocock-skills/patches/skills/engineering/domain-modeling/CONTEXT-FORMAT.md.patch
plugins/matt-engineering/provenance/mattpocock-skills/patches/skills/engineering/domain-modeling/SKILL.md.patch
plugins/matt-engineering/provenance/mattpocock-skills/patches/skills/engineering/grill-with-docs/SKILL.md.patch
plugins/matt-engineering/provenance/mattpocock-skills/patches/skills/engineering/setup-matt-pocock-skills/SKILL.md.patch
plugins/matt-engineering/provenance/mattpocock-skills/patches/skills/engineering/setup-matt-pocock-skills/domain.md.patch
plugins/matt-engineering/provenance/mattpocock-skills/patches/skills/productivity/grilling/SKILL.md.patch
plugins/matt-engineering/provenance/mattpocock-skills/patches/skills/productivity/writing-for-agents/SKILL-MECHANICS.md.patch
plugins/matt-engineering/provenance/mattpocock-skills/patches/skills/productivity/writing-for-agents/SKILL.md.patch
plugins/matt-engineering/provenance/mattpocock-skills/trees/0345ebb740dc47c09176a3b41a49cc11f4900073.raw
plugins/matt-engineering/provenance/mattpocock-skills/trees/1a0e4610dc7305e776f9619417bad296bc99ca01.raw
plugins/matt-engineering/provenance/mattpocock-skills/trees/344e3efc88ee60663b2e989555c2efdb548fbd42.raw
plugins/matt-engineering/provenance/mattpocock-skills/trees/3715f0eaf6fcc837da99f7b18bf908bec43f360a.raw
plugins/matt-engineering/provenance/mattpocock-skills/trees/388c9822641805ca2dcd5038e68a1d5282437ee5.raw
plugins/matt-engineering/provenance/mattpocock-skills/trees/44709f81e0e99fdbfad95a07bf5bdb571b0e9527.raw
plugins/matt-engineering/provenance/mattpocock-skills/trees/560d16960aa2757eef84f574e5173f6f69ebba99.raw
plugins/matt-engineering/provenance/mattpocock-skills/trees/8bacfedbf90e1a083c7cbd86f313d50cdd1d0165.raw
plugins/matt-engineering/provenance/mattpocock-skills/trees/ad2925850efb8973a72d2e666f7a975f9a2d4a9b.raw
plugins/matt-engineering/provenance/mattpocock-skills/trees/d8adf71d95e60b320608cf0aaf32f8587bc5cb0a.raw
plugins/matt-engineering/provenance/mattpocock-skills/trees/d8e341cee7980127dddda05159bedf25dc853615.raw
plugins/matt-engineering/provenance/mattpocock-skills/trees/e558f1f3c91f83f0eed9245f8b3d29b5a02a26ce.raw
plugins/matt-engineering/provenance/mattpocock-skills/trees/ec07f82df54064d01aa1648670e81da41e2cbdc2.raw
plugins/matt-engineering/provenance/mattpocock-skills/trees/eedaf2562c83155115e9c649fa3ecaac2e10e81d.raw
plugins/matt-engineering/provenance/mattpocock-skills/trees/f0732035b8b1b60ae39454e4191caef32fa91903.raw
plugins/matt-engineering/provenance/mattpocock-skills/trees/f142d14320695e1004d43997f20d2e98ff40e62c.raw
plugins/matt-engineering/provenance/mattpocock-skills/trees/f4eed2af42f99ada31a12e14b19189aea4dcc72f.raw
plugins/matt-engineering/provenance/mattpocock-skills/trees/f9e04d6e5228bdda9ccbac73f499cb672e23102d.raw
plugins/matt-engineering/skills/code-review/SKILL.md
plugins/matt-engineering/skills/code-review/agents/openai.yaml
plugins/matt-engineering/skills/codebase-design/DEEPENING.md
plugins/matt-engineering/skills/codebase-design/DESIGN-IT-TWICE.md
plugins/matt-engineering/skills/codebase-design/SKILL.md
plugins/matt-engineering/skills/codebase-design/agents/openai.yaml
plugins/matt-engineering/skills/domain-modeling/ADR-FORMAT.md
plugins/matt-engineering/skills/domain-modeling/CONTEXT-FORMAT.md
plugins/matt-engineering/skills/domain-modeling/SKILL.md
plugins/matt-engineering/skills/domain-modeling/agents/openai.yaml
plugins/matt-engineering/skills/grill-with-docs/SKILL.md
plugins/matt-engineering/skills/grill-with-docs/agents/openai.yaml
plugins/matt-engineering/skills/grilling/SKILL.md
plugins/matt-engineering/skills/grilling/agents/openai.yaml
plugins/matt-engineering/skills/setup-matt-pocock-skills/SKILL.md
plugins/matt-engineering/skills/setup-matt-pocock-skills/agents/openai.yaml
plugins/matt-engineering/skills/setup-matt-pocock-skills/domain.md
plugins/matt-engineering/skills/writing-for-agents/SKILL-MECHANICS.md
plugins/matt-engineering/skills/writing-for-agents/SKILL.md
plugins/matt-engineering/skills/writing-for-agents/agents/openai.yaml
plugins/superpowers-execution/.codex-plugin/plugin.json
plugins/superpowers-execution/.gitattributes
plugins/superpowers-execution/DEBUGGING.md
plugins/superpowers-execution/LICENSE.txt
plugins/superpowers-execution/NOTICE.md
plugins/superpowers-execution/provenance/superpowers-debugging/LICENSE.txt
plugins/superpowers-execution/provenance/superpowers-debugging/commit.raw
plugins/superpowers-execution/provenance/superpowers-debugging/files/LICENSE.source
plugins/superpowers-execution/provenance/superpowers-debugging/files/skills/systematic-debugging/SKILL.md.source
plugins/superpowers-execution/provenance/superpowers-debugging/files/skills/systematic-debugging/condition-based-waiting-example.ts.source
plugins/superpowers-execution/provenance/superpowers-debugging/files/skills/systematic-debugging/condition-based-waiting.md.source
plugins/superpowers-execution/provenance/superpowers-debugging/files/skills/systematic-debugging/defense-in-depth.md.source
plugins/superpowers-execution/provenance/superpowers-debugging/files/skills/systematic-debugging/root-cause-tracing.md.source
plugins/superpowers-execution/provenance/superpowers-debugging/patches/skills/systematic-debugging/SKILL.md.patch
plugins/superpowers-execution/provenance/superpowers-debugging/patches/skills/systematic-debugging/defense-in-depth.md.patch
plugins/superpowers-execution/provenance/superpowers-debugging/patches/skills/systematic-debugging/root-cause-tracing.md.patch
plugins/superpowers-execution/provenance/superpowers-debugging/trees/21219529a4e224bcb27baf8816b039c8bf7c6673.raw
plugins/superpowers-execution/provenance/superpowers-debugging/trees/9483dd00b0bda60c6ea631d88900f0436630d064.raw
plugins/superpowers-execution/provenance/superpowers-debugging/trees/ab83fc82f82582e047d96fc516bac9bc03095ee0.raw
plugins/superpowers-execution/provenance/superpowers/commit.raw
plugins/superpowers-execution/provenance/superpowers/files/LICENSE.source
plugins/superpowers-execution/provenance/superpowers/files/skills/receiving-code-review/SKILL.md.source
plugins/superpowers-execution/provenance/superpowers/files/skills/test-driven-development/SKILL.md.source
plugins/superpowers-execution/provenance/superpowers/files/skills/test-driven-development/writing-good-tests.md.source
plugins/superpowers-execution/provenance/superpowers/files/skills/verification-before-completion/SKILL.md.source
plugins/superpowers-execution/provenance/superpowers/patches/skills/receiving-code-review/SKILL.md.patch
plugins/superpowers-execution/provenance/superpowers/patches/skills/test-driven-development/SKILL.md.patch
plugins/superpowers-execution/provenance/superpowers/patches/skills/test-driven-development/writing-good-tests.md.patch
plugins/superpowers-execution/provenance/superpowers/patches/skills/verification-before-completion/SKILL.md.patch
plugins/superpowers-execution/provenance/superpowers/trees/3c7f2d3ef243f88d3394158983e6845e313c438b.raw
plugins/superpowers-execution/provenance/superpowers/trees/847144cf0824095922c0d4875648b9fa74877e1a.raw
plugins/superpowers-execution/provenance/superpowers/trees/a4cb0b69aaefeab540947a7f1642bdaad810e37a.raw
plugins/superpowers-execution/provenance/superpowers/trees/b5e154fc3ec7a6a0b1e710eebacc2168620cc428.raw
plugins/superpowers-execution/provenance/superpowers/trees/efab49a27a228b307cbaec46c77d6b9ae34be3d2.raw
plugins/superpowers-execution/skills/receiving-code-review/SKILL.md
plugins/superpowers-execution/skills/test-driven-development/SKILL.md
plugins/superpowers-execution/skills/test-driven-development/writing-good-tests.md
plugins/superpowers-execution/skills/verification-before-completion/SKILL.md
scripts/check-packages.py
scripts/refresh-package-lock.py
tests/test_packages.py
upstream.lock.json
```
