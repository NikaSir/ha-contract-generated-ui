#!/usr/bin/env python3
"""Read-only factual inventory and strict NikaS repository compliance checks.

Profile commands and application modules are never executed. A source marker is
not behavioral evidence. Unknown observations remain not_verified, never pass.
"""
from __future__ import annotations

import argparse
from datetime import datetime, timezone
import hashlib
import io
import json
import multiprocessing
from pathlib import Path, PurePosixPath
import re
import shlex
import subprocess
import sys
import tokenize
from typing import Any
from urllib.parse import urlsplit

import jsonschema
import yaml

TOOL_ROOT = Path(__file__).resolve().parents[1]
SCHEMA_PATH = TOOL_ROOT / "schemas/nikas_repository_contract.schema.json"
UI_VERSION = "2.2"
NAV_VERSION = "1.2"
UI_HASH = "3b6cc750b08aa0d2a375d1430ea04ac68c90525a527d197b014abd96728d23d1"
NAV_HASH = "d495eca80345b96976c168029a96146803f3d8195b6f6fc723827b601ffb578e"
TOOL_VERSION = "1.0.0"
MAX_BYTES = 16 * 1024 * 1024
MAX_GRAPH_FILES = 512
REQUIREMENTS = {
    "data_quality": {"missing_unknown_unavailable", "valid_zero_false", "stale_partial"},
    "command_safety": {"unavailable_no_write", "unknown_no_confirmation", "duplicate_submission"},
    "lifecycle": {"disconnect_reconnect", "late_response", "state_updates"},
    "repository_checks": {"existing_gates", "production_inputs"},
    "device_acceptance": {"ha_cold_load", "iphone_portrait"},
}


class InvalidInput(ValueError):
    """A malformed profile, untrusted path, or unreadable required input."""


def local_path(root: Path, relative: str) -> Path:
    if (not isinstance(relative, str) or not relative or "\\" in relative
            or any(c in relative for c in "\x00\r\n")
            or PurePosixPath(relative).is_absolute()
            or ".." in PurePosixPath(relative).parts):
        raise InvalidInput(f"Unsafe repository path: {relative!r}")
    resolved = (root / relative).resolve()
    if not resolved.is_relative_to(root.resolve()):
        raise InvalidInput(f"Path escapes repository: {relative!r}")
    return resolved


def read_text(root: Path, relative: str) -> str:
    path = local_path(root, relative)
    if path.stat().st_size > MAX_BYTES:
        raise InvalidInput(f"Input too large: {relative}")
    return path.read_text(encoding="utf-8")


def digest(path: Path) -> str:
    if path.stat().st_size > MAX_BYTES:
        raise InvalidInput(f"Input too large: {path.name}")
    return hashlib.sha256(path.read_bytes()).hexdigest()


def load_profile(path: Path) -> dict[str, Any]:
    try:
        profile = json.loads(path.read_text(encoding="utf-8"))
        schema = json.loads(SCHEMA_PATH.read_text(encoding="utf-8"))
        jsonschema.Draft202012Validator(schema).validate(profile)
        for field in ("artifacts", "findings"):
            ids = [item["id"] for item in profile[field]]
            if len(ids) != len(set(ids)):
                raise InvalidInput(f"Duplicate {field} IDs")
        evidence_ids = [item["requirement"] for item in profile["evidence"]]
        if len(evidence_ids) != len(set(evidence_ids)):
            raise InvalidInput("Duplicate requirement evidence")
        for artifact in profile["artifacts"]:
            for binding in artifact["bindings"]:
                compiled = re.compile(binding["pattern"])
                if compiled.groups != 1 or compiled.groupindex != {"value": 1}:
                    raise InvalidInput("Binding pattern must contain exactly one named group: value")
        return profile
    except (OSError, json.JSONDecodeError, jsonschema.ValidationError, re.error) as exc:
        raise InvalidInput(f"{path}: {exc}") from exc


def _regex_worker(connection: Any, pattern: str, source: str) -> None:
    try:
        values = []
        for match in re.finditer(pattern, source, re.MULTILINE):
            values.append(match.group("value"))
            if len(values) > 8:
                break
        connection.send(values)
    except Exception as exc:  # Child failure is an unverified binding, never PASS.
        connection.send({"error": type(exc).__name__})
    finally:
        connection.close()


