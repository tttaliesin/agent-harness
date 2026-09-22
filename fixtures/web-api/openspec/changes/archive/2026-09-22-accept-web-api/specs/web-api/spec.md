# web-api specification

## Purpose

Provide a reproducible real execution example that verifies the original shared-skill capabilities without modifying a production product.

## ADDED Requirements

### Requirement: HTTP and browser behavior

The fixture SHALL expose actual loopback HTTP behavior and a browser UI that reflects normal, invalid, unauthorized, forbidden and unavailable responses.

#### Scenario: Normal input

- **WHEN** a user submits Ada
- **THEN** the HTTP response is 200 and the UI shows Hello, Ada!

#### Scenario: Invalid input

- **WHEN** an empty name is submitted
- **THEN** the HTTP response is 422 and the UI displays the input error

#### Scenario: Authorization

- **WHEN** guest, viewer and admin identities request the admin endpoint
- **THEN** the actual statuses are respectively 401, 403 and 200 and match the UI

#### Scenario: Service recovery

- **WHEN** the fixture returns 503 followed by a valid greeting request
- **THEN** the UI displays the error then recovers to the successful response

#### Scenario: Safe rendering

- **WHEN** a name contains HTML markup
- **THEN** the UI renders literal text and creates no injected image

### Requirement: Test evidence

The fixture SHALL run saved Python and Playwright tests and validate the corresponding current JUnit reports against the actual command result.

#### Scenario: Real checks

- **WHEN** the Python and browser commands run
- **THEN** the reports contain actual testcases, no failures or errors, and executed cases

#### Scenario: Invalid report

- **WHEN** a required report is missing, stale, malformed, empty or contradicts a failing command
- **THEN** the report checker returns failure

### Requirement: Owned resources

The fixture SHALL own and terminate its loopback server and browser without reusing or stopping a preexisting server.

#### Scenario: Completion

- **WHEN** the tests finish or fail
- **THEN** owned processes are closed and unrelated listeners are preserved
