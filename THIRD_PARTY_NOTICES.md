# Third-party notices

The following public upstream sources supply the selected engineering and execution packages.
Local compatible release: `0.1.0`.
Original copyrights and full license texts are preserved; local adaptations are identified per file in `upstream.lock.json` and in retained patch files.

## Matt Pocock skills

Source: [mattpocock/skills](https://github.com/mattpocock/skills).
Pinned commit: `c55ee46073ed923f86ce59a5eb3b6d895095d1b7`.
Copyright (c) 2026 Matt Pocock.
License: [MIT](plugins/matt-engineering/LICENSE.txt).

Selected paths are under `skills/engineering/` for setup-matt-pocock-skills, domain-modeling, grill-with-docs, codebase-design, and code-review, and `skills/productivity/` for grilling and writing-for-agents.
Required supporting files and `agents/openai.yaml` metadata are retained.
Local changes replace tracker and instruction-file scaffolding with the existing OpenSpec/Core workflow, adapt invocation and delegation to Codex, and preserve established authorization.
See the [package notice](plugins/matt-engineering/NOTICE.md).

## Superpowers execution

Source: [obra/superpowers](https://github.com/obra/superpowers).
Pinned commit: `5bf4e78011075bcfc0dc295f0724994cd123ee71`.
Copyright (c) 2025 Jesse Vincent.
License: [MIT](plugins/superpowers-execution/LICENSE.txt).

Selected paths: `skills/test-driven-development/`, `skills/verification-before-completion/`, and `skills/receiving-code-review/`.
The test-writing reference is retained.
Local changes preserve red/green/refactor, review assessment, and evidence before claims while respecting existing work, current authorization, and proportionate Core verification.
See the [package notice](plugins/superpowers-execution/NOTICE.md).

## Existing systematic-debugging adaptation

Source: [obra/superpowers](https://github.com/obra/superpowers).
Pinned commit: `b36e0829c6d0140e93cfef2ca599b1b07d4a7797`.
Original path: `skills/systematic-debugging/`.
Copyright (c) 2025 Jesse Vincent.
Original pinned license: [MIT](plugins/superpowers-execution/provenance/superpowers-debugging/LICENSE.txt).
The existing supply also preserves its [license](skills/systematic-debugging/LICENSE.txt) and [notice](skills/systematic-debugging/NOTICE.md).

The existing approved adaptation is selected without copying another active skill into the plugin.
Its original selected upstream bytes and current adaptation diff are captured for provenance; its local supporting files are included in the artifact inventory.
See [single debugging supply](plugins/superpowers-execution/DEBUGGING.md) for source and installed-catalog correspondence.

## Other existing repository material

Existing root skills retain their own licenses and notices.
Hash coverage of those files does not relicense them or claim derivation from the two selected upstream projects.
Parent-owned policy migration and its publication decisions remain outside this selection.
