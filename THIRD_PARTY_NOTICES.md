# Third-party notices

Selected skills and adapted references retain the following upstream licenses.
Each installed skill carries the license needed for its selected or adapted material.
File mappings and reviewed patches are recorded in upstream.lock.json; the original bytes and Git objects are retained under provenance/.

## Matt Pocock skills

Source: [mattpocock/skills](https://github.com/mattpocock/skills)
Pinned commit: c55ee46073ed923f86ce59a5eb3b6d895095d1b7
Copyright (c) 2026 Matt Pocock
License: [MIT](provenance/mattpocock-skills/LICENSE.txt)

Active skills: domain-modeling, grilling, codebase-design and code-review.
Adapted references from grill-with-docs and writing-for-agents are included in grilling and markdown-authoring respectively.
Local adaptations use the current task, native Codex capabilities, product specifications and existing commands, preserving the user's authorization.
The code-review candidate preflight script is locally authored supporting code, explicitly listed in the package verifier, rather than an upstream file or a Git-object provenance claim.

## Superpowers

Source: [obra/superpowers](https://github.com/obra/superpowers)
Pinned commit: 5bf4e78011075bcfc0dc295f0724994cd123ee71
Copyright (c) 2025 Jesse Vincent
License: [MIT](provenance/superpowers/LICENSE.txt)

Active skills: test-driven-development and verification-before-completion.
The adapted receiving-code-review guidance is included as a reference in code-review with its own license copy.
Local changes preserve meaningful tests, independent assessment of feedback and evidence before completion claims.

## Existing systematic-debugging adaptation

Source: [obra/superpowers](https://github.com/obra/superpowers)
Pinned commit: b36e0829c6d0140e93cfef2ca599b1b07d4a7797
Copyright (c) 2025 Jesse Vincent
Original license: [MIT](provenance/superpowers-debugging/LICENSE.txt)
The existing adaptation retains its [license](skills/systematic-debugging/LICENSE.txt) and [notice](skills/systematic-debugging/NOTICE.md).

## Other repository material

Existing root skills retain their own licenses and notices.
Artifact hash coverage does not relicense files or claim that all repository material derives from the sources above.
