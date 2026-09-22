# Streaming fixture handoff

## Scope and authority

Repository: `tttaliesin/agent-harness`, integration branch `main`, fixture root `fixtures/streaming`.
The user authorized the original missing common-skill functionality and public push after a sensitive-information scan.
Base: `650a7d90e0963f17aa0203a811f8f9055798b374`.
Obtain the current full candidate with `git rev-parse HEAD`, inspect Git status and pass both to review; never substitute this base for the tested candidate.

## Inputs and observations

- Specification: this change's `specs/streaming/spec.md`, or `openspec/specs/streaming/spec.md` after archival.
- Commands, fixed native tool downloads and checksums: `README.md`, `tools.json`, `package.json` and `pnpm-lock.yaml`.
- Changes: MediaMTX source, FFmpeg decoded-frame probe, interruption/recovery and actual browser WebRTC receiver.
- Each fresh `.reports/run-*/result.json` records its own runtime outcomes; use the corresponding command log and source attribution, not a report from an unrelated run.
- Historical worker observations: 12 changing initial frames, a two-second live-server outage with zero frames, 12 recovery frames and advancing browser receive statistics.
- Review required stronger epoch verification, descendant cleanup, unavailable-tool classification and an early-return outage regression; the historical result alone does not establish those fixes.
- Current integrated and remote results are recorded in the common functional acceptance document and the common functional acceptance document. CI evidence must come from this candidate's `usage-fixture-results` artifact.

## Resumption

Inspect the current candidate and `tasks.md`, compare result source hashes and commit attribution, then rerun any invalidated media checks.
Use separate dynamic loopback ports and output paths; stop only this invocation's owned resources. A missing prerequisite is BLOCKED, a failed media criterion is FAIL.
Resolve both review axes before syncing/archiving the accepted fixture contract and delivering the resulting source.
After publication, verify exact remote head, CI run and artifacts. Keep the user's installed skills intact until their migration is separately validated.
CPU synthetic transport and a new browser receiver do not establish production forwarding, GPU inference, tracker continuity or persistence of an already-connected browser session.


## Verified candidate and review disposition

Tested functional candidate: `768f5e8cefa686e1593b7284bfa9a6233221cb3a`, clean before and after the recorded runs.
CI-only successor: `d06fb7929b77837d159b2178188930a3ad5e3c65`; functional source is unchanged.
Acceptance record (repository-root relative): `docs/implementation/functional-acceptance.md`.
The independent native Spec and Standards snapshot reviews found no confirmed source defect, but requested current evidence and explicit handoff locations; the links and results here resolve those record omissions.
Original CI run 35724708653 passed Linux; Windows failed before fixture execution because the report parent was absent. Successor run 35725047006 verifies the corrected workflow. Do not treat the original whole run as passed.

Current local evidence: `fixtures/streaming/.reports/run-5fa417a9646c462ba452f7d709241e20/result.json` and adjacent commands/probe/browser reports (repository-root paths).
Observed initial 12 frames, two-second zero-frame outage, recovery 12 blue-marked frames in 2.5 seconds, browser decoded +27 and zero cleanup survivors. The result attributes unchanged runtime hashes to the exact committed candidate above.
All four media review findings were fixed; 33 streaming regressions passed, including old-epoch pixels, early 404 and orphaned descendants.

Next action: inspect this checkout's head and any differences after the recorded candidate, verify the exact candidate's CI artifact, then follow remaining tasks or the archived canonical specification. Later documentation/archive commits do not by themselves establish new runtime behavior.
R2 installation and real product/operations acceptance remain unperformed; continue only the requested scope.

Verified CI: https://github.com/tttaliesin/agent-harness/actions/runs/35725047006 — both jobs SUCCESS for `d06fb7929b77837d159b2178188930a3ad5e3c65`. Downloaded package-and-helper-tests and usage-fixture-results artifacts; XML has 117 maintenance cases, five OpenSpec cases, 12 HTTP cases and seven browser cases with zero failures/errors/skips. Streaming JSON reports the same committed candidate, PASS and cleanup PASS.

Archival completed on 2026-09-22 by pinned OpenSpec 1.13.1: three requirements synchronized; canonical strict validation passed. The archival task itself was checked only after the CLI succeeded. All six fixture tasks are complete; original product and user-installation gates remain separate.
