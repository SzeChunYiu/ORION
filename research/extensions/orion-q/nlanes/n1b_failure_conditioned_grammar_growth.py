"""ORION-Q N1-B FIRST EXECUTION: hierarchical grammar under matched bounded search.

Frozen protocol: development/orion-q-nlane-closure/N1_B_PROTOCOL.md (issue #674, family N1-B).
N1-B had no prior recorded outcome in the issue thread; this is its first execution. Deterministic
exact-synthetic diagnostic (S_12 word world); no P10, novelty, or real-quantum authority.

Run:
    python research/extensions/orion-q/nlanes/n1b_failure_conditioned_grammar_growth.py
"""

from __future__ import annotations

import json
import os
from collections import Counter, deque

SCHEMA = "ORIONQ.N1B_FailureConditionedGrammarGrowth.v1"
AUTHORITY = "N1B_DIAGNOSTIC__NO_P10_AUTHORITY__NO_NOVELTY_AUTHORITY__EXACT_SYNTHETIC_ONLY"

N = 12
IDENT = tuple(range(N))
A = tuple((i + 1) % N for i in range(N))                      # 12-cycle
B = tuple([1, 0] + list(range(2, N)))                          # (0 1)
C = tuple([0, 1, 5, 3, 4, 2, 7, 6] + list(range(8, N)))        # (2 5)(6 7)
GEN = {"a": A, "b": B, "c": C}
GSTAR_WORD = ("a", "b", "a", "c")
BUDGET = 400_000
RANDOM_MACRO_WORD = ("c", "b", "b", "a")

ORIGIN_SPECS = [("a", "b"), ("b", "c"), ("c", "a"), ("aa", "b"), ("ab", "c"), ("ba", "a"),
                ("bc", "b"), ("ca", "c"), ("cb", "a"), ("a", "bb"), ("b", "aa"), ("c", "ab")]
D_DEV = ["a", "b", "c"]
K_DEV = (4, 5, 6)
D_TEST = ["aa", "ab", "ac", "ba", "bc", "ca"]  # amended pre-outcome: see protocol amendment note
K_TEST = (5, 6)


def comp(f: tuple, g: tuple) -> tuple:
    return tuple(f[g[i]] for i in range(N))


def inv(p: tuple) -> tuple:
    out = [0] * N
    for i, v in enumerate(p):
        out[v] = i
    return tuple(out)


def eval_word(word, lib) -> tuple:
    r = IDENT
    for s in word:
        r = comp(r, lib[s])
    return r


def budgeted_bfs(lib: dict, budget: int) -> tuple[dict, int]:
    """Deduplicated BFS from identity; returns {state: shortest word}, expansions used."""
    syms = sorted(lib)
    seen = {IDENT: ()}
    dq = deque([IDENT])
    expansions = 0
    while dq and expansions < budget:
        s = dq.popleft()
        w = seen[s]
        for sym in syms:
            if expansions >= budget:
                break
            expansions += 1
            ns = comp(s, lib[sym])
            if ns not in seen:
                seen[ns] = w + (sym,)
                dq.append(ns)
    return seen, expansions


def rewrite(word: list, gram: tuple, name: str) -> list:
    out, i, n = [], 0, len(gram)
    while i < len(word):
        if tuple(word[i:i + n]) == gram:
            out.append(name)
            i += n
        else:
            out.append(word[i])
            i += 1
    return out


def ngram_counts(corpus: list[list]) -> Counter:
    cnt: Counter = Counter()
    for w in corpus:
        for n in (2, 3, 4):
            for i in range(len(w) - n + 1):
                cnt[tuple(w[i:i + n])] += 1
    return cnt


def expand_to_primitives(sym: str, defs: dict) -> tuple:
    if sym in GEN:
        return (sym,)
    out: tuple = ()
    for s in defs[sym]:
        out += expand_to_primitives(s, defs)
    return out


def solve_count(seen: dict, tasks: list) -> int:
    return sum(t in seen for t in tasks)


