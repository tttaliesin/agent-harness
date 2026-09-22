"""Exercise the installed, dependency-free report checker through its CLI."""

import json
import os
import shutil
import subprocess
import sys
import time
from pathlib import Path

import pytest

ROOT = Path(__file__).resolve().parents[1]
SCRIPT = ROOT / "skills/python-testing/scripts/check-junit.py"
PASSING = '<testsuite tests="1" failures="0" errors="0"><testcase name="ok"/></testsuite>'


def invoke(tmp_path, xml=PASSING, *, exit_code=0, age=None, script=SCRIPT):
    started = time.time() - 1
    report = tmp_path / "report.xml"
    if xml is not None:
        report.write_bytes(xml.encode() if isinstance(xml, str) else xml)
        if age is not None:
            os.utime(report, (started - age, started - age))
    process = subprocess.run(
        [
            sys.executable,
            "-I",
            "-B",
            str(script),
            "--report",
            str(report),
            "--exit-code",
            str(exit_code),
            "--started-at",
            str(started),
        ],
        cwd=tmp_path,
        capture_output=True,
        text=True,
        timeout=10,
    )
    assert "Traceback" not in process.stderr
    return process, json.loads(process.stdout)


def test_selected_install_is_standalone(tmp_path):
    installed = tmp_path / "selected" / "python-testing"
    shutil.copytree(ROOT / "skills/python-testing", installed)
    process, result = invoke(tmp_path, script=installed / "scripts/check-junit.py")
    assert process.returncode == 0
    assert result["status"] == "PASS"
    assert result["tests"] == result["executed"] == 1


def test_nested_junit_counts_cases_once_and_allows_partial_skips(tmp_path):
    xml = """<testsuites tests="3" failures="0" errors="0" skipped="1">
      <testsuite tests="3"><testcase name="outer"/>
        <testsuite tests="2" skipped="1"><testcase name="inner"/>
          <testcase name="optional"><skipped/></testcase>
        </testsuite>
      </testsuite>
    </testsuites>"""
    process, result = invoke(tmp_path, xml)
    assert process.returncode == 0
    assert (result["tests"], result["executed"], result["skipped"]) == (3, 2, 1)


@pytest.mark.parametrize(
    ("xml", "reason"),
    [
        (None, "report"),
        ("PASS", "XML"),
        ("<testsuite>", "XML"),
        ("<passed/>", "root"),
        ('<testsuite tests="0"/>', "zero"),
        ('<testsuite tests="10"/>', "count"),
        ("<testsuite><testcase><skipped/></testcase></testsuite>", "skipped"),
        ("<testsuite><testcase><failure/></testcase></testsuite>", "failure"),
        ("<testsuite><testcase><error/></testcase></testsuite>", "error"),
        ('<testsuite failures="0"><testcase><failure/></testcase></testsuite>', "count"),
        ('<testsuite tests="-1"><testcase/></testsuite>', "count"),
        ('<testsuite tests="1.5"><testcase/></testsuite>', "count"),
        ("<testsuite><properties><testcase/></properties></testsuite>", "placement"),
        ("<testsuite><testcase><skipped/><failure/></testcase></testsuite>", "outcome"),
        ('<testsuite><error message="collection failed"/><testcase/></testsuite>', "placement"),
    ],
    ids=[
        "missing",
        "fake-pass",
        "malformed",
        "wrong-root",
        "zero",
        "count-only",
        "all-skipped",
        "failure",
        "error",
        "false-count",
        "negative",
        "fraction",
        "hidden-case",
        "conflicting-outcome",
        "suite-error",
    ],
)
def test_rejects_invalid_or_unsuccessful_report_even_after_exit_zero(tmp_path, xml, reason):
    process, result = invoke(tmp_path, xml)
    assert process.returncode == 1
    assert result["status"] == "FAIL"
    assert reason.lower() in result["reason"].lower()


def test_successful_report_cannot_hide_failed_command(tmp_path):
    process, result = invoke(tmp_path, exit_code=5)
    assert process.returncode == 1
    assert "exit" in result["reason"].lower()


def test_rejects_stale_report(tmp_path):
    process, result = invoke(tmp_path, age=30)
    assert process.returncode == 1
    assert "stale" in result["reason"].lower()


@pytest.mark.parametrize("encoding", ["utf-8", "utf-16"])
def test_rejects_entity_declarations_before_expansion(tmp_path, encoding):
    xml = """<?xml version="1.0"?><!DOCTYPE testsuite [
    <!ENTITY x "expanded"><!ENTITY y "&x;&x;&x;&x;">]>
    <testsuite><testcase name="&y;"/></testsuite>"""
    process, result = invoke(tmp_path, xml.encode(encoding))
    assert process.returncode == 1
    assert "DTD" in result["reason"]


@pytest.mark.parametrize(
    "xml",
    [
        '<!DOCTYPE testsuite SYSTEM "file:///nonexistent"><testsuite><testcase/></testsuite>',
        "<testsuite>" * 100 + "<testcase/>" + "</testsuite>" * 100,
        "<testsuite><testcase/><system-out>"
        + "x" * (8 * 1024 * 1024)
        + "</system-out></testsuite>",
    ],
    ids=["external-dtd", "deep", "oversized"],
)
def test_rejects_unbounded_xml_inputs(tmp_path, xml):
    process, result = invoke(tmp_path, xml)
    assert process.returncode == 1
    assert result["status"] == "FAIL"


def test_requires_explicit_run_start(tmp_path):
    process = subprocess.run(
        [
            sys.executable,
            "-I",
            "-B",
            str(SCRIPT),
            "--report",
            str(tmp_path / "r.xml"),
            "--exit-code",
            "0",
        ],
        capture_output=True,
        text=True,
        timeout=10,
    )
    assert process.returncode == 2
    assert "--started-at" in process.stderr


@pytest.mark.parametrize("started_at", ["nan", "inf", "0"])
def test_invalid_run_start_cannot_disable_freshness(tmp_path, started_at):
    report = tmp_path / "report.xml"
    report.write_text(PASSING)
    process = subprocess.run(
        [
            sys.executable,
            "-I",
            "-B",
            str(SCRIPT),
            "--report",
            str(report),
            "--exit-code",
            "0",
            "--started-at",
            started_at,
        ],
        capture_output=True,
        text=True,
        timeout=10,
    )
    assert process.returncode == 1
    assert json.loads(process.stdout)["status"] == "FAIL"


def test_unknown_xml_encoding_is_a_report_failure(tmp_path):
    process, result = invoke(tmp_path, '<?xml version="1.0" encoding="not-a-codec"?>' + PASSING)
    assert process.returncode == 1
    assert result["status"] == "FAIL"
    assert "XML" in result["reason"]
