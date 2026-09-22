---
name: code-review
description: Review a diff against its specification and repository standards, or assess review feedback before authorized fixes. Use for branch, PR and work-in-progress review and handling concrete review findings.
---

# Code review

For an existing review's feedback, go directly to [assess review feedback](references/receiving-review.md).
Run a fresh two-axis review only when requested or required by the change's acceptance criteria.

Two-axis review of the diff between `HEAD` and a fixed point the user supplies:

- **Standards**: does the code conform to this repo's documented coding standards?
- **Spec**: does the code faithfully implement the originating issue / spec?

Use native Codex sub-agents for independent Standards and Spec reviews when available and useful.
Give each a read-only scope, exact diff and acceptance source, and require evidence for findings.
If delegation is unavailable, perform the two passes directly and report that limitation.

Use the current task, repository review rules and applicable OpenSpec change as the authority for scope and review gates.
Tracker setup is not a prerequisite for reviewing a diff.
A review request remains read-only unless fixes are also authorized; publication of comments requires existing authorization.

## Process

### 1. Pin the fixed point

Whatever the user said is the fixed point (a commit SHA, branch name, tag, `main`, `HEAD~5`, etc.). Use a fixed point already established by the task or repository when available.
Ask only if competing comparisons would materially change the review.

Capture the diff command once: `git diff <fixed-point>...HEAD` (three-dot, so the comparison is against the merge-base). Also note the list of commits via `git log <fixed-point>..HEAD --oneline`.

For uncommitted work, include the relevant index and working-tree diff explicitly; three-dot HEAD alone omits it.
Capture the reviewed HEAD and working-tree state so later changes invalidate the evidence.
Before going further, confirm the fixed point resolves (`git rev-parse <fixed-point>`) and the diff is non-empty. A bad ref or empty diff should fail here, not inside two parallel sub-agents.

### 2. Identify the spec source

Look for the originating spec, in this order:

1. The acceptance source already supplied in the task or current OpenSpec change.
2. A specification path supplied by the user or referenced from the change.
3. An originating issue through the existing authorized tracker workflow when needed.
4. If no specification exists, a diagnostic Standards-only review may proceed with the Spec axis unavailable. For formal acceptance requiring a specification, report BLOCKED; never convert that partial review into acceptance.

### 3. Identify the standards sources

Anything in the repo that documents how code should be written, such as `CODING_STANDARDS.md` or `CONTRIBUTING.md`.

On top of whatever the repo documents, the Standards axis always carries the **smell baseline** below: a fixed set of Fowler code smells (_Refactoring_, ch.3) that applies even when a repo documents nothing. Two rules bind it:

- **The repo overrides.** A documented repo standard always wins; where it endorses something the baseline would flag, suppress the smell.
- **Always a judgement call.** Each smell is a labelled heuristic ("possible Feature Envy"), never a hard violation. Like any standard here, skip anything tooling already enforces.

Each smell reads *what it is* → *how to fix*; match it against the diff:

- **Mysterious Name**: a function, variable, or type whose name doesn't reveal what it does or holds. → rename it; if no honest name comes, the design's murky.
- **Duplicated Code**: the same logic shape appears in more than one hunk or file in the change. → extract the shared shape, call it from both.
- **Feature Envy**: a method that reaches into another object's data more than its own. → move the method onto the data it envies.
- **Data Clumps**: the same few fields or params keep travelling together (a type wanting to be born). → bundle them into one type, pass that.
- **Primitive Obsession**: a primitive or string standing in for a domain concept that deserves its own type. → give the concept its own small type.
- **Repeated Switches**: the same `switch`/`if`-cascade on the same type recurs across the change. → replace with polymorphism, or one map both sites share.
- **Shotgun Surgery**: one logical change forces scattered edits across many files in the diff. → gather what changes together into one module.
- **Divergent Change**: one file or module is edited for several unrelated reasons. → split so each module changes for one reason.
- **Speculative Generality**: abstraction, parameters, or hooks added for needs the spec doesn't have. → delete it; inline back until a real need shows.
- **Message Chains**: long `a.b().c().d()` navigation the caller shouldn't depend on. → hide the walk behind one method on the first object.
- **Middle Man**: a class or function that mostly just delegates onward. → cut it, call the real target direct.
- **Refused Bequest**: a subclass or implementer that ignores or overrides most of what it inherits. → drop the inheritance, use composition.

### 4. Run the independent review passes

**Standards sub-agent prompt** should include:

- The full diff command and commit list.
- The list of standards-source files you found in step 3, **plus the smell baseline from step 3** pasted in full (the sub-agent has no other access to it).
- The brief: "Report, per file/hunk where relevant, (a) every place the diff violates a documented standard: cite the standard (file + the rule); and (b) any baseline smell you spot: name it and quote the hunk. Distinguish hard violations from judgement calls: documented-standard breaches can be hard, but baseline smells are always judgement calls, and a documented repo standard overrides the baseline. Skip anything tooling enforces. Under 400 words."

**Spec sub-agent prompt** should include:

- The diff command and commit list.
- The path or fetched contents of the spec.
- The brief: "Report: (a) requirements the spec asked for that are missing or partial; (b) behaviour in the diff that wasn't asked for (scope creep); (c) requirements that look implemented but where the implementation looks wrong. Quote the spec line for each finding. Under 400 words."

If the spec is missing, skip the Spec sub-agent and note this in the final report.

### 5. Aggregate

Present the two reports under `## Standards` and `## Spec` headings, verbatim or lightly cleaned. Keep each finding's axis visible and consolidate duplicates.
Apply the repository review gate and severity rules when deciding readiness; one axis cannot hide a failure in the other.

End with a one-line summary: total findings per axis, and the worst issue _within each axis_ (if any). Include the applicable readiness decision and unresolved evidence gaps.

## Final acceptance and review feedback

For final acceptance, identify the repository, base, candidate commit, applicable specification, policy/skill revision and actual required-check results.
Before formal review, run `python scripts/check-candidate.py --repo <product> --base <base> --candidate <full-head-SHA> --spec <required-spec-path>` from this installed skill folder, repeating --spec for each required specification.
This read-only helper rejects a dirty tree, missing specifications, a changed candidate and an empty comparison; it does not run product checks or grant review permissions.
Give both review passes those same inputs; a changed candidate or relevant input requires updating the affected evidence.
Work-in-progress review may inspect a dirty tree, but it cannot establish final acceptance for an uncommitted or different candidate.
Missing required specifications, failed checks and stale results remain explicit gaps; neither axis can override the other's unresolved failure.
When independent read-only review is required, verify the actual delegation permissions and unchanged implementation tree. A role name, TOML setting or reviewer's assertion alone does not establish that boundary; report it as unavailable if the host cannot enforce it.
Use native Codex delegation when available; do not require generated product roles or a binding tool.

When acting on findings, read [assess review feedback](references/receiving-review.md).

## Why two axes

A change can pass one axis and fail the other:

- Code that follows every standard but implements the wrong thing → **Standards pass, Spec fail.**
- Code that does exactly what the issue asked but breaks the project's conventions → **Spec pass, Standards fail.**

Reporting them separately stops one axis from masking the other.
