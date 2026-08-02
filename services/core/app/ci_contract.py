"""Validate deterministic Phase 0 CI workflow and evidence contracts."""

from __future__ import annotations

import argparse
import json
import re
import struct
import sys
import xml.etree.ElementTree as element_tree
import zipfile
from collections.abc import Mapping, Sequence
from pathlib import Path
from typing import Any
from zlib import crc32, decompress
from zlib import error as ZlibError

REPO_ROOT = Path(__file__).resolve().parents[3]
CI_ARTIFACT_ROOT = REPO_ROOT / "output" / "ci-verification"
VIEWPORTS = ("1280x720", "1440x900", "1920x1080")
FEATURE_STATES = {
    "P0-SHELL-01": ("live", "degraded", "stale", "loading", "error"),
    "P0-SCENARIO-01": (
        "valid",
        "stale",
        "duplicate",
        "contradictory",
        "denied",
        "degraded",
        "timeout",
        "recovery",
    ),
}


class CiContractError(ValueError):
    """Raised when a Phase 0 CI contract or its required proof is invalid."""


def _require_mapping(value: object, description: str) -> Mapping[str, Any]:
    if not isinstance(value, Mapping):
        raise CiContractError(f"{description} must be a mapping.")
    return value


def _require_string(value: object, description: str) -> str:
    if not isinstance(value, str) or not value:
        raise CiContractError(f"{description} must be a non-empty string.")
    return value


def _expected_screenshots(feature: str) -> tuple[str, ...]:
    try:
        states = FEATURE_STATES[feature]
    except KeyError as error:
        raise CiContractError(f"Unsupported Phase 0 feature: {feature}") from error

    screenshots = tuple(
        f"screenshots/{state}-{viewport}.png"
        for state in states
        for viewport in VIEWPORTS
    )
    if feature == "P0-SHELL-01":
        screenshots += ("screenshots/source-setup-1440x900.png",)
    return screenshots


def _read_json(path: Path, description: str) -> Mapping[str, Any]:
    if not path.is_file():
        raise CiContractError(f"{description} is missing: {path}")
    try:
        payload = json.loads(path.read_text(encoding="utf-8-sig"))
    except json.JSONDecodeError as error:
        raise CiContractError(f"{description} is not valid JSON: {path}") from error
    return _require_mapping(payload, description)


def _require_nonempty_file(path: Path, description: str) -> None:
    if not path.is_file() or path.stat().st_size == 0:
        raise CiContractError(f"{description} is missing or empty: {path}")


def _expected_png_dimensions(path: Path, description: str) -> tuple[int, int]:
    match = re.search(r"-(\d+)x(\d+)\.png$", path.name)
    if match is None:
        raise CiContractError(f"{description} has no viewport dimensions in its filename: {path}")
    return int(match.group(1)), int(match.group(2))


