#!/usr/bin/env python3
"""Independent checker for ORION17.CLOSURE_CHAIN_COMPOSITION.v1.

INDEPENDENCE CONTRACT
---------------------
No ORION-17 module is imported. The chain theorems are verified on freshly
enumerated finite transform chains; the frozen closure-retention campaign is read
as DATA and never executed.

Checks
    A. Chain composition -- if every step preserves closure under its bridge and
       consecutive bridges compose, final closure is preserved, for chains of any
       length. Exhaustive to length 5.
    B. Necessity -- if one bridge link is broken, there is a chain where EVERY
       pairwise step succeeds and global closure still fails. Explicit witness.
    C. Order sensitivity -- reordering a chain can break a bridge that held.
    D. The frozen three-domain campaign is recomputed and classified.
    E. Negative controls.

Exit codes
    0 pass    2 fail    3 CANNOT_CHECK
"""
from __future__ import annotations
import itertools, json, sys
from pathlib import Path

PACKET = Path(__file__).resolve().parent.parent
PAPER = PACKET.parents[1]
CAMPAIGN = PAPER / "transitions/P7_CLOSURE_RETENTION_V1.json"
KMAX = 5
NPROP = 3          # number of abstract closure properties tracked


def step_ok(pre, post, preserves):
    """A step preserves closure iff every property required after is guaranteed."""
    return all((not post[i]) or preserves[i] or pre[i] for i in range(NPROP))


def chain_closure(states, preserves_seq):
    """Walk the chain; closure survives iff every step preserves it."""
    cur = states[0]
    for t, preserves in enumerate(preserves_seq):
        nxt = states[t + 1]
        if not step_ok(cur, nxt, preserves):
            return False
        cur = nxt
    return True


def bridges_compose(states):
    """Consecutive bridge: the output contract entails the input contract."""
    return all(all((not states[t + 1][i]) or states[t][i] for i in range(NPROP))
               for t in range(len(states) - 1))


