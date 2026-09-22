# Shared skills development

This repository owns reusable skills, policy references and their specific supporting tools.
Product commands, specifications, CI and deployment belong to the product or infrastructure owner.

## Locate and route

- Start with README.md, docs/implementation/layout-map.md and the affected skill.
- Common policy: skills/workspace-governance/references/workspace-rules/.
- Tool selection: skills/development-tooling/; CI: skills/github-actions-workflows/.
- Git operations and delivery: skills/github-operations/.

## Change and verify

Keep one active source per skill name under skills/ and make selected installation self-contained.
Use existing product commands; do not introduce a consumer runtime, adapter schema or generic state manager.
Keep a helper in its owning skill only when it has a concrete job.
Use the pinned maintainer tools in mise.toml, explicit just sync, then just check.
Checks must not install dependencies, modify locks or publish.
Review source pins, adaptation patches and licenses before refreshing upstream.lock.json.
The lock records source provenance and repository integrity; it is not product CI evidence.
Preserve user's installed modifications and avoid duplicate plugin/skill supply during migrations.
Do not generate instructions above the repository root.

## Completion

Report the candidate, observed checks, authorized delivery state and remaining installation or usage validation.
