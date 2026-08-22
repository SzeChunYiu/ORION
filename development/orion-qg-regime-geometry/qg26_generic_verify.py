#!/usr/bin/env python3
"""Independent from-primitives verifier for QG-26 (protocol gate G7).

Independent of `qg26_nerode_minimality`: it imports the committed DP module and
re-derives the alphabet, the rank, the subgroup and the minimal-DFA block count
itself. It never reads a number out of the receipt and checks it against itself.

Usage: qg26_generic_verify.py [results.json]
Exit 0 on ACCEPT, 1 on REJECT.
"""

from __future__ import annotations

import hashlib
import itertools
import json
import pathlib
import sys

HERE = pathlib.Path(__file__).resolve().parent
REPO = HERE.parents[1]
sys.path.insert(0, str(REPO / "research" / "extensions" / "orion-q"))

import max_r6i_exact_rank2_shared_tag_dp as r6i  # noqa: E402

DEFAULT = REPO / "research" / "extensions" / "orion-qg" / "QG26_NERODE_MINIMALITY_RESULTS.json"
PROTOCOL = HERE / "QG26_NERODE_MINIMALITY_PROTOCOL_V1.md"


def canonical(obj) -> str:
    return json.dumps(obj, sort_keys=True, separators=(",", ":"))


def sha_file(path: pathlib.Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def rebuild_alphabet() -> list[int]:
    letters = set()
    for values in itertools.product(range(4), repeat=6):
        code = 0
        for v in values:
            code = code * 4 + v
        letters.add(int(r6i._DELTA[code]))
    return sorted(letters)


def rank_and_span(letters: list[int]) -> tuple[int, set[int]]:
    basis: list[int] = []
    for value in letters:
        cur = value
        for b in basis:
            cur = min(cur, cur ^ b)
        if cur:
            basis.append(cur)
            basis.sort(reverse=True)
    span = {0}
    for b in basis:
        span |= {e ^ b for e in span}
    return len(basis), span


def minimal_blocks(states: list[int], letters: list[int], accepting: int) -> int:
    """Moore refinement, written independently of the analyzer's implementation."""
    idx = {s: i for i, s in enumerate(states)}
    succ = [[idx[s ^ a] for a in letters] for s in states]
    part = [int(s == accepting) for s in states]
    while True:
        seen: dict = {}
        nxt = []
        for i in range(len(states)):
            key = (part[i],) + tuple(part[j] for j in succ[i])
            nxt.append(seen.setdefault(key, len(seen)))
        if nxt == part:
            return len(set(part))
        part = nxt


def main(argv) -> int:
    path = pathlib.Path(argv[1]) if len(argv) > 1 else DEFAULT
    res = json.loads(path.read_text())
    checks: dict = {}
    failed: list[str] = []

    def record(name, ok, detail=None):
        checks[name] = {"ok": bool(ok), "detail": detail}
        if not ok:
            failed.append(name)

    record("protocol_sha256_recomputes",
           sha_file(PROTOCOL) == res.get("protocol_sha256"))
    record("result_digest_recomputes",
           hashlib.sha256(
               canonical({k: v for k, v in res.items() if k != "result_digest"}).encode()
           ).hexdigest() == res.get("result_digest"))

    letters = rebuild_alphabet()
    record("alphabet_reenumerated_from_the_committed_dp",
           letters == list(res["alphabet"]["letters"]),
           {"recomputed_distinct": len(letters)})
    record("enumeration_complete",
           res["alphabet"]["option_rows_enumerated"] == 4 ** 6
           and res["alphabet"]["complete"] is True)

    rank, span = rank_and_span(letters)
    record("gf2_rank_recomputed",
           rank == res["structural_method"]["gf2_rank_of_alphabet"],
           {"recomputed": rank})
    record("nerode_index_is_2_to_the_rank",
           2 ** rank == res["structural_method"]["nerode_index"] == len(span))

    record("committed_state_count_matches_the_module",
           int(r6i.STATES) == res["committed_state_count"],
           {"module": int(r6i.STATES)})

    states = sorted(span)
    mech_ok = True
    recomputed = {}
    for target, claim in res["mechanical_method"].items():
        t = int(target)
        if t in span:
            blocks = minimal_blocks(states, letters, t)
            recomputed[target] = blocks
            if claim.get("blocks") != blocks:
                mech_ok = False
        elif claim.get("blocks") is not None:
            mech_ok = False
    record("moore_refinement_reproduced", mech_ok, {"recomputed": recomputed})

    record("methods_agree_as_claimed",
           res["methods_agree"] is (
               len(set(recomputed.values())) == 1
               and set(recomputed.values()) == {2 ** rank}))

    expected_terminal = (
        "QG26_SYNDROME_IS_NERODE_MINIMAL" if 2 ** rank == int(r6i.STATES)
        else "QG26_SYNDROME_IS_LOOSE__FACTOR_MEASURED"
    )
    record("terminal_follows_from_the_recomputed_numbers",
           res["terminal"] == expected_terminal, {"expected": expected_terminal})
    record("looseness_factor_consistent",
           res["looseness_factor"] == int(r6i.STATES) // (2 ** rank))

    record("no_speed_claim_g3",
           "nothing here shows any algorithm is faster" in res["g3_scope_statement"])
    record("authority_ceiling_not_r6",
           res["authority_ceiling"] == "NOT_R6"
           and res["novelty_authority"] is False
           and res["physical_quantum_advantage_claim"] is False
           and res["protected_subject_read"] is False
           and res["chemistry_sources_read"] is False)

    verdict = "ACCEPT" if not failed else "REJECT"
    out = {
        "verifier": "qg26_generic_verify",
        "independent_of": ["qg26_nerode_minimality", "orion_research_harness", "numpy"],
        "results_file": str(path),
        "results_sha256": sha_file(path),
        "terminal_under_review": res["terminal"],
        "check_count": len(checks),
        "checks": checks,
        "failed_checks": failed,
        "scope_note": (
            "this verifier establishes the Nerode index of the FEASIBILITY language of "
            "the committed R6I state space, by two independent recomputations. It "
            "establishes nothing about the min-plus cost DP's running time."
        ),
        "verdict": verdict,
    }
    print(json.dumps(out, indent=2, sort_keys=True))
    print(f"QG26_GENERIC_VERIFY={verdict}")
    return 0 if verdict == "ACCEPT" else 1


if __name__ == "__main__":
    sys.exit(main(sys.argv))
