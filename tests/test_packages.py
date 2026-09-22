"""Behavioral checks against real copied packages, including hostile inputs."""

from __future__ import annotations

import hashlib
import importlib.util
import json
import os
import shutil
import socket
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path
from unittest.mock import patch

ROOT = Path(__file__).resolve().parents[1]
SPEC = importlib.util.spec_from_file_location(
    "packaging_checks", ROOT / "scripts/check-packages.py"
)
checks = importlib.util.module_from_spec(SPEC)
SPEC.loader.exec_module(checks)


def hash_file(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()


class PackageTests(unittest.TestCase):
    def setUp(self):
        self.temporary = tempfile.TemporaryDirectory(prefix="skills-check-")
        self.addCleanup(self.temporary.cleanup)
        self.root = Path(self.temporary.name) / "package"
        self.root.mkdir()
        # Preserve actual bytes, including provenance, rather than synthesizing
        # the same records with the implementation under test.
        for directory in checks.PACKAGE_DIRS:
            if (ROOT / directory).is_dir():
                shutil.copytree(
                    ROOT / directory,
                    self.root / directory,
                    ignore=shutil.ignore_patterns(*checks.IGNORED_DIRS, "*.egg-info", "*.pyc"),
                )
        for relative in (*checks.EXTRA_FILES, "upstream.lock.json"):
            destination = self.root / relative
            destination.parent.mkdir(parents=True, exist_ok=True)
            shutil.copyfile(ROOT / relative, destination)
        self.lock = json.loads((self.root / "upstream.lock.json").read_text())

    def write(self, relative, data):
        path = self.root / relative
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_bytes(data.encode() if isinstance(data, str) else data)
        return path

    def rehash(self, relative):
        self.lock["artifacts"][relative] = hash_file(self.root / relative)

    def save_lock(self):
        self.write("upstream.lock.json", json.dumps(self.lock, indent=2) + "\n")

    def failure(self, message):
        with self.assertRaisesRegex(checks.PackageError, message):
            checks.verify(self.root, self.lock)

    def command(self, script, *args):
        result = subprocess.run(
            [
                sys.executable,
                "-B",
                str(self.root / "scripts" / script),
                "--root",
                str(self.root),
                *args,
            ],
            text=True,
            encoding="utf-8",
            capture_output=True,
            cwd=self.temporary.name,
        )
        self.assertNotIn("Traceback", result.stderr)
        return result, json.loads(result.stdout)

    def test_real_packages_verify_without_network_or_external_commands(self):
        with (
            patch.object(
                socket, "create_connection", side_effect=AssertionError("network forbidden")
            ),
            patch.object(
                subprocess, "run", side_effect=AssertionError("external command forbidden")
            ),
        ):
            result = checks.verify(self.root)
        self.assertEqual("PASS", result["status"])
        self.assertFalse(result["native_installation_validated"])
        self.assertEqual(19, result["active_skills"])

    def test_check_cli_never_refreshes_changed_bytes(self):
        before = (self.root / "upstream.lock.json").read_bytes()
        path = "docs/upstream-selection.md"
        self.write(path, (self.root / path).read_bytes() + b"\nChanged.\n")
        result, report = self.command("check-packages.py")
        self.assertEqual(1, result.returncode)
        self.assertEqual("FAIL", report["status"])
        self.assertIn("hash mismatch", report["errors"][0])
        self.assertEqual(before, (self.root / "upstream.lock.json").read_bytes())

    def test_added_unlocked_file_is_rejected(self):
        self.write("plugins/matt-engineering/unreviewed.txt", "extra")
        self.failure("unlocked artifacts")

    def test_missing_support_file_is_rejected(self):
        (self.root / "skills/domain-modeling/ADR-FORMAT.md").unlink()
        self.failure("missing artifacts")

    def test_removed_required_skill_cannot_be_hidden_by_rehashing(self):
        prefix = "skills/grilling/"
        path = (self.root / prefix).resolve()
        self.assertTrue(path.is_relative_to(self.root.resolve()))
        shutil.rmtree(path)
        self.lock["artifacts"] = {
            p: h for p, h in self.lock["artifacts"].items() if not p.startswith(prefix)
        }
        self.failure("required active skill missing")

    def test_missing_license_is_rejected(self):
        (self.root / "provenance/superpowers/LICENSE.txt").unlink()
        self.failure("missing file|missing artifacts")

    def test_rehashed_changed_license_is_rejected(self):
        relative = "provenance/mattpocock-skills/LICENSE.txt"
        self.write(relative, "MIT\n")
        self.rehash(relative)
        self.failure("adapted hash mismatch|license integrity")

    def test_wrong_license_identifier_is_rejected(self):
        self.lock["sources"][0]["license"]["spdx"] = "Apache-2.0"
        self.failure("incorrect license identifier")

    def test_missing_third_party_notice_is_rejected_after_rehash(self):
        self.write("THIRD_PARTY_NOTICES.md", "# Notices\n")
        self.rehash("THIRD_PARTY_NOTICES.md")
        self.failure("missing third-party notice")

    def test_duplicate_name_in_nested_skill_is_rejected(self):
        relative = "skills/duplicate/test-driven-development/SKILL.md"
        self.write(
            relative,
            "---\nname: test-driven-development\ndescription: Duplicate\n---\n# Duplicate\n",
        )
        self.rehash(relative)
        self.failure("duplicate active skill name")

    def test_duplicate_debugging_skill_is_rejected(self):
        relative = "skills/duplicate/systematic-debugging/SKILL.md"
        self.write(relative, (self.root / "skills/systematic-debugging/SKILL.md").read_bytes())
        self.rehash(relative)
        self.failure("duplicate active skill name")

    def test_standalone_skill_license_is_required(self):
        relative = "skills/code-review/LICENSE.txt"
        self.write(relative, "Altered license\n")
        self.rehash(relative)
        self.failure("standalone skill license mismatch")

    def test_legacy_plugin_supply_is_rejected(self):
        relative = "plugins/old/.codex-plugin/plugin.json"
        self.write(relative, "{}\n")
        self.rehash(relative)
        self.failure("legacy plugin supply remains")

    def test_missing_source_record_is_rejected(self):
        self.lock["sources"].pop()
        self.failure("source IDs")

    def test_invented_well_formed_commit_is_rejected(self):
        self.lock["sources"][0]["commit"] = "a" * 40
        self.failure("commit proof mismatch")

    def test_wrong_repository_is_rejected(self):
        self.lock["sources"][0]["repository"] = "https://github.com/other/skills"
        self.failure("unexpected repository")

    def test_unpinned_source_is_rejected(self):
        self.lock["sources"][0]["commit"] = "main"
        self.failure("40-hex pin")

    def test_missing_selected_path_record_is_rejected(self):
        self.lock["sources"][0]["selected_paths"].pop()
        self.failure("patch coverage mismatch")

    def test_upstream_blob_cannot_be_forged_by_updating_sha256(self):
        source = self.lock["sources"][0]
        record = next(
            p for p in source["patches"] if p["upstream_path"].endswith("grilling/SKILL.md")
        )
        relative = f"provenance/mattpocock-skills/files/{record['upstream_path']}.source"
        self.write(relative, (self.root / relative).read_bytes() + b"\nForged.\n")
        self.rehash(relative)
        record["upstream_sha256"] = hash_file(self.root / relative)
        self.failure("blob proof mismatch")

    def test_git_tree_proof_is_verified(self):
        relative = next(p for p in self.lock["artifacts"] if "/mattpocock-skills/trees/" in p)
        self.write(relative, b"forged tree")
        self.rehash(relative)
        self.failure("tree proof mismatch")

    def test_adaptation_patch_content_is_verified(self):
        record = next(p for p in self.lock["sources"][0]["patches"] if "patch" in p)
        relative = record["patch"]
        self.write(relative, b"forged delta\n")
        self.rehash(relative)
        record["patch_sha256"] = hash_file(self.root / relative)
        self.failure("patch content mismatch")

    def test_unsafe_artifact_paths_are_rejected(self):
        for relative in [
            "../outside",
            "/absolute",
            "C:/outside",
            "skills\\escape",
            "skills/./bad",
            "skills/a/../bad",
            "skills/NUL",
            "skills/trailing.",
            "skills/file:stream",
        ]:
            with self.subTest(path=relative):
                self.lock["artifacts"][relative] = "0" * 64
                self.failure("unsafe path")
                del self.lock["artifacts"][relative]

    def test_source_target_cannot_escape(self):
        self.lock["sources"][0]["patches"][0]["target"] = "../outside"
        self.failure("invalid target mapping")

    def test_broken_relative_reference_is_rejected_after_rehash(self):
        relative = "docs/upstream-selection.md"
        for text in [
            "[Required](missing.md)",
            "[Required][r]\n\n[r]: missing.md",
            "![Diagram](missing.png)",
        ]:
            with self.subTest(text=text):
                self.write(relative, "# Notice\n\n" + text + "\n")
                self.rehash(relative)
                self.failure("missing file or directory")

    def test_undefined_reference_is_rejected(self):
        relative = "docs/upstream-selection.md"
        self.write(relative, "# Notice\n\n[Required][unknown]\n")
        self.rehash(relative)
        self.failure("undefined Markdown reference")

    def test_relative_reference_cannot_escape_root(self):
        relative = "docs/upstream-selection.md"
        self.write(relative, "# Notice\n\n[Required](%2e%2e/%2e%2e/%2e%2e/escape.md)\n")
        self.rehash(relative)
        self.failure("reference escapes root")

    def test_fenced_examples_and_external_links_are_not_dependencies(self):
        relative = "docs/upstream-selection.md"
        self.write(
            relative,
            "# Notice\n\n```markdown\n[Example](missing.md)\n```\n\n[Upstream](https://github.com/mattpocock/skills)\n",
        )
        self.rehash(relative)
        self.assertEqual("PASS", checks.verify(self.root, self.lock)["status"])

    def test_symlink_or_windows_junction_escape_is_rejected(self):
        outside = Path(self.temporary.name) / "outside"
        outside.mkdir()
        (outside / "secret.txt").write_text("must not be read")
        link = self.root / "skills/escape"
        try:
            link.symlink_to(outside, target_is_directory=True)
        except OSError:
            if os.name != "nt":
                raise
            result = subprocess.run(
                ["cmd.exe", "/d", "/c", "mklink", "/J", str(link), str(outside)],
                capture_output=True,
            )
            self.assertEqual(0, result.returncode, result.stderr)
        try:
            self.failure("symlink/reparse path rejected")
            self.assertEqual("must not be read", (outside / "secret.txt").read_text())
        finally:
            if link.is_symlink():
                link.unlink()
            else:
                os.rmdir(link)  # Remove only this junction, never its target.

    def test_duplicate_json_keys_fail_cli(self):
        self.write(
            "upstream.lock.json",
            '{"schema_version":1,"schema_version":1,"sources":[],"artifacts":{}}',
        )
        result, report = self.command("check-packages.py")
        self.assertEqual(1, result.returncode)
        self.assertIn("duplicate JSON key", report["errors"][0])

    def test_unknown_lock_keys_are_rejected(self):
        self.lock["auto_refresh"] = True
        self.failure("unknown fields")

    def test_missing_dependency_reports_blocked(self):
        result = subprocess.run(
            [
                sys.executable,
                "-I",
                "-S",
                "-B",
                str(self.root / "scripts/check-packages.py"),
                "--root",
                str(self.root),
            ],
            text=True,
            capture_output=True,
        )
        self.assertEqual(2, result.returncode)
        self.assertEqual("BLOCKED", json.loads(result.stdout)["status"])

    def test_refresh_dry_run_preserves_lock_and_source_records(self):
        before = (self.root / "upstream.lock.json").read_bytes()
        self.write("docs/new-reference.md", "# Maintainer reference\n")
        result, report = self.command("refresh-package-lock.py")
        self.assertEqual(0, result.returncode, report)
        self.assertFalse(report["written"])
        self.assertIn("docs/new-reference.md", report["added"])
        self.assertEqual(before, (self.root / "upstream.lock.json").read_bytes())

    def test_refresh_refuses_to_bless_changed_upstream_adaptation(self):
        relative = "skills/grilling/SKILL.md"
        self.write(relative, (self.root / relative).read_bytes() + b"\nChanged.\n")
        before = (self.root / "upstream.lock.json").read_bytes()
        result, report = self.command("refresh-package-lock.py", "--write")
        self.assertEqual(1, result.returncode)
        self.assertIn("adapted hash mismatch", report["errors"][0])
        self.assertEqual(before, (self.root / "upstream.lock.json").read_bytes())
        self.assertEqual([], list(self.root.glob(".package-lock-*.tmp")))


if __name__ == "__main__":
    unittest.main()
