#!/usr/bin/env python3
"""Independent from-primitives verifier for QG-27 (protocol gate G7).

Independent of `qg27_cost_minimality`: it imports the committed DP and re-derives
the cost table, the letter span, the structural conclusion, the counterexample
that refutes the lane's own frozen criterion, and the exhibited rejection that
`criterion_binding` demanded. It never reads a number out of the receipt and
checks it against itself.

Usage: qg27_generic_verify.py [results.json]   Exit 0 ACCEPT, 1 REJECT.
"""

from __future__ import annotations

import hashlib
import json
import pathlib
import sys

HERE = pathlib.Path(__file__).resolve().parent
REPO = HERE.parents[1]
sys.path.insert(0, str(REPO / "research" / "extensions" / "orion-q"))

import max_r6i_exact_rank2_shared_tag_dp as r6i  # noqa: E402

DEFAULT = REPO / "research" / "extensions" / "orion-qg" / "QG27_COST_MINIMALITY_RESULTS.json"
PROTOCOL = HERE / "QG27_COST_MINIMALITY_PROTOCOL_V1.md"
INF = 1 << 40
CB_VERDICTS = {"PASS", "FAIL", "INDETERMINATE"}

FROZEN_CRITERION = (
    "QG27_COST_DP_IS_ALREADY_MINIMAL - 1024 classes at every R examined. "
    "The committed DP is tight for cost as well as feasibility."
)


def canonical(o) -> str:
    return json.dumps(o, sort_keys=True, separators=(",", ":"))


def sha_file(p: pathlib.Path) -> str:
    return hashlib.sha256(p.read_bytes()).hexdigest()


def crit_digest(text: str) -> str:
    return hashlib.sha256(" ".join(str(text).split()).encode("utf-8")).hexdigest()


def rebuild_cost(key) -> list[int]:
    costs, _ = r6i._local_table(tuple(key))
    return [int(c) if int(c) < int(r6i.INF) else INF for c in costs]


def span_rank(cost: list[int]) -> tuple[int, set[int]]:
    basis: list[int] = []
    for d, c in enumerate(cost):
        if c >= INF:
            continue
        cur = d
        for b in basis:
            cur = min(cur, cur ^ b)
        if cur:
            basis.append(cur)
            basis.sort(reverse=True)
    span = {0}
    for b in basis:
        span |= {e ^ b for e in span}
    return len(basis), span


def cost_to_go_first(cost: list[int], accepting: set[int]) -> list[int]:
    cur = [0 if s in accepting else INF for s in range(r6i.STATES)]
    return [min((c + cur[s ^ d] for d, c in enumerate(cost)
                 if c < INF and cur[s ^ d] < INF), default=INF)
            for s in range(r6i.STATES)]


def check_criterion_binding(records, frozen_texts) -> list:
    """Reimplemented, not imported: this verifier declares itself independent."""
    bad = []
    if not isinstance(records, list) or not records:
        return [[-1, "criterion_binding block missing or empty"]]
    for i, rec in enumerate(records):
        if not isinstance(rec, dict):
            bad.append([i, "record is not an object"]); continue
        frozen = rec.get("frozen_criterion_digest")
        applied = rec.get("applied_criterion_digest")
        verdict = rec.get("reported_verdict")
        if not frozen:
            bad.append([i, "frozen_criterion_digest missing"]); continue
        if not applied:
            bad.append([i, "applied_criterion_digest missing -- silence is not sameness"]); continue
        if verdict not in CB_VERDICTS:
            bad.append([i, f"reported_verdict {verdict!r} invalid"]); continue
        text = frozen_texts.get(rec.get("criterion"))
        if text is None:
            bad.append([i, "criterion not one this verifier holds frozen text for"]); continue
        if crit_digest(text) != frozen:
            bad.append([i, "frozen_criterion_digest does not match the frozen protocol text"]); continue
        if applied == frozen:
            # Concealment is the cheapest bypass: set the applied digest equal to
            # the frozen one and none of the checks below ever run. This verifier
            # ACCEPTed exactly that tampered receipt until this existed.
            contradictions = [f for f in ("deviation", "verdict_under_frozen_criterion",
                                          "exhibited_rejection_ref") if rec.get(f)]
            if contradictions:
                bad.append([i, "declares the criterion unchanged yet carries "
                               f"{contradictions}; the change is being concealed"])
            continue
        if verdict != "PASS":
            continue
        dev = rec.get("deviation")
        if not isinstance(dev, dict) or not str(dev.get("description", "")).strip() \
                or not str(dev.get("rationale", "")).strip():
            bad.append([i, "PASS under a changed criterion without a full deviation"]); continue
        counter = rec.get("verdict_under_frozen_criterion")
        if counter not in CB_VERDICTS:
            bad.append([i, "PASS under a changed criterion without the counterfactual"]); continue
        if counter != "PASS" and not str(rec.get("exhibited_rejection_ref", "")).strip():
            bad.append([i, "frozen criterion would not have passed and no exhibited rejection is bound"])
    return bad