def main() -> None:
    gstar = eval_word(GSTAR_WORD, GEN)
    gk = [IDENT]
    for _ in range(8):
        gk.append(comp(gk[-1], gstar))

    origin_targets = [eval_word(tuple(w1) + GSTAR_WORD + tuple(w2), GEN) for w1, w2 in ORIGIN_SPECS]
    dev_tasks = {(k, d): comp(gk[k], eval_word(tuple(d), GEN)) for k in K_DEV for d in D_DEV}
    test_tasks = [comp(gk[k], eval_word(tuple(d), GEN)) for k in K_TEST for d in D_TEST]
    all_targets = origin_targets + list(dev_tasks.values()) + test_tasks
    assert len(set(test_tasks)) == len(test_tasks)
    assert not set(test_tasks) & set(origin_targets), "origin leaked into held-out"
    assert not set(test_tasks) & set(dev_tasks.values()), "dev leaked into held-out"

    # --- Arm 1: primitive enumeration (one budgeted BFS serves all tasks at matched budget).
    prim_seen, prim_exp = budgeted_bfs(GEN, BUDGET)
    assert prim_seen.get(gstar) is not None and len(prim_seen[gstar]) == 4, "g* geodesic != 4"
    prim_origin = solve_count(prim_seen, origin_targets)
    prim_test = solve_count(prim_seen, test_tasks)
    prim_dev = {kd: (t in prim_seen) for kd, t in dev_tasks.items()}

    # --- Arm 2: library-learning parent, three frozen variants, entitled to solved ORIGIN traces.
    traces = [list(prim_seen[t]) for t in origin_targets if t in prim_seen]
    parent_variants: dict[str, dict] = {}

    # P1: iterative DL-greedy compression, up to 3 rounds.
    corpus = [list(w) for w in traces]
    defs: dict[str, tuple] = {}
    promoted = []
    for rnd in range(3):
        cnt = ngram_counts(corpus)
        best, best_gain = None, 0
        for g in sorted(cnt):  # deterministic tie-break: lexicographic scan, strict improvement
            gain = (len(g) - 1) * cnt[g] - len(g)
            if gain > best_gain:
                best, best_gain = g, gain
        if best is None:
            break
        name = f"M{rnd + 1}"
        defs[name] = best
        promoted.append((name, best, best_gain))
        corpus = [rewrite(w, best, name) for w in corpus]
    lib_p1 = dict(GEN)
    p1_macros = {}
    for name in defs:
        word = expand_to_primitives(name, defs)
        lib_p1[name] = eval_word(word, GEN)
        p1_macros[name] = "".join(word)
    seen_p1, exp_p1 = budgeted_bfs(lib_p1, BUDGET)
    parent_variants["P1_DL_ITERATIVE"] = {
        "macros_primitive_words": p1_macros,
        "held_out_solved": solve_count(seen_p1, test_tasks),
        "search_expansions": exp_p1,
    }

    # P2: single most frequent 4-gram (length-prior variant).
    cnt0 = ngram_counts([list(w) for w in traces])
    four = sorted((g for g in cnt0 if len(g) == 4), key=lambda g: (-cnt0[g], g))
    p2_word = four[0]
    lib_p2 = dict(GEN)
    lib_p2["M"] = eval_word(p2_word, GEN)
    seen_p2, exp_p2 = budgeted_bfs(lib_p2, BUDGET)
    parent_variants["P2_TOP_4GRAM"] = {
        "macros_primitive_words": {"M": "".join(p2_word)},
        "count": cnt0[p2_word],
        "held_out_solved": solve_count(seen_p2, test_tasks),
        "search_expansions": exp_p2,
    }

    # P3: single best gram by one-shot DL gain.
    p3_word = min(sorted(cnt0), key=lambda g: -((len(g) - 1) * cnt0[g] - len(g)))
    lib_p3 = dict(GEN)
    lib_p3["M"] = eval_word(p3_word, GEN)
    seen_p3, exp_p3 = budgeted_bfs(lib_p3, BUDGET)
    parent_variants["P3_TOP_DL_SINGLE"] = {
        "macros_primitive_words": {"M": "".join(p3_word)},
        "held_out_solved": solve_count(seen_p3, test_tasks),
        "search_expansions": exp_p3,
    }

    parent_max = max(v["held_out_solved"] for v in parent_variants.values())

    # --- Arm 3: ORION failure-conditioned growth (no solved traces).
    quotients = set()
    used_pairs = []
    for d in D_DEV:
        for k in K_DEV[:-1]:
            t_lo, t_hi = dev_tasks[(k, d)], dev_tasks[(k + 1, d)]
            if t_lo not in prim_seen and t_hi not in prim_seen:  # both certified failures
                quotients.add(comp(t_hi, inv(t_lo)))
                used_pairs.append([k, k + 1, d])
    quotient_certified = len(used_pairs) >= 2 and len(quotients) == 1
    orion_result: dict = {"usable_failed_pairs": used_pairs, "distinct_quotients": len(quotients)}
    if quotient_certified:
        q = next(iter(quotients))
        q_word = prim_seen.get(q)  # realized from the already-paid primitive BFS table
        assert q_word is not None, "quotient word not realizable within paid budget"
        lib_o = dict(GEN)
        lib_o["Q"] = q
        seen_o, exp_o = budgeted_bfs(lib_o, BUDGET)
        orion_test = solve_count(seen_o, test_tasks)
        orion_result.update({
            "quotient_primitive_word": "".join(q_word),
            "quotient_equals_gstar": bool(q == gstar),
            "held_out_solved": orion_test,
            "search_expansions": exp_o,
        })
    else:
        orion_test = 0
        orion_result["held_out_solved"] = 0

    # --- Arm 4: random-macro hostile control.
    lib_r = dict(GEN)
    lib_r["R"] = eval_word(RANDOM_MACRO_WORD, GEN)
    seen_r, _ = budgeted_bfs(lib_r, BUDGET)
    random_test = solve_count(seen_r, test_tasks)

    p1_elems = {lib_p1[n] for n in p1_macros}
    orion_elem_in_p1 = bool(quotient_certified and next(iter(quotients)) in p1_elems)

    gates = {
        "G1_WORLD_VALID": bool(prim_origin == 12 and prim_test == 0),
        "G2_RANDOM_MACRO_FAILS": bool(random_test == 0),
        "G3_QUOTIENT_CERTIFIED": bool(quotient_certified),
        "G4_ORION_MACRO_EQUALS_A_P1_COMPRESSION_MACRO": orion_elem_in_p1,
        "G5_PARENT_MAX_GEQ_ORION": bool(parent_max >= orion_test),
    }
    if not (gates["G1_WORLD_VALID"] and gates["G2_RANDOM_MACRO_FAILS"]):
        terminal = "N1B_WORLD_INVALID"
    elif parent_max >= orion_test:
        terminal = "N1B_LIBRARY_LEARNING_SUFFICIENT"
    elif orion_test > parent_max and quotient_certified:
        terminal = "N1B_FAILURE_CONDITIONED_LANGUAGE_GROWTH_VALUE"
    else:
        terminal = "N1B_NO_REACH"

    result = {
        "schema": SCHEMA,
        "issue": 674,
        "family": "N1-B",
        "execution_status": "FIRST_EXECUTION (no prior recorded outcome in issue #674 thread)",
        "protocol": "development/orion-q-nlane-closure/N1_B_PROTOCOL.md",
        "date": "2026-08-21",
        "deterministic": True,
        "world": {
            "carrier": "S_12 word world, primitives {a,b,c}, hidden gadget g*=eval('abac')",
            "budget_expansions_per_library": BUDGET,
            "origin_tasks": len(origin_targets),
            "dev_tasks": len(dev_tasks),
            "held_out_tasks": len(test_tasks),
            "held_out_amendment": "aliased decorations {bb,cb,cc} removed pre-outcome; see protocol amendment note",
        },
        "arms": {
            "PRIMITIVE_ENUMERATION": {
                "origin_solved_of_12": prim_origin,
                "origin_trace_lengths": sorted(len(prim_seen[t]) for t in origin_targets if t in prim_seen),
                "dev_failed": sum(1 for v in prim_dev.values() if not v),
                "dev_total": len(prim_dev),
                "held_out_solved": prim_test,
                "search_expansions": prim_exp,
            },
            "LIBRARY_LEARNING_PARENT": {
                "variants": parent_variants,
                "held_out_solved_max": parent_max,
            },
            "ORION_FAILURE_CONDITIONED_GROWTH": orion_result,
            "RANDOM_MACRO_CONTROL": {"held_out_solved": random_test},
        },
        "gates": gates,
        "terminal": terminal,
        "authority": AUTHORITY,
        "claim_boundary": (
            "Exact-synthetic group-word diagnostic only. Whatever the terminal, DreamCoder/Stitch/"
            "library-learning and gadget-learning remain acknowledged parents; inter-instance "
            "quotienting is adjacent to known abduction/CEGIS-style reasoning; no novelty, P10, or "
            "real-quantum authority is granted."
        ),
    }

    out_path = os.path.join(os.path.dirname(os.path.abspath(__file__)), "N1_B_GRAMMAR_GROWTH_RESULTS.json")
    with open(out_path, "w") as fh:
        json.dump(result, fh, indent=2, sort_keys=True)
        fh.write("\n")
    print("ORIONQ_N1B_GRAMMAR_GROWTH=" + json.dumps(result, sort_keys=True))


if __name__ == "__main__":
    main()
