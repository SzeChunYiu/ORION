#!/usr/bin/env python3
"""MAX-R6R prospective fresh-subject prediction experiment.

Frozen by MAX_R6R_PROSPECTIVE_FRESH_SUBJECT_PROTOCOL.md (frozen BEFORE any
coefficient of any non-committed DUCC library file was read).

Capstone form: prediction before computation. Stage 1 deterministically selects
a never-before-read subject from the pinned public DUCC Hamiltonian library,
builds the frozen R6B six-term batch, evaluates the committed R6Q predicate
P(t) := [C_R6L == C_Dplus] AND [f_B >= C_R6L] together with the two-trade
completeness prediction C_DP == min(C_R6L, C_Dplus, f_B) on all 15 matchings,
and prints the prediction with a digest. Only then does stage 2 run the
unrestricted frozen R6M DP referee and compare, matching by matching.

Honest outcome space: PREDICTION_CONFIRMED / PREDICTION_REFUTED /
FRESH_SUBJECT_UNAVAILABLE. Not R6; no novelty credit; the protected
stretched-N2 discriminator is never read (the N2 molecule is excluded from
candidacy entirely). All frozen machinery is imported unmodified.
"""
from __future__ import annotations

import hashlib
import json
import os
import re
import shutil
import subprocess
import sys
import tempfile
import time
from pathlib import Path
from typing import Any

import numpy as np

sys.path.insert(0, str(Path(__file__).resolve().parent))

import max_r6_p10_candidate_blind_frame_optimizer as p10  # noqa: E402
import max_r6f_donor_clifford_preconditioned_tare3 as r6f  # noqa: E402
import max_r6m_exact_three_tare2_shared_factor_dp as r6m  # noqa: E402
import max_r6o_enlarged_tag_donor_closure as r6o  # noqa: E402
import max_r6q_regime_predicate as r6q  # noqa: E402

REPO = "npbauman/DUCC-Hamiltonian-Library"
CLONE_URL = f"https://github.com/{REPO}"
PINNED_COMMIT = "be306f5830549304176365750d712093950bbdde"
EXCLUDED_MOLECULES = ("H2", "H2O", "H4", "LiH", "N2")
COMMITTED_SUBJECT_BLOBS = (
    "b98792b1055dbac0ebf2a7576f72412e3e4ac6c5",  # H4 cc-pVDZ 2.0au DUCC3
    "15369e8e886efbb3d32f3b2dfe2cfbb96ddebeba",  # N2 equilibrium DUCC2
    "5f157e7bd05aac26b30b10dcea44b7650b7f8648",  # H2O Eq cc-pVTZ
)
PROTECTED_STRETCHED_N2_PATH = (
    "N2/cc-pVTZ/6Elec_6Orbs/1.5_Eq-3.1020au/DUCC2/N2.cc-pvtz.ducc.results.txt"
)
ACTIVE_SPACE_RE = re.compile(r"^(?:FrozenCoreCCSD_)?(\d+)Elec_(\d+)Orbs$")
CANDIDATE_CAP = 6
INF = r6q.INF
PROTOCOL_NAME = "MAX_R6R_PROSPECTIVE_FRESH_SUBJECT_PROTOCOL.md"

_STAGE1_EMITTED = False


def canonical_json(value: Any) -> str:
    return json.dumps(value, sort_keys=True, separators=(",", ":"), allow_nan=False)


def sha256_text(text: str) -> str:
    return hashlib.sha256(text.encode()).hexdigest()


# ---- pinned tree enumeration (paths + git blob ids only; no coefficients) ----

def _git(args, cwd=None) -> str:
    out = subprocess.run(
        ["git", *args],
        cwd=cwd,
        check=True,
        capture_output=True,
        text=True,
        timeout=540,
    )
    return out.stdout


def pinned_tree_listing() -> list[tuple[str, str]]:
    """[(path, blob_sha1)] of every blob at the pinned commit, path-sorted."""
    root = Path(os.environ.get("ORIONQ_R6R_CACHE") or tempfile.gettempdir())
    clone = root / "orionq_r6r_ducc_tree"
    usable = False
    if clone.is_dir():
        try:
            usable = (
                _git(["cat-file", "-t", PINNED_COMMIT], cwd=clone).strip() == "commit"
            )
        except (subprocess.SubprocessError, OSError):
            usable = False
    if not usable:
        if clone.exists():
            shutil.rmtree(clone)
        clone.parent.mkdir(parents=True, exist_ok=True)
        _git(
            [
                "clone",
                "--quiet",
                "--filter=blob:none",
                "--no-checkout",
                CLONE_URL,
                str(clone),
            ]
        )
        if _git(["cat-file", "-t", PINNED_COMMIT], cwd=clone).strip() != "commit":
            raise AssertionError({"r6r_pinned_commit_unreachable": PINNED_COMMIT})
    rows = []
    for line in _git(
        ["ls-tree", "-r", "--full-tree", PINNED_COMMIT], cwd=clone
    ).splitlines():
        meta, path = line.split("\t", 1)
        _mode, otype, sha1 = meta.split()
        if otype == "blob":
            rows.append((path, sha1))
    rows.sort()
    if not rows:
        raise AssertionError("r6r pinned tree listing is empty")
    return rows