def bounded_matches(pattern: str, source: str) -> list[str] | None:
    """Untrusted regexes have bounded input, output, and wall-clock execution."""
    method = "fork" if "fork" in multiprocessing.get_all_start_methods() else "spawn"
    context = multiprocessing.get_context(method)
    parent, child = context.Pipe(duplex=False)
    process = context.Process(target=_regex_worker, args=(child, pattern, source))
    process.start()
    child.close()
    try:
        if not parent.poll(0.5 if method == "fork" else 3):
            return None
        result = parent.recv()
        return result if isinstance(result, list) else None
    except EOFError:
        return None
    finally:
        if process.is_alive():
            process.terminate()
        process.join(timeout=1)
        parent.close()


def js_tokens(source: str) -> tuple[list[tuple[str, str]], list[str]]:
    """Small conservative lexer; unresolved template imports stay explicit.

    This is deliberately not a JavaScript evaluator. Regex literals and comments
    are skipped so documentation examples do not masquerade as executed imports.
    """
    tokens: list[tuple[str, str]] = []
    unresolved: list[str] = []
    index = 0
    while index < len(source):
        char = source[index]
        if char.isspace():
            index += 1
            continue
        if source.startswith("//", index):
            end = source.find("\n", index)
            index = len(source) if end < 0 else end
            continue
        if source.startswith("/*", index):
            end = source.find("*/", index + 2)
            if end < 0:
                unresolved.append("unterminated comment")
                break
            index = end + 2
            continue
        if char in "\"'`":
            quote, start = char, index
            index += 1
            escaped = False
            while index < len(source):
                if source[index] == "\\":
                    escaped = True
                    index += 2
                elif source[index] == quote:
                    break
                else:
                    index += 1
            value = source[start + 1:index]
            if index >= len(source):
                unresolved.append("unterminated string/template")
            if quote == "`" and "${" in value and re.search(r"\bimport\s*\(", value):
                unresolved.append("import inside template interpolation")
            kind = "template" if quote == "`" else "string"
            if escaped:
                kind = "escaped_string"
            tokens.append((kind, value))
            index += 1
            continue
        # Regex literals can contain text such as import('example').
        previous = tokens[-1][1] if tokens else "="
        if char == "/" and previous in {"=", "(", ":", ",", "[", "!", "return", "=>", "|", "&", "?", ";", "{"}:
            index += 1
            in_class = False
            while index < len(source):
                if source[index] == "\\":
                    index += 2
                    continue
                if source[index] == "[":
                    in_class = True
                elif source[index] == "]":
                    in_class = False
                elif source[index] == "/" and not in_class:
                    index += 1
                    break
                index += 1
            while index < len(source) and source[index].isalpha():
                index += 1
            tokens.append(("regex", ""))
            continue
        if char.isalpha() or char in "_$":
            end = index + 1
            while end < len(source) and (source[end].isalnum() or source[end] in "_$"):
                end += 1
            tokens.append(("name", source[index:end]))
            index = end
            continue
        if source.startswith("=>", index):
            tokens.append(("punctuation", "=>"))
            index += 2
        else:
            tokens.append(("punctuation", char))
            index += 1
    return tokens, unresolved


def imports_from(source: str) -> tuple[list[dict[str, Any]], list[str]]:
    tokens, unresolved = js_tokens(source)
    imports = []
    for index, (kind, token) in enumerate(tokens):
        if kind != "name" or token not in {"import", "export"}:
            continue
        if index and tokens[index - 1][1] in {".", "?."}:
            continue
        following = tokens[index + 1:]
        if not following or following[0][1] == ".":
            continue
        dynamic = token == "import" and following[0][1] == "("
        if dynamic:
            value = following[1] if len(following) > 1 else ("", "")
            closing = following[2][1] if len(following) > 2 else ""
            if value[0] in {"string", "template"} and "${" not in value[1] and closing == ")":
                imports.append({"specifier": value[1], "dynamic": True})
            else:
                unresolved.append("computed dynamic import")
            continue
        if token == "import" and following[0][0] == "string":
            imports.append({"specifier": following[0][1], "dynamic": False})
            continue
        if token == "import" and following[0][0] == "escaped_string":
            unresolved.append("escaped static import specifier")
            continue
        for offset, (next_kind, next_value) in enumerate(following[:128]):
            if next_value == ";":
                break
            if next_kind == "name" and next_value == "from":
                value = following[offset + 1] if len(following) > offset + 1 else ("", "")
                if value[0] == "string":
                    imports.append({"specifier": value[1], "dynamic": False})
                else:
                    unresolved.append("unresolved import/export source")
                break
    return imports, unresolved


