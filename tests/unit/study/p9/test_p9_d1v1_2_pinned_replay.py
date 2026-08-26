"""Pin the pinned-replay increment to what holds on every build, not local weather.

The divergence-root-cause test in this directory already documents the lesson:
asserting that a given environment reproduces the archived 0.5 turned the
finding into a flake, because CI executes a different binary build of the
numerical stack and lands on the other attractor. The same rule applies here.

What this file asserts instead:

* the pinned replay's CONTRACT, on whichever build runs it -- a known numeric
  canary predicts the observed attractor, while an unregistered canary fails
  closed with exit 5 instead of being classified after outcome access; the
  dataset content digest is guarded, the knife-edge band is the historical 32,
  and the attractor is one of the two known values (a third value means
  something new is going on and must fail);
* the two committed receipts R1/R2 are genuinely two clean replays: identical
  deterministic cores, honestly recomputed identical digests, per-case equality
  with the archived result on all four arms;
* the committed toggle receipt is internally consistent and the canary constants
  are duplicated identically in both executable scripts;
* the binding checker passes over the committed tree.
"""

from __future__ import annotations

import importlib.util
import json
import subprocess
import sys
from pathlib import Path

import pytest

REPO = Path(__file__).resolve().parents[4]
PAPER = REPO / "papers/paper-09-structured-epistemic-learning"
EVIDENCE = PAPER / "evidence"
TOP_TIER = PAPER / "top_tier"

ARCHIVE_MATCH_COEF = "494186ed594e077904dea4adbd75dbf8104496825e4cdf18d7e075316ecaf3de"
ARCHIVE_MATCH_INTERCEPT = "af3a6c166e56cceb9cef6caed28776cf949f022049c180051774fb5c75711d1e"
DIVERGENT_PREFIX = "9b56df6a102b9b57"


def _load_module(name: str, path: Path):
    spec = importlib.util.spec_from_file_location(name, path)
    assert spec is not None and spec.loader is not None
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


@pytest.fixture(scope="module")
def replay_process() -> subprocess.CompletedProcess[str]:
    """One pinned replay process in this test process's build (~5 s)."""
    proc = subprocess.run(
        [sys.executable, str(TOP_TIER / "replay_d1v1_2_pinned.py")],
        capture_output=True,
        text=True,
        timeout=300,
        cwd=str(REPO),
    )
    if proc.returncode == 3:
        pytest.skip("pinned replay CANNOT_CHECK in this environment")
    assert proc.returncode in (0, 5), (
        f"pinned replay exited {proc.returncode} (0=coherent, 3=cannot-check, "
        f"5=unknown-canary/third-attractor fail-closed); stderr: {proc.stderr[-2000:]}"
    )
    return proc


@pytest.fixture(scope="module")
def replay(replay_process: subprocess.CompletedProcess[str]) -> dict:
    """The complete receipt emitted for a coherent or fail-closed replay."""
    return json.loads(replay_process.stdout)


def _receipt(name: str) -> dict:
    return json.loads((EVIDENCE / name).read_text(encoding="utf-8"))


# --- the contract, on whichever build executes -------------------------------


def test_the_canary_predicts_the_attractor_on_this_build(
    replay: dict, replay_process: subprocess.CompletedProcess[str]
) -> None:
    """Require a correct known prediction or the executable's UNKNOWN stop."""
    core = replay["core"]
    assert core["observed_attractor"] in ("ARCHIVE_MATCH", "DIVERGENT_SIDE")
    if core["canary_attractor"] == "UNKNOWN":
        assert replay_process.returncode == 5
        assert replay["checks"]["canary_predicted_the_observed_attractor"] is False
        return

    assert core["canary_attractor"] in ("ARCHIVE_MATCH", "DIVERGENT_SIDE")
    assert core["canary_attractor"] == core["observed_attractor"]
    assert replay_process.returncode == 0
    assert replay["checks"]["canary_predicted_the_observed_attractor"] is True


def test_the_dataset_content_digest_is_guarded(replay: dict) -> None:
    assert (
        replay["core"]["dataset_manifest_digest"]
        == "sha256:2775298457b7bdee815b207733507cd27d55719df314ef6352bb601bd709c19c"
    )


def test_the_knife_edge_band_is_the_historical_thirty_two(replay: dict) -> None:
    assert replay["serialized_arm_summary"]["knife_edge_cases"] == 32
    band = [p for p in replay["core"]["arms"]["TYPED_SERIALIZED_BAG"]["predictions"] if p["knife_edge"]]
    assert len(band) == 32
    assert all(p["target"] == "UNRESOLVED" for p in band)


def test_the_digest_is_honest(replay: dict) -> None:
    module = _load_module("replay_d1v1_2_pinned", TOP_TIER / "replay_d1v1_2_pinned.py")
    assert module._canonical_digest(replay["core"]) == replay["result_digest"]
    # Digest stability does not depend on key insertion order.
    shuffled = {k: replay["core"][k] for k in reversed(list(replay["core"]))}
    assert module._canonical_digest(shuffled) == replay["result_digest"]


