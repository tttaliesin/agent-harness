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
- Current integrated and remote results are recorded in the common functional acceptance document and the final task handoff. CI evidence must come from this candidate's `usage-fixture-results` artifact.

## Resumption

Inspect the current candidate and `tasks.md`, compare result source hashes and commit attribution, then rerun any invalidated media checks.
Use separate dynamic loopback ports and output paths; stop only this invocation's owned resources. A missing prerequisite is BLOCKED, a failed media criterion is FAIL.
Resolve both review axes before syncing/archiving the accepted fixture contract and delivering the resulting source.
After publication, verify exact remote head, CI run and artifacts. Keep the user's installed skills intact until their migration is separately validated.
CPU synthetic transport and a new browser receiver do not establish production forwarding, GPU inference, tracker continuity or persistence of an already-connected browser session.