def import_graph(root: Path, entry: str) -> dict[str, Any]:
    queue = [entry]
    files: dict[str, str] = {}
    edges, unresolved, missing = [], [], []
    while queue:
        relative = queue.pop()
        if relative in files:
            continue
        if len(files) >= MAX_GRAPH_FILES:
            unresolved.append("runtime graph exceeds limit")
            break
        path = local_path(root, relative)
        if not path.is_file():
            missing.append(relative)
            continue
        source = read_text(root, relative)
        files[relative] = digest(path)
        imports, unknowns = imports_from(source)
        unresolved.extend(f"{relative}: {item}" for item in unknowns)
        for imported in imports:
            specifier = imported["specifier"]
            edge = {"from": relative, **imported}
            if specifier.startswith("."):
                target = (path.parent / specifier.split("?", 1)[0].split("#", 1)[0]).resolve()
                if not target.is_relative_to(root.resolve()):
                    raise InvalidInput(f"Runtime import escapes repository: {specifier}")
                edge["to"] = target.relative_to(root.resolve()).as_posix()
                queue.append(edge["to"])
            else:
                edge["external"] = True
            edges.append(edge)
    return {"files": files, "edges": edges, "unresolved": unresolved, "missing": sorted(set(missing))}


def uncomment(source: str, suffix: str) -> str:
    if suffix == ".py":
        try:
            tokens = tokenize.generate_tokens(io.StringIO(source).readline)
            return tokenize.untokenize(t for t in tokens if t.type != tokenize.COMMENT)
        except (tokenize.TokenError, IndentationError):
            return ""
    # Bindings are anchored declarations; erase actual comments while preserving
    # quoted strings (including https://) and source coordinates.
    result, index = [], 0
    quote = None
    while index < len(source):
        char = source[index]
        if quote:
            result.append(char)
            if char == "\\" and index + 1 < len(source):
                index += 1
                result.append(source[index])
            elif char == quote:
                quote = None
        elif char in "\"'`":
            quote = char
            result.append(char)
        elif source.startswith("//", index) or (char == "#" and suffix in {".sh", ".yaml", ".yml"}):
            end = source.find("\n", index)
            if end < 0:
                break
            result.append("\n")
            index = end
        elif source.startswith("/*", index):
            end = source.find("*/", index + 2)
            if end < 0:
                break
            result.append(" " + "\n" * source[index:end + 2].count("\n"))
            index = end + 1
        else:
            result.append(char)
        index += 1
    return "".join(result)


def _result(requirement: str, status: str, detail: str, **facts: Any) -> dict[str, Any]:
    return {"requirement": requirement, "status": status, "detail": detail, **facts}


def git_value(root: Path, *args: str) -> str | None:
    try:
        result = subprocess.run(["git", "-C", str(root), *args], capture_output=True,
                                text=True, timeout=5, check=False)
        return result.stdout.strip() if result.returncode == 0 else None
    except (OSError, subprocess.TimeoutExpired):
        return None