def _require_png(path: Path, description: str) -> None:
    _require_nonempty_file(path, description)
    data = path.read_bytes()
    if data[:8] != b"\x89PNG\r\n\x1a\n":
        raise CiContractError(f"{description} is not a PNG image: {path}")
    expected_dimensions = _expected_png_dimensions(path, description)
    offset = 8
    saw_ihdr = False
    saw_idat = False
    saw_iend = False
    dimensions: tuple[int, int] | None = None
    image_format: tuple[int, int, int] | None = None
    compressed_pixels: list[bytes] = []
    while offset < len(data):
        if offset + 12 > len(data):
            raise CiContractError(f"{description} is a truncated PNG image: {path}")
        length = struct.unpack(">I", data[offset : offset + 4])[0]
        chunk_end = offset + 12 + length
        if chunk_end > len(data):
            raise CiContractError(f"{description} is a truncated PNG image: {path}")
        chunk_type = data[offset + 4 : offset + 8]
        payload = data[offset + 8 : offset + 8 + length]
        expected_crc = struct.unpack(">I", data[offset + 8 + length : chunk_end])[0]
        if crc32(chunk_type + payload) & 0xFFFFFFFF != expected_crc:
            raise CiContractError(f"{description} has an invalid PNG chunk checksum: {path}")
        if not saw_ihdr:
            if chunk_type != b"IHDR" or length != 13:
                raise CiContractError(f"{description} has an invalid PNG IHDR chunk: {path}")
            width, height, bit_depth, color_type, compression, filter_method, interlace = (
                struct.unpack(">IIBBBBB", payload)
            )
            if width == 0 or height == 0:
                raise CiContractError(f"{description} has invalid PNG dimensions: {path}")
            allowed_depths = {
                0: {1, 2, 4, 8, 16},
                2: {8, 16},
                3: {1, 2, 4, 8},
                4: {8, 16},
                6: {8, 16},
            }
            if bit_depth not in allowed_depths.get(color_type, set()):
                raise CiContractError(f"{description} has an invalid PNG pixel format: {path}")
            if compression != 0 or filter_method != 0 or interlace != 0:
                raise CiContractError(f"{description} uses an unsupported PNG encoding: {path}")
            dimensions = (width, height)
            image_format = (bit_depth, color_type, height)
            saw_ihdr = True
        elif chunk_type == b"IDAT":
            saw_idat = True
            compressed_pixels.append(payload)
        elif chunk_type == b"IEND":
            if length != 0 or chunk_end != len(data):
                raise CiContractError(f"{description} has an invalid PNG IEND chunk: {path}")
            saw_iend = True
        offset = chunk_end
    if not saw_ihdr or not saw_idat or not saw_iend:
        raise CiContractError(f"{description} is missing required PNG chunks: {path}")
    if dimensions != expected_dimensions:
        raise CiContractError(
            f"{description} PNG dimensions {dimensions} do not match {expected_dimensions}: {path}"
        )
    assert image_format is not None
    bit_depth, color_type, height = image_format
    channels = {0: 1, 2: 3, 3: 1, 4: 2, 6: 4}[color_type]
    row_bytes = (dimensions[0] * channels * bit_depth + 7) // 8
    try:
        pixels = decompress(b"".join(compressed_pixels))
    except ZlibError as error:
        raise CiContractError(f"{description} has invalid PNG image data: {path}") from error
    if len(pixels) != height * (row_bytes + 1):
        raise CiContractError(f"{description} has incomplete PNG image data: {path}")
    if any(pixels[offset] > 4 for offset in range(0, len(pixels), row_bytes + 1)):
        raise CiContractError(f"{description} has an invalid PNG row filter: {path}")


def _require_junit(path: Path) -> None:
    _require_nonempty_file(path, "Playwright JUnit result")
    try:
        root = element_tree.parse(path).getroot()
    except element_tree.ParseError as error:
        raise CiContractError(f"Playwright JUnit result is not valid XML: {path}") from error
    if root.tag not in {"testsuite", "testsuites"}:
        raise CiContractError(f"Playwright JUnit root is invalid: {root.tag}")
    test_count = sum(
        1 for node in root.iter() if node.tag.rsplit("}", maxsplit=1)[-1] == "testcase"
    )
    if test_count == 0:
        raise CiContractError("Playwright JUnit result contains zero test cases.")
    for node in root.iter():
        for attribute in ("failures", "errors", "skipped"):
            value = node.attrib.get(attribute, "0")
            try:
                count = int(value)
            except ValueError as error:
                raise CiContractError(
                    f"Playwright JUnit {attribute} count is invalid: {value}"
                ) from error
            if count != 0:
                raise CiContractError(
                    f"Playwright JUnit {attribute} count must be zero: {count}"
                )
        if node.tag.rsplit("}", maxsplit=1)[-1] in {"failure", "error", "skipped"}:
            raise CiContractError("Playwright JUnit result contains a failed or skipped test.")


