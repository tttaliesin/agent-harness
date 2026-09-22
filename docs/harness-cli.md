# Harness CLI

`harnesskit` 0.1.0 requires Python 3.12 or newer, PyYAML, jsonschema, and native Git.
It connects product commands, real reports, local evidence, and cooperative resource ownership.
An installed package exposes both `harnesskit` and `python -m harnesskit`.
The integration owner supplies `uv.lock`, the root `just` commands, product templates, and Desktop launchers.

## Run commands

Run from the product root, or pass `--root PRODUCT` before the command.
Use `--git EXECUTABLE` before the command when Git is not on `PATH`.
Commands emit JSON with exit codes `0` for `PASS`, `1` for `FAIL`, and `2` for `BLOCKED`.
Help output is plain text.

The following commands use a full immutable `BASE_SHA` selected from an independently trusted product baseline.
That commit must contain `harness/project.yaml`; missing baseline policy is `BLOCKED`.

```text
harnesskit doctor
harnesskit check --change sample
harnesskit verify --change sample --base BASE_SHA
harnesskit evidence --change sample --base BASE_SHA --file .harness/evidence/RUN.json
harnesskit evidence --change sample --base BASE_SHA --file .harness/evidence/RUN.json --require-ci
harnesskit review --change sample --base BASE_SHA --evidence .harness/evidence/RUN.json --spec .harness/spec.json --standards .harness/standards.json
harnesskit handoff --change sample --base BASE_SHA --evidence .harness/evidence/RUN.json --next "harnesskit doctor"
```

Repeat `--change ID` for the union of several changes.
Repeat `--lock PATH` to fingerprint additional upstream or dependency locks; `harness/lock.json` is always included.
`verify --local` allows a dirty tree and records its contents, but its evidence cannot complete an official review.
`review --local` checks the two supplied local reviews while retaining `official: false` and `readonly_verified: false`.
Handoff accepts repeated `--durable REFERENCE`; it records references without claiming that uploads or remote accessibility were verified.
Writing and committing a handoff changes the candidate and requires refreshed verification.

## Product inputs and checks

The [project schema](../schemas/project.schema.json) validates `harness/project.yaml`.
The [change schema](../schemas/change.schema.json) validates `openspec/changes/ID/harness.yaml`, using the product's `documents.specs` path.
Each declared document must exist; each specification reference must contain nonempty files.
Archive paths may be used in `spec_refs`, while the ID resolver requires its active `harness.yaml` entry.
Archive-only ID resolution is not implemented in this release.

Unknown fields, duplicate YAML keys, aliases, unsupported versions, missing check IDs, duplicate selected IDs, and omitted dependency changes fail validation.
Product-relative paths reject absolute paths, parent traversal, Windows drive/stream syntax, reserved device names, symlinks, junctions, and Git metadata paths.
Only `{run_id}` is substituted, and only in report paths.
Configured commands are trusted executable code; path checks are not a sandbox for arbitrary product commands or concurrent hostile filesystem mutation.

The product baseline and each selected change's required checks form a sorted union.
A shared check ID executes once; distinct IDs are not combined even if their argv happens to match.
Existing check definitions cannot change against the trusted baseline except for increasing the minimum test count or tightening skip policy.
Removing checks, reducing the baseline, dropping packs, and increasing the repair budget fail.
Policy changes require a separately reviewed trusted baseline; a candidate's own revised commands cannot approve that policy change.

Each check has argv `command`, `kind`, and `timeout_seconds`.
`kind` is `structural`, `static`, or `tests`.
Tests also require `report`, `report_format` (`junit` or `playwright-json`), and `minimum_tests` of at least one.
Optional `allow_skipped` defaults to false; `required_tools` checks native executable availability.
Optional `resources: [browser, gpu]` returns `BLOCKED` until a verified product resource probe is available.

Commands run with `shell=False`, stdin closed, separate logs, and a timeout.
The runner exports `HARNESS_RUN_ID`, `HARNESS_RUN_DIR`, and `HARNESS_ACTIVE_VERIFY=1`; these are execution inputs, never CI proof.
The leaf command creates its reports under `$HARNESS_RUN_DIR/reports` using its native environment syntax.
Windows `.bat`/`.cmd` executable entry points are blocked because Windows can implicitly interpret them through a shell.
Windows descendants belong to a Job Object before the target executable starts; POSIX descendants belong to a new process group.
The runner terminates owned descendants on timeout and after normal completion.
An unavailable containment interface returns `BLOCKED`.

JUnit counts come from actual `testcase` elements and are checked against declared suite counts.
Playwright counts come from suite/spec/test results and actual retry attempts.
Failures, errors, interrupted or timed-out attempts, flaky retries, missing reports, inconsistent counts, and zero executed tests cannot pass.
Skipped cases never count toward the minimum executed count and fail unless explicitly allowed.

## Evidence and reviews

Official verification requires the native Git root, a clean index/worktree including untracked files, `.harness/` ignored by Git, and changed paths covered by the selected write scopes.
Assume-unchanged and skip-worktree flags block official verification.
Fingerprints bind HEAD, base, committed tree, actual worktree bytes, adapter, selected change mappings, specification files, effective policy, required checks, and locks.
Mutation during execution fails the run.
Evidence and report artifacts stay under ignored `.harness/` paths.

`evidence` reparses reports, rehashes logs, checks the exact required/executed sets, and compares current fingerprints.
The [evidence schema](../schemas/evidence.schema.json) always marks these records `provenance: {kind: local, verified: false}`.
Local files and environment variables cannot attest a CI run.
`--require-ci` returns `BLOCKED` without a trusted external provider, even if local checks pass.

