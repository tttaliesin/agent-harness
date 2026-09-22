---
name: test-driven-development
description: Develop meaningful behavior changes through a failing test, minimal implementation, and refactoring. Use for new behavior and regression fixes with an appropriate test surface.
---

# Test-driven development

Write a behavioral test, observe its expected failure, implement the smallest change, and observe the pass.
Use the current task acceptance criteria, applicable OpenSpec change and repository checks to choose the scope.
Read [writing good tests](writing-good-tests.md) when adding or changing tests.

## Choose evidence for the change

For a behavior change, name the concrete failure the test should catch before writing it.
Prefer a deterministic test through the real public interface, with literal expectations independent of the implementation.
An existing failing reproduction may supply the red evidence for a bug fix.
Preserve existing work; do not delete implementation merely because it predates the test.

For documentation, generated output, configuration, or a reversible change without a useful automated test surface, use the applicable repository check or narrow repeatable verification.
Follow existing task authorization and policy; a process exception alone does not require another approval.
Do not add tautological tests or tests that only mirror source text.

## Red

Write the smallest test that exposes the missing or incorrect behavior.
Run it and inspect the output and exit code.
Confirm the failure is the intended assertion, rather than a setup error or unrelated environmental problem.
If it already passes, determine whether existing behavior satisfies the requirement or the assertion misses the defect.

## Green

Implement the smallest change that satisfies the test.
Run the failing test and directly affected regression checks.
Use real components; mock only external or expensive boundaries whose behavior you understand.
Keep test helpers out of production interfaces.

## Refactor

After the test passes, simplify names, remove duplication, or improve the interface within the authorized scope.
Retest the affected behavior after each material change.
Avoid speculative features and unrelated cleanup.

## Complete

Run applicable repository-required checks and tests proportionate to the affected behavior.
Broaden verification when dependencies, failures, new changes, or a required gate justify it.
Report pre-existing failures without expanding the mutation scope automatically.
Report the observed failing and passing behavior, executed checks and remaining limits.
Use verification-before-completion or systematic-debugging when installed and relevant; otherwise assess the evidence or investigate the failure directly.