def check_identity(profile: dict[str, Any], root: Path) -> list[dict[str, Any]]:
    results = []
    actual_revision = git_value(root, "rev-parse", "HEAD")
    if actual_revision is None:
        results.append(_result("source_identity", "not_verified", "Git source revision is unavailable"))
    else:
        dirty = git_value(root, "status", "--porcelain", "--untracked-files=no")
        status = "pass" if actual_revision == profile["source_revision"] and dirty == "" else "not_verified"
        results.append(_result("source_identity", status, "Observed revision compared with pinned inventory",
                               observed=actual_revision, declared=profile["source_revision"], tracked_worktree_modified=bool(dirty)))
    remote = git_value(root, "config", "--get", "remote.origin.url")
    if remote:
        if remote.startswith("git@github.com:"):
            remote_identity = remote[len("git@github.com:"):]
            recognized = True
        else:
            parsed = urlsplit(remote)
            recognized = parsed.hostname == "github.com" and parsed.scheme in {"https", "ssh"}
            remote_identity = parsed.path.lstrip("/")
        normalized = re.sub(r"\.git$", "", remote_identity.rstrip("/"))
        matched = recognized and normalized == profile["repository"]
        status = "pass" if matched else "fail" if recognized else "not_verified"
        results.append(_result("repository_identity", status,
                               "Origin repository matches declared identity" if matched else "Origin identity differs or its host is unsupported"))
    else:
        results.append(_result("repository_identity", "not_verified", "Origin repository is unavailable"))
    if profile["kind"] != "ha_integration":
        manifests = list((root / "custom_components").glob("*/manifest.json"))
        results.append(_result("manifest_identity", "fail" if manifests else "not_applicable",
                               "HA manifests exist despite non-integration kind" if manifests else "No HA integration declared or observed"))
        return results
    try:
        manifest = json.loads(read_text(root, profile["manifest_path"]))
    except (OSError, json.JSONDecodeError) as exc:
        results.append(_result("manifest_identity", "fail", f"Manifest cannot be read: {type(exc).__name__}"))
        return results
    if not isinstance(manifest, dict):
        results.append(_result("manifest_identity", "fail", "Manifest must be a JSON object"))
        return results
    expected_path = f"custom_components/{profile['domain']}/manifest.json"
    valid = (manifest.get("domain") == profile["domain"] and profile["manifest_path"] == expected_path
             and isinstance(manifest.get("version"), str) and bool(manifest["version"]))
    results.append(_result("manifest_identity", "pass" if valid else "fail", "Manifest domain/path/version checked",
                           observed_domain=manifest.get("domain"), integration_version=manifest.get("version")))
    return results


def check_artifact(artifact: dict[str, Any], root: Path) -> tuple[list[dict[str, Any]], dict[str, Any]]:
    graph = import_graph(root, artifact["path"])
    prefix = artifact["id"]
    results = []
    if graph["missing"]:
        results.append(_result("artifact_integrity", "fail", "Missing shipped runtime files", artifact=prefix, paths=graph["missing"]))
    elif not graph["files"]:
        results.append(_result("artifact_integrity", "not_verified", "No runtime inspected", artifact=prefix))
    else:
        results.append(_result("artifact_integrity", "pass", "Declared runtime files exist", artifact=prefix))
    # Absence from a partial lexer cannot prove absence of indirect loaders,
    # eval, constructed scripts, or other executable dependency mechanisms.
    autonomous = "fail" if graph["edges"] else "not_verified"
    results.append(_result("artifact_autonomy", autonomous, "Recognized runtime imports inspected; full autonomy needs build/runtime evidence",
                           artifact=prefix, imports=graph["edges"], unresolved=graph["unresolved"]))
    results.append(_result("artifact_syntax", "not_verified", "Runtime graph inventoried but not checked by the JavaScript engine", artifact=prefix))
    results.append(_result("reproducible_build", "not_verified", "No deterministic build execution evidence; profile commands are never executed", artifact=prefix))
    roles: dict[str, list[str]] = {}
    for binding in artifact["bindings"]:
        role = binding["role"]
        roles.setdefault(role, []).append(binding["path"])
        try:
            source = uncomment(read_text(root, binding["path"]), Path(binding["path"]).suffix)
            values = bounded_matches(binding["pattern"], source)
        except OSError:
            values = None
        expected = binding["expected"]
        if values is None or len(values) != 1:
            results.append(_result("artifact_bindings", "not_verified", "Binding unresolved or ambiguous",
                                   artifact=prefix, role=role, path=binding["path"], observed=values))
            continue
        actual = values[0]
        valid = actual == expected
        if role == "entrypoint":
            if binding.get("path_mode", "relative") == "basename":
                valid = valid and PurePosixPath(actual).name == PurePosixPath(artifact["path"]).name
            else:
                valid = valid and actual == artifact["path"]
        elif role == "ui_version":
            valid = valid and actual == artifact["ui_version"]
        results.append(_result("artifact_bindings", "pass" if valid else "fail", "Static binding compared to declared artifact",
                               artifact=prefix, role=role, path=binding["path"], observed=actual, expected=expected))
        if role == "ui_version" and binding["path"] not in graph["files"]:
            results.append(_result("version_coherence", "not_verified", "UI version source is outside inspected runtime graph",
                                   artifact=prefix, path=binding["path"]))
    required_roles = {"entrypoint", "ui_version", "cache_key"}
    missing_roles = sorted(required_roles.difference(roles))
    if missing_roles:
        results.append(_result("version_coherence", "not_verified", "Required version/registration bindings missing",
                               artifact=prefix, missing=missing_roles))
    evidence = artifact["registration_evidence_paths"]
    absent = [p for p in evidence if not local_path(root, p).is_file()]
    # Listed registration files are review inputs, not proof of a reachable call.
    # A supplied registration binding must additionally resolve its actual value.
    if not evidence or absent or "registration" not in roles:
        results.append(_result("registration_reachability", "not_verified", "Active setup-to-registration chain needs verification",
                               artifact=prefix, evidence_paths=evidence, missing=absent))
    else:
        results.append(_result("registration_reachability", "not_verified", "Static markers do not establish execution reachability",
                               artifact=prefix, evidence_paths=evidence))
    if artifact["binding_limitations"]:
        results.append(_result("version_coherence", "not_verified", "Declared static-resolution limitations remain",
                               artifact=prefix, limitations=artifact["binding_limitations"]))
    # A comparison to the preceding published artifact is needed to prove that
    # changed runtime content has received a new UI version and cache key.
    results.append(_result("version_change_policy", "not_verified", "Previous-publication version/cache comparison has no execution evidence", artifact=prefix))
    return results, graph