# ---- frozen eligibility + candidate order -----------------------------------

def parse_candidate(path: str, blob: str):
    if not path.endswith(".ducc.results.txt"):
        return None
    parts = path.split("/")
    if parts[0] in EXCLUDED_MOLECULES:
        return None
    if not any(seg in ("DUCC2", "DUCC3") for seg in parts):
        return None
    space = None
    for seg in parts:
        m = ACTIVE_SPACE_RE.match(seg)
        if m:
            space = (int(m.group(1)), int(m.group(2)))
            break
    if space is None:
        return None
    elec, orbs = space
    if elec % 2 != 0:
        return None
    n_occ = elec // 2
    if not (1 <= n_occ < orbs):
        return None
    return {
        "commit": PINNED_COMMIT,
        "blob": blob,
        "path": path,
        "n_occ": n_occ,
        "n_virt": orbs - n_occ,
        "n_orb": orbs,
        "n_qubits": 2 * orbs,
    }


def eligible_candidates(listing) -> list[dict[str, Any]]:
    cands = [c for c in (parse_candidate(p, b) for p, b in listing) if c is not None]
    cands.sort(key=lambda c: (c["n_qubits"], c["path"]))
    return cands


# ---- frozen batch admission (R6B rules, as enforced by the R6M lane) --------

def try_admit(cfg) -> dict[str, Any]:
    try:
        terms, source_indices, champions, max_imag, observed_blob = r6f._frozen_batch(
            cfg
        )
    except (AssertionError, RuntimeError) as exc:
        return {"admitted": False, "reason": f"frozen_batch_failed: {exc!r:.300}"}
    if observed_blob != cfg["blob"]:
        return {"admitted": False, "reason": "blob_mismatch"}
    if len(source_indices) != 6:
        return {
            "admitted": False,
            "reason": "fewer_than_two_window_champions",
            "window_champions_available": len(champions),
        }
    six = [int(i) for i in source_indices]
    six_targets = [terms[i][0] for i in six]
    if not all(
        p10.symp(six_targets[i], six_targets[j]) == 0
        for i in range(6)
        for j in range(i + 1, 6)
    ):
        return {"admitted": False, "reason": "six_targets_not_pairwise_commuting"}
    return {
        "admitted": True,
        "terms": terms,
        "six": six,
        "champion_windows": [int(c["window_start"]) for c in champions[:2]],
        "window_champions_available": len(champions),
        "max_imag": float(max_imag),
    }


# ---- stage 1: prediction before computation ---------------------------------

def stage1_predict(terms, six, n: int) -> tuple[list[Any], list[dict[str, Any]]]:
    matchings = r6m.perfect_matchings(six)
    rows = []
    for pairs in matchings:
        r6m._local_table.cache_clear()
        c_r6l = int(r6m.donor_r6l_matching(terms, pairs, n, six)["C_R6L"])
        target_pairs = tuple((terms[i][0], terms[j][0]) for i, j in pairs)
        c_dplus = int(r6o.dplus_pairs(target_pairs, n)["C_Dplus"])
        if not c_dplus <= c_r6l:
            raise AssertionError({"r6r_dplus_r6l_order_violated": [c_dplus, c_r6l]})
        f_b = r6q.borrow_family_min(target_pairs, n)
        f_b_eff = INF if f_b is None else int(f_b)
        feats = r6q.simple_features(target_pairs, n)
        predicate_p1 = (c_dplus == c_r6l) and (f_b_eff >= c_r6l)
        predicted_c_dp = min(c_r6l, c_dplus, f_b_eff)
        predicted_donor_exact = predicted_c_dp == c_r6l
        if predicted_donor_exact != predicate_p1:
            raise AssertionError({"r6r_predicate_identity_violated": pairs})
        if predicted_c_dp == c_r6l:
            predicted_regime = "donor_exact"
        elif predicted_c_dp == c_dplus:
            predicted_regime = "split"
        else:
            predicted_regime = "borrow"
        rows.append(
            {
                "matching": [list(p) for p in pairs],
                "C_R6L": c_r6l,
                "C_Dplus": c_dplus,
                "f_B": f_b_eff,
                "Gsplit": c_r6l - c_dplus,
                "predicate_P1": predicate_p1,
                "predicted_donor_exact": predicted_donor_exact,
                "predicted_C_DP": int(predicted_c_dp),
                "predicted_regime": predicted_regime,
                **feats,
            }
        )
        r6q._borrow_block_cache.clear()
    r6o._block_cache.clear()
    return matchings, rows