The [review schema](../schemas/review.schema.json) binds each axis to the same fingerprint and evidence hash.
Spec and Standards require distinct reviewers, each different from the implementer; unresolved findings fail that axis independently.
Official reviews remain `BLOCKED` because a supplied provider name or receipt string cannot prove actual read-only enforcement.
Live Desktop permissions and CI/runner acceptance are not established by this CLI's tests.

## Binding ownership

Supply an explicit template root and [binding manifest](../schemas/binding.schema.json).
Each `files` entry contains a relative `source`, relative `target`, and SHA-256 of the actual source bytes; the top level contains `schema_version: 1`, `package_version`, and the required 64-hex `package_digest`.
The integration owner supplies the actual common runtime digest, normally SHA-256 of `upstream.lock.json`, from the explicitly trusted template source.
Templates copy byte for byte without interpolation.

```text
harnesskit sync --template-root TEMPLATE_ROOT --manifest binding.json
harnesskit check
```

The [product lock](../schemas/lock.schema.json) copies `package_digest` from that manifest and records the package version and generated target hashes.
This supplied digest identifies the selected common package; its presence is not authoritative CI provenance or independent verification of a remote publication.
Repeated sync with identical inputs makes no content or timestamp changes.
Sync preflights all conflicts before writes: user edits, user deletions, duplicate targets, and removing previously owned files preserve existing state and report a conflict.
Writes are atomic per file; interruption of a multi-file update may leave a partial update, and the next sync rechecks every hash.
An abandoned exclusive lock requires owner inspection; it is never silently stolen.

## Resource ownership and follow-up

Use the same explicit local `REGISTRY` directory for all worktrees sharing a resource.
The owner token and matching directory marker control release and cleanup; PID presence never grants deletion authority.
An expired lease remains blocked until its owner explicitly recovers/releases it.

```text
harnesskit lease acquire --change sample --owner TASK --resource RESOURCE --registry REGISTRY
harnesskit clean --change sample --owner TASK --registry REGISTRY --token TOKEN
harnesskit lease release --change sample --owner TASK --registry REGISTRY --token TOKEN
harnesskit followup --input event.json --registry REGISTRY
harnesskit followup --input event.json --registry REGISTRY --complete --token CLAIM_TOKEN
```

`clean` removes only the token-owned directory under `.harness/resources` and releases that lease.
`lease release` retains its directory; use `clean` while the lease is held if those files should be removed.
These are cooperative local reservations with `readiness_verified: false`; they do not bind ports, start Compose, allocate GPUs, kill external PIDs, or prove host resource readiness.
Service and remote-host lifecycle interfaces remain later product integration work.

The [follow-up event](../schemas/followup.schema.json) pins repository/PR, change, branch, worktree, head, owner, scope, event ID, and stop conditions.
The handler checks the native branch/head and declared scope, claims a single writer per repository common-dir/change, and deduplicates completed event/head pairs.
The caller performs work and explicitly completes its claim; a repair commit may advance HEAD before completion.
Crashes retain the claim for owner recovery instead of starting a second writer.
No scheduler or daemon is installed; responses retain `schedule: NOT_CONFIGURED`.

## Hooks

The [hook adapter schema](../schemas/hook.schema.json) is an explicit internal input, not the raw Desktop event schema.
The parent launcher maps native input into this schema and supplies bounded turn/session state.

```text
harnesskit hook --input event.json
harnesskit hook --input -
```

`adapter: local-v1` emits the internal JSON result and normal CLI exits.
`adapter: codex-desktop` emits the supported native JSON shape and exits zero, including on errors, since native exit two can itself request continuation.
Native errors are visible on stderr and do not request continuation.
The implementation follows the [official hook output contract](https://learn.chatgpt.com/docs/hooks).
Reentry, interruption, `BLOCKED`, and exhausted budgets never emit `decision: block`; Interrupt emits only an optional `systemMessage`.
Unsupported events or adapters are internally `BLOCKED`.
Handlers run no verification commands; an exclusive non-waiting lock and a 256-entry event history bound local handling.
The native launcher still needs an outer event timeout and per-session continuation bound.

After real verification, `.harness/hooks/verification-context.json` follows the [context schema](../schemas/verification-context.schema.json).
It includes `change_ids`, singleton `change_id` when applicable, `state`, `unresolved_findings`, fingerprint, evidence path/hash, and local provenance.
`unresolved_findings` counts failed verification checks; it does not clear review findings.
A new verify attempt invalidates old context before preflight; context is published only after persisted evidence validation.
The wrapper must reject missing, malformed, stale, or hash-mismatched context and must not treat a mutable local file as CI or permission proof.
Internal hook metadata is written to `.harness/hooks/latest.json`; actual Desktop event acceptance remains `NOT_RUN`.

## Development verification

The integration owner resolves the declared dependencies with uv and supplies the committed lock.
After `uv lock --check` and a deliberate locked environment sync, run these from the package root:

```text
uv run --no-sync pytest tests/test_core.py -q
uv run --no-sync ruff check src/harnesskit tests/test_core.py
uv run --no-sync ruff format --check src/harnesskit tests/test_core.py
```

Set `HARNESS_TEST_GIT` to an explicit native Git path if needed.
Tests use temporary repositories, failure reports, real subprocesses and child cleanup, stale/tampered evidence, binding conflicts, lease isolation, review gates, and hook/follow-up boundaries.
The schemas under `schemas/` are generated exports of `src/harnesskit/schema.py`; a test enforces equality.
Passing these checks verifies the common CLI slice, not product fixtures, live Desktop, trusted CI, runners, or deployment acceptance.
