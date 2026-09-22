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
If this record is archived, consult the canonical spec and the common functional acceptance document for delivery status.
Do not disable existing installed skills/plugins or report production, deployment, GPU or tracker acceptance from this fixture.


## Verified candidate and review disposition

Tested functional candidate: `768f5e8cefa686e1593b7284bfa9a6233221cb3a`, clean before and after the recorded runs.
CI-only successor: `d06fb7929b77837d159b2178188930a3ad5e3c65`; functional source is unchanged.
Acceptance record (repository-root relative): `docs/implementation/functional-acceptance.md`.
The independent native Spec and Standards snapshot reviews found no confirmed source defect, but requested current evidence and explicit handoff locations; the links and results here resolve those record omissions.
Original CI run 35724708653 passed Linux; Windows failed before fixture execution because the report parent was absent. Successor run 35725047006 verifies the corrected workflow. Do not treat the original whole run as passed.

Current local evidence: `fixtures/web-api/.reports/candidate-768f5e8/summary.json` and adjacent command, JUnit and checker reports (repository-root paths).
Observed HTTP 12 and Edge 7 passes, both checker exits 0, source hashes unchanged, owned listener/processes absent after completion.

Next action: inspect this checkout's head and any differences after the recorded candidate, verify the exact candidate's CI artifact, then follow remaining tasks or the archived canonical specification. Later documentation/archive commits do not by themselves establish new runtime behavior.
R2 installation and real product/operations acceptance remain unperformed; continue only the requested scope.

Verified CI: https://github.com/tttaliesin/agent-harness/actions/runs/35725047006 — both jobs SUCCESS for `d06fb7929b77837d159b2178188930a3ad5e3c65`. Downloaded package-and-helper-tests and usage-fixture-results artifacts; XML has 117 maintenance cases, five OpenSpec cases, 12 HTTP cases and seven browser cases with zero failures/errors/skips. Streaming JSON reports the same committed candidate, PASS and cleanup PASS.

Archival completed on 2026-09-22 by pinned OpenSpec 1.13.1: three requirements synchronized; canonical strict validation passed. The archival task itself was checked only after the CLI succeeded. All six fixture tasks are complete; original product and user-installation gates remain separate.
