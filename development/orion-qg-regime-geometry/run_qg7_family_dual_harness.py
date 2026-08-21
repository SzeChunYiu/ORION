#!/usr/bin/env python3
"""Dual-instrument custody for the QG-7 classification ladder.

The QG-7 family (QG-7 -> QG-7b -> QG-7c -> QG-7d) carries the programme's
TARE support-<=2 classification result, but until now its receipts had only
single-instrument custody: they were produced by direct script execution.
This runner closes that gap the way lanes QG-3/6/8/9/12/13/16/17 already do.

Lane A (generic ORION research harness)
    For every QG-7-family receipt that exists, a *content-bound* PYTHON
    capability is serviced through ``ResearchWorkspace`` +
    ``service_local_request``.  Each request payload names exactly one
    receipt path, its expected schema and the stdout token prefix, so the
    immutable request digest binds which receipt was re-read and how.  The
    subprocess re-derives that receipt's own ``result_digest`` from its
    canonical body and re-reports its terminal, authority, gate booleans and
    chain bindings.  Lane A then decides on the ladder using its own rule,
    written out longhand below and deliberately *not* shared with Lane B.

Lane B (native ORION-Q typed campaign layer)
    The campaign state is built from the Lane-A stdout tokens only -- the
    analyzers' in-process values are never consulted -- mapped onto campaign
    observations by the manifest's own ``derive_observations`` and handed to
    ``decide_campaign`` against
    ``QG7_CLASSIFICATION_CAMPAIGN_MANIFEST``.

The two lanes are then compared.  AGREE, PARTIAL and DISAGREE are all valid
outcomes; divergence is data, not a defect to be tuned away.  A missing
QG-7d receipt is not an error: the ladder is simply not yet four rungs long.

Nothing in this lane reads any chemistry subject.  The protected stretched-N2
reference is declared and never released.  NOT_R6, non-authorizing.
"""
from __future__ import annotations

import json
import shutil
import sys
from pathlib import Path
from typing import Any

from orion_research_harness import corroboration
from orion_research_harness.campaign_control import (
    decide_campaign,
    manifest_digest,
    validate_manifest,
)
from orion_research_harness.campaign_protocol import CampaignState, ProtectedReference
from orion_research_harness.domains.orion_qg import QG7_CLASSIFICATION_CAMPAIGN_MANIFEST
from orion_research_harness.domains.orion_qg.qg7_classification import (
    QG7_DECISION_BY_HYPOTHESIS,
    QG7_LADDER_RUNGS,
    QG7_RUNG_TOKEN_PREFIX,
    derive_observations,
    rung_probe_code,
)
from orion_research_harness.local_tools import service_local_request
from orion_research_harness.workspace import ResearchWorkspace

ROOT = Path(__file__).resolve().parents[2]
ARTIFACTS = ROOT / "artifacts"
DUAL = ARTIFACTS / "orion-qg-qg7-family-dual-admission.json"
LANE_A_WS = ROOT / ".orion-qg-qg7-family-generic"
TOKEN_PREFIX = "ORIONQG_QG7_FAMILY_DUAL="

# Terminal vocabulary, restated here so Lane A does not borrow Lane B's.
A_POSITIVE = "QG7_FOURTH_SUPPORT2_REGIME_FOUND"
B_POSITIVE = "QG7B_HYBRID_FAMILY_CLOSES_ON_VERIFIED_DOMAINS"
C_THEOREM = "QG7C_FOUR_CONFIGURATION_CLASSIFICATION_ALL_N_MACHINE_CHECKED"
C_PARTIAL = "QG7C_PARTIAL__"
D_THEOREM = "QG7D_ALL_N_CLASSIFICATION_THEOREM_COMPLETE"
D_PARTIAL = "QG7D_PARTIAL__"
SECTOR_CLOSED_MARK = "COMM_S2_PINNED_SECTOR_CLOSED"
SECTOR_OPEN_MARK = "COMM_S2_PINNED_SECTOR_OPEN"

ACCEPT_CHAIN = "ACCEPT_CLASSIFICATION_CHAIN"
ACCEPT_PARTIAL = "ACCEPT_PARTIAL_CHAIN"
REJECT = "REJECT_OR_CANNOT_CHECK"


def canonical(value: Any) -> str:
    return json.dumps(value, sort_keys=True, separators=(",", ":"), allow_nan=False)


def token_of(stdout: str, prefix: str) -> dict[str, Any]:
    rows = [line for line in stdout.splitlines() if line.startswith(prefix)]
    if len(rows) != 1:
        raise ValueError(f"expected exactly one {prefix} token, got {len(rows)}")
    parsed = json.loads(rows[0][len(prefix):])
    if not isinstance(parsed, dict):
        raise TypeError("rung token must be a JSON object")
    return parsed