def check_standards(profile: dict[str, Any], root: Path) -> list[dict[str, Any]]:
    standard = profile["standards"]
    if not standard["applicable"]:
        if profile["artifacts"]:
            return [_result("ui_standard", "fail", "Frontend artifacts cannot disable applicable UI requirements")]
        evidence = standard["evidence_paths"]
        for path in evidence:
            local_path(root, path)
        return [_result("ui_standard", "not_verified", "Declared UI exclusion requires actual setup/capability verification",
                        declared_reason=standard["reason"], evidence_paths=evidence)]
    declaration_path = standard.get("declaration_path")
    if not declaration_path:
        return [_result("ui_standard", "not_verified", "No UI standard declaration")]
    try:
        declaration = json.loads(read_text(root, declaration_path))
    except (OSError, json.JSONDecodeError):
        return [_result("ui_standard", "fail", "UI declaration missing or malformed")]
    if not isinstance(declaration, dict):
        return [_result("ui_standard", "fail", "UI declaration must be a JSON object")]
    results = []
    for field, target in (("version", UI_VERSION), ("navigation_contract_version", NAV_VERSION)):
        observed = declaration.get(field, declaration.get("standard_version") if field == "version" else None)
        conflict = field == "version" and "version" in declaration and "standard_version" in declaration and declaration["version"] != declaration["standard_version"]
        status = "fail" if conflict else "not_verified" if observed is None else "pass" if observed == target else "fail"
        results.append(_result("ui_standard", status, "Normative version compared with canonical target",
                               field=field, observed=observed, required=target))
    for path_key, hash_key, target in (("standard_path", "standard_sha256", UI_HASH),
                                      ("navigation_contract_path", "navigation_contract_sha256", NAV_HASH)):
        declared_path = declaration.get(path_key)
        if not isinstance(declared_path, str):
            results.append(_result("ui_standard", "not_verified", f"Missing {path_key}"))
            continue
        try:
            actual_hash = digest(local_path(root, declared_path))
        except OSError:
            actual_hash = None
        declared_hash = declaration.get(hash_key)
        status = "not_verified" if actual_hash is None or declared_hash is None else "pass" if actual_hash == target and declared_hash == target else "fail"
        results.append(_result("ui_standard", status, "Actual document and declared hash compared with canonical target",
                               path=declared_path, observed_hash=actual_hash, declared_hash=declaration.get(hash_key), required_hash=target))
    results.append(_result("ui_behavior", "not_verified" if profile["artifacts"] else "not_applicable",
                           "Document parity does not prove shell behavior" if profile["artifacts"] else "No active frontend declared"))
    return results


