---
name: verification-before-completion
description: Require observed evidence before claiming work complete, fixed, or passing; assess what the checks actually prove and report remaining limits.
---

# Verification before completion

Evidence must support the exact claim being made.
Use the current task acceptance criteria, applicable OpenSpec change and authorized delivery endpoint to determine what completion means.

## Verify the claim

1. Identify the test, inspection, build, or operational evidence that demonstrates the claim.
2. Run the applicable check against the changed state, or reuse recorded evidence still valid for the same code, inputs, and environment.
3. Read its output, exit code, test count, failures, and skipped checks.
4. Compare that evidence with the requirement and state any gap.
5. Report the supported outcome and the scope actually verified.

Changed files or dependencies, new failures, and environmental changes can invalidate earlier evidence.
Rerun the affected checks when that happens.
Do not repeat unchanged checks solely because another message or process step has occurred.
A zero-test run, skipped suite, or missing tool does not establish a passing implementation.

## Match evidence to claims

| Claim | Required evidence |
| --- | --- |
| Behavior fixed | Original symptom reproduced and the changed behavior verified |
| Regression test protects the fix | Expected failure observed before the fix and pass after it |
| Tests pass | Actual executed test count, output, and successful exit |
| Build succeeds | Successful build command for the relevant state |
| Requirements met | Evidence mapped to the actual acceptance criteria |
| Delegated work integrated | Inspected changes and integration checks at the destination |
| Skill installed and available | Actual discovery and invocation in addition to static file validation |
| Deployment healthy | Relevant deployed-state evidence, beyond local unit tests |

Keep partial evidence useful by stating what it proves and what remains unverified.
Run required gates, then broaden or repeat checks only for a concrete remaining risk.
For a CI claim, compare the actual repository, checked-out commit, run/job and required reports with the candidate being delivered.
Do not infer remote CI provenance from local JSON or a worker's success message.
A missing required tool, browser or GPU leaves that check unavailable; an exit-zero command with zero tests or a missing required report is not sufficient evidence.
Preserve the authorized delivery endpoint and report pending integration, installation, or external validation with its owner.