def _require_trace(path: Path) -> None:
    _require_nonempty_file(path, "critical-journey trace")
    if not zipfile.is_zipfile(path):
        raise CiContractError(f"critical-journey trace is not a zip archive: {path}")
    try:
        with zipfile.ZipFile(path) as archive:
            if archive.testzip() is not None:
                raise CiContractError(f"critical-journey trace is corrupt: {path}")
            entries = set(archive.namelist())
            entry_sizes = {name: archive.getinfo(name).file_size for name in entries}
    except zipfile.BadZipFile as error:
        raise CiContractError(
            f"critical-journey trace is not a valid zip archive: {path}"
        ) from error
    trace_entries = {
        name
        for name in entries
        if name == "trace.trace" or name.endswith("-trace.trace")
    }
    network_entries = {
        name
        for name in entries
        if name == "trace.network" or name.endswith("-trace.network")
    }
    if not trace_entries or not network_entries or "test.trace" not in entries:
        raise CiContractError(
            "critical-journey trace is missing Playwright trace entries."
        )
    required_entries = trace_entries | network_entries | {"test.trace"}
    empty_entries = sorted(name for name in required_entries if entry_sizes[name] == 0)
    if empty_entries:
        raise CiContractError(
            f"critical-journey trace contains empty Playwright entries: {empty_entries}"
        )


def _require_api_contract(feature: str, path: Path) -> None:
    api = _read_json(path, "runtime API proof")
    if feature == "P0-SHELL-01":
        expected = {
            "contract_version": "health.v1",
            "service": "omniscience-core",
            "mode": "local",
            "local_only": True,
            "cloud_inference_enabled": False,
            "timezone": "Asia/Karachi",
        }
        for field, value in expected.items():
            if api.get(field) != value:
                raise CiContractError(f"runtime API proof has invalid {field} for {feature}.")
        if api.get("status") not in {"healthy", "degraded"}:
            raise CiContractError(f"runtime API proof has invalid status for {feature}.")
        _require_string(api.get("version"), "runtime API proof version")
        _require_string(api.get("checked_at"), "runtime API proof checked_at")
        prerequisites = _require_mapping(
            api.get("prerequisites"), "runtime API proof prerequisites"
        )
        for name in (
            "core_api",
            "postgresql",
            "evidence_vault",
            "audit_chain",
            "retention_worker",
            "backup_restore",
        ):
            requirement = _require_mapping(
                prerequisites.get(name), f"runtime API proof prerequisite {name}"
            )
            if requirement.get("status") not in {
                "ready",
                "planned",
                "not_configured",
                "unavailable",
            }:
                raise CiContractError(f"runtime API proof prerequisite {name} has invalid status.")
            _require_string(
                requirement.get("detail"), f"runtime API proof prerequisite {name} detail"
            )
        data_connection = _require_mapping(
            api.get("data_connection"), "runtime API proof data_connection"
        )
        if data_connection.get("status") != "not_connected":
            raise CiContractError("runtime API proof data_connection must be not_connected.")
        _require_string(data_connection.get("detail"), "runtime API proof data_connection detail")
        return

    expected = {
        "contract_version": "scenario.v1",
        "fixture_mode": True,
        "anonymized": True,
        "local_only": True,
        "consequential_actions_enabled": False,
    }
    for field, value in expected.items():
        if api.get(field) != value:
            raise CiContractError(f"runtime API proof has invalid {field} for {feature}.")
    for field in ("fixture_version", "action_lock_reason"):
        _require_string(api.get(field), f"runtime API proof {field}")
    scenario = _require_mapping(api.get("scenario"), "runtime API proof scenario")
    if scenario.get("id") != "valid":
        raise CiContractError("runtime API proof scenario must be valid.")
    for field in ("label", "status", "headline", "detail"):
        _require_string(scenario.get(field), f"runtime API proof scenario {field}")
    available = api.get("available_scenarios")
    if not isinstance(available, Sequence) or isinstance(available, (str, bytes)) or not available:
        raise CiContractError("runtime API proof available_scenarios is invalid.")
    clock = _require_mapping(api.get("clock"), "runtime API proof clock")
    if clock.get("deterministic") is not True or clock.get("timezone") != "Asia/Karachi":
        raise CiContractError("runtime API proof clock is invalid.")
    for field in ("stored_at_utc", "displayed_at_local"):
        _require_string(clock.get(field), f"runtime API proof clock {field}")
    summary = _require_mapping(api.get("summary"), "runtime API proof summary")
    if (
        not isinstance(summary.get("entity_family_count"), int)
        or summary["entity_family_count"] <= 0
    ):
        raise CiContractError("runtime API proof entity_family_count is invalid.")
    if not isinstance(summary.get("record_count"), int) or summary["record_count"] < 0:
        raise CiContractError("runtime API proof record_count is invalid.")
    entities = _require_mapping(api.get("entities"), "runtime API proof entities")
    if not entities:
        raise CiContractError("runtime API proof entities is empty.")
    signals = api.get("signals")
    if not isinstance(signals, Sequence) or isinstance(signals, (str, bytes)) or not signals:
        raise CiContractError("runtime API proof signals is invalid.")


