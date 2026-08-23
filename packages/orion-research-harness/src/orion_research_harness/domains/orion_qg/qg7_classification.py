"""QG-7 native ORION-Q admission for the support-<=2 classification ladder.

The QG-7 ladder is the four-rung chain that carries the programme's TARE
classification result::

    QG-7   B' completeness / fourth support-two regime
    QG-7b  frozen hybrid family B'' closure on verified domains
    QG-7c  L4b / L4c classification endgame
    QG-7d  the last link -- the comm-s2 pinned sector

Unlike the other ORION-QG lanes, this manifest does not admit a single
analyzer receipt: it admits the *chain*.  Its decision is deliberately
three-valued and follows only from observations serialized out of the
receipts at runtime:

``ACCEPT_CLASSIFICATION_CHAIN``
    all four rungs present and mutually bound, and the comm-s2 pinned
    sector is closed by the QG-7d last link.
``ACCEPT_PARTIAL_CHAIN``
    the rungs that exist are bound and integral, but the comm-s2 pinned
    sector is still open (QG-7c reports ``QG7C_PARTIAL__*`` and QG-7d is
    absent or itself partial).
``REJECT_OR_CANNOT_CHECK``
    a rung is refuted, cannot-check, digest-broken, gate-failing, chain
    unbound, authority-ceiling violating, or the observations are mutually
    inconsistent.

Nothing here hardcodes which branch is true.  ``derive_observations`` is a
pure function of the serialized per-rung probe tokens; the manifest phases
carry the discrimination.  The lane is non-authorizing and NOT_R6.
"""
from __future__ import annotations

import hashlib
import json
from pathlib import Path
from typing import Any, Mapping

_LOAD = "ORIONQG_QG7_NATIVE_LOAD="
_DECISION = "ORIONQG_QG7_NATIVE_DECISION="

QG7_RUNG_TOKEN_PREFIX = "ORIONQG_QG7_FAMILY_RUNG="

PROTECTED_STRETCHED_N2_PATH = (
    "N2/cc-pVTZ/6Elec_6Orbs/1.5_Eq-3.1020au/DUCC2/N2.cc-pvtz.ducc.results.txt"
)

#: Ordered rungs of the ladder.  ``rung`` is the discriminator suffix used in
#: the campaign observation keys; ``receipt_path`` is repo-root relative.
QG7_LADDER_RUNGS: tuple[dict[str, str], ...] = (
    {
        "rung": "A",
        "lane": "QG-7",
        "receipt_path": "research/extensions/orion-qg/QG7_BPRIME_COMPLETENESS_RESULTS.json",
        "schema": "ORIONQG.QG7.BprimeCompleteness.v1",
    },
    {
        "rung": "B",
        "lane": "QG-7b",
        "receipt_path": "research/extensions/orion-qg/QG7B_HYBRID_FAMILY_RESULTS.json",
        "schema": "ORIONQG.QG7B.HybridFamily.v1",
    },
    {
        "rung": "C",
        "lane": "QG-7c",
        "receipt_path": "research/extensions/orion-qg/QG7C_CLASSIFICATION_RESULTS.json",
        "schema": "ORIONQG.QG7C.Classification.v1",
    },
    {
        "rung": "D",
        "lane": "QG-7d",
        "receipt_path": "research/extensions/orion-qg/QG7D_LAST_LINK_RESULTS.json",
        "schema": "ORIONQG.QG7D.LastLink.v1",
    },
)

_RUNG_BY_KEY = {row["rung"]: row for row in QG7_LADDER_RUNGS}

# Terminal vocabularies, frozen from the analyzers.
_A_POSITIVE = "QG7_FOURTH_SUPPORT2_REGIME_FOUND"
_B_POSITIVE = "QG7B_HYBRID_FAMILY_CLOSES_ON_VERIFIED_DOMAINS"
_C_THEOREM = "QG7C_FOUR_CONFIGURATION_CLASSIFICATION_ALL_N_MACHINE_CHECKED"
_C_PARTIAL_PREFIX = "QG7C_PARTIAL__"
_D_THEOREM = "QG7D_ALL_N_CLASSIFICATION_THEOREM_COMPLETE"
_D_PARTIAL_PREFIX = "QG7D_PARTIAL__"