def emit_stage1(payload: dict[str, Any]) -> str:
    global _STAGE1_EMITTED
    blob = canonical_json(payload)
    digest = sha256_text(blob)
    print("ORIONQ_MAX_R6R_STAGE1_PREDICTION=" + blob)
    print("ORIONQ_MAX_R6R_STAGE1_DIGEST=" + digest)
    sys.stdout.flush()
    _STAGE1_EMITTED = True
    return digest


# ---- stage 2: unrestricted DP referee ---------------------------------------

def stage2_referee(terms, six, n: int, matchings, predictions) -> list[dict[str, Any]]:
    rows = []
    for pairs, pred in zip(matchings, predictions, strict=True):
        if not _STAGE1_EMITTED:
            raise AssertionError("r6r staging violated: referee before prediction")
        r6m._local_table.cache_clear()
        wit = r6m.exact_r6m_matching(terms, pairs, n, six)
        if not all(wit["checks"].values()):
            raise AssertionError({"r6r_dp_witness_failed": [list(p) for p in pairs]})
        c_dp = int(wit["C_R6M"])
        c_dplus = int(pred["C_Dplus"])
        c_r6l = int(pred["C_R6L"])
        f_b_eff = int(pred["f_B"])
        if not (c_dp <= c_dplus <= c_r6l):
            raise AssertionError(
                {"r6r_sandwich_violated": [c_dp, c_dplus, c_r6l]}
            )
        if c_dp > f_b_eff:
            raise AssertionError({"r6r_borrow_soundness_violated": [c_dp, f_b_eff]})
        truth_donor_exact = c_dp == c_r6l
        if truth_donor_exact:
            truth_regime = "donor_exact"
        elif c_dp == c_dplus:
            truth_regime = "split"
        else:
            truth_regime = "borrow"
        pinched = c_dp == c_dplus
        rows.append(
            {
                "matching": pred["matching"],
                "C_DP": c_dp,
                "truth_donor_exact": truth_donor_exact,
                "truth_regime": truth_regime,
                "C_Dxx_pinched": c_dp if pinched else None,
                "dxx_pinched_equal": pinched,
                "dp_witness_checks_pass": True,
                "cost_match": c_dp == int(pred["predicted_C_DP"]),
                "regime_match": truth_regime == pred["predicted_regime"],
            }
        )
    return rows


# ---- receipt ----------------------------------------------------------------

CLAIM_BOUNDARY = {
    "covers": (
        "One prospective test of the committed R6Q predicate P1 and the "
        "two-trade completeness identity C_DP == min(C_R6L, C_Dplus, f_B) on "
        "the 15 frozen-grammar matchings of the frozen R6B six-term batch of "
        "a single deterministically selected, never previously read subject "
        "from the pinned public DUCC Hamiltonian library, with the prediction "
        "recorded and digest-printed before the unrestricted R6M DP referee "
        "was run."
    ),
    "machine_evidenced_only": (
        "Any confirmation is machine-evidenced only on this one subject's 15 "
        "matchings, in addition to the domains already recorded in the R6Q "
        "receipt. It is NOT a theorem for all n or all targets; the D++ value "
        "is recorded only via the exact containment pinch where C_DP == "
        "C_Dplus, exactly as the committed R6P chemistry lane."
    ),
    "does_not_cover": (
        "Other objectives, other grammars, rotation-count trade-offs, other "
        "batches or subjects, or any claim of donor or R6 novelty credit. A "
        "refutation claims exactly the mismatches reported verbatim."
    ),
}