def _require_audit_proof(feature: str, path: Path) -> None:
    audit = _read_json(path, "audit proof")
    if audit.get("schema") != "omniscience.audit-proof.v1":
        raise CiContractError("audit proof schema is invalid.")
    if audit.get("feature") != feature:
        raise CiContractError("audit proof feature does not match the requested feature.")
    events = audit.get("events")
    if not isinstance(events, Sequence) or isinstance(events, (str, bytes)) or events:
        raise CiContractError("audit proof events must be an empty list for Phase 0.")
    _require_string(audit.get("reason"), "audit proof reason")


def _require_passed_command(manifest: Mapping[str, Any], name: str) -> None:
    commands = manifest.get("commands")
    if not isinstance(commands, Sequence) or isinstance(commands, (str, bytes)):
        raise CiContractError("manifest commands must be a list.")
    for command in commands:
        if isinstance(command, Mapping) and command.get("name") == name:
            if command.get("status") != "passed":
                raise CiContractError(f"manifest command did not pass: {name}")
            return
    raise CiContractError(f"manifest command is missing: {name}")


def validate_phase0_evidence(
    feature: str,
    artifact_root: Path,
    *,
    require_ci_scope: bool = False,
) -> None:
    """Reject incomplete or invalid evidence emitted by a Phase 0 CI parity run."""
    if require_ci_scope and artifact_root.resolve() != CI_ARTIFACT_ROOT.resolve():
        raise CiContractError(
            f"CI evidence must stay in {CI_ARTIFACT_ROOT}; received {artifact_root.resolve()}."
        )

    feature_dir = artifact_root / feature
    manifest = _read_json(feature_dir / "manifest.json", "verification manifest")
    if manifest.get("schema") != "omniscience.verification.v1":
        raise CiContractError("manifest schema is invalid.")
    if manifest.get("feature_id") != feature:
        raise CiContractError("manifest feature_id does not match the requested feature.")
    if manifest.get("status") != "automated_gates_passed":
        raise CiContractError("manifest status is not automated_gates_passed.")
    if manifest.get("visual_review_status") != "pending_final_inspection":
        raise CiContractError("manifest visual review state is invalid.")
    source_commit = manifest.get("source_commit")
    if not isinstance(source_commit, str) or len(source_commit) != 40:
        raise CiContractError("manifest source_commit is invalid.")
    try:
        int(source_commit, 16)
    except ValueError as error:
        raise CiContractError("manifest source_commit is invalid.") from error
    if manifest.get("source_worktree_dirty") is not False:
        raise CiContractError("manifest source worktree must be clean.")

    _require_passed_command(manifest, "Runtime HTTP proof")
    _require_passed_command(manifest, "Browser state and interaction proof")

    expected_states = FEATURE_STATES.get(feature)
    if tuple(manifest.get("states", ())) != expected_states:
        raise CiContractError("manifest states do not match the feature contract.")
    if tuple(manifest.get("viewports", ())) != VIEWPORTS:
        raise CiContractError("manifest viewports do not match the feature contract.")

    expected_screenshots = _expected_screenshots(feature)
    if tuple(manifest.get("screenshots", ())) != expected_screenshots:
        raise CiContractError("manifest screenshot inventory is incomplete or invalid.")
    for relative_path in expected_screenshots:
        _require_png(feature_dir / relative_path, f"copied screenshot {relative_path}")

    _require_api_contract(feature, feature_dir / "api-contract.json")
    _require_audit_proof(feature, feature_dir / "audit-events.json")
    _require_nonempty_file(feature_dir / "visual-review.md", "visual review")
    console_log = feature_dir / "console.log"
    _require_nonempty_file(console_log, "browser proof")
    console_text = console_log.read_text(encoding="utf-8")
    for expected_line in (
        "Console errors: 0",
        "Page errors: 0",
        "Failed requests and HTTP responses >= 400: 0",
    ):
        if expected_line not in console_text:
            raise CiContractError(f"browser proof is missing: {expected_line}")
    _require_junit(feature_dir / "test-results.xml")
    _require_trace(feature_dir / "trace.zip")

    playwright_root = artifact_root / "playwright"
    raw_screenshot_dir = playwright_root / (
        "phase0-scenarios" if feature == "P0-SCENARIO-01" else "phase0"
    )
    for relative_path in expected_screenshots:
        _require_png(raw_screenshot_dir / Path(relative_path).name, "CI-scoped raw screenshot")
    _require_junit(playwright_root / "phase0" / "test-results.xml")