_SECTOR_CLOSED_MARK = "COMM_S2_PINNED_SECTOR_CLOSED"
_SECTOR_OPEN_MARK = "COMM_S2_PINNED_SECTOR_OPEN"


def _yes(value: bool) -> str:
    return "YES" if value else "NO"


def _canonical(value: Any) -> str:
    return json.dumps(value, sort_keys=True, separators=(",", ":"), allow_nan=False)


def probe_rung(rung: str, receipt_path: str, expected_schema: str) -> dict[str, Any]:
    """Re-read one QG-7-family receipt and re-derive its own bindings.

    Returns a JSON-serializable token.  Nothing in the token is a decision:
    it is raw, independently re-derived fact about a single receipt.  A
    missing receipt is reported as ``present: False`` rather than raising --
    QG-7d may still be running.
    """
    path = Path(receipt_path)
    token: dict[str, Any] = {
        "rung": str(rung),
        "receipt_path": str(receipt_path),
        "expected_schema": str(expected_schema),
        "present": path.exists(),
    }
    if not token["present"]:
        return token

    raw = json.loads(path.read_text(encoding="utf-8"))
    unsigned = dict(raw)
    observed_digest = unsigned.pop("result_digest", None)
    # R6P convention: timing is excluded from the canonical digest.
    unsigned.pop("timing", None)
    rederived = hashlib.sha256(_canonical(unsigned).encode("utf-8")).hexdigest()

    gates = raw.get("gates", {})
    bindings = raw.get("receipt_bindings", {})
    authority = str(raw.get("authority", ""))

    token.update(
        {
            "schema": raw.get("schema"),
            "schema_matches": raw.get("schema") == expected_schema,
            "terminal": raw.get("terminal"),
            "authority": authority,
            "authority_not_r6": "NOT_R6" in authority,
            "protocol": raw.get("protocol"),
            "protocol_sha256": raw.get("protocol_sha256"),
            "result_digest_declared": observed_digest,
            "result_digest_rederived": rederived,
            "result_digest_rebinds": observed_digest == rederived,
            "gates_present": bool(gates),
            "gates_all_true": bool(gates) and all(bool(v) for v in gates.values()),
            "r6_authority_false": raw.get("r6_authority") is False,
            "novelty_credit_false": raw.get("novelty_credit") is False
            and raw.get("donor_novelty_credit") is False,
            "physical_advantage_false": raw.get("physical_quantum_advantage_claim")
            is False,
            "protected_unread": raw.get("reserved_stretched_n2_accessed") is False
            and raw.get("chemistry_data_read") is False,
            "r6s_receipt_bound": bindings.get("r6s_receipt_bound") is True,
            "binds": {
                "qg7_receipt_bound": bindings.get("qg7_receipt_bound"),
                "qg7_authority": bindings.get("qg7_authority"),
                "qg7_protocol_sha256_recomputed": bindings.get(
                    "qg7_protocol_sha256_recomputed"
                ),
                "qg7b_receipt_bound": bindings.get("qg7b_receipt_bound"),
                "qg7b_result_digest": bindings.get("qg7b_result_digest"),
                "qg7b_terminal": bindings.get("qg7b_terminal"),
                "qg7c_receipt_bound": bindings.get("qg7c_receipt_bound"),
                "qg7c_result_digest": bindings.get("qg7c_result_digest"),
            },
        }
    )
    return token


def probe_all(root: str = ".") -> dict[str, dict[str, Any]]:
    """Probe every declared rung, relative to ``root``."""
    base = Path(root)
    return {
        row["rung"]: probe_rung(
            row["rung"], str(base / row["receipt_path"]), row["schema"]
        )
        for row in QG7_LADDER_RUNGS
    }


