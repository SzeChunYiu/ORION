from __future__ import annotations

import copy
import importlib.util
import json
import subprocess
import sys
from fractions import Fraction
from pathlib import Path
from typing import Any

import pytest

ROOT = Path(__file__).resolve().parents[2]
PACKET = ROOT / "research/self-orion/reusable-sealed-promotion-v1"
RUNNER = PACKET / "run_conformance_campaign.py"
CHECKER = PACKET / "independent_checker/verify_campaign.py"
LEDGER_PATH = PACKET / "sealed_ledger.py"
PROTOCOL = PACKET / "PROTOCOL.json"


def _load_ledger() -> Any:
    spec = importlib.util.spec_from_file_location("reusable_sealed_ledger", LEDGER_PATH)
    assert spec is not None and spec.loader is not None
    module = importlib.util.module_from_spec(spec)
    sys.modules[spec.name] = module
    spec.loader.exec_module(module)
    return module


def _run_campaign(path: Path) -> None:
    completed = subprocess.run(
        [sys.executable, str(RUNNER), "--output", str(path)],
        cwd=ROOT,
        capture_output=True,
        text=True,
        check=False,
    )
    assert completed.returncode == 0, completed.stderr + completed.stdout


def _verify(path: Path, output: Path) -> tuple[subprocess.CompletedProcess[str], dict[str, Any]]:
    completed = subprocess.run(
        [
            sys.executable,
            str(CHECKER),
            "--campaign",
            str(path),
            "--output",
            str(output),
        ],
        cwd=ROOT,
        capture_output=True,
        text=True,
        check=False,
    )
    return completed, json.loads(output.read_text())


def _events(path: Path) -> list[dict[str, Any]]:
    return [json.loads(line) for line in (path / "events.jsonl").read_text().splitlines()]


def _write_events(path: Path, events: list[dict[str, Any]]) -> None:
    (path / "events.jsonl").write_text(
        "".join(json.dumps(event, sort_keys=True, separators=(",", ":")) + "\n" for event in events)
    )


def _fresh_campaign(ledger: Any, path: Path, *, alpha: Fraction = Fraction(1, 20)) -> None:
    ledger.initialize_campaign(
        path,
        campaign_id="HOSTILE-CONTROL",
        alpha_total=alpha,
        protocol_sha256="a" * 64,
        subject_revision="b" * 40,
        candidate_generator_identity="generator",
        protected_evaluator_identity="evaluator",
        promotion_authority_identity="authority",
        archivist_identity="archivist",
    )


def _payload(
    *,
    receipt_id: str,
    raw_alpha: dict[str, int] | None = None,
    components: dict[str, bool] | None = None,
    deterministic: dict[str, bool] | None = None,
) -> dict[str, Any]:
    return {
        "receipt_id": receipt_id,
        "candidate_id": f"candidate-{receipt_id}",
        "candidate_sha256": "c" * 64,
        "subject_revision": "b" * 40,
        "epoch_id": "epoch",
        "protected_dataset_commitment": "d" * 64,
        "raw_alpha": raw_alpha or {"numerator": 1, "denominator": 1000},
        "leakage_inflation": {"numerator": 2, "denominator": 1},
        "leakage_beta": {"numerator": 0, "denominator": 1},
        "component_gates": components
        or {"fresh": True, "retention": True, "harm": True},
        "deterministic_gates": deterministic
        or {
            "resource": True,
            "custody": True,
            "authority": True,
            "candidate_bytes": True,
            "current_execution": True,
            "negative_history_retained": True,
        },
        "candidate_generator_identity": "generator",
        "protected_evaluator_identity": "evaluator",
        "promotion_authority_identity": "authority",
        "outcome_note": "hostile control",
    }