def _workflow_step_by_name(steps: object, name: str) -> Mapping[str, Any]:
    if not isinstance(steps, Sequence) or isinstance(steps, (str, bytes)):
        raise CiContractError("workflow steps must be a list.")
    for step in steps:
        if isinstance(step, Mapping) and step.get("name") == name:
            return step
    raise CiContractError(f"workflow step is missing: {name}")


def _require_step_uses(steps: object, name: str, action: str) -> None:
    step = _workflow_step_by_name(steps, name)
    if step.get("uses") != action:
        raise CiContractError(f"workflow step {name} must use {action}.")


def _strip_powershell_comments(run: str) -> str:
    """Return executable PowerShell text with line and block comments removed."""
    uncommented = re.sub(r"<#.*?#>", "", run, flags=re.DOTALL)
    lines: list[str] = []
    for line in uncommented.splitlines():
        quote: str | None = None
        escaped = False
        characters: list[str] = []
        for character in line:
            if escaped:
                characters.append(character)
                escaped = False
                continue
            if character == "`" and quote is not None:
                characters.append(character)
                escaped = True
                continue
            if character in {"'", '"'}:
                if quote == character:
                    quote = None
                elif quote is None:
                    quote = character
                characters.append(character)
                continue
            if character == "#" and quote is None:
                break
            characters.append(character)
        lines.append("".join(characters))
    return "\n".join(lines)


def _require_step_run(steps: object, name: str, required_tokens: tuple[str, ...]) -> None:
    step = _workflow_step_by_name(steps, name)
    run = _require_string(step.get("run"), f"workflow step {name} run command")
    executable_run = _strip_powershell_comments(run)
    missing_tokens = [token for token in required_tokens if token not in executable_run]
    if missing_tokens:
        raise CiContractError(f"workflow step {name} is missing commands: {missing_tokens}")