def forbidden_shell_commands(script: str) -> list[str]:
    """Inspect shell command positions; comments and echo examples are ignored."""
    findings = []
    for line in script.replace("\\\n", "").splitlines():
        try:
            lexer = shlex.shlex(line, posix=True, punctuation_chars=";&|()")
            lexer.whitespace_split = True
            lexer.commenters = "#"
            tokens = list(lexer)
        except ValueError:
            continue
        commands, command = [], []
        for token in tokens:
            if token and all(c in ";&|()" for c in token):
                if command:
                    commands.append(command)
                    command = []
            else:
                command.append(token)
        if command:
            commands.append(command)
        for parts in commands:
            while parts and (parts[0] in {"if", "then", "do", "!", "env", "command"} or re.match(r"^[A-Za-z_][A-Za-z0-9_]*=", parts[0])):
                parts = parts[1:]
            if len(parts) >= 3 and parts[:3] == ["gh", "release", "create"]:
                findings.append("gh release create")
            if len(parts) >= 2 and parts[:2] == ["gh", "api"] and any("/releases" in p for p in parts):
                if "POST" in parts or "-f" in parts or "-F" in parts:
                    findings.append("gh api release mutation")
            if len(parts) > 2 and parts[:2] == ["git", "tag"] and not any(p in {"-l", "--list", "-v", "--verify"} for p in parts):
                findings.append("git tag mutation")
    return findings


def check_publication(profile: dict[str, Any], root: Path) -> list[dict[str, Any]]:
    policy = profile["publication"]
    valid = policy == {"default_branch": "main", "github_releases": False, "automatic_tags": False}
    results = [_result("publication_policy", "pass" if valid else "fail", "Declared publication policy compared with main/no-Releases target")]
    paths = sorted(set((root / ".github/workflows").glob("*.yml")) | set((root / ".github/workflows").glob("*.yaml")))
    findings, parse_errors, jobs = [], [], []
    for path in paths:
        relative = path.relative_to(root).as_posix()
        try:
            workflow = yaml.safe_load(read_text(root, relative))
            if not isinstance(workflow, dict) or not isinstance(workflow.get("jobs"), dict):
                raise ValueError("workflow jobs are missing")
        except (yaml.YAMLError, ValueError, OSError):
            parse_errors.append(relative)
            continue
        for job_id, job in workflow["jobs"].items():
            if not isinstance(job, dict):
                parse_errors.append(relative)
                continue
            jobs.append({"workflow": relative, "job": job_id, "name": job.get("name", job_id)})
            steps = job.get("steps", [])
            if not isinstance(steps, list):
                parse_errors.append(relative)
                continue
            for step in steps:
                if not isinstance(step, dict):
                    continue
                uses = str(step.get("uses", "")).lower()
                if any(uses.startswith(action + "@") for action in ("softprops/action-gh-release", "ncipollo/release-action", "actions/create-release")):
                    findings.append({"path": relative, "command": uses})
                run = step.get("run")
                if isinstance(run, str):
                    findings.extend({"path": relative, "command": item} for item in forbidden_shell_commands(run))
    status = "fail" if findings or parse_errors else "not_verified"
    results.append(_result("publication_workflows", status, "Recognized release/tag commands inspected; indirect scripts/actions need further evidence",
                           findings=findings, invalid_workflows=parse_errors))
    names = [item["name"] for item in jobs if isinstance(item["name"], str)]
    duplicates = sorted({name for name in names if names.count(name) > 1})
    results.append(_result("ci_job_identity", "fail" if duplicates else "pass" if jobs else "not_verified",
                           "Job names must be unique across workflows", duplicates=duplicates, jobs=jobs))
    # Profile baseline is preserved as an observation; it cannot stand in for a
    # dated GitHub ruleset/API response. No remote settings are changed here.
    results.append(_result("required_ci", "not_verified", "Effective GitHub branch protection and required contexts need live evidence",
                           observed_required_checks=profile.get("existing_required_checks", [])))
    return results