def main(argv) -> int:
    path = pathlib.Path(argv[1]) if len(argv) > 1 else DEFAULT
    res = json.loads(path.read_text())
    checks, failed = {}, []

    def record(name, ok, detail=None):
        checks[name] = {"ok": bool(ok), "detail": detail}
        if not ok:
            failed.append(name)

    record("protocol_sha256_recomputes", sha_file(PROTOCOL) == res.get("protocol_sha256"))
    record("result_digest_recomputes",
           hashlib.sha256(canonical({k: v for k, v in res.items()
                                     if k != "result_digest"}).encode()).hexdigest()
           == res.get("result_digest"))

    cost = rebuild_cost(res["frozen_key"])
    record("cost_table_rebuilt_from_the_committed_dp",
           sum(1 for c in cost if c < INF) == res["letters_with_finite_cost"]
           and len({c for c in cost if c < INF}) == res["distinct_finite_costs"],
           {"finite": sum(1 for c in cost if c < INF)})

    accepting = {int(p) for p, _ in r6i._accepting_states()}
    record("accepting_states_recomputed", sorted(accepting) == res["accepting_states"])

    rank, span = span_rank(cost)
    red = res["cost_mergeability_reduces_to_feasibility"]
    record("letters_span_rank_recomputed", rank == red["letters_span_rank"], {"recomputed": rank})
    record("subgroup_order_is_2_to_the_rank",
           len(span) == red["reachable_subgroup_order"] == 2 ** rank)
    # Recompute separation the way the CLAIM requires: the accepting set's
    # translation stabiliser must be trivial. Checking that every state reaches
    # one accepting state is implied by a full span and tests nothing.
    stabiliser = sorted(
        d for d in range(r6i.STATES) if {a ^ d for a in accepting} == accepting)
    separated = (len(span) == r6i.STATES) and stabiliser == [0]
    record("accepting_set_stabiliser_recomputed",
           stabiliser == red["accepting_set_translation_stabiliser"]
           and red["stabiliser_is_trivial"] == (stabiliser == [0]),
           {"recomputed": stabiliser})
    record("every_state_separated_recomputed",
           separated == red["every_state_separated_from_every_other"])

    record("costs_are_state_independent",
           len(r6i._local_table(tuple(res["frozen_key"]))[0]) == r6i.STATES
           and res["costs_are_state_independent"]["table_length"] == r6i.STATES)

    # the lane's own frozen criterion must really be refuted by the pair it names
    C1 = cost_to_go_first(cost, accepting)
    ref = res["frozen_criterion_refutation"]
    record("frozen_criterion_refutation_holds",
           bool(ref.get("refuted"))
           and C1[ref["state_a"]] == ref["optimal_cost_to_go_a"]
           and C1[ref["state_b"]] == ref["optimal_cost_to_go_b"]
           and C1[ref["state_b"]] != C1[ref["state_a"]],
           {"recomputed_a": C1[ref["state_a"]], "recomputed_b": C1[ref["state_b"]]})

    # and the exhibited rejection must really reject
    ex = res["exhibited_rejection"]
    deficient = [c if (d & 0b1111111000) == 0 and c < INF else INF
                 for d, c in enumerate(cost)]
    drank, dspan = span_rank(deficient)
    # Separation under the rank-deficient construction, recomputed the same way
    # the claim requires -- span full AND stabiliser trivial -- not by reachability.
    deficient_separated = (len(dspan) == r6i.STATES) and stabiliser == [0]
    record("exhibited_rejection_really_rejects",
           drank == ex["letters_span_rank"]
           and len(dspan) == ex["reachable_subgroup_order"]
           and deficient_separated is False
           and ex["every_state_separated"] is False,
           {"recomputed_rank": drank, "recomputed_order": len(dspan),
            "recomputed_separated": deficient_separated})

    bad = check_criterion_binding(res.get("criterion_binding"),
                                  {"protocol section 6, QG27_COST_DP_IS_ALREADY_MINIMAL":
                                   FROZEN_CRITERION})
    record("criterion_binding_gate_reimplemented", not bad, {"bad": bad})

    expected = ("QG27_COST_DP_IS_ALREADY_MINIMAL" if separated
                else "QG27_COST_REDUCTION_CANDIDATE__UNPROVEN_BEYOND_HORIZON")
    record("terminal_follows_from_the_recomputed_numbers",
           res["terminal"] == expected, {"expected": expected})

    record("no_efficiency_claim_g4",
           "no reduction is claimed" in res["g4_no_efficiency_claim"])
    record("timing_appears_in_no_argument_g3",
           "appears in no argument" in res["g3_timing_note"])
    record("scope_limit_declares_the_single_key",
           "ONE cost-table key" in res["scope_limit"]
           and res["frozen_key_is_the_only_key_used"] is True)
    record("authority_ceiling_not_r6",
           res["authority_ceiling"] == "NOT_R6"
           and res["novelty_authority"] is False
           and res["physical_quantum_advantage_claim"] is False
           and res["protected_subject_read"] is False
           and res["chemistry_sources_read"] is False)

    verdict = "ACCEPT" if not failed else "REJECT"
    out = {
        "verifier": "qg27_generic_verify",
        "independent_of": ["qg27_cost_minimality", "orion_research_harness"],
        "results_file": str(path),
        "results_sha256": sha_file(path),
        "terminal_under_review": res["terminal"],
        "check_count": len(checks),
        "checks": checks,
        "failed_checks": failed,
        "scope_note": (
            "establishes cost-minimality for the time-invariant automaton obtained "
            "by freezing ONE cost-table key. Says nothing about the key-varying DP "
            "the programme runs, and nothing about any algorithm's speed."
        ),
        "verdict": verdict,
    }
    print(json.dumps(out, indent=2, sort_keys=True))
    print(f"QG27_GENERIC_VERIFY={verdict}")
    return 0 if verdict == "ACCEPT" else 1


if __name__ == "__main__":
    sys.exit(main(sys.argv))
