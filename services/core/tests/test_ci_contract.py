import copy
import json
from pathlib import Path

import pytest
import yaml

from services.core.app.ci_contract import (
    CI_ARTIFACT_ROOT,
    FEATURE_STATES,
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
    (feature_dir / "api-contract.json").write_text("{}", encoding="utf-8")
    (feature_dir / "audit-events.json").write_text("{}", encoding="utf-8")
    (feature_dir / "console.log").write_text(
        "Console errors: 0\nPage errors: 0\nFailed requests and HTTP responses >= 400: 0\n",
        encoding="utf-8",
    )
    (feature_dir / "visual-review.md").write_text("Pending review", encoding="utf-8")
    (feature_dir / "test-results.xml").write_text("<testsuites />", encoding="utf-8")
    (feature_dir / "trace.zip").write_bytes(b"PK\x03\x04")

    raw_screenshot_dir = root / "playwright" / (
        "phase0-scenarios" if feature == "P0-SCENARIO-01" else "phase0"
    )
    raw_screenshot_dir.mkdir(parents=True)
    for screenshot in screenshot_paths:
        png = b"\x89PNG\r\n\x1a\nproof"
        (feature_dir / screenshot).parent.mkdir(parents=True, exist_ok=True)
        (feature_dir / screenshot).write_bytes(png)
        (raw_screenshot_dir / Path(screenshot).name).write_bytes(png)
    raw_junit = root / "playwright" / "phase0" / "test-results.xml"
    raw_junit.parent.mkdir(parents=True, exist_ok=True)
    raw_junit.write_text("<testsuites />", encoding="utf-8")
    return feature_dir


def test_workflow_parses_and_enforces_the_deterministic_phase0_contract() -> None:
    validate_workflow_contract(_workflow())


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


@pytest.mark.parametrize(
    "mutation, expected_error",
    (
        ("runtime", "runtime API proof"),
        ("browser", "browser proof"),
        ("screenshot", "copied screenshot"),
        ("junit", "JUnit"),
        ("trace", "trace"),
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
    elif mutation == "browser":
        (feature_dir / "console.log").write_text("Console errors: 1", encoding="utf-8")
    elif mutation == "screenshot":
        (feature_dir / "screenshots" / "live-1280x720.png").unlink()
    elif mutation == "junit":
        (feature_dir / "test-results.xml").unlink()
    elif mutation == "trace":
        (feature_dir / "trace.zip").unlink()
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