def check_evidence(profile: dict[str, Any], root: Path, hashes: dict[str, str]) -> list[dict[str, Any]]:
    records = {item["requirement"]: item for item in profile["evidence"]}
    results = []
    for requirement, scenarios in REQUIREMENTS.items():
        record = records.get(requirement)
        if record is None or record["status"] != "recorded" or not record.get("report_path"):
            results.append(_result(requirement, "not_verified", record["note"] if record else "No executable result evidence",
                                   evidence_paths=record["paths"] if record else []))
            continue
        try:
            report = json.loads(read_text(root, record["report_path"]))
        except (OSError, json.JSONDecodeError):
            results.append(_result(requirement, "not_verified", "Machine evidence report unavailable or not JSON"))
            continue
        if not isinstance(report, dict):
            results.append(_result(requirement, "not_verified", "Machine evidence must be an object"))
            continue
        evidence_hashes = report.get("subject_files", {})
        subject_valid = isinstance(evidence_hashes, dict) and bool(evidence_hashes) and bool(hashes)
        for relative, expected in evidence_hashes.items() if isinstance(evidence_hashes, dict) else []:
            try:
                subject_valid = subject_valid and digest(local_path(root, relative)) == expected
            except OSError:
                subject_valid = False
        report_scenarios = report.get("scenarios", [])
        scenarios_valid = (isinstance(report_scenarios, list) and all(isinstance(item, str) for item in report_scenarios)
                           and scenarios.issubset(set(report_scenarios)))
        expected_runners = {"device_acceptance"} if requirement == "device_acceptance" else {"behavior_test", "browser_test"}
        provenance_valid = (isinstance(report.get("runner_id"), str) and bool(report["runner_id"].strip())
                            and isinstance(report.get("environment"), dict) and bool(report["environment"]))
        revision = git_value(root, "rev-parse", "HEAD")
        revision_valid = isinstance(revision, str) and re.fullmatch(r"[0-9a-f]{40}", revision) is not None
        scope_valid = (report.get("schema_version") == 1 and report.get("repository") == profile["repository"]
                       and report.get("requirement") == requirement
                       and revision_valid and report.get("source_revision") == revision
                       and isinstance(evidence_hashes, dict)
                       and all(evidence_hashes.get(path) == value for path, value in hashes.items())
                       and scenarios_valid
                       and report.get("runner_kind") in expected_runners and provenance_valid)
        if not subject_valid or not scope_valid:
            results.append(_result(requirement, "not_verified", "Evidence scope, subjects, scenarios, or source revision do not match"))
        else:
            result = report.get("result")
            status = "pass" if result == "pass" else "fail" if result == "fail" else "not_verified"
            results.append(_result(requirement, status, "Recorded machine evidence checked against source and scenario scope; not re-executed",
                                   evidence_path=record["report_path"]))
    return results


def aggregate(results: list[dict[str, Any]]) -> str:
    statuses = {item["status"] for item in results}
    return "fail" if "fail" in statuses else "not_verified" if "not_verified" in statuses else "pass"


def validate_repository(profile: dict[str, Any], root: Path) -> dict[str, Any]:
    root = root.resolve()
    if not root.is_dir():
        return {"repository": profile["repository"], "source_revision": profile["source_revision"], "status": "not_verified",
                "requirements": [_result("repository_available", "not_verified", "Repository checkout is missing")], "artifacts": []}
    results = check_identity(profile, root)
    graphs, hashes = [], {}
    for artifact in profile["artifacts"]:
        checks, graph = check_artifact(artifact, root)
        results.extend(checks)
        graphs.append({"id": artifact["id"], "path": artifact["path"], **graph})
        hashes.update(graph["files"])
    if profile["kind"] == "ha_integration":
        component = root / "custom_components" / profile["domain"]
        for path in sorted(component.rglob("*")):
            if path.is_file() and path.suffix in {".py", ".json", ".js", ".mjs"}:
                relative = path.relative_to(root).as_posix()
                hashes[relative] = digest(local_path(root, relative))
    untracked_subjects = [relative for relative in hashes
                          if git_value(root, "ls-files", "--error-unmatch", "--", relative) is None]
    if untracked_subjects:
        results.append(_result("source_subject_tracking", "not_verified", "Inspected product files are not tracked at the source revision",
                               paths=untracked_subjects))
    if not profile["artifacts"]:
        results.append(_result("runtime_applicability", "not_verified", "Empty frontend inventory requires capability/setup verification; kind alone is not proof"))
    results.extend(check_standards(profile, root))
    results.extend(check_publication(profile, root))
    results.extend(check_evidence(profile, root, hashes))
    for finding in profile["findings"]:
        results.append(_result(finding["requirement"], "fail" if finding["status"] == "open" else "not_verified",
                               finding["note"], finding=finding["id"]))
    return {"repository": profile["repository"], "source_revision": profile["source_revision"],
            "observed_revision": git_value(root, "rev-parse", "HEAD"),
            "policy": {"contract_version": 1, "ui_version": UI_VERSION, "navigation_version": NAV_VERSION,
                       "ui_sha256": UI_HASH, "navigation_sha256": NAV_HASH},
            "status": aggregate(results), "requirements": results, "artifacts": graphs}