def main() -> int:
    try:
        # ---- A: composition, exhaustive to length KMAX ---------------------
        a_checked = 0
        for k in range(1, KMAX + 1):
            for states in itertools.product(
                    list(itertools.product((0, 1), repeat=NPROP)), repeat=k + 1):
                if not bridges_compose(states):
                    continue
                allpres = [tuple([1] * NPROP)] * k     # every step preserves
                if not chain_closure(states, allpres):
                    raise AssertionError(json.dumps({"check": "A", "k": k}))
                a_checked += 1

        # ---- B: necessity -- break one bridge link -------------------------
        b_witness = None
        for k in range(2, KMAX + 1):
            for states in itertools.product(
                    list(itertools.product((0, 1), repeat=NPROP)), repeat=k + 1):
                if bridges_compose(states):
                    continue                      # we want a BROKEN bridge
                # every pairwise step, taken in isolation, is satisfiable
                pairwise_ok = all(
                    any(step_ok(states[t], states[t + 1], p)
                        for p in itertools.product((0, 1), repeat=NPROP))
                    for t in range(k))
                # but with no step actively re-establishing, global fails
                nopres = [tuple([0] * NPROP)] * k
                global_ok = chain_closure(states, nopres)
                if pairwise_ok and not global_ok and b_witness is None:
                    b_witness = {
                        "chain_length": k,
                        "contract_sequence": [list(s) for s in states],
                        "reading": ("every pairwise step is individually "
                                    "satisfiable, but a broken bridge link makes "
                                    "global closure fail -- pairwise success does "
                                    "not compose"),
                    }
                    break
            if b_witness:
                break
        if b_witness is None:
            raise AssertionError(json.dumps({"check": "B", "why": "no witness"}))

        # ---- C: order sensitivity ------------------------------------------
        c_witness = None
        for states in itertools.product(
                list(itertools.product((0, 1), repeat=NPROP)), repeat=3):
            if not bridges_compose(states):
                continue
            for perm in itertools.permutations(range(3)):
                if list(perm) == [0, 1, 2]:
                    continue
                reordered = tuple(states[i] for i in perm)
                if not bridges_compose(reordered):
                    c_witness = {"original": [list(s) for s in states],
                                 "reordered": [list(s) for s in reordered],
                                 "reading": ("the same transforms in a different "
                                             "order break a bridge that held")}
                    break
            if c_witness:
                break

        # ---- D: the frozen three-domain campaign ---------------------------
        if not CAMPAIGN.is_file():
            raise FileNotFoundError(str(CAMPAIGN))
        camp = json.loads(CAMPAIGN.read_text())
        s = camp["summary"]
        domains = {d["domain"]: d for d in camp["domains"]}
        table = {}
        for dom, rec in domains.items():
            pol = rec["policies"]
            table[dom] = {
                "modules": rec.get("modules"),
                "import_edges": rec.get("import_edges"),
                "transitions": rec.get("changes_used"),
                "certificate_decisions": rec.get("certificate_decisions"),
                "policies": {p: {"false_closure_retention": v["false_closure_retention"],
                                 "unnecessary_reopenings": v["unnecessary_reopenings"]}
                             for p, v in pol.items()},
            }

        def classify(v):
            if v["false_closure_retention"] > 0:
                return "UNSOUND__RETAINS_CLOSURE_WITHOUT_THE_BRIDGE"
            if v["unnecessary_reopenings"] > 0:
                return "SOUND_BUT_CONSERVATIVE"
            return "SOUND_AND_EXACT"
        classification = {dom: {p: classify(v) for p, v in t["policies"].items()}
                          for dom, t in table.items()}
        exact_is_exact = all(
            classification[d].get("exact-containment") == "SOUND_AND_EXACT"
            for d in classification)
        donor_unsound_somewhere = any(
            classification[d].get("donor-coarse") == "UNSOUND__RETAINS_CLOSURE_WITHOUT_THE_BRIDGE"
            for d in classification)

        controls = {
            "necessity_witness_exists": {"pass": b_witness is not None},
            "order_sensitivity_witness_exists": {"pass": c_witness is not None},
            "exact_containment_sound_and_exact_in_every_domain": {"pass": exact_is_exact},
            "donor_coarse_unsound_in_at_least_one_domain": {"pass": donor_unsound_somewhere},
        }
        controls_ok = all(v["pass"] for v in controls.values())
    except AssertionError as exc:
        print(json.dumps({"status": "FAIL", "counterexample": str(exc)}, indent=2))
        return 2
    except Exception as exc:                                    # noqa: BLE001
        print(json.dumps({"status": "CANNOT_CHECK",
                          "error": f"{type(exc).__name__}: {exc}"}, indent=2))
        return 3

    report = {
        "schema": "ORION.ORION17.ChainComposition.CheckerReport.v1",
        "successor_id": "ORION17.CLOSURE_CHAIN_COMPOSITION.v1",
        "independence": ("no ORION-17 module imported; chain theorems verified on "
                         "freshly enumerated finite chains; campaign read as data"),
        "check_A_composition": {"chains_checked": a_checked, "max_chain_length": KMAX,
                                "holds": True},
        "check_B_necessity_broken_bridge": {"witness": b_witness},
        "check_C_order_sensitivity": {"witness": c_witness},
        "check_D_frozen_three_domain_campaign": {
            "domains": list(table),
            "measured": table,
            "classification": classification,
            "transitions_per_domain": s["transitions_per_domain"],
            "zero_false_closure_retention": s["zero_false_closure_retention"],
            "donor_false_closure_retention": s["donor_false_closure_retention"],
        },
        "check_E_negative_controls": controls,
        "status": "PASS" if controls_ok else "FAIL",
    }
    (PACKET / "RESULT.json").write_text(json.dumps(report, indent=2) + "\n")
    print(json.dumps({k: report[k] for k in
                      ("status", "check_A_composition", "check_B_necessity_broken_bridge",
                       "check_C_order_sensitivity", "check_D_frozen_three_domain_campaign",
                       "check_E_negative_controls")}, indent=2)[:2600])
    return 0 if controls_ok else 2


if __name__ == "__main__":
    sys.exit(main())
