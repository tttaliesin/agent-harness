---
name: webapp-testing
description: Inspect and test local web application behavior, rendered UI, browser errors, and end-to-end flows using the available browser or repository test stack.
license: Complete terms in LICENSE.txt
---

# Web Application Testing

## Choose the execution surface

For interactive inspection, follow the available Browser skill and the user's selected browser/session.
Preserve login state and browser permissions; do not switch to a separate browser session to bypass a limitation.
For repository E2E work, inspect existing test commands, framework, language, fixtures, and browser configuration first.
Use that stack rather than imposing native Python Playwright, Chromium, or headless mode.
Python Playwright is an optional fallback only when compatible with the task and environment.
Do not add a second framework or download browser binaries just to follow an example.
When compatible test setup is part of the authorized implementation, add the required saved tests and lock their dependencies in the product.

Use Playwright MCP for interactive exploration and reproduction when that surface is available and appropriate.
Use saved Playwright Test cases for repeatable acceptance evidence; an MCP connection, snapshot or successful click does not count as a Test run.
For MCP setup and converting a reproduction into saved tests, read [browser reproduction and Test evidence](references/playwright-evidence.md).

A read-only task does not implicitly authorize writing repository scripts, screenshot/report files, application data changes, or server startup.
Nonmutating inspection through existing tools, including ephemeral browser screenshots, can remain within read-only scope; honor any stricter user restrictions.
Use available inspection tools and report unavailable execution evidence when the requested flow exceeds scope.
Reuse existing approvals for the same target; preserve explicit approval, credential, and production gates.

## Establish server ownership and readiness

Reuse an existing server after verifying its address and application identity.
An open port alone proves neither application identity nor readiness.
If startup is authorized and necessary, use the repository's existing lifecycle tooling.
Before first use or after a helper update, inspect its subprocess, network, output, and cleanup behavior; unchanged reviewed helpers need not be reread.
Use help output after this check when needed for correct arguments.
Record task-owned processes and stop only those processes and their owned children.
Never kill a preexisting server or all processes on a port as cleanup.
The upstream with_server.py helper and Python examples are not included in this package.

## Inspect, wait, act, verify

1. Inspect the route, rendered DOM, visible state, and relevant browser errors.
2. Wait with a bounded timeout for the observable condition needed by the next action: expected route, visible element, enabled control, or loaded data state.
3. Select elements from observed state, preferring roles, labels, or existing test IDs.
4. Perform only actions within the user's scope and verify the resulting UI/data state.
5. Record reproducible steps, expected versus actual behavior, and what was or was not executed.

Choose cases from the requested behavior: real URL, normal flow, service error, invalid input, missing identity and insufficient permissions where relevant.
Use the product's account fixtures and expected responses; public loopback demonstration identities prove only fixture behavior.
Verify both the visible outcome and the relevant HTTP/backend effect instead of counting a button click as success.

Persistent connections, polling, SSE, or WebSockets can prevent network idle indefinitely.
`networkidle` is optional diagnostic evidence, never a prerequisite for inspection or proof that the UI is ready.
Avoid fixed sleeps as readiness proof; fail with the missing expected condition at the bounded timeout.
For asynchronous commands, distinguish UI acceptance from confirmed backend/device execution.

## Evidence and cleanup

Capture screenshots or focused console excerpts only when authorized and useful, using the requested artifact location.
Avoid capturing credentials, session tokens, or unrelated sensitive screen/log content.
Use repository browser fixtures to close task-owned sessions; do not close the user's interactive browser.
Report the tested browser/configuration and limitations instead of inferring broad browser compatibility or production health.
Retain the actual Test exit code and report counts; zero tests, missing reports, all-skipped runs and required unavailable browsers cannot establish PASS.
Keep required unavailable browser checks BLOCKED and preserve their need for execution.
