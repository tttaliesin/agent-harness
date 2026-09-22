---
name: grilling
description: Stress-test a plan, decision or idea through focused questions when the user requests an interview or design challenge. Record resolved decisions in existing documents when requested.
---

# Grilling

Interview the user about the unresolved decisions that materially affect the requested outcome.
Reuse settled decisions and authorization from the current OpenSpec change and conversation. Map this as a **design tree**: every decision branches into the decisions that hang off it.

Work the tree in **rounds**. The **frontier** is every decision whose prerequisites are already settled: the questions you can ask _now_ without guessing at answers you haven't heard yet. Ask a small coherent set from the frontier in one round: number each question and give your recommended answer. Then wait for the user's answers before the next round.

Format a round like so:

```
❓ **Q1** - **<question title>**: <question body, might be multiple paragraphs, including multiple choices>

➡️ <your recommended answer>

---

❓ **Q2** - **<question title>**: <question body, might be multiple paragraphs, including multiple choices>

➡️ <your recommended answer>
```

Each round the user answers reshapes the tree: settled decisions push the frontier outward and unblock questions that depended on them. Recompute the frontier and ask the next round. A question whose answer depends on another question still open in this round belongs to a _later_ round, not this one.

Finding _facts_ is your job, never the user's. When a frontier question needs a fact from the environment (filesystem, tools, etc.), use native Codex delegation when independent exploration benefits from it, or inspect directly; do not ask the user for facts you can look up. Give delegated work a clear scope and expected evidence, then inspect the result. Don't block on it: a running exploration is an unsettled prerequisite, so only the questions downstream of it wait for the sub-agent to report; ask the rest of the frontier now. The _decisions_ are the user's: put each to them and wait.

The interview is complete when material decisions are settled and remaining assumptions are stated.
When recording resolved terms or decisions, read [record decisions](references/record-decisions.md).
Continue already authorized work; ask for a decision only when an unresolved choice blocks a dependent action.
Do not turn the interview into a blanket approval gate or another planning lifecycle.
