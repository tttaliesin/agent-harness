# Web/API fixture handoff

## Scope and authority

Repository: `tttaliesin/agent-harness`, integration branch `main`, fixture root `fixtures/web-api`.
The user authorized restoration of the original common-skill functionality and public push after a sensitive-information scan.
This fixture implements the Web/Python acceptance example; production Allsen changes and installed-user migration remain separate gates.
Base: `650a7d90e0963f17aa0203a811f8f9055798b374`.
Read the containing checkout's `git rev-parse HEAD` and status before resuming; a task must supply that full candidate to formal review.

## Inputs and observations

- Specification: this change's `specs/web-api/spec.md`, or `openspec/specs/web-api/spec.md` after archival.
- Commands and prerequisites: `USAGE.md`, the fixture's uv/npm locks and `playwright.config.cjs`.
- Changes: HTTP service, browser page, 12 HTTP cases, seven Edge cases, and the shared Python JUnit checker.
- Integrated local observation at `481f6a827b5d081f005baf2ba2f15a0dfd48e51b`: 12 HTTP and seven Edge cases passed; source/checker/lock hashes unchanged across execution.
- Both actual XML reports passed `check-junit.py` with captured command exits and start times; fixture processes and the exact listening port were absent afterward.
- The worktree also contained in-progress integration instructions. This observation does not certify an arbitrary later commit or a clean formal-review candidate.
- Local details: `.reports/integrated-web-python/summary.json`, `python-run.json`, `browser-run.json`, corresponding XML and logs; ignored and regenerable.
- Durable remote evidence after publication: the exact candidate's `Skill repository checks` run and `usage-fixture-results` artifact, not a latest-branch badge.

## Resumption

Compare the supplied candidate, current Git state and changed inputs with the observation above. Preserve unaffected runtime evidence and rerun invalidated checks.
Run the remaining checks/review in `tasks.md`, record finding dispositions, and sync/archive only after fixture acceptance; the archive must be delivered with the source.
Check public delivery against the exact remote SHA and CI artifact before reporting it complete.
If this record is archived, consult the canonical spec and the current task's final handoff for delivery status.
Do not disable existing installed skills/plugins or report production, deployment, GPU or tracker acceptance from this fixture.
