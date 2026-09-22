"""Parse test cases, never trust a report's top-level PASS or summary count."""

import json
import xml.etree.ElementTree as ET

from .common import HarnessError, bytes_at, digest, unique_pairs


def junit(content):
    if b"<!DOCTYPE" in content.upper() or b"<!ENTITY" in content.upper():
        raise HarnessError("unsafe_xml")
    root = ET.fromstring(content)
    if root.tag not in {"testsuite", "testsuites"}:
        raise HarnessError("invalid_junit_root")
    cases = list(root.iter("testcase"))
    seen = set()
    totals = {"tests": len(cases), "passed": 0, "failed": 0, "skipped": 0}
    for case in cases:
        identity = (case.get("classname"), case.get("name"), case.get("file"))
        if not identity[1] or identity in seen:
            raise HarnessError("missing_or_duplicate_testcase")
        seen.add(identity)
        failure = case.find("failure") is not None or case.find("error") is not None
        skipped = case.find("skipped") is not None
        totals["failed" if failure else "skipped" if skipped else "passed"] += 1
    for suite in root.iter():
        if suite.tag not in {"testsuite", "testsuites"}:
            continue
        descendants = list(suite.iter("testcase"))
        observed = {
            "tests": len(descendants),
            "failures": sum(c.find("failure") is not None for c in descendants),
            "errors": sum(c.find("error") is not None for c in descendants),
            "skipped": sum(c.find("skipped") is not None for c in descendants),
        }
        for name, count in observed.items():
            if name in suite.attrib and int(suite.attrib[name]) != count:
                raise HarnessError("junit_count_mismatch", field=name)
    return totals


def playwright(content):
    data = json.loads(content, object_pairs_hook=unique_pairs)
    if not isinstance(data, dict) or not isinstance(data.get("suites"), list):
        raise HarnessError("invalid_playwright_report")
    if data.get("errors"):
        raise HarnessError("playwright_global_errors")
    totals = {"tests": 0, "passed": 0, "failed": 0, "skipped": 0}
    seen = set()

    def visit(suites):
        for suite in suites:
            for spec in suite.get("specs", []):
                for index, test in enumerate(spec["tests"]):
                    identity = (
                        spec.get("id", spec.get("title")),
                        test.get("projectId", test.get("projectName")),
                        index,
                    )
                    if not identity[0] or identity in seen:
                        raise HarnessError("missing_or_duplicate_playwright_test")
                    seen.add(identity)
                    attempts = test["results"]
                    if not attempts:
                        if test.get("status") != "skipped":
                            raise HarnessError("playwright_test_not_run")
                        state = "skipped"
                    else:
                        states = [attempt["status"] for attempt in attempts]
                        if any(
                            s not in {"passed", "failed", "timedOut", "skipped", "interrupted"}
                            for s in states
                        ):
                            raise HarnessError("unknown_playwright_status")
                        if any(s in {"failed", "timedOut", "interrupted"} for s in states):
                            state = "failed"
                        elif all(s == "passed" for s in states):
                            state = "passed"
                        else:
                            state = "skipped"
                    if test.get("status") in {"unexpected", "flaky"} or any(
                        a.get("errors") or a.get("error") for a in attempts
                    ):
                        state = "failed"
                    totals["tests"] += 1
                    totals[state] += 1
            visit(suite.get("suites", []))

    visit(data["suites"])
    return totals


def parse(root, path, format_name, minimum=1, allow_skipped=False):
    content = bytes_at(root, path)
    try:
        totals = {"junit": junit, "playwright-json": playwright}[format_name](content)
    except (ET.ParseError, ValueError, TypeError, KeyError, AttributeError, RecursionError) as exc:
        raise HarnessError("invalid_test_report", path=path, detail=str(exc)) from exc
    report = {"format": format_name, "path": path, "sha256": digest(content), **totals}
    reason = None
    if totals["passed"] + totals["failed"] < minimum:
        reason = "insufficient_executed_tests"
    elif totals["failed"]:
        reason = "test_failures"
    elif totals["skipped"] and not allow_skipped:
        reason = "skipped_tests_forbidden"
    return report, reason