def rung_probe_code(rung: str) -> str:
    """Content-bound PYTHON payload that probes exactly one rung.

    The returned source pins the rung key, the receipt path, the expected
    receipt schema and the stdout token prefix, so the harness request digest
    binds *which* receipt was re-derived and *how*.
    """
    row = _RUNG_BY_KEY[rung]
    return (
        "import json\n"
        "from orion_research_harness.domains.orion_qg.qg7_classification "
        "import probe_rung\n"
        "token = probe_rung(%r, %r, %r)\n"
        "print(%r + json.dumps(token, sort_keys=True, separators=(',', ':')))\n"
        % (
            row["rung"],
            row["receipt_path"],
            row["schema"],
            QG7_RUNG_TOKEN_PREFIX,
        )
    )


def _terminal_class(rung: str, token: Mapping[str, Any] | None) -> str:
    if token is None or not token.get("present"):
        return "ABSENT"
    terminal = str(token.get("terminal") or "")
    if rung == "A":
        return "POSITIVE" if terminal == _A_POSITIVE else "OTHER"
    if rung == "B":
        return "POSITIVE" if terminal == _B_POSITIVE else "OTHER"
    if rung == "C":
        if terminal == _C_THEOREM:
            return "THEOREM"
        return "PARTIAL" if terminal.startswith(_C_PARTIAL_PREFIX) else "OTHER"
    if terminal == _D_THEOREM:
        return "THEOREM"
    return "PARTIAL" if terminal.startswith(_D_PARTIAL_PREFIX) else "OTHER"


def _sector_state(
    c_token: Mapping[str, Any] | None, d_token: Mapping[str, Any] | None
) -> str:
    """Where the comm-s2 pinned sector stands, from the receipts alone."""
    if d_token is not None and d_token.get("present"):
        terminal = str(d_token.get("terminal") or "")
        authority = str(d_token.get("authority") or "")
        if terminal == _D_THEOREM and _SECTOR_CLOSED_MARK in authority:
            return "CLOSED"
        if terminal.startswith(_D_PARTIAL_PREFIX):
            return "OPEN"
        return "INDETERMINATE"
    if c_token is not None and c_token.get("present"):
        terminal = str(c_token.get("terminal") or "")
        authority = str(c_token.get("authority") or "")
        if terminal.startswith(_C_PARTIAL_PREFIX) and _SECTOR_OPEN_MARK in authority:
            return "OPEN"
    return "INDETERMINATE"


def _chain_bindings(tokens: Mapping[str, Mapping[str, Any] | None]) -> bool:
    a, b, c, d = (tokens.get(key) for key in ("A", "B", "C", "D"))
    if not (a and a.get("present") and b and b.get("present") and c and c.get("present")):
        return False
    ab = b["binds"]
    ok = (
        ab.get("qg7_receipt_bound") is True
        and ab.get("qg7_authority") == a.get("authority")
        and ab.get("qg7_protocol_sha256_recomputed") == a.get("protocol_sha256")
    )
    bc = c["binds"]
    ok = ok and (
        bc.get("qg7_receipt_bound") is True
        and bc.get("qg7b_receipt_bound") is True
        and bc.get("qg7b_result_digest") == b.get("result_digest_declared")
        and bc.get("qg7b_terminal") == b.get("terminal")
    )
    ok = ok and all(
        tokens[key]["r6s_receipt_bound"] is True for key in ("A", "B", "C")
    )
    if d is not None and d.get("present"):
        cd = d["binds"]
        ok = ok and (
            cd.get("qg7_receipt_bound") is True
            and cd.get("qg7b_receipt_bound") is True
            and cd.get("qg7c_receipt_bound") is True
            and cd.get("qg7c_result_digest") == c.get("result_digest_declared")
            and cd.get("qg7b_result_digest") == b.get("result_digest_declared")
            and d["r6s_receipt_bound"] is True
        )
    return bool(ok)