def test_attractor_classification_is_total() -> None:
    module = _load_module("replay_d1v1_2_pinned", TOP_TIER / "replay_d1v1_2_pinned.py")
    assert module._attractor_from_canary(
        {"coef_sha256": ARCHIVE_MATCH_COEF, "intercept_sha256": ARCHIVE_MATCH_INTERCEPT}
    ) == "ARCHIVE_MATCH"
    assert (
        module._attractor_from_canary({"coef_sha256": DIVERGENT_PREFIX + "0" * 48})
        == "DIVERGENT_SIDE"
    )
    assert module._attractor_from_canary({"coef_sha256": None}) == "UNKNOWN"
    assert module._attractor_from_canary({"coef_sha256": "f" * 64}) == "UNKNOWN"
    # The archive-match canary requires BOTH hashes: a mixed pair is unknown.
    assert (
        module._attractor_from_canary(
            {"coef_sha256": ARCHIVE_MATCH_COEF, "intercept_sha256": "0" * 64}
        )
        == "UNKNOWN"
    )


# --- the two committed clean replays ------------------------------------------


def test_r1_and_r2_are_two_clean_identical_replays() -> None:
    r1, r2 = _receipt("P9_D1V1_2_PINNED_REPLAY_R1_2026-08-24.json"), _receipt(
        "P9_D1V1_2_PINNED_REPLAY_R2_2026-08-24.json"
    )
    assert r1["run_id"] != r2["run_id"]
    assert r1["executed_at"] != r2["executed_at"]
    assert r1["core"] == r2["core"]
    assert r1["result_digest"] == r2["result_digest"]
    module = _load_module("replay_d1v1_2_pinned", TOP_TIER / "replay_d1v1_2_pinned.py")
    assert module._canonical_digest(r1["core"]) == r1["result_digest"]


def test_r1_matches_the_archive_per_case_on_all_four_arms() -> None:
    r1 = _receipt("P9_D1V1_2_PINNED_REPLAY_R1_2026-08-24.json")
    archived = json.loads(
        (REPO / "research/extensions/p9-structured-neural/execution/D1_EXECUTION_RESULT_V1_2.json").read_text(
            encoding="utf-8"
        )
    )
    for family_value, arm in r1["core"]["arms"].items():
        arch_pred = {
            p["instance_id"]: p["prediction"]
            for p in archived["results"][family_value]["test_predictions"]
        }
        assert len(arm["predictions"]) == len(arch_pred) == 128
        for p in arm["predictions"]:
            assert arch_pred[p["instance_id"]] == p["prediction"]
    assert r1["core"]["observed_attractor"] == "ARCHIVE_MATCH"
    assert r1["core"]["numeric_canary"]["coef_sha256"] == ARCHIVE_MATCH_COEF


# --- the committed toggle receipt ----------------------------------------------


def test_the_toggle_receipt_reproduces_both_numbers_by_one_factor() -> None:
    toggle = _receipt("P9_D1V1_2_BINARY_BUILD_TOGGLE_2026-08-24.json")
    for key, val in toggle["cross_side_invariants"].items():
        if isinstance(val, bool):
            assert val, key
    a, b, c = (
        toggle["sides"]["A_archive_matching"],
        toggle["sides"]["B_divergent"],
        toggle["sides"]["C_divergent_independent_env"],
    )
    assert {a["design_digest"], b["design_digest"], c["design_digest"]} == {
        a["design_digest"]
    }
    assert a["test_accuracy"] == 0.5 and a["flips_vs_archive"]["count"] == 0
    assert b["test_accuracy"] == 0.75 and b["flips_vs_archive"]["count"] == 32
    assert b["flips_vs_archive"]["targets"] == ["UNRESOLVED"]
    assert b["numeric_canary"] == c["numeric_canary"]
    assert a["numeric_canary"]["n_iter"] != b["numeric_canary"]["n_iter"]
    # Identical scipy + scikit-learn on every side: the versions are not the
    # deciding factor; the executing binary build is.
    assert len({s["environment"]["scipy"] for s in (a, b, c)}) == 1
    assert len({s["environment"]["scikit_learn"] for s in (a, b, c)}) == 1


def test_the_canary_constants_are_identical_in_both_scripts() -> None:
    for const in (ARCHIVE_MATCH_COEF, ARCHIVE_MATCH_INTERCEPT, DIVERGENT_PREFIX):
        assert const in (TOP_TIER / "replay_d1v1_2_pinned.py").read_text(encoding="utf-8")
        assert const in (TOP_TIER / "demonstrate_d1v1_2_build_toggle.py").read_text(
            encoding="utf-8"
        )


# --- the binding checker over the committed tree -------------------------------


def test_the_binding_checker_passes() -> None:
    proc = subprocess.run(
        [sys.executable, str(TOP_TIER / "check_d1v1_2_pinned_replay_v1.py")],
        capture_output=True,
        text=True,
        timeout=300,
        cwd=str(REPO),
    )
    if proc.returncode == 3:
        pytest.skip("binding checker CANNOT_CHECK in this environment")
    assert proc.returncode == 0, proc.stdout[-2000:] + proc.stderr[-2000:]
    report = json.loads(proc.stdout)
    assert report["status"] == "PASS"
    assert report["failures"] == []
