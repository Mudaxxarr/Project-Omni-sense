import copy
import json
import struct
import zipfile
import zlib
from pathlib import Path

import pytest
import yaml

from services.core.app.ci_contract import (
    CI_ARTIFACT_ROOT,
    FEATURE_STATES,
    SCENARIO_ENTITY_FAMILIES,
    VIEWPORTS,
    CiContractError,
    _expected_screenshots,
    main,
    validate_phase0_evidence,
    validate_workflow_contract,
)

REPO_ROOT = Path(__file__).resolve().parents[3]
WORKFLOW = REPO_ROOT / ".github" / "workflows" / "phase0-ci.yml"
CI_SCRIPT = REPO_ROOT / "scripts" / "ci.ps1"
FEATURE_VERIFIER = REPO_ROOT / "scripts" / "verify-feature.ps1"


def _read_required(path: Path) -> str:
    assert path.is_file(), f"required CI contract file is missing: {path.relative_to(REPO_ROOT)}"
    return path.read_text(encoding="utf-8")


def _workflow() -> dict[str, object]:
    return yaml.load(_read_required(WORKFLOW), Loader=yaml.BaseLoader)


def _png(width: int, height: int) -> bytes:
    def chunk(kind: bytes, payload: bytes) -> bytes:
        return (
            struct.pack(">I", len(payload))
            + kind
            + payload
            + struct.pack(">I", zlib.crc32(kind + payload) & 0xFFFFFFFF)
        )

    raw_row = b"\x00" + (b"\x00" * ((width + 7) // 8))
    raw_pixels = raw_row * height
    return b"\x89PNG\r\n\x1a\n" + b"".join(
        (
            chunk(b"IHDR", struct.pack(">IIBBBBB", width, height, 1, 0, 0, 0, 0)),
            chunk(b"IDAT", zlib.compress(raw_pixels)),
            chunk(b"IEND", b""),
        )
    )


def _screenshot_dimensions(name: str) -> tuple[int, int]:
    dimensions = name.removesuffix(".png").rsplit("-", maxsplit=1)[1]
    width, height = dimensions.split("x")
    return int(width), int(height)


def _api_contract(feature: str) -> dict[str, object]:
    if feature == "P0-SHELL-01":
        prerequisite = {"status": "ready", "detail": "local proof"}
        return {
            "contract_version": "health.v1",
            "service": "omniscience-core",
            "version": "0.0.0",
            "mode": "local",
            "status": "healthy",
            "local_only": True,
            "cloud_inference_enabled": False,
            "timezone": "Asia/Karachi",
            "checked_at": "2026-08-02T00:00:00Z",
            "prerequisites": {
                "core_api": prerequisite,
                "postgresql": prerequisite,
                "storage_environment": prerequisite,
                "evidence_vault": prerequisite,
                "audit_chain": prerequisite,
                "retention_worker": prerequisite,
                "backup_restore": prerequisite,
            },
            "data_connection": {"status": "not_connected", "detail": "Phase 0"},
        }
    entities = {
        family: [
            {
                "id": f"fx-{family.replace('_', '-')}",
                "label": f"Fixture {family}",
                "recorded_at_utc": "2026-08-02T00:00:00Z",
                "attributes": {},
            }
        ]
        for family in SCENARIO_ENTITY_FAMILIES
    }
    return {
        "contract_version": "scenario.v1",
        "fixture_version": "phase0-fixtures.v1",
        "fixture_mode": True,
        "anonymized": True,
        "local_only": True,
        "consequential_actions_enabled": False,
        "action_lock_reason": "Phase 0 is read only.",
        "scenario": {
            "id": "valid",
            "label": "Valid",
            "status": "ready",
            "headline": "OK",
            "detail": "OK",
        },
        "available_scenarios": [
            {"id": state, "label": state.title(), "status": "ready"}
            for state in FEATURE_STATES[feature]
        ],
        "clock": {
            "deterministic": True,
            "stored_at_utc": "2026-08-02T00:00:00Z",
            "displayed_at_local": "2026-08-02T05:00:00+05:00",
            "timezone": "Asia/Karachi",
        },
        "summary": {
            "entity_family_count": len(SCENARIO_ENTITY_FAMILIES),
            "record_count": len(SCENARIO_ENTITY_FAMILIES),
        },
        "entities": entities,
        "signals": ["read only"],
    }


def _write_trace(path: Path, feature: str) -> None:
    api_url = (
        "http://127.0.0.1:8765/v1/health"
        if feature == "P0-SHELL-01"
        else "http://127.0.0.1:8765/v1/scenarios/valid"
    )
    test_records = (
        {"type": "context-options", "origin": "testRunner"},
        {"type": "before", "class": "Test", "method": "hook"},
    )
    browser_records = (
        {
            "type": "context-options",
            "origin": "library",
            "browserName": "chromium",
            "playwrightVersion": "1.62.0",
        },
        {"type": "before", "class": "BrowserContext", "method": "newPage"},
    )
    network_records = tuple(
        {
            "type": "resource-snapshot",
            "snapshot": {
                "request": {"method": "GET", "url": url},
                "response": {"status": 200},
            },
        }
        for url in ("http://127.0.0.1:4173/", api_url)
    )
    with zipfile.ZipFile(path, "w") as archive:
        archive.writestr("test.trace", "\n".join(map(json.dumps, test_records)))
        archive.writestr("0-trace.trace", "\n".join(map(json.dumps, browser_records)))
        archive.writestr("0-trace.network", "\n".join(map(json.dumps, network_records)))


def _write_valid_evidence(root: Path, feature: str) -> Path:
    feature_dir = root / feature
    screenshot_paths = _expected_screenshots(feature)
    manifest = {
        "schema": "omniscience.verification.v1",
        "feature_id": feature,
        "status": "automated_gates_passed",
        "visual_review_status": "pending_final_inspection",
        "source_commit": "a" * 40,
        "source_worktree_dirty": False,
        "commands": [
            {"name": "Runtime HTTP proof", "status": "passed"},
            {"name": "Browser state and interaction proof", "status": "passed"},
        ],
        "states": list(FEATURE_STATES[feature]),
        "viewports": list(VIEWPORTS),
        "screenshots": list(screenshot_paths),
    }
    feature_dir.mkdir(parents=True)
    (feature_dir / "manifest.json").write_text(json.dumps(manifest), encoding="utf-8")
    (feature_dir / "api-contract.json").write_text(
        json.dumps(_api_contract(feature)), encoding="utf-8"
    )
    (feature_dir / "audit-events.json").write_text(
        json.dumps(
            {
                "schema": "omniscience.audit-proof.v1",
                "feature": feature,
                "events": [],
                "reason": "Phase 0 cannot emit a business audit event.",
            }
        ),
        encoding="utf-8",
    )
    (feature_dir / "console.log").write_text(
        "Console errors: 0\nPage errors: 0\nFailed requests and HTTP responses >= 400: 0\n",
        encoding="utf-8",
    )
    (feature_dir / "visual-review.md").write_text("Pending review", encoding="utf-8")
    junit = (
        '<testsuites tests="1" failures="0" errors="0" skipped="0">'
        '<testsuite tests="1" failures="0" errors="0" skipped="0">'
        '<testcase name="proof" /></testsuite></testsuites>'
    )
    (feature_dir / "test-results.xml").write_text(junit, encoding="utf-8")
    _write_trace(feature_dir / "trace.zip", feature)

    raw_screenshot_dir = root / "playwright" / (
        "phase0-scenarios" if feature == "P0-SCENARIO-01" else "phase0"
    )
    raw_screenshot_dir.mkdir(parents=True)
    for screenshot in screenshot_paths:
        png = _png(*_screenshot_dimensions(Path(screenshot).name))
        (feature_dir / screenshot).parent.mkdir(parents=True, exist_ok=True)
        (feature_dir / screenshot).write_bytes(png)
        (raw_screenshot_dir / Path(screenshot).name).write_bytes(png)
    raw_junit = root / "playwright" / "phase0" / "test-results.xml"
    raw_junit.parent.mkdir(parents=True, exist_ok=True)
    raw_junit.write_text(junit, encoding="utf-8")
    return feature_dir


def test_workflow_parses_and_enforces_the_deterministic_phase0_contract() -> None:
    validate_workflow_contract(_workflow())


def test_pull_requests_use_one_deterministic_parity_run() -> None:
    triggers = _workflow()["on"]
    assert isinstance(triggers, dict)
    assert "pull_request" in triggers
    assert "push" not in triggers


def test_workflow_pins_windows_python_uv_and_postgresql_server_version() -> None:
    workflow = _workflow()
    job = workflow["jobs"]["phase0-parity"]
    assert job["runs-on"] == "windows-2025"

    steps = job["steps"]
    uv_step = next(step for step in steps if step.get("name") == "Set up uv")
    assert uv_step["with"]["version"] == "0.11.32"
    assert uv_step["with"]["python-version"] == "3.12.13"
    assert (REPO_ROOT / ".python-version").read_text(encoding="utf-8").strip() == "3.12.13"

    postgres_step = next(
        step for step in steps if step.get("name") == "Ensure native PostgreSQL 16"
    )
    assert 'postgres (PostgreSQL) 16.14' in postgres_step["run"]


@pytest.mark.parametrize(
    "step_name",
    (
        "Set up Node.js",
        "Install locked dependencies",
        "Run repository-owned CI parity",
        "Upload deterministic verification evidence",
    ),
)
def test_workflow_mutations_reject_missing_setup_parity_and_upload_behavior(step_name: str) -> None:
    workflow = copy.deepcopy(_workflow())
    steps = workflow["jobs"]["phase0-parity"]["steps"]
    workflow["jobs"]["phase0-parity"]["steps"] = [
        step for step in steps if step.get("name") != step_name
    ]

    with pytest.raises(CiContractError, match="missing"):
        validate_workflow_contract(workflow)


def test_workflow_rejects_a_mutable_node_runtime_or_non_fail_safe_upload() -> None:
    workflow = copy.deepcopy(_workflow())
    steps = workflow["jobs"]["phase0-parity"]["steps"]
    node_step = next(step for step in steps if step.get("name") == "Set up Node.js")
    node_step["with"]["node-version"] = "22"
    with pytest.raises(CiContractError, match="22.23.1"):
        validate_workflow_contract(workflow)

    workflow = copy.deepcopy(_workflow())
    steps = workflow["jobs"]["phase0-parity"]["steps"]
    upload_step = next(
        step
        for step in steps
        if step.get("name") == "Upload deterministic verification evidence"
    )
    upload_step.pop("if")
    with pytest.raises(CiContractError, match="failed gate"):
        validate_workflow_contract(workflow)


def test_workflow_rejects_mutable_runner_python_uv_or_postgresql_server_version(
    tmp_path: Path,
) -> None:
    workflow = copy.deepcopy(_workflow())
    workflow["jobs"]["phase0-parity"]["runs-on"] = "windows-latest"
    with pytest.raises(CiContractError, match="windows-2025"):
        validate_workflow_contract(workflow)

    workflow = copy.deepcopy(_workflow())
    steps = workflow["jobs"]["phase0-parity"]["steps"]
    uv_step = next(step for step in steps if step.get("name") == "Set up uv")
    uv_step["with"]["python-version"] = "3.12"
    with pytest.raises(CiContractError, match="Python"):
        validate_workflow_contract(workflow)

    wrong_python_version = tmp_path / ".python-version"
    wrong_python_version.write_text("3.12\n", encoding="utf-8")
    with pytest.raises(CiContractError, match=".python-version"):
        validate_workflow_contract(_workflow(), python_version_path=wrong_python_version)

    workflow = copy.deepcopy(_workflow())
    steps = workflow["jobs"]["phase0-parity"]["steps"]
    postgres_step = next(
        step for step in steps if step.get("name") == "Ensure native PostgreSQL 16"
    )
    postgres_step["run"] = postgres_step["run"].replace("16.14", "16.13")
    with pytest.raises(CiContractError, match="16.14"):
        validate_workflow_contract(workflow)


def test_workflow_does_not_treat_commented_commands_as_required_steps() -> None:
    workflow = copy.deepcopy(_workflow())
    steps = workflow["jobs"]["phase0-parity"]["steps"]
    install_step = next(step for step in steps if step.get("name") == "Install locked dependencies")
    install_step["run"] = "# corepack.cmd pnpm install --frozen-lockfile\n# uv sync --locked"

    with pytest.raises(CiContractError, match="missing commands"):
        validate_workflow_contract(workflow)


def test_ci_wrapper_uses_the_shared_ci_scoped_evidence_validator() -> None:
    ci_script = _read_required(CI_SCRIPT)

    assert "services.core.app.ci_contract" in ci_script
    assert "-PlaywrightRoot $ciPlaywrightRoot" in ci_script
    assert '"output\\ci-verification\\playwright"' not in ci_script


def test_feature_verifier_preserves_default_playwright_output_and_supports_ci_scope() -> None:
    verifier = _read_required(FEATURE_VERIFIER)
    playwright_config = _read_required(REPO_ROOT / "apps" / "desktop" / "playwright.config.ts")

    assert '[string]$ArtifactRoot = "artifacts\\verification"' in verifier
    assert '[string]$PlaywrightRoot = "output\\playwright"' in verifier
    assert "OMNISCIENCE_PLAYWRIGHT_ROOT" in verifier
    assert "OMNISCIENCE_PLAYWRIGHT_ROOT" in playwright_config


@pytest.mark.parametrize("feature", ("P0-SHELL-01", "P0-SCENARIO-01"))
def test_shared_evidence_validator_accepts_structurally_valid_feature_proof(
    tmp_path: Path, feature: str
) -> None:
    _write_valid_evidence(tmp_path, feature)

    validate_phase0_evidence(feature, tmp_path)


def test_shared_evidence_validator_rejects_a_wrong_scenario_api_contract(tmp_path: Path) -> None:
    feature = "P0-SCENARIO-01"
    feature_dir = _write_valid_evidence(tmp_path, feature)
    (feature_dir / "api-contract.json").write_text(
        json.dumps(_api_contract("P0-SHELL-01")), encoding="utf-8"
    )

    with pytest.raises(CiContractError, match="runtime API proof"):
        validate_phase0_evidence(feature, tmp_path)


@pytest.mark.parametrize(
    "mutation, expected_error",
    (
        ("missing_family", "families"),
        ("clock_mismatch", "same instant"),
        ("record_mismatch", "does not reconcile"),
    ),
)
def test_shared_evidence_validator_rejects_incomplete_scenario_facts(
    tmp_path: Path, mutation: str, expected_error: str
) -> None:
    feature = "P0-SCENARIO-01"
    feature_dir = _write_valid_evidence(tmp_path, feature)
    api = _api_contract(feature)
    if mutation == "missing_family":
        entities = api["entities"]
        assert isinstance(entities, dict)
        entities.pop("model_outcomes")
    elif mutation == "clock_mismatch":
        clock = api["clock"]
        assert isinstance(clock, dict)
        clock["displayed_at_local"] = "2026-08-02T06:00:00+05:00"
    else:
        summary = api["summary"]
        assert isinstance(summary, dict)
        summary["record_count"] = 99
    (feature_dir / "api-contract.json").write_text(json.dumps(api), encoding="utf-8")

    with pytest.raises(CiContractError, match=expected_error):
        validate_phase0_evidence(feature, tmp_path)


@pytest.mark.parametrize(
    "mutation, expected_error",
    (
        ("runtime", "runtime API proof"),
        ("wrong_api", "runtime API proof"),
        ("wrong_audit", "audit proof"),
        ("browser", "browser proof"),
        ("fake_png", "PNG"),
        ("wrong_png_dimensions", "dimensions"),
        ("zero_test_junit", "JUnit"),
        ("failing_junit", "JUnit"),
        ("fake_trace", "trace"),
        ("missing_trace_entries", "trace entries"),
        ("empty_trace_entries", "empty Playwright entries"),
        ("placeholder_trace", "Playwright"),
        ("truncated_trace", "trace"),
        ("manifest", "manifest status"),
    ),
)
def test_shared_evidence_validator_rejects_missing_or_invalid_proof(
    tmp_path: Path, mutation: str, expected_error: str
) -> None:
    feature = "P0-SHELL-01"
    feature_dir = _write_valid_evidence(tmp_path, feature)
    if mutation == "runtime":
        (feature_dir / "api-contract.json").unlink()
    elif mutation == "wrong_api":
        (feature_dir / "api-contract.json").write_text("{}", encoding="utf-8")
    elif mutation == "wrong_audit":
        (feature_dir / "audit-events.json").write_text("{}", encoding="utf-8")
    elif mutation == "browser":
        (feature_dir / "console.log").write_text("Console errors: 1", encoding="utf-8")
    elif mutation == "fake_png":
        (feature_dir / "screenshots" / "live-1280x720.png").write_bytes(b"\x89PNG\r\n\x1a\nproof")
    elif mutation == "wrong_png_dimensions":
        (feature_dir / "screenshots" / "live-1280x720.png").write_bytes(_png(1, 1))
    elif mutation == "zero_test_junit":
        (feature_dir / "test-results.xml").write_text(
            '<testsuites tests="0" />', encoding="utf-8"
        )
    elif mutation == "failing_junit":
        (feature_dir / "test-results.xml").write_text(
            (
                '<testsuite tests="1" failures="1">'
                '<testcase name="proof"><failure /></testcase></testsuite>'
            ),
            encoding="utf-8",
        )
    elif mutation == "fake_trace":
        (feature_dir / "trace.zip").write_bytes(b"PK\x03\x04")
    elif mutation == "missing_trace_entries":
        with zipfile.ZipFile(feature_dir / "trace.zip", "w") as archive:
            archive.writestr("not-playwright.txt", "proof")
    elif mutation == "empty_trace_entries":
        with zipfile.ZipFile(feature_dir / "trace.zip", "w") as archive:
            archive.writestr("test.trace", "")
            archive.writestr("0-trace.trace", "")
            archive.writestr("0-trace.network", "")
    elif mutation == "placeholder_trace":
        with zipfile.ZipFile(feature_dir / "trace.zip", "w") as archive:
            archive.writestr("test.trace", "{}")
            archive.writestr("0-trace.trace", "{}")
            archive.writestr("0-trace.network", "{}")
    elif mutation == "truncated_trace":
        (feature_dir / "trace.zip").write_bytes((feature_dir / "trace.zip").read_bytes()[:-5])
    else:
        manifest_path = feature_dir / "manifest.json"
        manifest = json.loads(manifest_path.read_text(encoding="utf-8"))
        manifest["status"] = "failed"
        manifest_path.write_text(json.dumps(manifest), encoding="utf-8")

    with pytest.raises(CiContractError, match=expected_error):
        validate_phase0_evidence(feature, tmp_path)


def test_ci_validator_cli_rejects_evidence_outside_the_ci_artifact_root(tmp_path: Path) -> None:
    _write_valid_evidence(tmp_path, "P0-SHELL-01")

    assert main(["--artifact-root", str(tmp_path), "--feature", "P0-SHELL-01"]) == 1
    assert CI_ARTIFACT_ROOT.as_posix().endswith("output/ci-verification")