def write_outputs(report: dict[str, Any], args: argparse.Namespace) -> None:
    report.setdefault("checked_at", datetime.now(timezone.utc).isoformat())
    report.setdefault("tool", {"version": TOOL_VERSION, "inspector_sha256": digest(Path(__file__)), "schema_sha256": digest(SCHEMA_PATH)})
    if args.json_output:
        path = Path(args.json_output)
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_text(json.dumps(report, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    if args.markdown_output:
        path = Path(args.markdown_output)
        path.parent.mkdir(parents=True, exist_ok=True)
        scope = report.get("scope", "strict compliance")
        rows = ["# NikaS repository contract v1", "", f"Scope: {scope}.", "", f"Result: **{report['status']}**.", "",
                "Missing verification is not a pass. Static inventory and behavioral acceptance are separate evidence.", ""]
        repositories = report.get("repositories", [report] if "requirements" in report else [])
        for repository in repositories:
            rows.extend([f"## {repository['repository']}", "", f"Result: **{repository['status']}**.", "",
                         "| Requirement | Status | Detail |", "|---|---|---|"])
            for item in repository["requirements"]:
                clean = lambda value: str(value).replace("|", "\\|").replace("\n", " ")
                rows.append(f"| {clean(item['requirement'])} | {item['status']} | {clean(item['detail'])} |")
            rows.append("")
        if report.get("errors"):
            rows.extend(["Input errors:", "", *[f"- {str(item).replace(chr(10), ' ')}" for item in report["errors"]], ""])
        path.write_text("\n".join(rows), encoding="utf-8")


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    subparsers = parser.add_subparsers(dest="command", required=True)
    for name in ("schema", "validate", "fleet"):
        child = subparsers.add_parser(name)
        child.add_argument("--json-output")
        child.add_argument("--markdown-output")
        if name in {"schema", "fleet"}:
            child.add_argument("--registry", type=Path, required=True)
        if name == "validate":
            child.add_argument("--profile", type=Path, required=True)
            child.add_argument("--root", type=Path, required=True)
        if name == "fleet":
            child.add_argument("--repos-root", type=Path, required=True)
    args = parser.parse_args(argv)
    try:
        if args.command == "validate":
            profile = load_profile(args.profile)
            report = validate_repository(profile, args.root)
        else:
            paths = sorted(args.registry.glob("*.json"))
            if not paths:
                raise InvalidInput(f"Registry contains no profiles: {args.registry}")
            profiles = [load_profile(path) for path in paths]
            identities = [profile["repository"] for profile in profiles]
            if len(identities) != len(set(identities)):
                raise InvalidInput("Registry contains duplicate repositories")
            if args.command == "schema":
                report = {"schema_version": 1, "status": "pass", "scope": "profile schema only; no product compliance asserted",
                          "profiles": identities}
            else:
                reports = [validate_repository(profile, args.repos_root / profile["repository"].split("/")[1]) for profile in profiles]
                report = {"schema_version": 1, "status": aggregate(reports), "repositories": reports}
        write_outputs(report, args)
        print(json.dumps({"status": report["status"], "scope": report.get("scope", "strict compliance")}, ensure_ascii=False))
        return 0 if report["status"] == "pass" else 1
    except (InvalidInput, OSError, UnicodeError) as exc:
        report = {"schema_version": 1, "status": "fail", "scope": "malformed input", "errors": [str(exc)]}
        write_outputs(report, args)
        print(f"Invalid contract input: {exc}", file=sys.stderr)
        return 2


if __name__ == "__main__":
    raise SystemExit(main())
