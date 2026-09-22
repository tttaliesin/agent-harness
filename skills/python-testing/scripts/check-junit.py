"""Validate a JUnit report from an explicitly identified test run."""

import argparse
import json
import math
import xml.etree.ElementTree as ET
from pathlib import Path

MAX_BYTES = 8 * 1024 * 1024
COUNTERS = ("tests", "failures", "errors", "skipped")


class InvalidReport(ValueError):
    """The supplied report cannot establish a successful test run."""


class BoundedTree(ET.TreeBuilder):
    """Reject DTDs before entity processing, including UTF-16 documents."""

    def __init__(self):
        super().__init__()
        self.depth = 0
        self.elements = 0

    def doctype(self, name, pubid, system):
        raise InvalidReport("DTD and entity declarations are not accepted")

    def start(self, tag, attrs):
        self.depth += 1
        self.elements += 1
        if self.depth > 64 or self.elements > 100_000:
            raise InvalidReport("XML depth or element limit exceeded")
        return super().start(tag, attrs)

    def end(self, tag):
        self.depth -= 1
        return super().end(tag)


def count_cases(root):
    if root.tag not in {"testsuite", "testsuites"}:
        raise InvalidReport("JUnit root must be testsuite or testsuites")
    nodes = list(root.iter())
    for parent in nodes:
        for child in parent:
            allowed = {
                "testsuite": {"testsuite", "testsuites"},
                "testsuites": {"testsuites"},
                "testcase": {"testsuite"},
                "failure": {"testcase"},
                "error": {"testcase"},
                "skipped": {"testcase"},
            }
            if child.tag in allowed and parent.tag not in allowed[child.tag]:
                raise InvalidReport(f"Invalid JUnit placement of {child.tag}")

    totals = {}
    for node in reversed(nodes):
        counts = dict.fromkeys(COUNTERS, 0)
        if node.tag == "testcase":
            outcomes = [child.tag for child in node if child.tag in {"failure", "error", "skipped"}]
            if len(set(outcomes)) > 1:
                raise InvalidReport("Conflicting testcase outcome elements")
            counts.update(
                tests=1,
                failures=int("failure" in outcomes),
                errors=int("error" in outcomes),
                skipped=int("skipped" in outcomes),
            )
        elif node.tag in {"testsuite", "testsuites"}:
            for child in node:
                for name in COUNTERS:
                    counts[name] += totals[child][name]
            for name in COUNTERS:
                declared = node.get(name)
                if declared is not None:
                    if not declared.isascii() or not declared.isdecimal():
                        raise InvalidReport(f"Invalid {name} count")
                    if len(declared) > 10 or int(declared) != counts[name]:
                        raise InvalidReport(
                            f"Declared {name} count disagrees with testcase evidence"
                        )
        totals[node] = counts
    return totals[root]


def check_report(path, started_at, exit_code):
    if not math.isfinite(started_at) or started_at <= 0:
        raise InvalidReport("Run start must be a finite positive Unix timestamp")
    if exit_code != 0:
        raise InvalidReport(f"Test command exit code was {exit_code}")
    with path.open("rb") as stream:
        if path.stat().st_mtime < started_at:
            raise InvalidReport("Stale report: modified before this run started")
        data = stream.read(MAX_BYTES + 1)
    if len(data) > MAX_BYTES:
        raise InvalidReport("XML report exceeds 8 MiB limit")
    root = ET.fromstring(data, parser=ET.XMLParser(target=BoundedTree()))
    counts = count_cases(root)
    if counts["tests"] == 0:
        raise InvalidReport("Report contains zero testcases")
    if counts["failures"] or counts["errors"]:
        raise InvalidReport("Report contains test failures or errors")
    counts["executed"] = counts["tests"] - counts["skipped"]
    if counts["executed"] == 0:
        raise InvalidReport("All testcases were skipped")
    return counts


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--report", required=True, type=Path)
    parser.add_argument("--exit-code", required=True, type=int)
    parser.add_argument(
        "--started-at",
        required=True,
        type=float,
        help="Unix timestamp captured immediately before the test command",
    )
    args = parser.parse_args()
    try:
        counts = check_report(args.report, args.started_at, args.exit_code)
    except (InvalidReport, OSError, ET.ParseError, LookupError) as error:
        reason = (
            f"Invalid XML: {error}"
            if isinstance(error, (ET.ParseError, LookupError))
            else str(error)
        )
        print(json.dumps({"status": "FAIL", "reason": reason}))
        return 1
    print(
        json.dumps(
            {
                "status": "PASS",
                **counts,
                "report": str(args.report),
                "started_at": args.started_at,
                "exit_code": args.exit_code,
            }
        )
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
