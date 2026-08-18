"""V1 headline facts re-derived from raw artifacts; V1 files are not rewritten."""

from __future__ import annotations

import hashlib
from pathlib import Path

from orion.study.p1_causal.protocol import V1_PROTOCOL_PATH, assert_v1_protocol_untouched
from orion.study.p1_causal.reproduce_v1 import (
    FROZEN_SUITE,
    PAPER01,
    SCORED,
    reproduce_v1,
)

EXPECTED_SCORED = "f37db6247dd1f5883e443b6d7b454e099759cb26baa3e09f74e7fd275e4d7f7b"
EXPECTED_V1_PROTOCOL = "91d5dca84d927ccb5cc5a54fece12502f23c8cba22f8eb8e5a48377539eca0b7"


def test_v1_protocol_hash_unchanged() -> None:
    assert assert_v1_protocol_untouched() == EXPECTED_V1_PROTOCOL
    assert hashlib.sha256(V1_PROTOCOL_PATH.read_bytes()).hexdigest() == EXPECTED_V1_PROTOCOL


def test_raw_scored_archive_hash() -> None:
    assert hashlib.sha256(SCORED.read_bytes()).hexdigest() == EXPECTED_SCORED


def test_independent_reproduction_matches_claimed_facts() -> None:
    receipt = reproduce_v1()
    assert receipt["verdict"] == "VERIFIED", receipt["blockers"]
    assert receipt["v1_files_mutated"] is False
    assert receipt["archive"]["n_scored_records"] == 2880
    assert receipt["archive"]["n_cases"] == 48
    assert receipt["archive"]["cannot_check_records"] == 0
    assert receipt["archive"]["suite_fingerprints"] == [FROZEN_SUITE]
    assert receipt["orion_full"]["majority_root_success_cases"] == 1
    assert receipt["orion_full"]["rate_4dp"] == 0.0208
    assert receipt["orion_full"]["abstention_cases_all_repeats"] == 47
    assert receipt["orion_full"]["abstention_trials"] == 235
    assert receipt["h1"]["point"] == 0.0
    assert receipt["h1"]["low"] == 0.0
    assert receipt["h1"]["high"] == 0.0
    assert receipt["h1"]["h_r6_majority_masks_seed_gains"] is False
    live = receipt["orion_live_provider"]
    assert live["failure_mode_cases"]["MISSED_REFRAME"] == 32
    assert live["failure_modes"]["MISSED_REFRAME"] == 160
    assert live["failure_mode_cases"]["WRONG_RESPONSIBILITY"] == 16
    assert live["failure_modes"]["WRONG_RESPONSIBILITY"] == 80
    assert receipt["power"]["underpowered"] is True
    assert receipt["power"]["licenses_h1_superiority"] is False
    assert receipt["comparator"]["majority_root_success_cases"] == 1


def test_reproduction_does_not_create_v1_result_sidecars() -> None:
    results = PAPER01 / "results"
    before = {path.name for path in results.iterdir()}
    reproduce_v1()
    after = {path.name for path in results.iterdir()}
    assert after == before
    assert not Path(results / "V1_REPRODUCTION_RECEIPT.json").exists()