def test_conformance_campaign_is_independently_accepted(tmp_path: Path) -> None:
    campaign = tmp_path / "campaign"
    _run_campaign(campaign)
    completed, report = _verify(campaign, tmp_path / "verification.json")
    assert completed.returncode == 0, completed.stderr + completed.stdout
    assert report["decision"] == "ACCEPT_SELF_ORION_REUSABLE_SEALED_FORMAL_CONFORMANCE"
    assert all(report["checks"].values())
    assert report["decision_counts"] == {"PROMOTE": 2, "REJECT": 2, "UNRESOLVED": 2}
    assert report["protected_longitudinal_transfer_authority"] is False
    assert report["frontier_agent_performance_authority"] is False


def test_protocol_starts_without_empirical_authority() -> None:
    raw = json.loads(PROTOCOL.read_text())
    assert raw["protocol_id"] == "SELF_ORION.REUSABLE_SEALED_LONGITUDINAL.v1"
    assert all(value is False for value in raw["authority"].values())
    assert raw["registered_campaign_floor"]["ordered_revision_rounds_per_replicate"] == 6
    assert len(raw["registered_campaign_floor"]["required_arms"]) == 9


def test_identical_duplicate_is_idempotent_and_conflict_blocks(tmp_path: Path) -> None:
    ledger = _load_ledger()
    campaign = tmp_path / "campaign"
    _run_campaign(campaign)
    events = _events(campaign)
    first_payload = events[0]["payload"]
    before = len(events)
    returned = ledger.append_payload(campaign, first_payload)
    assert returned["event_digest"] == events[0]["event_digest"]
    assert len(_events(campaign)) == before

    conflicting = copy.deepcopy(first_payload)
    conflicting["outcome_note"] = "conflicting duplicate"
    conflict = ledger.append_payload(campaign, conflicting)
    assert conflict["event_type"] == "DUPLICATE_CONFLICT"
    assert conflict["decision"] == "UNRESOLVED"
    ledger.finalize_campaign(campaign)
    completed, report = _verify(campaign, tmp_path / "conflict-verification.json")
    assert completed.returncode == 1
    assert report["checks"]["no_duplicate_conflict_in_conformance"] is False


def test_missing_retention_gate_is_rejected_even_after_resigning(tmp_path: Path) -> None:
    ledger = _load_ledger()
    campaign = tmp_path / "campaign"
    _run_campaign(campaign)
    events = _events(campaign)
    events[0]["payload"]["component_gates"].pop("retention")
    events[0]["payload_digest"] = ledger.digest(events[0]["payload"])
    prior = json.loads((campaign / "CAMPAIGN.json").read_text())["initial_chain_digest"]
    for event in events:
        event["prior_digest"] = prior
        unsigned = dict(event)
        unsigned.pop("event_digest", None)
        event["event_digest"] = ledger.digest(unsigned)
        prior = event["event_digest"]
    _write_events(campaign, events)
    final = json.loads((campaign / "FINAL_RECEIPT.json").read_text())
    final["final_chain_digest"] = prior
    unsigned_final = dict(final)
    unsigned_final.pop("receipt_digest", None)
    final["receipt_digest"] = ledger.digest(unsigned_final)
    (campaign / "FINAL_RECEIPT.json").write_text(json.dumps(final, indent=2, sort_keys=True) + "\n")
    completed, report = _verify(campaign, tmp_path / "missing-retention.json")
    assert completed.returncode == 1
    assert report["checks"]["all_event_checks"] is False
    assert report["event_checks"][0]["checks"]["component_gate_shape"] is False


