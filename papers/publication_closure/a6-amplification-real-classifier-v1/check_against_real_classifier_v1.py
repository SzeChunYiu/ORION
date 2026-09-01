#!/usr/bin/env python3
"""Run the A6 amplification attack against ORION-16's real transition classifier.

The previous amplification check ran against a model written for the occasion, which
is the weakest possible target. This one imports the shipped classifier by path and
never copies it, so the subject cannot be shaped to lose.

Protocol and pre-declared prediction: PROTOCOL_V1.md, frozen before this ran.
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
PROTOCOL = HERE / "PROTOCOL_V1.md"

# sha256 of the subject as frozen in PROTOCOL_V1.md. A mismatch voids the run:
# the protocol names one specific classifier and this must be that one.
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

# Coordinates a re-grounding can satisfy by absence rather than by discharge.
# Justified in PROTOCOL_V1.md; this is the load-bearing assumption of the result.
VACUOUS = ("evidence_transport_known", "evidence_transport_valid", "obligations_clear")


class ProtocolViolation(RuntimeError):
    """The run cannot be trusted, as distinct from the attack failing."""


def load_real_classify():
    """Import the shipped classifier by path, refusing any substitute."""
    if not SUBJECT.exists():
        raise ProtocolViolation(f"subject absent: {SUBJECT}")
    got = hashlib.sha256(SUBJECT.read_bytes()).hexdigest()
    if got != EXPECTED_SUBJECT_SHA:
        raise ProtocolViolation(
            f"subject changed since the protocol was frozen: {got} != {EXPECTED_SUBJECT_SHA}"
        )
    spec = importlib.util.spec_from_file_location("orion16_real_transition_audit", SUBJECT)
    if spec is None or spec.loader is None:
        raise ProtocolViolation("could not build an import spec for the subject")
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    if not hasattr(module, "classify"):
        raise ProtocolViolation("subject exposes no classify()")
    return module.classify, got


def state(**overrides) -> dict:
    base = dict.fromkeys(FIELDS, True)
    unknown = set(overrides) - set(FIELDS)
    if unknown:
        raise ProtocolViolation(f"unknown coordinates: {sorted(unknown)}")
    base.update(overrides)
    return base


def flips(before: dict, after: dict) -> tuple[str, ...]:
    return tuple(f for f in FIELDS if before[f] != after[f])


def main() -> int:
    classify, subject_sha = load_real_classify()

    # --- step 2/3: exhaustive enumeration over the whole 2^8 state space -------------
    all_states = [
        dict(zip(FIELDS, bits)) for bits in itertools.product((False, True), repeat=len(FIELDS))
    ]
    verdicts = {tuple(s[f] for f in FIELDS): classify(s) for s in all_states}

    amplifying: list[dict] = []
    legitimate_promotions = 0
    for before in all_states:
        key_b = tuple(before[f] for f in FIELDS)
        if verdicts[key_b] != "CANNOT_CHECK":
            continue
        for after in all_states:
            key_a = tuple(after[f] for f in FIELDS)
            if verdicts[key_a] != "ADMISSIBLE":
                continue
            delta = flips(before, after)
            if not delta:
                continue
            # a promotion may only turn things on; a flip to False is not repair
            if any(before[f] and not after[f] for f in delta):
                continue
            if all(f in VACUOUS for f in delta):
                amplifying.append(
                    {
                        "before": {f: before[f] for f in FIELDS},
                        "flips": list(delta),
                    }
                )
            else:
                legitimate_promotions += 1

    attack_lands = bool(amplifying)

    # Prediction 2: no amplifying edge starts from an outer-layer unknown.
    outer = ("execution_support", "provenance_binding", "source_current")
    amplifying_from_outer = [e for e in amplifying if not all(e["before"][f] for f in outer)]
    minimal_before = sorted({tuple(sorted(e["flips"])) for e in amplifying})

    # --- step 4: controls -------------------------------------------------------------
    # The attack's own start state: everything present except the transport evidence.
    s0 = state(evidence_transport_known=False, evidence_transport_valid=False)
    s1 = state()  # the same claim after a re-grounding that transports nothing

    controls = {
        "C-NULL": (s0, s0, "CANNOT_CHECK"),
        "C-DENY": (s0, state(generic_permission=False), "DENIED"),
        "C-REOPEN": (s0, state(obligations_clear=False), "REOPEN"),
        "C-OUTER": (
            state(evidence_transport_known=False, evidence_transport_valid=False, source_current=False),
            state(source_current=False),
            "CANNOT_CHECK",
        ),
        # Same coordinate delta as the attack, different cause. See PROTOCOL_V1.md.
        "C-LEGIT": (s0, s1, "ADMISSIBLE"),
    }
    control_results = {}
    control_failures = []
    for cid, (before, after, required) in controls.items():
        got = classify(after)
        control_results[cid] = {
            "start_verdict": classify(before),
            "end_verdict": got,
            "required": required,
            "held": got == required,
            "flips": list(flips(before, after)),
        }
        if got != required:
            control_failures.append(cid)

    # The attack itself, spelled out separately from the enumeration.
    attack = {
        "start_verdict": classify(s0),
        "end_verdict": classify(s1),
        "flips": list(flips(s0, s1)),
        "unchanged_evidence_coordinates": {f: s0[f] for f in outer},
        "promoted": classify(s0) == "CANNOT_CHECK" and classify(s1) == "ADMISSIBLE",
    }

    # C-LEGIT and the attack apply the identical delta. That is the point: if both
    # land on ADMISSIBLE the classifier cannot separate them, because no coordinate
    # records why a flag became true.
    indistinguishable = (
        control_results["C-LEGIT"]["end_verdict"] == attack["end_verdict"]
        and control_results["C-LEGIT"]["flips"] == attack["flips"]
    )

    # --- step 5: do the 24 real cases realize an amplifying edge? ---------------------
    real_pairs_checked = 0
    real_amplifying = []
    real_case_note = "cases file absent"
    if CASES.exists():
        cases = json.loads(CASES.read_text(encoding="utf-8"))["cases"]
        real_case_note = f"{len(cases)} real cases, all ordered pairs examined"
        for a, b in itertools.permutations(cases, 2):
            sa = {f: bool(a[f]) for f in FIELDS}
            sb = {f: bool(b[f]) for f in FIELDS}
            real_pairs_checked += 1
            if classify(sa) != "CANNOT_CHECK" or classify(sb) != "ADMISSIBLE":
                continue
            delta = flips(sa, sb)
            if delta and all(f in VACUOUS for f in delta) and not any(
                sa[f] and not sb[f] for f in delta
            ):
                real_amplifying.append({"from": a["id"], "to": b["id"], "flips": list(delta)})

    if control_failures:
        verdict = "VOID__CONTROL_FAILED"
    elif not attack_lands:
        verdict = "ATTACK_REFUTED_BY_REAL_CLASSIFIER"
    elif amplifying_from_outer:
        verdict = "ATTACK_LANDS_INCLUDING_OUTER_LAYER"
    else:
        verdict = "ATTACK_LANDS_ON_INNER_LAYER_ONLY"

    payload = {
        "schema": "A6.AmplificationAgainstRealClassifier.v1",
        "subject": str(SUBJECT.relative_to(ROOT)),
        "subject_sha256": subject_sha,
        "protocol_sha256": hashlib.sha256(PROTOCOL.read_bytes()).hexdigest(),
        "vacuous_coordinates": list(VACUOUS),
        "states_enumerated": len(all_states),
        "verdict_histogram": {
            v: sum(1 for x in verdicts.values() if x == v) for v in sorted(set(verdicts.values()))
        },
        "amplifying_edges": len(amplifying),
        "amplifying_edges_from_outer_unknown": len(amplifying_from_outer),
        "minimal_amplifying_flip_sets": [list(x) for x in minimal_before],
        "legitimate_promotion_edges": legitimate_promotions,
        "attack": attack,
        "controls": control_results,
        "control_failures": control_failures,
        "attack_and_legitimate_repair_indistinguishable": indistinguishable,
        "real_cases": {
            "note": real_case_note,
            "ordered_pairs_checked": real_pairs_checked,
            "amplifying_pairs_found": real_amplifying,
        },
        "predicates_not_evaluated": [
            "whether ORION-16 anywhere claims non-amplification (it does not; that is the gap)",
            "whether any real transition was actually promoted this way in practice",
            "whether the VACUOUS mapping is the papers' intended reading, which is argued and not proved",
        ],
        "scientific_authority_delta": "NONE",
        "verdict": verdict,
    }
    raw = json.dumps(payload, sort_keys=True, separators=(",", ":")).encode()
    payload["receipt_sha256"] = hashlib.sha256(raw).hexdigest()
    print(json.dumps(payload, indent=2, sort_keys=True))
    return 0 if not control_failures else 1


if __name__ == "__main__":
    raise SystemExit(main())
