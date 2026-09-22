"""Real pinned OpenSpec CLI integration; separate from product behavior acceptance."""

import hashlib
import json
import os
import subprocess
from pathlib import Path

import pytest

CLI = Path(__file__).parent / "node_modules/@fission-ai/openspec/bin/openspec.js"
WORKFLOWS = ["explore", "propose", "apply", "update", "verify", "sync", "archive"]
NAMES = {
    "openspec-explore",
    "openspec-propose",
    "openspec-apply-change",
    "openspec-update-change",
    "openspec-verify-change",
    "openspec-sync-specs",
    "openspec-archive-change",
}


@pytest.fixture
def project(tmp_path):
    if not CLI.is_file():
        pytest.fail(
            "Install pinned fixture tools: pnpm --dir fixtures/openspec install --frozen-lockfile"
        )
    root = tmp_path / "product"
    root.mkdir()
    (root / "CLAUDE.md").write_text("Existing product instructions.\n", encoding="utf-8")
    (root / "AGENTS.md").write_text("Use existing product tests.\n", encoding="utf-8")
    env = dict(
        os.environ,
        XDG_CONFIG_HOME=str(tmp_path / "config"),
        XDG_DATA_HOME=str(tmp_path / "data"),
        OPENSPEC_TELEMETRY="0",
        DO_NOT_TRACK="1",
    )

    def run(*args, expected=0, environment=None):
        result = subprocess.run(
            ["node", str(CLI.resolve()), *args],
            cwd=root,
            env=environment or env,
            capture_output=True,
            text=True,
            encoding="utf-8",
            errors="replace",
            timeout=60,
            check=False,
        )
        assert result.returncode == expected, result.stderr + result.stdout
        return result.stdout

    assert run("--version").strip() == "1.13.1"
    run("config", "set", "profile", "custom")
    run("config", "set", "workflows", json.dumps(WORKFLOWS))
    run("init", ".", "--tools", "codex", "--profile", "custom", "--no-animation")
    return root, run


def skill_hashes(root):
    files = list((root / ".agents/skills").glob("*/SKILL.md"))
    assert {p.parent.name for p in files} == NAMES
    assert all('generatedBy: "1.13.1"' in p.read_text(encoding="utf-8") for p in files)
    return {p.parent.name: hashlib.sha256(p.read_bytes()).hexdigest() for p in files}


def test_seven_workflows_repeat_install_and_existing_instructions(project):
    root, run = project
    before = skill_hashes(root)
    run("init", ".", "--tools", "codex", "--profile", "custom", "--no-animation")
    run("update", ".")
    assert before == skill_hashes(root)
    assert (root / "CLAUDE.md").read_text() == "Existing product instructions.\n"
    assert (root / "AGENTS.md").read_text() == "Use existing product tests.\n"
    assert json.loads(run("doctor", "--json"))["root"]["healthy"] is True
    assert Path(json.loads(run("list", "--json"))["root"]["path"]).resolve() == root.resolve()


def test_artifact_lifecycle_and_canonical_spec(project):
    root, run = project
    run("new", "change", "verify-cli-lifecycle")
    change = root / "openspec/changes/verify-cli-lifecycle"
    (change / "proposal.md").write_text(
        "# CLI lifecycle\n\n## Why\nExercise artifact transitions.\n\n## What Changes\n"
        "Add a fixture contract.\n\n## Capabilities\n\n### New Capabilities\n"
        "- `cli-fixture`: Keep a validated artifact through archival.\n"
        "\n### Modified Capabilities\nNone.\n\n## Impact\nFixture only.\n",
        encoding="utf-8",
    )
    run("instructions", "specs", "--change", "verify-cli-lifecycle", "--json")
    (change / "specs/cli-fixture").mkdir(parents=True)
    delta = change / "specs/cli-fixture/spec.md"
    delta.write_text(
        "# Fixture specification\n\n## Purpose\n"
        "Exercise real OpenSpec artifact validation and canonical specification "
        "archival in isolation.\n"
        "\n## ADDED Requirements\n\n### Requirement: Retain fixture contract\n"
        "The fixture SHALL preserve the approved specification after archival.\n"
        "\n#### Scenario: Archive validated artifacts\n"
        "- **WHEN** the fixture artifacts are validated and archived\n"
        "- **THEN** the canonical specification retains this requirement\n",
        encoding="utf-8",
    )
    (change / "design.md").write_text(
        "# Design\n\nUse the pinned CLI in an isolated product and assert preserved text.\n",
        encoding="utf-8",
    )
    (change / "tasks.md").write_text("## 1. Exercise CLI\n\n- [ ] 1.1 Validate artifacts\n")
    instructions = json.loads(
        run("instructions", "apply", "--change", "verify-cli-lifecycle", "--json")
    )
    assert instructions["contextFiles"]["specs"]
    # A complete planning graph is not evidence of implemented product behavior.
    status = json.loads(run("status", "--change", "verify-cli-lifecycle", "--json"))
    assert status["isPlanningComplete"] is True
    assert "[ ]" in (change / "tasks.md").read_text()
    run("validate", "verify-cli-lifecycle", "--strict", "--json")
    (change / "tasks.md").write_text("## 1. Exercise CLI\n\n- [x] 1.1 Validate artifacts\n")
    run("archive", "verify-cli-lifecycle", "--json", "--yes")
    canonical = root / "openspec/specs/cli-fixture/spec.md"
    assert "Retain fixture contract" in canonical.read_text(encoding="utf-8")
    assert "## ADDED Requirements" not in canonical.read_text(encoding="utf-8")
    assert not change.exists()
    assert len(list((root / "openspec/changes/archive").glob("*-verify-cli-lifecycle"))) == 1
    assert json.loads(run("doctor", "--json"))["root"]["healthy"] is True


def test_invalid_spec_cannot_validate(project):
    root, run = project
    run("new", "change", "invalid-fixture")
    folder = root / "openspec/changes/invalid-fixture/specs/invalid"
    folder.mkdir(parents=True)
    (folder / "spec.md").write_text(
        "## ADDED Requirements\n\n### Requirement: No scenario\n"
        "The fixture SHALL refuse this incomplete requirement.\n"
    )
    run("validate", "invalid-fixture", "--strict", "--json", expected=1)


@pytest.mark.parametrize("profile", [None, "core"])
def test_later_isolated_update_preserves_original_user_config(project, tmp_path, profile):
    root, run = project
    before_skills = skill_hashes(root)
    user_config = tmp_path / "existing-user-config"
    user_config.mkdir()
    prior_env = dict(
        os.environ,
        XDG_CONFIG_HOME=str(user_config),
        XDG_DATA_HOME=str(user_config),
        OPENSPEC_TELEMETRY="0",
    )
    if profile:
        run("config", "set", "profile", profile, environment=prior_env)
    before_config = {
        p.relative_to(user_config): p.read_bytes() for p in user_config.rglob("*") if p.is_file()
    }
    # A later setup session starts from the restored user environment, then
    # overrides both homes afresh; it must not rely on the first session.
    later_env = dict(
        prior_env,
        XDG_CONFIG_HOME=str(tmp_path / "later-config"),
        XDG_DATA_HOME=str(tmp_path / "later-data"),
    )
    run("config", "set", "profile", "custom", environment=later_env)
    run("config", "set", "workflows", json.dumps(WORKFLOWS), environment=later_env)
    run("update", ".", environment=later_env)
    assert skill_hashes(root) == before_skills
    assert {
        p.relative_to(user_config): p.read_bytes() for p in user_config.rglob("*") if p.is_file()
    } == before_config
