"""Validate deterministic Phase 0 CI workflow and evidence contracts."""

from __future__ import annotations

import argparse
import json
import sys
import xml.etree.ElementTree as element_tree
from collections.abc import Mapping, Sequence
from pathlib import Path
from typing import Any

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


def _require_png(path: Path, description: str) -> None:
    _require_nonempty_file(path, description)
    if path.read_bytes()[:8] != b"\x89PNG\r\n\x1a\n":
        raise CiContractError(f"{description} is not a PNG image: {path}")


def _require_junit(path: Path) -> None:
    _require_nonempty_file(path, "Playwright JUnit result")
    try:
        root = element_tree.parse(path).getroot()
    except element_tree.ParseError as error:
        raise CiContractError(f"Playwright JUnit result is not valid XML: {path}") from error
    if root.tag not in {"testsuite", "testsuites"}:
        raise CiContractError(f"Playwright JUnit root is invalid: {root.tag}")


def _require_trace(path: Path) -> None:
    _require_nonempty_file(path, "critical-journey trace")
    if path.read_bytes()[:2] != b"PK":
        raise CiContractError(f"critical-journey trace is not a zip archive: {path}")


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

    _read_json(feature_dir / "api-contract.json", "runtime API proof")
    _read_json(feature_dir / "audit-events.json", "audit proof")
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


def _require_step_run(steps: object, name: str, required_tokens: tuple[str, ...]) -> None:
    step = _workflow_step_by_name(steps, name)
    run = _require_string(step.get("run"), f"workflow step {name} run command")
    missing_tokens = [token for token in required_tokens if token not in run]
    if missing_tokens:
        raise CiContractError(f"workflow step {name} is missing commands: {missing_tokens}")


def validate_workflow_contract(workflow: Mapping[str, Any]) -> None:
    """Validate parsed GitHub Actions structure for deterministic Phase 0 parity."""
    triggers = _require_mapping(workflow.get("on"), "workflow triggers")
    schedule = triggers.get("schedule")
    if not isinstance(schedule, Sequence) or isinstance(schedule, (str, bytes)):
        raise CiContractError("workflow nightly schedule is missing.")
    jobs = _require_mapping(workflow.get("jobs"), "workflow jobs")
    parity_job = _require_mapping(jobs.get("phase0-parity"), "phase0-parity job")
    if parity_job.get("runs-on") != "windows-latest":
        raise CiContractError("phase0-parity must run on windows-latest.")
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
        ("postgresql16 --version=16.14.0", "pg_isready.exe"),
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