def test_alpha_reset_at_epoch_boundary_is_rejected(tmp_path: Path) -> None:
    ledger = _load_ledger()
    campaign = tmp_path / "campaign"
    _run_campaign(campaign)
    events = _events(campaign)
    fifth = events[4]
    fifth["cumulative_effective_debit"] = fifth["effective_debit"]
    prior = events[3]["event_digest"]
    for event in events[4:]:
        event["prior_digest"] = prior
        unsigned = dict(event)
        unsigned.pop("event_digest", None)
        event["event_digest"] = ledger.digest(unsigned)
        prior = event["event_digest"]
    _write_events(campaign, events)
    final = json.loads((campaign / "FINAL_RECEIPT.json").read_text())
    final["final_chain_digest"] = prior
    unsigned_final = dict(final)
    unsigned_final.pop("receipt_digest", None)
    final["receipt_digest"] = ledger.digest(unsigned_final)
    (campaign / "FINAL_RECEIPT.json").write_text(json.dumps(final, indent=2, sort_keys=True) + "\n")
    completed, report = _verify(campaign, tmp_path / "alpha-reset.json")
    assert completed.returncode == 1
    assert report["event_checks"][4]["checks"]["cumulative_debit"] is False


def test_deleted_negative_history_breaks_registered_conformance(tmp_path: Path) -> None:
    ledger = _load_ledger()
    campaign = tmp_path / "campaign"
    _run_campaign(campaign)
    events = _events(campaign)
    del events[1]
    prior = json.loads((campaign / "CAMPAIGN.json").read_text())["initial_chain_digest"]
    for sequence, event in enumerate(events, start=1):
        event["sequence"] = sequence
        event["prior_digest"] = prior
        unsigned = dict(event)
        unsigned.pop("event_digest", None)
        event["event_digest"] = ledger.digest(unsigned)
        prior = event["event_digest"]
    _write_events(campaign, events)
    final = ledger.finalize_campaign(campaign)
    assert final["event_count"] == 5
    completed, report = _verify(campaign, tmp_path / "deleted-history.json")
    assert completed.returncode == 1
    assert report["checks"]["conformance_decision_mix"] is False


def test_over_budget_candidate_fails_closed(tmp_path: Path) -> None:
    ledger = _load_ledger()
    campaign = tmp_path / "over-budget"
    _fresh_campaign(ledger, campaign, alpha=Fraction(1, 100))
    event = ledger.append_payload(
        campaign,
        _payload(
            receipt_id="overspend-1",
            raw_alpha={"numerator": 1, "denominator": 100},
        ),
    )
    assert event["within_global_budget"] is False
    assert event["decision"] == "UNRESOLVED"


def test_statistical_failure_with_execution_veto_is_unresolved(tmp_path: Path) -> None:
    ledger = _load_ledger()
    campaign = tmp_path / "execution-veto"
    _fresh_campaign(ledger, campaign)
    event = ledger.append_payload(
        campaign,
        _payload(
            receipt_id="execution-veto-1",
            components={"fresh": False, "retention": True, "harm": True},
            deterministic={
                "resource": True,
                "custody": True,
                "authority": True,
                "candidate_bytes": True,
                "current_execution": False,
                "negative_history_retained": True,
            },
        ),
    )
    assert event["decision"] == "UNRESOLVED"
    assert event["disposition"] == "FAIL_CLOSED_CONTROL_OR_AUTHORITY_GATE"


def test_statistical_failure_over_budget_is_unresolved(tmp_path: Path) -> None:
    ledger = _load_ledger()
    campaign = tmp_path / "statistical-overspend"
    _fresh_campaign(ledger, campaign, alpha=Fraction(1, 100))
    event = ledger.append_payload(
        campaign,
        _payload(
            receipt_id="statistical-overspend-1",
            raw_alpha={"numerator": 1, "denominator": 100},
            components={"fresh": False, "retention": True, "harm": True},
        ),
    )
    assert event["within_global_budget"] is False
    assert event["decision"] == "UNRESOLVED"


def test_negative_raw_alpha_is_rejected_without_appending(tmp_path: Path) -> None:
    ledger = _load_ledger()
    campaign = tmp_path / "negative-alpha"
    _fresh_campaign(ledger, campaign)
    with pytest.raises(ledger.LedgerError, match="raw alpha"):
        ledger.append_payload(
            campaign,
            _payload(
                receipt_id="negative-alpha-1",
                raw_alpha={"numerator": -1, "denominator": 1000},
            ),
        )
    assert _events(campaign) == []