def main() -> dict[str, Any]:
    start = time.monotonic()

    f3_binding = bool(np.array_equal(r6q.F3.astype(np.int64), r6m._F3))
    if not f3_binding:
        raise AssertionError("r6r F3 table binding to frozen r6m._F3 failed")

    protocol_path = (
        Path(__file__).resolve().parents[3]
        / "development"
        / "orion-q-max-r0"
        / PROTOCOL_NAME
    )
    protocol_sha = sha256_text(protocol_path.read_text())

    listing = pinned_tree_listing()
    ducc_listing = [(p, b) for p, b in listing if p.endswith(".ducc.results.txt")]
    listing_digest = sha256_text(
        "\n".join(f"{b} {p}" for p, b in ducc_listing) + "\n"
    )
    if any(p.split("/")[0] == "N2" for p, _ in ducc_listing):
        stretched_present = any(
            p == PROTECTED_STRETCHED_N2_PATH for p, _ in ducc_listing
        )
    else:
        stretched_present = False

    candidates = eligible_candidates(listing)
    attempts = []
    selected = None
    admitted = None
    for cfg in candidates[:CANDIDATE_CAP]:
        if cfg["path"].split("/")[0] in EXCLUDED_MOLECULES:
            raise AssertionError("r6r exclusion breached in candidate order")
        result = try_admit(cfg)
        attempts.append(
            {
                "path": cfg["path"],
                "blob": cfg["blob"],
                "n_qubits": cfg["n_qubits"],
                "admitted": result["admitted"],
                "reason": None if result["admitted"] else result["reason"],
            }
        )
        if result["admitted"]:
            selected = cfg
            admitted = result
            break

    base_receipt = {
        "schema": "ORIONQ.MAXR6R.ProspectiveFreshSubject.v1",
        "scope": (
            "PROSPECTIVE_FRESH_SUBJECT_PREDICTION_BEFORE_COMPUTATION_OVER_"
            "FROZEN_R6M_GRAMMAR__NOT_R6"
        ),
        "protocol": "MAX_R6R_PROSPECTIVE_FRESH_SUBJECT_PROTOCOL",
        "protocol_sha256": protocol_sha,
        "library": {
            "repo": REPO,
            "commit": PINNED_COMMIT,
            "ducc_results_files_at_commit": len(ducc_listing),
            "ducc_listing_sha256": listing_digest,
            "protected_stretched_n2_present_in_tree": stretched_present,
        },
        "selection_rule": {
            "excluded_molecules": list(EXCLUDED_MOLECULES),
            "requires_ducc2_or_ducc3_segment": True,
            "requires_explicit_active_space_segment": True,
            "order": "n_qubits_ascending_then_path_ascending",
            "candidate_cap": CANDIDATE_CAP,
            "eligible_candidate_count": len(candidates),
            "eligible_candidates_in_order": [
                {"path": c["path"], "blob": c["blob"], "n_qubits": c["n_qubits"]}
                for c in candidates
            ],
        },
        "admission_attempts": attempts,
        "claim_boundary": CLAIM_BOUNDARY,
        "donor_novelty_credit": False,
        "novelty_credit": False,
        "r6_authority": False,
        "reserved_stretched_n2_accessed": False,
    }

    if selected is None:
        result = {
            **base_receipt,
            "authority": "MAX_R6R_PROSPECTIVE_FRESH_SUBJECT_UNAVAILABLE__NOT_R6",
            "responsibility": (
                "RESP:FROZEN_SELECTION_RULE_EXHAUSTED_WITHOUT_ADMISSIBLE_SUBJECT__"
                "RULE_NOT_WEAKENED"
            ),
            "outcome": "FRESH_SUBJECT_UNAVAILABLE",
            "subject": None,
            "gates": {
                "f3_table_binding_exact": f3_binding,
                "protocol_frozen_and_hashed": True,
                "pinned_commit_and_blobs": True,
                "no_excluded_molecule_fetched": True,
                "reserved_stretched_n2_unread": True,
            },
        }
        finish(result, start)
        return result

    n = int(selected["n_qubits"])
    terms = admitted["terms"]
    six = admitted["six"]

    matchings, pred_rows = stage1_predict(terms, six, n)
    stage1_payload = {
        "protocol": "MAX_R6R_PROSPECTIVE_FRESH_SUBJECT_PROTOCOL",
        "protocol_sha256": protocol_sha,
        "subject": {
            "path": selected["path"],
            "commit": PINNED_COMMIT,
            "blob": selected["blob"],
            "n_qubits": n,
            "n_occ": selected["n_occ"],
            "n_virt": selected["n_virt"],
            "n_orb": selected["n_orb"],
            "terms": len(terms),
            "max_imag": admitted["max_imag"],
            "frozen_source_indices": six,
            "champion_windows": admitted["champion_windows"],
            "window_champions_available": admitted["window_champions_available"],
        },
        "predicate": (
            "P1(t) := [C_R6L(t) == C_Dplus(t)] AND [f_B(t) >= C_R6L(t)]; "
            "predicted_C_DP := min(C_R6L, C_Dplus, f_B)"
        ),
        "matchings": pred_rows,
        "predicted_donor_exact_count": sum(
            r["predicted_donor_exact"] for r in pred_rows
        ),
    }
    stage1_digest = emit_stage1(stage1_payload)

    truth_rows = stage2_referee(terms, six, n, matchings, pred_rows)

    merged = [
        {**pred, **truth}
        for pred, truth in zip(pred_rows, truth_rows, strict=True)
    ]
    mismatches = [
        row for row in merged if not (row["cost_match"] and row["regime_match"])
    ]
    all_match = not mismatches
    confirmed = all_match

    gates = {
        "f3_table_binding_exact": f3_binding,
        "protocol_frozen_and_hashed": True,
        "pinned_commit_and_blobs": True,
        "subject_blob_verified": True,  # hard-asserted inside r6f._frozen_batch
        "subject_molecule_outside_exclusion_list": selected["path"].split("/")[0]
        not in EXCLUDED_MOLECULES,
        "subject_blob_not_any_committed_subject_blob": selected["blob"]
        not in COMMITTED_SUBJECT_BLOBS,
        "six_term_batch_rules_identical_to_r6b": True,
        "six_targets_pairwise_commuting": True,  # admission-asserted
        "stage1_digest_printed_before_ground_truth": _STAGE1_EMITTED,
        "sandwich_and_borrow_soundness_all_matchings": True,  # hard-asserted
        "dp_witness_checks_all_matchings": all(
            row["dp_witness_checks_pass"] for row in truth_rows
        ),
        "prediction_matches_ground_truth_every_matching": all_match,
        "reserved_stretched_n2_unread": True,
        "no_excluded_molecule_fetched": all(
            a["path"].split("/")[0] not in EXCLUDED_MOLECULES for a in attempts
        ),
    }

    if confirmed:
        authority = (
            "MAX_R6R_PROSPECTIVE_FRESH_SUBJECT_PREDICTION_CONFIRMED__"
            "TWO_TRADE_PREDICATE_HELD_ON_UNSEEN_SUBJECT__NOT_R6"
        )
        responsibility = (
            "RESP:REGIME_AND_EXACT_DP_COST_PREDICTED_BEFORE_COMPUTATION_ON_"
            "ALL_15_MATCHINGS_OF_A_FRESH_SUBJECT"
        )
        outcome = "PREDICTION_CONFIRMED"
    else:
        authority = (
            "MAX_R6R_PROSPECTIVE_FRESH_SUBJECT_PREDICTION_REFUTED__"
            "PREDICATE_DOMAIN_BOUNDARY_LOCALIZED__NOT_R6"
        )
        responsibility = (
            "RESP:MISMATCHING_MATCHINGS_REPORTED_VERBATIM__"
            "VERIFIED_DOMAIN_BOUNDARY_LOCALIZED"
        )
        outcome = "PREDICTION_REFUTED"

    result = {
        **base_receipt,
        "authority": authority,
        "responsibility": responsibility,
        "outcome": outcome,
        "subject": stage1_payload["subject"],
        "stage1_digest": stage1_digest,
        "stage1_predicted_donor_exact_count": stage1_payload[
            "predicted_donor_exact_count"
        ],
        "matchings": merged,
        "matching_count": len(merged),
        "match_count": sum(
            1 for row in merged if row["cost_match"] and row["regime_match"]
        ),
        "mismatches_verbatim": mismatches,
        "truth_donor_exact_count": sum(r["truth_donor_exact"] for r in merged),
        "dxx_direct_sweep_run": False,
        "dxx_obtained_by_exact_containment_pinch_where_applicable": True,
        "gates": gates,
    }
    if "NOT_R6" not in result["authority"]:
        raise AssertionError("R6R authority ceiling violated")
    finish(result, start)
    return result


def finish(result: dict[str, Any], start: float) -> None:
    Path(__file__).with_name(
        "MAX_R6R_PROSPECTIVE_FRESH_SUBJECT_RESULTS.json"
    ).write_text(json.dumps(result, indent=2, sort_keys=True) + "\n")
    print("ORIONQ_MAX_R6R_PROSPECTIVE_FRESH_SUBJECT=" + canonical_json(result))
    print(
        "r6r_runtime_seconds=%.3f" % (time.monotonic() - start),
        file=sys.stderr,
    )


if __name__ == "__main__":
    main()
