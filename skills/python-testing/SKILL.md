---
name: python-testing
description: Run and assess a Python project's existing tests with uv or its established tooling, diagnose missing or misleading test results, and validate JUnit reports against the actual command exit and run start. Use for Python test execution and evidence; toolchain migrations remain a separate task.
---

# Python Testing

## Route the task

- For an existing test request, inspect `pyproject.toml`, the lock, test configuration and documented commands; run the relevant existing checks.
- For a regression or new behavior, reproduce the observable failure, add a test at the public boundary, implement the change, and rerun the affected checks.
- For a completion claim or suspicious CI result, examine the actual command, exit code, collected/executed counts, skips, failures and report freshness.
- For HTTP or browser behavior, use the product's real server and saved browser tests when required; Python unit results alone do not establish browser behavior.

Preserve the selected framework and product command ownership.
If compatible test setup is part of the authorized implementation, add the smallest necessary test dependency and lock it in the product.
Installing this skill alone requires no Python environment; its report helper requires Python 3.12+ and no third-party packages or other skills.

## Execute and collect evidence

Use the product's locked environment.
For uv projects, separate an explicitly requested setup (`uv sync --locked`) from checks (`uv run --frozen --no-sync ...`); tests must not silently install dependencies or rewrite the lock.
Use an isolated environment/cache for an assigned worktree and bounded command timeouts.
For non-uv projects, preserve their equivalent existing commands.

Capture the run start immediately before invoking the real test command and retain its exit code before another command replaces it.
Write the report to an owned run location and inspect stdout/stderr when collection, setup or execution fails.
Record the revision, command, selected tests, environment, report location and actual result for the owning workflow.
Do not substitute this fixture's results, a parser result or a hand-written PASS marker for product tests.

## Check JUnit evidence

For pytest/Playwright-style JUnit, run the standalone [report checker](scripts/check-junit.py) with the report, test command exit code and start time.
Resolve the script relative to this installed skill directory, regardless of the product working directory.
Read [JUnit usage and accepted format](references/junit.md) for commands, counted fields, size limits and freshness constraints.

Any nonzero command exit, malformed/missing/stale report, zero actual cases, all-skipped run, failure/error or contradictory counts prevents PASS.
Partial skips remain visible; a required skipped check remains unverified even when other cases pass.
Unavailable required tools or environments remain BLOCKED, with the missing prerequisite identified.
For other test report formats, inspect the framework's actual result or its existing parser; do not fabricate JUnit to make this checker accept it.

The checker assesses local report consistency, not CI provenance, candidate identity, specification coverage or authenticity.
The owning workflow must tie evidence to the actual current candidate and required checks.