def derive_observations(
    tokens: Mapping[str, Mapping[str, Any] | None],
) -> dict[str, str]:
    """Map serialized per-rung probe tokens onto campaign observations.

    Pure: the only input is what the probes serialized.  The caller never
    feeds an analyzer's in-process values here.
    """
    present = [key for key in ("A", "B", "C", "D") if (tokens.get(key) or {}).get("present")]
    core_present = [key for key in ("A", "B", "C") if key in present]
    if len(present) == 4:
        rungs_present = "FOUR"
    elif len(core_present) == 3:
        rungs_present = "THREE"
    else:
        rungs_present = "FEWER"

    live = [tokens[key] for key in present]
    digests = bool(live) and all(t["result_digest_rebinds"] for t in live)
    schemas = bool(live) and all(t["schema_matches"] for t in live)
    gates = bool(live) and all(t["gates_all_true"] for t in live)
    not_r6 = bool(live) and all(t["authority_not_r6"] for t in live)
    r6_false = bool(live) and all(t["r6_authority_false"] for t in live)
    novelty_false = bool(live) and all(
        t["novelty_credit_false"] and t["physical_advantage_false"] for t in live
    )
    protected_unread = bool(live) and all(t["protected_unread"] for t in live)
    bindings = _chain_bindings(tokens)

    classes = {key: _terminal_class(key, tokens.get(key)) for key in ("A", "B", "C", "D")}
    sector = _sector_state(tokens.get("C"), tokens.get("D"))

    integrity = (
        digests
        and schemas
        and gates
        and not_r6
        and r6_false
        and novelty_false
        and protected_unread
        and bindings
    )
    rungs_ok = (
        rungs_present in {"FOUR", "THREE"}
        and classes["A"] == "POSITIVE"
        and classes["B"] == "POSITIVE"
        and classes["C"] in {"THEOREM", "PARTIAL"}
        and classes["D"] in {"THEOREM", "PARTIAL", "ABSENT"}
    )
    # The comm-s2 sector may only read CLOSED when the declared last link
    # (QG-7d) is present and reached its theorem terminal.  Any other pairing
    # is an inconsistency, not an acceptance.
    consistent = sector in {"CLOSED", "OPEN"} and (sector == "CLOSED") == (
        rungs_present == "FOUR" and classes["D"] == "THEOREM"
    )
    admissible = integrity and rungs_ok and consistent

    return {
        "QG7_RUNGS_PRESENT": rungs_present,
        "QG7_DIGESTS_REDERIVED": _yes(digests),
        "QG7_SCHEMAS_MATCH": _yes(schemas),
        "QG7_GATES_ALL_TRUE": _yes(gates),
        "QG7_AUTHORITY_NOT_R6": _yes(not_r6),
        "QG7_R6_AUTHORITY_FALSE": _yes(r6_false),
        "QG7_NOVELTY_CREDIT_FALSE": _yes(novelty_false),
        "QG7_PROTECTED_UNREAD": _yes(protected_unread),
        "QG7_CHAIN_BINDINGS": _yes(bindings),
        "QG7_RUNG_A_TERMINAL": classes["A"],
        "QG7_RUNG_B_TERMINAL": classes["B"],
        "QG7_RUNG_C_TERMINAL": classes["C"],
        "QG7_RUNG_D_TERMINAL": classes["D"],
        "QG7_COMM_S2_SECTOR": sector,
        "QG7_LADDER_ADMISSIBLE": _yes(admissible),
    }


#: Observation keys the manifest discriminates on, in manifest order.
QG7_OBSERVATION_KEYS: tuple[str, ...] = tuple(
    derive_observations({key: None for key in ("A", "B", "C", "D")})
)