def run_capability(ws: ResearchWorkspace, code: str, timeout: int = 120):
    """Service one content-bound PYTHON request and keep both receipts."""
    request = ws.get_or_create_request(
        capability="PYTHON", payload={"code": code, "cwd": ".", "timeout": timeout}
    )
    result = service_local_request(ws, request.request_id)
    if not result.success:
        raise RuntimeError(f"QG-7 family capability failed: {result.error}")
    if not isinstance(result.output, dict) or result.output.get("returncode") != 0:
        raise RuntimeError(f"QG-7 family process did not exit cleanly: {result.output}")
    if result.output.get("sandboxed") is not False:
        raise RuntimeError("QG-7 family process receipt must retain sandboxed=false")
    return request, result


# ---------------------------------------------------------------------------
# Lane A's own ladder rule.  Independent restatement over serialized tokens.
# ---------------------------------------------------------------------------


def lane_a_rung_sound(token: dict[str, Any]) -> tuple[bool, list[str]]:
    """Integrity of a single serialized rung token."""
    faults: list[str] = []
    if not token.get("schema_matches"):
        faults.append("SCHEMA_MISMATCH")
    if not token.get("result_digest_rebinds"):
        faults.append("RESULT_DIGEST_DOES_NOT_REBIND")
    if not token.get("gates_all_true"):
        faults.append("GATE_FALSE_OR_ABSENT")
    if not token.get("authority_not_r6"):
        faults.append("AUTHORITY_CEILING_MISSING_NOT_R6")
    if not token.get("r6_authority_false"):
        faults.append("R6_AUTHORITY_NOT_FALSE")
    if not token.get("novelty_credit_false"):
        faults.append("NOVELTY_CREDIT_NOT_FALSE")
    if not token.get("physical_advantage_false"):
        faults.append("PHYSICAL_ADVANTAGE_CLAIMED")
    if not token.get("protected_unread"):
        faults.append("PROTECTED_OR_CHEMISTRY_SUBJECT_TOUCHED")
    if not token.get("r6s_receipt_bound"):
        faults.append("R6S_ANCHOR_UNBOUND")
    return (not faults), faults


def lane_a_decide(tokens: dict[str, dict[str, Any]]) -> dict[str, Any]:
    """Decide the ladder from Lane-A's serialized evidence alone."""
    faults: list[str] = []
    live = {k: t for k, t in tokens.items() if t.get("present")}

    for key in ("A", "B", "C"):
        if key not in live:
            faults.append(f"CORE_RUNG_{key}_RECEIPT_ABSENT")
    for key, token in sorted(live.items()):
        ok, rung_faults = lane_a_rung_sound(token)
        if not ok:
            faults.extend(f"RUNG_{key}:{fault}" for fault in rung_faults)

    a, b, c, d = (live.get(k) for k in ("A", "B", "C", "D"))

    # Chain links, each re-checked against the *other* receipt's own values.
    if a and b:
        binds = b["binds"]
        if not (
            binds.get("qg7_receipt_bound") is True
            and binds.get("qg7_authority") == a.get("authority")
            and binds.get("qg7_protocol_sha256_recomputed") == a.get("protocol_sha256")
        ):
            faults.append("LINK_B_TO_A_UNBOUND")
    if b and c:
        binds = c["binds"]
        if not (
            binds.get("qg7_receipt_bound") is True
            and binds.get("qg7b_receipt_bound") is True
            and binds.get("qg7b_result_digest") == b.get("result_digest_declared")
            and binds.get("qg7b_terminal") == b.get("terminal")
        ):
            faults.append("LINK_C_TO_B_UNBOUND")
    if c and d:
        binds = d["binds"]
        if not (
            binds.get("qg7_receipt_bound") is True
            and binds.get("qg7b_receipt_bound") is True
            and binds.get("qg7c_receipt_bound") is True
            and binds.get("qg7c_result_digest") == c.get("result_digest_declared")
            and binds.get("qg7b_result_digest") == (b or {}).get("result_digest_declared")
        ):
            faults.append("LINK_D_TO_C_UNBOUND")

    # Terminals.
    if a and a.get("terminal") != A_POSITIVE:
        faults.append("RUNG_A_TERMINAL_NOT_FOURTH_REGIME")
    if b and b.get("terminal") != B_POSITIVE:
        faults.append("RUNG_B_TERMINAL_NOT_FAMILY_CLOSURE")
    c_terminal = str((c or {}).get("terminal") or "")
    if c and not (c_terminal == C_THEOREM or c_terminal.startswith(C_PARTIAL)):
        faults.append("RUNG_C_TERMINAL_REFUTED_OR_CANNOT_CHECK")
    d_terminal = str((d or {}).get("terminal") or "")
    if d and not (d_terminal == D_THEOREM or d_terminal.startswith(D_PARTIAL)):
        faults.append("RUNG_D_TERMINAL_REFUTED_OR_CANNOT_CHECK")

    # Where the comm-s2 pinned sector stands.
    if d:
        d_authority = str(d.get("authority") or "")
        if d_terminal == D_THEOREM and SECTOR_CLOSED_MARK in d_authority:
            sector = "CLOSED"
        elif d_terminal.startswith(D_PARTIAL):
            sector = "OPEN"
        else:
            sector = "INDETERMINATE"
    elif c and c_terminal.startswith(C_PARTIAL) and SECTOR_OPEN_MARK in str(
        c.get("authority") or ""
    ):
        sector = "OPEN"
    else:
        sector = "INDETERMINATE"

    if faults:
        decision = REJECT
    elif len(live) == 4 and sector == "CLOSED":
        decision = ACCEPT_CHAIN
    elif sector == "OPEN":
        decision = ACCEPT_PARTIAL
    else:
        decision = REJECT
        faults.append("COMM_S2_SECTOR_INDETERMINATE")

    return {
        "decision": decision,
        "comm_s2_pinned_sector": sector,
        "rungs_present": sorted(live),
        "rungs_absent": sorted(set(tokens) - set(live)),
        "faults": sorted(set(faults)),
        "rung_terminals": {k: t.get("terminal") for k, t in sorted(live.items())},
    }


