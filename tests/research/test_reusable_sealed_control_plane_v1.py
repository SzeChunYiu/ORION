from __future__ import annotations

import json
import subprocess
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
PACKET = ROOT / "research/self-orion/reusable-sealed-promotion-v1"
RUNNER = PACKET / "run_conformance_campaign.py"
CHECKER = PACKET / "verify_control_plane.py"
TERMINAL = "CONTROL_PLANE_VERIFIED__EMPIRICAL_CAMPAIGN_NOT_RUN"


def run_campaign(path: Path) -> None:
    completed = subprocess.run(
        [sys.executable, str(RUNNER), "--output", str(path)],
        cwd=ROOT,
        capture_output=True,
        text=True,
        check=False,
    )
    assert completed.returncode == 0, completed.stderr + completed.stdout


def verify(path: Path | None = None) -> subprocess.CompletedProcess[str]:
    command = [sys.executable, str(CHECKER)]
    if path is not None:
        command.extend(["--campaign", str(path)])
    return subprocess.run(
        command,
        cwd=ROOT,
        capture_output=True,
        text=True,
        check=False,
    )


def test_current_tree_control_plane_is_verified() -> None:
    completed = verify()
    assert completed.returncode == 0, completed.stderr + completed.stdout
    assert completed.stdout.strip().splitlines()[-1] == TERMINAL


def test_generated_campaign_matches_frozen_control_plane(tmp_path: Path) -> None:
    campaign = tmp_path / "campaign"
    run_campaign(campaign)
    completed = verify(campaign)
    assert completed.returncode == 0, completed.stderr + completed.stdout
    assert completed.stdout.strip().splitlines()[-1] == TERMINAL


def test_resigned_alpha_ceiling_change_is_rejected(tmp_path: Path) -> None:
    campaign = tmp_path / "campaign"
    run_campaign(campaign)
    config_path = campaign / "CAMPAIGN.json"
    config = json.loads(config_path.read_text())
    config["alpha_total"] = {"numerator": 1, "denominator": 1}
    config_path.write_text(json.dumps(config, indent=2, sort_keys=True) + "\n")
    completed = verify(campaign)
    assert completed.returncode == 1
    assert "campaign control plane differs from frozen config" in completed.stdout


def test_distinct_but_unregistered_identities_are_rejected(tmp_path: Path) -> None:
    campaign = tmp_path / "campaign"
    run_campaign(campaign)
    config_path = campaign / "CAMPAIGN.json"
    config = json.loads(config_path.read_text())
    config["identities"]["candidate_generator"] = "replacement-generator"
    config["identities"]["promotion_authority"] = "replacement-authority"
    config_path.write_text(json.dumps(config, indent=2, sort_keys=True) + "\n")
    completed = verify(campaign)
    assert completed.returncode == 1
    assert "campaign control plane differs from frozen config" in completed.stdout


def test_subject_redefinition_is_rejected(tmp_path: Path) -> None:
    campaign = tmp_path / "campaign"
    run_campaign(campaign)
    config_path = campaign / "CAMPAIGN.json"
    config = json.loads(config_path.read_text())
    config["subject_revision"] = "f" * 40
    config_path.write_text(json.dumps(config, indent=2, sort_keys=True) + "\n")
    completed = verify(campaign)
    assert completed.returncode == 1
    assert "campaign control plane differs from frozen config" in completed.stdout
