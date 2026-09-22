"""Strict product/change loading and conservative baseline policy composition."""

from pathlib import Path

import yaml

from .common import HarnessError, bytes_at, digest, identifier, relative, safe_path
from .schema import validate


class StrictLoader(yaml.SafeLoader):
    def compose_node(self, parent, index):
        if self.check_event(yaml.AliasEvent):
            raise HarnessError("yaml_aliases_forbidden")
        return super().compose_node(parent, index)


def mapping(loader, node):
    result = {}
    for key, value in node.value:
        key = loader.construct_object(key, deep=True)
        if not isinstance(key, str) or key in result:
            raise HarnessError("duplicate_or_nonstring_yaml_key", key=str(key))
        result[key] = loader.construct_object(value, deep=True)
    return result


StrictLoader.add_constructor(yaml.resolver.BaseResolver.DEFAULT_MAPPING_TAG, mapping)


def yaml_data(text, name):
    try:
        return validate(name, yaml.load(text, Loader=StrictLoader))
    except (yaml.YAMLError, RecursionError, UnicodeError) as exc:
        raise HarnessError("invalid_yaml", detail=str(exc)) from exc


def project(root):
    config = yaml_data(bytes_at(root, "harness/project.yaml"), "project")
    for path in config["documents"].values():
        safe_path(root, path, must_exist=True)
    for key, path in config["outputs"].items():
        safe_path(root, path)
        if not path.startswith(".harness/") or path.rstrip("/") == ".harness":
            raise HarnessError("outputs_must_be_under_harness", field=key)
    if config["outputs"]["state"].rstrip("/") == config["outputs"]["evidence"].rstrip("/"):
        raise HarnessError("overlapping_outputs")
    checks = config["verification"]["checks"]
    for check in checks.values():
        if check["kind"] != "tests" and any(
            k in check for k in ("report", "report_format", "minimum_tests")
        ):
            raise HarnessError("test_fields_on_nontest_check")
        if check["kind"] == "tests":
            relative(check["report"], template=True)
            if not check["report"].startswith(".harness/runs/{run_id}/reports/"):
                raise HarnessError("report_must_be_run_scoped")
    reports = [c["report"] for c in checks.values() if "report" in c]
    if len(reports) != len(set(reports)):
        raise HarnessError("duplicate_report_path")
    unknown = set(config["verification"]["baseline_checks"]) - checks.keys()
    if unknown:
        raise HarnessError("unknown_check", checks=sorted(unknown))
    return config


def change(root, change_id, specs_root="openspec"):
    identifier(change_id)
    path = f"{specs_root}/changes/{change_id}/harness.yaml"
    data = yaml_data(bytes_at(root, path), "change")
    if data["change_id"] != change_id:
        raise HarnessError("change_id_mismatch", path=path)
    for ref in data["spec_refs"]:
        safe_path(root, ref, must_exist=True)
        if not ref.startswith(specs_root.rstrip("/") + "/"):
            raise HarnessError("spec_outside_spec_root", path=ref)
    for scope in data["write_scope"]:
        safe_path(root, scope)
    return data


def select(root, config, change_ids):
    if not change_ids or len(change_ids) != len(set(change_ids)):
        raise HarnessError("missing_or_duplicate_change_ids")
    changes = {cid: change(root, cid, config["documents"]["specs"]) for cid in sorted(change_ids)}
    required = set(config["verification"]["baseline_checks"])
    for data in changes.values():
        missing = set(data["dependency_change_ids"]) - changes.keys()
        if missing:
            raise HarnessError("missing_dependency_changes", change_ids=sorted(missing))
        if data["change_id"] in data["dependency_change_ids"]:
            raise HarnessError("self_dependency")
        required.update(data["required_check_ids"])
    unknown = required - config["verification"]["checks"].keys()
    if unknown:
        raise HarnessError("unknown_check", checks=sorted(unknown))
    return changes, sorted(required)


def policy(config, baseline):
    old = baseline["verification"]
    current = config["verification"]
    if not set(old["baseline_checks"]).issubset(current["baseline_checks"]):
        raise HarnessError("baseline_check_removed")
    # All existing definitions are protected, including checks required by older changes.
    for key, definition in old["checks"].items():
        new = current["checks"].get(key)
        if new is None:
            raise HarnessError("policy_check_removed", check=key)
        for field in definition.keys() | new.keys():
            before, after = definition.get(field), new.get(field)
            if field == "minimum_tests" and after is not None and after >= before:
                continue
            if field == "allow_skipped" and not after:
                continue
            if before != after:
                raise HarnessError(
                    "policy_check_changed_requires_trusted_policy_review", check=key, field=field
                )
    if config["workflow"]["maximum_repair_rounds"] > baseline["workflow"]["maximum_repair_rounds"]:
        raise HarnessError("repair_budget_weakened")
    if not set(baseline["project"]["packs"]).issubset(config["project"]["packs"]):
        raise HarnessError("required_pack_removed")
    return digest({"baseline": baseline, "effective": config})


def spec_hashes(root, changes):
    def descendants(path):
        if path.is_file():
            yield path
        elif path.is_dir():
            for item in sorted(path.iterdir()):
                checked = safe_path(root, item.relative_to(Path(root)).as_posix(), must_exist=True)
                yield from descendants(checked)

    hashes = {}
    for change_data in changes.values():
        for ref in change_data["spec_refs"]:
            path = safe_path(root, ref, must_exist=True)
            files = 0
            for item in descendants(path):
                rel = item.relative_to(Path(root)).as_posix()
                checked = safe_path(root, rel, must_exist=True)
                if checked.is_file():
                    content = bytes_at(root, rel)
                    if not content.strip():
                        raise HarnessError("empty_spec", path=rel)
                    hashes[rel] = digest(content)
                    files += 1
            if not files:
                raise HarnessError("empty_spec_reference", path=ref)
    return hashes


def covers(path, scopes):
    return any(
        path == scope.rstrip("/") or path.startswith(scope.rstrip("/") + "/") for scope in scopes
    )
