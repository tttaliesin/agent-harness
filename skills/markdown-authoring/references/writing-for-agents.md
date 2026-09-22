# Instructions intended for agents

Use this reference for AGENTS.md and similar instruction documents.
For authoring a skill, use the available skill-creator guidance; if unavailable, preserve the supported SKILL.md format and validate against the target agent's documentation.

- Include repository-specific commands, ownership boundaries and non-obvious decisions that change the agent's actions.
- Prefer a short entrypoint linked to existing maintained documents over duplicated policy prose.
- Separate instructions that always apply from conditional workflows; load detailed references only for the relevant task.
- Verify paths and commands against the repository and preserve the user's task and existing authorization.
- Remove generic advice and instructions already supplied by the agent runtime.
- Validate a substantial workflow with a realistic request; file format checks alone do not prove useful behavior.

Adapted from Matt Pocock's writing-for-agents; see the bundled [MIT license](../LICENSE.mattpocock.txt).
