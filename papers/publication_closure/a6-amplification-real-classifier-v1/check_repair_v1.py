#!/usr/bin/env python3
"""Test the proposed repair against the attack that landed on the real classifier.

Protocol and pre-declared predictions: REPAIR_PROTOCOL_V1.md, frozen before this ran.

The repaired classifier is defined here as a wrapper that calls the *real* shipped
classify() and adds one guard. It does not reimplement it, so the repair cannot
accidentally fix the attack by rewriting the thing under test.
"""
from __future__ import annotations

import hashlib
import importlib.util
import itertools
import json
from pathlib import Path

HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[2]
SUBJECT = (
    ROOT
    / "papers/orion-16-formal-epistemic-structures-and-mechanics/top_tier"
    / "check_real_transition_audit_independent_v1.py"
)
CASES = SUBJECT.parent / "p6_real_transition_cases_v1.json"
GOLD = SUBJECT.parent / "p6_real_transition_gold_v1.json"
PROTOCOL = HERE / "REPAIR_PROTOCOL_V1.md"
EXPECTED_SUBJECT_SHA = "698f49ca952f59ec015ff50aafec9f78a44c4a17481723dcede4a3b5e4c8c4db"

FIELDS = (
    "execution_support",
    "provenance_binding",
    "source_current",
    "evidence_transport_known",
    "evidence_transport_valid",
    "obligations_clear",
    "generic_permission",
    "commit_authority",
)
VACUOUS = ("evidence_transport_known", "evidence_transport_valid", "obligations_clear")
NEW = "transport_vacuous"


class ProtocolViolation(RuntimeError):
    pass


def load_real_classify():
    got = hashlib.sha256(SUBJECT.read_bytes()).hexdigest()
    if got != EXPECTED_SUBJECT_SHA:
        raise ProtocolViolation(f"subject changed since freeze: {got}")
    spec = importlib.util.spec_from_file_location("orion16_rta", SUBJECT)
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module.classify, got


def main() -> int:
    classify, subject_sha = load_real_classify()

    def repaired(c: dict) -> str:
        """The real classifier plus one guard. See REPAIR_PROTOCOL_V1.md."""
        if c.get(NEW, False):
            # A route that transports nothing has not shown transport is known;
            # it has shown there is nothing to know. That is not a discharge.
            return "CANNOT_CHECK"
        return classify(c)

    base_states = [dict(zip(FIELDS, b)) for b in itertools.product((False, True), repeat=8)]
    ext_states = [{**s, NEW: v} for s in base_states for v in (False, True)]

    def key(s):
        return tuple(s[f] for f in FIELDS) + (s[NEW],)

    def edges(fn, states):
        """Amplifying edges: CANNOT_CHECK -> ADMISSIBLE by vacuity-only turn-ons."""
        verdicts = {key(s): fn(s) for s in states}
        found = []
        legit = 0
        for a in states:
            if verdicts[key(a)] != "CANNOT_CHECK":
                continue
            for b in states:
                if verdicts[key(b)] != "ADMISSIBLE":
                    continue
                delta = [f for f in FIELDS + (NEW,) if a[f] != b[f]]
                if not delta or any(a[f] and not b[f] for f in delta):
                    continue
                if all(f in VACUOUS for f in delta):
                    found.append({"before": dict(a), "flips": delta})
                else:
                    legit += 1
        return found, legit, verdicts

    before_edges, before_legit, _ = edges(lambda s: classify(s), ext_states)
    after_edges, after_legit, after_verdicts = edges(repaired, ext_states)

    # Prediction 4: forcing the vacuous route admits nothing, anywhere.
    forced_vacuous_admissible = sum(
        1 for s in ext_states if s[NEW] and repaired(s) == "ADMISSIBLE"
    )

    # Prediction 2: the sixteen real cases keep their gold verdicts exactly.
    cases = json.loads(CASES.read_text(encoding="utf-8"))["cases"]
    gold = json.loads(GOLD.read_text(encoding="utf-8"))["gold"]
    gold_preserved = {}
    gold_broken = []
    for c in cases:
        s = {f: bool(c[f]) for f in FIELDS}
        s[NEW] = False  # every real case has a genuine transport
        got = repaired(s)
        gold_preserved[c["id"]] = got
        if got != gold[c["id"]]:
            gold_broken.append({"id": c["id"], "got": got, "gold": gold[c["id"]]})

    # The five realized pairs from RESULT_V1.json must no longer amplify when the
    # destination is reached by the vacuous route.
    realized_blocked = []
    src = next(c for c in cases if c["id"] == "RC-ALIAS-MISSING")
    s_src = {f: bool(src[f]) for f in FIELDS}
    s_src[NEW] = False
    for c in cases:
        if gold[c["id"]] != "ADMISSIBLE":
            continue
        s_dst = {f: bool(c[f]) for f in FIELDS}
        s_dst[NEW] = True  # reached by a route that transports nothing
        realized_blocked.append(
            {
                "from": "RC-ALIAS-MISSING",
                "to": c["id"],
                "unrepaired": classify({k: v for k, v in s_dst.items() if k != NEW}),
                "repaired": repaired(s_dst),
                "blocked": repaired(s_dst) != "ADMISSIBLE",
            }
        )

    holds = {
        "P1_zero_amplifying_edges_survive": len(after_edges) == 0,
        "P2_all_gold_preserved": not gold_broken,
        "P3_legitimate_routes_retained": after_legit > 0,
        "P4_forced_vacuous_never_admissible": forced_vacuous_admissible == 0,
        "P5_all_realized_pairs_blocked": all(r["blocked"] for r in realized_blocked),
    }
    failed = [k for k, v in holds.items() if not v]

    payload = {
        "schema": "A6.AmplificationRepairCheck.v1",
        "subject": str(SUBJECT.relative_to(ROOT)),
        "subject_sha256": subject_sha,
        "protocol_sha256": hashlib.sha256(PROTOCOL.read_bytes()).hexdigest(),
        "repair": "one guard: transport_vacuous -> CANNOT_CHECK, wrapping the real classify()",
        "extended_states_enumerated": len(ext_states),
        "amplifying_edges_before_repair": len(before_edges),
        "amplifying_edges_after_repair": len(after_edges),
        "legitimate_promotion_edges_before": before_legit,
        "legitimate_promotion_edges_after": after_legit,
        "forced_vacuous_admissible_states": forced_vacuous_admissible,
        "gold_verdicts_checked": len(cases),
        "gold_broken": gold_broken,
        "realized_pairs": realized_blocked,
        "predictions": holds,
        "predictions_failed": failed,
        "predicates_not_evaluated": [
            "whether transport_vacuous can itself be misreported — it can, and the repair "
            "relocates trust rather than removing it (REPAIR_PROTOCOL_V1.md states this)",
            "whether ORION-16's authors intend this reading of the transport coordinates",
            "whether the repair is sound over the papers' full formal cores, as opposed to "
            "this eight-coordinate audit classifier",
        ],
        "scientific_authority_delta": "NONE",
        "verdict": "REPAIR_HOLDS_ON_ALL_PREDECLARED_PREDICATES"
        if not failed
        else "REPAIR_FAILS__" + ",".join(failed),
    }
    raw = json.dumps(payload, sort_keys=True, separators=(",", ":")).encode()
    payload["receipt_sha256"] = hashlib.sha256(raw).hexdigest()
    print(json.dumps(payload, indent=2, sort_keys=True))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