def validate_workflow_contract(
    workflow: Mapping[str, Any], *, python_version_path: Path = REPO_ROOT / ".python-version"
) -> None:
    """Validate parsed GitHub Actions structure for deterministic Phase 0 parity."""
    triggers = _require_mapping(workflow.get("on"), "workflow triggers")
    schedule = triggers.get("schedule")
    if not isinstance(schedule, Sequence) or isinstance(schedule, (str, bytes)):
        raise CiContractError("workflow nightly schedule is missing.")
    jobs = _require_mapping(workflow.get("jobs"), "workflow jobs")
    parity_job = _require_mapping(jobs.get("phase0-parity"), "phase0-parity job")
    if parity_job.get("runs-on") != "windows-2025":
        raise CiContractError("phase0-parity must run on windows-2025.")
    steps = parity_job.get("steps")

    _require_step_uses(
        steps,
        "Check out source",
        "actions/checkout@d23441a48e516b6c34aea4fa41551a30e30af803",
    )
    _require_step_uses(
        steps,
        "Set up Node.js",
        "actions/setup-node@249970729cb0ef3589644e2896645e5dc5ba9c38",
    )
    node_step = _workflow_step_by_name(steps, "Set up Node.js")
    node_with = _require_mapping(node_step.get("with"), "Node.js setup configuration")
    if node_with.get("node-version") != "22.23.1":
        raise CiContractError("Node.js must be pinned to 22.23.1.")
    _require_step_uses(
        steps,
        "Set up uv",
        "astral-sh/setup-uv@08807647e7069bb48b6ef5acd8ec9567f424441b",
    )
    uv_step = _workflow_step_by_name(steps, "Set up uv")
    uv_with = _require_mapping(uv_step.get("with"), "uv setup configuration")
    if uv_with.get("version") != "0.11.32":
        raise CiContractError("setup-uv must be pinned to 0.11.32.")
    if uv_with.get("python-version") != "3.12.13":
        raise CiContractError("setup-uv must pin Python to 3.12.13.")
    if uv_with.get("enable-cache") != "true":
        raise CiContractError(
            "setup-uv must explicitly enable its deterministic cache configuration."
        )
    try:
        pinned_python_version = python_version_path.read_text(encoding="utf-8").strip()
    except OSError as error:
        raise CiContractError(f".python-version is missing: {python_version_path}") from error
    if pinned_python_version != "3.12.13":
        raise CiContractError(".python-version must pin Python to 3.12.13.")
    _require_step_run(
        steps,
        "Install locked dependencies",
        ("corepack.cmd pnpm install --frozen-lockfile", "uv sync --locked"),
    )
    _require_step_run(
        steps,
        "Install Chromium",
        ("playwright install chromium",),
    )
    _require_step_run(
        steps,
        "Ensure native PostgreSQL 16",
        (
            "postgresql16 --version=16.14.0",
            "postgres.exe",
            "--version",
            "postgres (PostgreSQL) 16.14",
            "pg_isready.exe",
        ),
    )
    _require_step_run(steps, "Run repository-owned CI parity", (r".\scripts\ci.ps1",))
    upload = _workflow_step_by_name(steps, "Upload deterministic verification evidence")
    if upload.get("uses") != "actions/upload-artifact@b7c566a772e6b6bfb58ed0dc250532a479d7789f":
        raise CiContractError("verification evidence must use the pinned upload-artifact action.")
    if upload.get("if") != "always()":
        raise CiContractError("verification evidence upload must run even after a failed gate.")
    upload_with = _require_mapping(upload.get("with"), "artifact upload configuration")
    artifact_path = _require_string(upload_with.get("path"), "artifact upload path")
    if "output/ci-verification" not in artifact_path or "output/playwright" in artifact_path:
        raise CiContractError(
            "artifact upload must contain only the isolated CI verification root."
        )


def _parse_args(args: Sequence[str] | None) -> argparse.Namespace:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--artifact-root", required=True, type=Path)
    parser.add_argument("--feature", required=True, choices=tuple(FEATURE_STATES))
    return parser.parse_args(args)


def main(args: Sequence[str] | None = None) -> int:
    parsed = _parse_args(args)
    artifact_root = parsed.artifact_root
    if not artifact_root.is_absolute():
        artifact_root = REPO_ROOT / artifact_root
    try:
        validate_phase0_evidence(parsed.feature, artifact_root, require_ci_scope=True)
    except CiContractError as error:
        print(f"CI evidence validation failed: {error}", file=sys.stderr)
        return 1
    print(f"CI evidence validation passed: {parsed.feature}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