# ---------------------------------------------------------------------------


def agreement_verdict(lane_a: str, lane_b: str | None) -> str:
    if lane_b is None:
        return "PARTIAL"
    return "AGREE" if lane_a == lane_b else "DISAGREE"


def main() -> int:
    if LANE_A_WS.exists():
        shutil.rmtree(LANE_A_WS)
    DUAL.unlink(missing_ok=True)
    ARTIFACTS.mkdir(parents=True, exist_ok=True)

    # ---- Lane A -----------------------------------------------------------
    workspace = ResearchWorkspace.initialize(
        LANE_A_WS, project_root=ROOT, allow_process_tools=True
    )
    tokens: dict[str, dict[str, Any]] = {}
    lane_a_receipts: list[dict[str, Any]] = []
    for row in QG7_LADDER_RUNGS:
        rung = row["rung"]
        code = rung_probe_code(rung)
        request, result = run_capability(workspace, code)
        token = token_of(str(result.output.get("stdout", "")), QG7_RUNG_TOKEN_PREFIX)
        if token.get("rung") != rung or token.get("receipt_path") != row["receipt_path"]:
            raise ValueError(f"rung token does not bind its own request: {rung}")
        tokens[rung] = token
        lane_a_receipts.append(
            {
                "rung": rung,
                "lane": row["lane"],
                "receipt_path": row["receipt_path"],
                "receipt_present": bool(token.get("present")),
                "receipt_result_digest_declared": token.get("result_digest_declared"),
                "receipt_result_digest_rederived": token.get("result_digest_rederived"),
                "receipt_result_digest_rebinds": token.get("result_digest_rebinds"),
                "terminal": token.get("terminal"),
                "authority": token.get("authority"),
                "probe_request": request.as_dict(),
                "probe_result": result.as_dict(),
                "probe_token": token,
            }
        )

    lane_a = lane_a_decide(tokens)

    # ---- Lane B -----------------------------------------------------------
    manifest = QG7_CLASSIFICATION_CAMPAIGN_MANIFEST
    validate_manifest(manifest)
    if "NOT_R6" not in str(manifest["authority_ceiling"]):
        raise AssertionError("QG-7 ladder manifest authority ceiling must carry NOT_R6")

    # Observations come from the serialized Lane-A tokens and nothing else.
    observations = derive_observations({k: dict(v) for k, v in tokens.items()})
    state = CampaignState.create(
        campaign_id=manifest["campaign_id"],
        claim_id=manifest["claim_id"],
        phase_id="D0",
        cycle_index=1,
        manifest_digest=manifest_digest(manifest),
        observations=observations,
        active_hard_obligations=(),
        protected_refs=tuple(
            ProtectedReference.from_dict(item) for item in manifest["protected_refs"]
        ),
        authority_ceiling=manifest["authority_ceiling"],
    )
    decision = decide_campaign(state, manifest)
    identified = decision.responsibility.get("identified_hypothesis_id")
    lane_b_decision = QG7_DECISION_BY_HYPOTHESIS.get(identified) if identified else None

    verdict = agreement_verdict(lane_a["decision"], lane_b_decision)

    dual = {
        "schema": "ORION.QG.QG7Family.DualAdmission.v2",
        "programme": "ORION-QG (charter PROGRAMME_CHARTER_V1.md, issue #740)",
        "ladder": "QG-7 -> QG-7b -> QG-7c -> QG-7d (TARE support-<=2 classification)",
        "agreement": verdict,
        # Both lanes here re-derive each receipt's DECLARED digest and compare
        # terminals. That establishes the artifacts are intact and mutually
        # consistent -- it cannot establish that the computations inside were
        # correct. On 2026-08-21 this runner returned ACCEPT_PARTIAL_CHAIN /
        # AGREE against QG-7d receipt f80deba7..., which a menu-reduction bug
        # had made scientifically wrong; the run was deterministic,
        # replay-identical and digest-valid throughout. The defect was caught by
        # a cross-lemma check and a from-primitives verifier, neither of which
        # is this runner. See RECEIPT_CHURN_HAZARD_2026-08-21.md.
        "corroboration_kind": corroboration.PROVENANCE_ONLY,
        "scientific_corroboration": False,
        "corroboration_note": corroboration.describe(corroboration.PROVENANCE_ONLY),
        "generic_lane": {
            "instrument": "ORION research harness (ResearchWorkspace + service_local_request)",
            "capability": "PYTHON",
            "decision": lane_a["decision"],
            "comm_s2_pinned_sector": lane_a["comm_s2_pinned_sector"],
            "rungs_present": lane_a["rungs_present"],
            "rungs_absent": lane_a["rungs_absent"],
            "rung_terminals": lane_a["rung_terminals"],
            "faults": lane_a["faults"],
            "receipts": lane_a_receipts,
        },
        "native_lane": {
            "instrument": "ORION-Q typed campaign layer (campaign_control.decide_campaign)",
            "campaign_id": manifest["campaign_id"],
            "claim_id": manifest["claim_id"],
            "manifest_digest": manifest_digest(manifest),
            "authority_ceiling": manifest["authority_ceiling"],
            "protected_refs": [item.as_dict() for item in state.protected_refs],
            "observations": dict(observations),
            "observation_source": "LANE_A_SERIALIZED_TOKENS_ONLY",
            "responsibility_status": decision.responsibility.get("status"),
            "identified_hypothesis_id": identified,
            "decision": lane_b_decision,
            "selected_kind": decision.selected_kind,
            "selected_id": decision.selected_id,
            "state_digest": state.state_digest,
            "decision_digest": decision.decision_digest,
            "campaign_state": state.as_dict(),
            "campaign_decision": decision.as_dict(),
        },
        "receipt_digests": {
            row["rung"]: {
                "receipt_path": row["receipt_path"],
                "present": bool(tokens[row["rung"]].get("present")),
                "declared": tokens[row["rung"]].get("result_digest_declared"),
                "rederived": tokens[row["rung"]].get("result_digest_rederived"),
                "rebinds": tokens[row["rung"]].get("result_digest_rebinds"),
                "probe_request_digest": receipt["probe_request"]["request_digest"],
                "probe_result_digest": receipt["probe_result"]["result_digest"],
            }
            for row, receipt in zip(QG7_LADDER_RUNGS, lane_a_receipts, strict=True)
        },
        "custody": "DUAL_INSTRUMENT",
        "divergence_is_data": True,
        "r6_authority": False,
        "novelty_authority": False,
        "scientific_authority": False,
        "physical_quantum_advantage_claim": False,
        "chemistry_data_read": False,
        "reserved_stretched_n2_accessed": False,
    }
    DUAL.write_text(json.dumps(dual, indent=2, sort_keys=True) + "\n", encoding="utf-8")

    corroboration.validate_corroboration(dual)

    summary = {
        "agreement": verdict,
        "generic_decision": lane_a["decision"],
        "native_decision": lane_b_decision,
        "responsibility_status": decision.responsibility.get("status"),
        "comm_s2_pinned_sector": lane_a["comm_s2_pinned_sector"],
        "rungs_present": lane_a["rungs_present"],
        "rungs_absent": lane_a["rungs_absent"],
        "rung_terminals": lane_a["rung_terminals"],
        "manifest_digest": manifest_digest(manifest),
        "decision_digest": decision.decision_digest,
        "artifact": str(DUAL.relative_to(ROOT)),
        "r6_authority": False,
        "novelty_authority": False,
    }
    print(TOKEN_PREFIX + canonical(summary))
    print(json.dumps(summary, indent=2, sort_keys=True), file=sys.stderr)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
