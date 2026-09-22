# Skill mechanics in Codex

Use [writing-for-agents](SKILL.md) for the writing discipline.
Keep a useful name and description in SKILL.md front matter so Codex can discover the skill.
Put optional interface metadata in agents/openai.yaml.
For an explicitly invoked skill, use policy.allow_implicit_invocation: false in that YAML file, as the selected setup and grill-with-docs skills do.
Do not put disable-model-invocation: true in Codex SKILL.md front matter; the local plugin validator rejects it.

Split a skill only when the trigger or conditional reference earns its own entry.
Keep shared reference in a single linked file and state when to read it.
Use relative Markdown links for required packaged references so offline packaging verification can check them.

Use the current Codex skill catalog and native delegation tools that are actually available.
Do not invent a Skill tool, spawn a second workflow engine, or require another agent's planner.
Keep OpenSpec and Core routing authoritative, preserve user authorization, and write only the requested documentation.
Static validation establishes package shape and file integrity; verify native loading separately before claiming installation.