_INTEGRITY_EXPECTATIONS = {
    "QG7_LADDER_ADMISSIBLE": ["YES"],
    "QG7_DIGESTS_REDERIVED": ["YES"],
    "QG7_SCHEMAS_MATCH": ["YES"],
    "QG7_GATES_ALL_TRUE": ["YES"],
    "QG7_AUTHORITY_NOT_R6": ["YES"],
    "QG7_R6_AUTHORITY_FALSE": ["YES"],
    "QG7_NOVELTY_CREDIT_FALSE": ["YES"],
    "QG7_PROTECTED_UNREAD": ["YES"],
    "QG7_CHAIN_BINDINGS": ["YES"],
    "QG7_RUNG_A_TERMINAL": ["POSITIVE"],
    "QG7_RUNG_B_TERMINAL": ["POSITIVE"],
    "QG7_RUNG_C_TERMINAL": ["THEOREM", "PARTIAL"],
}

_ACCEPT_CHAIN_OBS = dict(
    _INTEGRITY_EXPECTATIONS,
    QG7_RUNGS_PRESENT=["FOUR"],
    QG7_RUNG_D_TERMINAL=["THEOREM"],
    QG7_COMM_S2_SECTOR=["CLOSED"],
)

_ACCEPT_PARTIAL_OBS = dict(
    _INTEGRITY_EXPECTATIONS,
    QG7_RUNGS_PRESENT=["FOUR", "THREE"],
    QG7_RUNG_D_TERMINAL=["PARTIAL", "ABSENT"],
    QG7_COMM_S2_SECTOR=["OPEN"],
)

_REJECT_OBS = {"QG7_LADDER_ADMISSIBLE": ["NO"]}


def _decision_capability(
    decision: str, sector: str, next_phase: str
) -> dict[str, Any]:
    payload = {
        "decision": decision,
        "comm_s2_pinned_sector": sector,
        "ladder_scope": "QG7_LADDER_CUSTODY_ONLY__UNIT_SUPPORT_COUNT_OBJECTIVE__NOT_R6",
        "r6_authority": False,
        "novelty_authority": False,
        "scientific_authority": False,
        "physical_quantum_advantage_claim": False,
        "protected_subject_read": False,
    }
    code = (
        "import json; print('" + _DECISION + "' + json.dumps("
        + repr(payload) + ", sort_keys=True, separators=(',', ':')))"
    )
    return {
        "host_capability": "PYTHON",
        "payload": {"code": code, "cwd": ".", "timeout": 30},
        "result_contract": {
            "kind": "SHELL_JSON_TOKEN",
            "prefix": _DECISION,
            "required_payload_values": [
                {"path": ["decision"], "equals": decision},
                {"path": ["comm_s2_pinned_sector"], "equals": sector},
                {"path": ["r6_authority"], "equals": False},
                {"path": ["novelty_authority"], "equals": False},
                {"path": ["scientific_authority"], "equals": False},
                {"path": ["physical_quantum_advantage_claim"], "equals": False},
                {"path": ["protected_subject_read"], "equals": False},
            ],
            "evidence_rules": [
                {
                    "evidence_key": "QG7_NATIVE_DECISION",
                    "path": ["decision"],
                    "transform": "STRING",
                }
            ],
        },
        "next_phase": next_phase,
    }


_LOAD_CODE = (
    "import json\n"
    "from orion_research_harness.domains.orion_qg.qg7_classification "
    "import derive_observations, probe_all\n"
    "out = derive_observations(probe_all())\n"
    "print('" + _LOAD + "' + json.dumps(out, sort_keys=True, separators=(',', ':')))\n"
)

_LOAD_EVIDENCE_RULES = [
    {"evidence_key": key, "path": [key], "transform": "STRING"}
    for key in QG7_OBSERVATION_KEYS
]


QG7_CLASSIFICATION_CAMPAIGN_MANIFEST: dict[str, Any] = {
    "schema": "ORION.ResearchCampaignManifest.v1",
    "campaign_id": "orion-qg:qg7-classification-ladder",
    "claim_id": "orion-qg:qg7-support2-classification-chain",
    "description": (
        "Native ORION-Q typed custody for the QG-7 -> QG-7b -> QG-7c -> QG-7d "
        "classification ladder. It admits the chain, not a single receipt, and "
        "distinguishes a closed chain from a chain whose comm-s2 pinned sector "
        "is still open. Non-authorizing; NOT_R6; no chemistry subject is read."
    ),
    "initial_phase": "S0",
    "initial_observations": {"QG7_LADDER_NEED": "YES"},
    "authority_ceiling": (
        "NON_AUTHORIZING_QG7_LADDER_CUSTODY_EVIDENCE__CHAIN_BINDING_ONLY__NOT_R6"
    ),
    "protected_refs": [
        {
            "ref_id": "protected-stretched-n2",
            "path": PROTECTED_STRETCHED_N2_PATH,
            "released": False,
        }
    ],
    "capabilities": {
        "qg7.load": {
            "host_capability": "PYTHON",
            "payload": {"code": _LOAD_CODE, "cwd": ".", "timeout": 120},
            "declared_read_paths": [row["receipt_path"] for row in QG7_LADDER_RUNGS],
            "result_contract": {
                "kind": "SHELL_JSON_TOKEN",
                "prefix": _LOAD,
                "required_payload_values": [
                    {"path": ["QG7_PROTECTED_UNREAD"], "equals": "YES"},
                    {"path": ["QG7_AUTHORITY_NOT_R6"], "equals": "YES"},
                ],
                "evidence_rules": _LOAD_EVIDENCE_RULES,
            },
            "next_phase": "D0",
        },
        "qg7.accept-chain": _decision_capability(
            "ACCEPT_CLASSIFICATION_CHAIN", "CLOSED", "ACCEPT_CHAIN_RECORDED"
        ),
        "qg7.accept-partial": _decision_capability(
            "ACCEPT_PARTIAL_CHAIN", "OPEN", "ACCEPT_PARTIAL_RECORDED"
        ),
        "qg7.reject": _decision_capability(
            "REJECT_OR_CANNOT_CHECK", "INDETERMINATE", "REJECT_RECORDED"
        ),
    },
    "phases": {
        "S0": {
            "active_hard_obligations": ["QG7_LADDER_LOAD"],
            "responsibility_hypotheses": [
                {
                    "hypothesis_id": "RESP:LOAD",
                    "expected_observations": {"QG7_LADDER_NEED": ["YES"]},
                }
            ],
            "interface_checks": [
                {
                    "check_id": "IFACE:SERIALIZED",
                    "scope": "EVIDENCE_BINDING",
                    "state": "PASS",
                }
            ],
            "revision_mechanics": [
                {
                    "mechanic_id": "REV:WAIT",
                    "kind": "WAIT_EVIDENCE",
                    "write_coordinates": ["EVIDENCE"],
                    "cost": 0.1,
                }
            ],
            "computation_actions": [
                {
                    "action_id": "COMPUTE:LOAD",
                    "kind": "VERIFY",
                    "expected_decision_value": 5.0,
                    "cost": 0.1,
                    "discharges_obligations": ["QG7_LADDER_LOAD"],
                }
            ],
            "responsibility_bindings": {"RESP:LOAD": ["REV:WAIT"]},
            "selected_capabilities": {"COMPUTE:LOAD": "qg7.load"},
        },
        "D0": {
            "active_hard_obligations": [],
            "responsibility_hypotheses": [
                {
                    "hypothesis_id": "RESP:ACCEPT_CLASSIFICATION_CHAIN",
                    "expected_observations": _ACCEPT_CHAIN_OBS,
                },
                {
                    "hypothesis_id": "RESP:ACCEPT_PARTIAL_CHAIN",
                    "expected_observations": _ACCEPT_PARTIAL_OBS,
                },
                {
                    "hypothesis_id": "RESP:REJECT_OR_CANNOT_CHECK",
                    "expected_observations": _REJECT_OBS,
                },
            ],
            "interface_checks": [
                {"check_id": "IFACE:CHAIN_BINDING", "scope": "EVIDENCE_BINDING", "state": "PASS"},
                {"check_id": "IFACE:PROTECTED_SUBJECT", "scope": "PROTECTED_REF", "state": "PASS"},
                {"check_id": "IFACE:NO_R6_LAUNDER", "scope": "AUTHORITY", "state": "PASS"},
            ],
            "revision_mechanics": [
                {
                    "mechanic_id": "REV:ACCEPT_CHAIN",
                    "kind": "ACCEPT_BOUNDED_CHAIN_EVIDENCE",
                    "read_coordinates": ["EVIDENCE", "CHAIN"],
                    "write_coordinates": ["BOUNDED_RESULT"],
                    "cost": 0.1,
                },
                {
                    "mechanic_id": "REV:ACCEPT_PARTIAL",
                    "kind": "ACCEPT_BOUNDED_PARTIAL_CHAIN_EVIDENCE",
                    "read_coordinates": ["EVIDENCE", "CHAIN"],
                    "write_coordinates": ["BOUNDED_RESULT"],
                    "cost": 0.1,
                },
                {
                    "mechanic_id": "REV:REJECT",
                    "kind": "REJECT",
                    "read_coordinates": ["EVIDENCE"],
                    "write_coordinates": ["TERMINAL"],
                    "cost": 0.1,
                },
            ],
            "computation_actions": [
                {
                    "action_id": "COMPUTE:NONE",
                    "kind": "NONE",
                    "expected_decision_value": 0.0,
                    "cost": 1.0,
                }
            ],
            "responsibility_bindings": {
                "RESP:ACCEPT_CLASSIFICATION_CHAIN": ["REV:ACCEPT_CHAIN"],
                "RESP:ACCEPT_PARTIAL_CHAIN": ["REV:ACCEPT_PARTIAL"],
                "RESP:REJECT_OR_CANNOT_CHECK": ["REV:REJECT"],
            },
            "selected_capabilities": {
                "REV:ACCEPT_CHAIN": "qg7.accept-chain",
                "REV:ACCEPT_PARTIAL": "qg7.accept-partial",
                "REV:REJECT": "qg7.reject",
            },
        },
        "ACCEPT_CHAIN_RECORDED": {
            "terminal": True,
            "terminal_name": "QG7_NATIVE_ACCEPT_CLASSIFICATION_CHAIN_RECORDED",
            "active_hard_obligations": [],
        },
        "ACCEPT_PARTIAL_RECORDED": {
            "terminal": True,
            "terminal_name": "QG7_NATIVE_ACCEPT_PARTIAL_CHAIN_RECORDED",
            "active_hard_obligations": [],
        },
        "REJECT_RECORDED": {
            "terminal": True,
            "terminal_name": "QG7_NATIVE_REJECT_OR_CANNOT_CHECK_RECORDED",
            "active_hard_obligations": [],
        },
    },
}

#: Map from an identified responsibility hypothesis to the recorded decision.
QG7_DECISION_BY_HYPOTHESIS = {
    "RESP:ACCEPT_CLASSIFICATION_CHAIN": "ACCEPT_CLASSIFICATION_CHAIN",
    "RESP:ACCEPT_PARTIAL_CHAIN": "ACCEPT_PARTIAL_CHAIN",
    "RESP:REJECT_OR_CANNOT_CHECK": "REJECT_OR_CANNOT_CHECK",
}

__all__ = [
    "QG7_CLASSIFICATION_CAMPAIGN_MANIFEST",
    "QG7_DECISION_BY_HYPOTHESIS",
    "QG7_LADDER_RUNGS",
    "QG7_OBSERVATION_KEYS",
    "QG7_RUNG_TOKEN_PREFIX",
    "PROTECTED_STRETCHED_N2_PATH",
    "derive_observations",
    "probe_all",
    "probe_rung",
    "rung_probe_code",
]
