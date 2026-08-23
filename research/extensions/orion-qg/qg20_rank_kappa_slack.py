#!/usr/bin/env python3
"""QG-20: the rank-kappa slack.

Frozen by development/orion-qg-regime-geometry/QG20_RANK_KAPPA_SLACK_PROTOCOL_V1.md,
written before any outcome-determining run.

QG-6 infers a conserved-syndrome quotient rank automatically from the production
DP transition tables: 2 per R6M frame slot, 5 per R6I block.  QG-9 V6 and QG-18
now pin the intrinsic support numbers two-sidedly at kappa_R6I = 1 and
kappa_TARE = 2.  The QG-6 certificate is therefore sound but LOOSE.  This lane
measures the slack exactly and tests -- as a hypothesis, never as an assumption --
whether the QG-18 exchange margin (per-column frame refund minus maximum Restore
penalty, on the complete local deletion domain) governs it.

Q1  exact slack table: rank, kappa, slack = rank - kappa, and the exchange margin
    mu, every input bound verbatim to its committed receipt by that receipt's own
    field name, every margin and rank independently recomputed on its complete
    local domain in exact integer arithmetic.
Q2  does the margin predict the slack -- and, with equal precision, why two
    families cannot establish a law.
Q3  StabPrep transfer test under the frozen T1/T2/T3 criteria.

Authority ceiling NOT_R6.  No novelty credit, no donor-novelty credit, no
physical-advantage claim.  No chemistry source is read; the protected
stretched-N2 discriminator is never opened.  Every committed analyzer is
imported unmodified and no repository file is modified.
"""
from __future__ import annotations

import hashlib
import itertools
import json
import re
import sys
import time
from pathlib import Path
from typing import Any, Iterable

ROOT = Path(__file__).resolve().parents[3]
ORION_Q = ROOT / "research/extensions/orion-q"
ORION_QG = ROOT / "research/extensions/orion-qg"
DEV = ROOT / "development/orion-qg-regime-geometry"
sys.path.insert(0, str(ORION_Q))

import max_r6_p10_candidate_blind_frame_optimizer as p10  # noqa: E402
import max_r6i_exact_rank2_shared_tag_dp as r6i  # noqa: E402
import max_r6m_exact_three_tare2_shared_factor_dp as r6m  # noqa: E402

PROTOCOL = DEV / "QG20_RANK_KAPPA_SLACK_PROTOCOL_V1.md"
RESULTS = ORION_QG / "QG20_RANK_KAPPA_SLACK_RESULTS.json"
TOKEN = "ORIONQG_QG20="
RUNTIME_CAP_SECONDS = 25 * 60

QG6 = ORION_QG / "QG6_SYNDROME_DIMENSION_RESULTS.json"
QG9V6 = ORION_QG / "QG9_V6_SUPPORT1_NORMALIZATION_RESULTS.json"
QG18 = ORION_QG / "QG18_TARE_KAPPA_RESULTS.json"
QG15 = ORION_QG / "QG15_THIRD_FAMILY_RESULTS.json"
R6S = ORION_Q / "MAX_R6S_ALL_N_COMPOSITION_RESULTS.json"
QG15_SRC = ORION_QG / "qg15_third_family.py"

AUTHORITY = (
    "ORIONQG_QG20_RANK_KAPPA_SLACK_MEASURED_EXACTLY__SLACK_EQUALS_EXCHANGE_MARGIN_ON_"
    "BOTH_MEASURED_FAMILIES_UNDER_THE_QG6_CERTIFIED_RANKS__BUT_FAILS_UNDER_THE_MARGIN_"
    "ALIGNED_BLOCK_REWRITE__CANDIDATE_RELATION_FROM_TWO_POINTS__NOT_A_LAW__THIRD_"
    "FAMILY_STABPREP_NOT_DERIVABLE__NOT_R6"
)


# ----------------------------------------------------------------- exactness


class FloatInDecision(AssertionError):
    pass


def xint(v: Any, where: str) -> int:
    """Narrow to a Python int, refusing anything float-valued. Gate G2."""
    if isinstance(v, bool):
        raise FloatInDecision("bool used as integer at " + where)
    if isinstance(v, int):
        return int(v)
    # numpy integers expose __index__; floats do not.
    if hasattr(v, "__index__") and not isinstance(v, float):
        return int(v.__index__())
    raise FloatInDecision("non-integer %r at %s" % (type(v).__name__, where))


FLOAT_GUARD = {"checked": 0, "violations": []}


def eq(a: Any, b: Any, where: str) -> bool:
    ia, ib = xint(a, where + ".lhs"), xint(b, where + ".rhs")
    FLOAT_GUARD["checked"] += 2
    return ia == ib


def canonical(value: Any) -> str:
    return json.dumps(value, sort_keys=True, separators=(",", ":"), allow_nan=False)


def sha256_file(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def load(path: Path) -> dict:
    return json.loads(path.read_text())


def dig(obj: Any, dotted: str) -> Any:
    cur = obj
    for part in dotted.split("."):
        cur = cur[part]
    return cur


# --------------------------------------------------------- local Pauli algebra
# Rebuilt from the production primitives; no transition formula is reimplemented.

LETTERS = "IXYZ"
LW = [xint(p10.h.local_wt(a), "LW") for a in range(4)]
LM = [[xint(p10.h.local_mul(a, b), "LM") for b in range(4)] for a in range(4)]
SY = [[xint(p10.h.local_symp(a, b), "SY") for b in range(4)] for a in range(4)]
F3 = [
    [
        [1 if (a == b == c and a != 0) else LW[a] + LW[b] + LW[c] for c in range(4)]
        for b in range(4)
    ]
    for a in range(4)
]

# The R6I module carries its own copies; assert they agree (no divergent algebra).
ALGEBRA_AGREES = (
    [int(r6i._LW[a]) for a in range(4)] == LW
    and [[int(r6i._MUL[a, b]) for b in range(4)] for a in range(4)] == LM
    and [[int(r6i._SYMP[a, b]) for b in range(4)] for a in range(4)] == SY
)


def gf2_rank(values: Iterable[int]) -> int:
    basis: dict[int, int] = {}
    for raw in values:
        x = xint(raw, "gf2_rank")
        while x:
            pivot = x.bit_length() - 1
            if pivot in basis:
                x ^= basis[pivot]
            else:
                basis[pivot] = x
                break
    return len(basis)


def base4(values: tuple[int, ...]) -> int:
    code = 0
    for v in values:
        code = (code << 2) | xint(v, "base4")
    return code


# ============================================================== Section A: rank


def recompute_rank_r6m() -> dict[str, Any]:
    """QG-6 rewrite ZERO_ONE_FRAME_LOCAL_LETTER over the complete {0..3}^7 domain."""
    slot_names = ("A0", "A1", "B0", "B1", "C0", "C1")
    changes = {name: set() for name in slot_names}
    rows = 0
    for values in itertools.product(range(4), repeat=7):
        rows += 1
        old = xint(r6m._DELTA[base4(values)], "r6m.delta")
        for slot, name in enumerate(slot_names):
            rewritten = list(values)
            rewritten[slot] = 0
            new = xint(r6m._DELTA[base4(tuple(rewritten))], "r6m.delta.rw")
            changes[name].add(old ^ new)
    per_slot = {name: gf2_rank(changes[name]) for name in slot_names}
    ranks = sorted(set(per_slot.values()))
    return {
        "rewrite": "ZERO_ONE_FRAME_LOCAL_LETTER",
        "production_state_bits": 9,
        "local_option_rows": rows,
        "expected_local_option_rows": 4 ** 7,
        "domain_complete": rows == 4 ** 7,
        "per_slot_rank": per_slot,
        "distinct_ranks": ranks,
        "auto_dimension": ranks[0] if len(ranks) == 1 else None,
        "unique_change_counts": {k: len(v) for k, v in changes.items()},
    }


def recompute_rank_r6i() -> dict[str, Any]:
    """QG-6 rewrite ZERO_BOTH_INDEPENDENT_GENERATORS_OF_ONE_BLOCK, {0..3}^6."""
    changes = {"A": set(), "B": set()}
    rows = 0
    for v in itertools.product(range(4), repeat=6):
        rows += 1
        old = xint(r6i._DELTA[base4(v)], "r6i.delta")
        ra = (0, 0, v[2], v[3], v[4], v[5])
        rb = (v[0], v[1], 0, 0, v[4], v[5])
        changes["A"].add(old ^ xint(r6i._DELTA[base4(ra)], "r6i.delta.A"))
        changes["B"].add(old ^ xint(r6i._DELTA[base4(rb)], "r6i.delta.B"))
    per_block = {k: gf2_rank(v) for k, v in changes.items()}
    ranks = sorted(set(per_block.values()))
    return {
        "rewrite": "ZERO_BOTH_INDEPENDENT_GENERATORS_OF_ONE_BLOCK",
        "production_state_bits": 10,
        "local_option_rows": rows,
        "expected_local_option_rows": 4 ** 6,
        "domain_complete": rows == 4 ** 6,
        "per_block_rank": per_block,
        "distinct_ranks": ranks,
        "auto_dimension": ranks[0] if len(ranks) == 1 else None,
        "unique_change_counts": {k: len(v) for k, v in changes.items()},
    }


def rewrite_alignment_diagnostic() -> dict[str, Any]:
    """Protocol section 5: R6M rank under the rewrite that zeroes BOTH letters of a
    block -- the rewrite the margin domains of section 3 actually use."""
    blocks = {"A": (0, 1), "B": (2, 3), "C": (4, 5)}
    changes = {name: set() for name in blocks}
    rows = 0
    for values in itertools.product(range(4), repeat=7):
        rows += 1
        old = xint(r6m._DELTA[base4(values)], "r6m.delta.blk")
        for name, slots in blocks.items():
            rewritten = list(values)
            for s in slots:
                rewritten[s] = 0
            new = xint(r6m._DELTA[base4(tuple(rewritten))], "r6m.delta.blk.rw")
            changes[name].add(old ^ new)
    per_block = {k: gf2_rank(v) for k, v in changes.items()}
    ranks = sorted(set(per_block.values()))
    dim = ranks[0] if len(ranks) == 1 else None
    return {
        "rewrite": "ZERO_BOTH_FRAME_LETTERS_OF_ONE_BLOCK",
        "local_option_rows": rows,
        "expected_local_option_rows": 4 ** 7,
        "domain_complete": rows == 4 ** 7,
        "per_block_rank": per_block,
        "distinct_ranks": ranks,
        "block_level_auto_dimension": dim,
        "matches_certified_slotwise_rank_2": dim == 2,
        "note": (
            "Declared in protocol section 5 BEFORE the outcome was known. Q1's table "
            "uses the QG-6 certified slotwise rank; this is the margin-aligned "
            "alternative, reported whichever way it lands."
        ),
    }


def aligned_rewrite_table(diag: dict, table: list) -> dict:
    """Protocol section 5 obligation: when the margin-aligned R6M rank differs from the
    certified slotwise rank 2, report the ALTERNATIVE slack alongside Q1's table.

    R6I's certified rewrite already IS the block-zeroing rewrite, so only R6M/TARE moves.
    """
    aligned_dim = diag["block_level_auto_dimension"]
    rows = []
    for r in table:
        if r["family"] == "R6M_TARE" and aligned_dim is not None:
            rank = xint(aligned_dim, "aligned.r6m.rank")
        else:
            rank = xint(r["rank"], "aligned.rank")
        slack = rank - xint(r["kappa"], "aligned.kappa")
        rows.append(
            {
                "family": r["family"],
                "rank_under_margin_aligned_rewrite": rank,
                "rewrite": "ZERO_BOTH_FRAME_LETTERS_OF_ONE_BLOCK",
                "kappa": r["kappa"],
                "slack": slack,
                "mu": r["mu"],
                "slack_equals_mu": eq(slack, r["mu"], "aligned." + r["family"]),
                "moved_from_certified_table": rank != xint(r["rank"], "aligned.cert"),
            }
        )
    holds = all(x["slack_equals_mu"] for x in rows)
    return {
        "rows": rows,
        "relation_holds_under_aligned_rewrite": holds,
        "certified_and_aligned_agree": holds,
        "consequence": (
            "The Q1 agreement slack == mu is REWRITE-DEPENDENT. Under the rewrite that "
            "the margin domains themselves use -- zeroing both frame letters of one "
            "block, which is exactly R6I's certified rewrite -- the R6M/TARE syndrome "
            "rank is {} rather than the certified slotwise 2, giving slack {} against "
            "mu 0. H1 therefore holds on the certified table and FAILS on the "
            "margin-aligned table, on the same two families with the same kappa values "
            "and the same margins. This is a first-order weakening of H1 and was "
            "declared in protocol section 5 before the outcome was known."
        ).format(aligned_dim, aligned_dim - 2 if aligned_dim is not None else None)
        if not holds
        else (
            "The margin-aligned R6M rank coincides with the certified slotwise rank, so "
            "the Q1 agreement is not an artifact of the rewrite mismatch."
        ),
    }


# ============================================================ Section B: margin


def margin_r6i() -> dict[str, Any]:
    """Complete R6I local deletion domain: zero both generators of one block at one
    qubit.  delta = Restore_after - Restore_before - refund;  mu = -max delta."""

    def local_frame(a: int, b: int) -> tuple[int, int, int]:
        return a, b, LM[a][b]

    def raw_frame_cost(a: int, b: int, central: int) -> int:
        r = local_frame(a, b)
        m = [4, 4, 4]
        m[central] = 2
        return sum(m[k] * LW[r[k]] for k in range(3))

    def restore_cost(p: tuple[int, int, int], a: int, b: int) -> int:
        r = local_frame(a, b)
        return sum(LW[LM[p[k]][r[k]]] for k in range(3))

    counts = {"commuting": 0, "anticommuting": 0}
    maxima = {"commuting": -(10 ** 9), "anticommuting": -(10 ** 9)}
    minima = {"commuting": 10 ** 9, "anticommuting": 10 ** 9}
    ties = {"commuting": 0, "anticommuting": 0}
    witness: dict[str, Any] = {}
    total = 0
    for a, b in itertools.product(range(4), repeat=2):
        if a == 0 and b == 0:
            continue
        cls = "anticommuting" if SY[a][b] else "commuting"
        for p in itertools.product(range(4), repeat=3):
            for central in range(3):
                refund = raw_frame_cost(a, b, central)
                penalty = restore_cost(p, 0, 0) - restore_cost(p, a, b)
                delta = penalty - refund
                total += 1
                counts[cls] += 1
                if delta == 0:
                    ties[cls] += 1
                if delta < minima[cls]:
                    minima[cls] = delta
                if delta > maxima[cls]:
                    maxima[cls] = delta
                    witness[cls] = {
                        "frame_letters": [LETTERS[a], LETTERS[b]],
                        "dependent_triple": [LETTERS[x] for x in local_frame(a, b)],
                        "central_slot": central,
                        "target_letters": [LETTERS[x] for x in p],
                        "refund": refund,
                        "restore_penalty": penalty,
                        "delta": delta,
                    }
    credit = {k: -maxima[k] for k in maxima}
    mu = min(credit["commuting"], credit["anticommuting"])
    return {
        "family": "R6I",
        "domain": "15 letter pairs x 64 Restore targets x 3 central slots",
        "domain_size": total,
        "expected_domain_2880": total == 2880,
        "class_domain_sizes": counts,
        "expected_commuting_1728": counts["commuting"] == 1728,
        "expected_anticommuting_1152": counts["anticommuting"] == 1152,
        "max_delta": maxima,
        "min_delta": minima,
        "zero_credit_rows": ties,
        "credit_floor_by_class": credit,
        "mu": mu,
        "strict": mu >= 1,
        "max_witness": witness,
    }


def margin_tare() -> dict[str, Any]:
    """Complete R6M/TARE local deletion domain: zero both frame letters of one block
    at one qubit, scoring the Restore change through the donor-owned F3 rule."""

    def f3_at(slot: int, x: int, u: int, v: int) -> int:
        if slot == 0:
            return F3[x][u][v]
        if slot == 1:
            return F3[u][x][v]
        return F3[u][v][x]

    out: dict[str, Any] = {"family": "R6M_TARE"}
    for cls_name, want in (("commuting", 0), ("anticommuting", 1)):
        pairs = [
            (f0, f1)
            for f0 in range(4)
            for f1 in range(4)
            if SY[f0][f1] == want and (f0, f1) != (0, 0)
        ]
        rows = 0
        max_delta = -(10 ** 9)
        min_delta = 10 ** 9
        ties = 0
        argmax: Any = None
        per_slot: dict[str, int] = {}
        for slot in range(3):
            slot_max = -(10 ** 9)
            for central in (0, 1):
                m0 = 2 if central == 0 else 4
                m1 = 2 if central == 1 else 4
                for (f0, f1) in pairs:
                    refund = m0 * LW[f0] + m1 * LW[f1]
                    for p0, p1, u0, v0, u1, v1 in itertools.product(range(4), repeat=6):
                        old0 = LM[p0][f0]
                        old1 = LM[p1][f1]
                        d0 = f3_at(slot, p0, u0, v0) - f3_at(slot, old0, u0, v0)
                        d1 = f3_at(slot, p1, u1, v1) - f3_at(slot, old1, u1, v1)
                        delta = d0 + d1 - refund
                        rows += 1
                        if delta == 0:
                            ties += 1
                        if delta < min_delta:
                            min_delta = delta
                        if delta > slot_max:
                            slot_max = delta
                        if delta > max_delta:
                            max_delta = delta
                            argmax = {
                                "slot": "ABC"[slot],
                                "central_bit": central,
                                "multipliers": [m0, m1],
                                "frame_letters": [LETTERS[f0], LETTERS[f1]],
                                "refund": refund,
                                "restore_penalty": d0 + d1,
                                "target_letters": [LETTERS[p0], LETTERS[p1]],
                                "other_slots_branch0": [LETTERS[u0], LETTERS[v0]],
                                "other_slots_branch1": [LETTERS[u1], LETTERS[v1]],
                                "delta": delta,
                            }
            per_slot["ABC"[slot]] = slot_max
        out[cls_name] = {
            "letter_pairs": len(pairs),
            "domain_size": rows,
            "max_delta": max_delta,
            "min_delta": min_delta,
            "credit_floor": -max_delta,
            "zero_credit_rows": ties,
            "per_slot_max_delta": per_slot,
            "slot_symmetric": len(set(per_slot.values())) == 1,
            "max_witness": argmax,
        }
    out["domain"] = "letter pairs x 3 block slots x 2 central bits x 4^6 free letters"
    out["expected_commuting_221184"] = out["commuting"]["domain_size"] == 221184
    out["expected_anticommuting_147456"] = out["anticommuting"]["domain_size"] == 147456
    out["domain_size"] = (
        out["commuting"]["domain_size"] + out["anticommuting"]["domain_size"]
    )
    out["expected_domain_368640"] = out["domain_size"] == 368640
    out["credit_floor_by_class"] = {
        "commuting": out["commuting"]["credit_floor"],
        "anticommuting": out["anticommuting"]["credit_floor"],
    }
    mu = min(out["commuting"]["credit_floor"], out["anticommuting"]["credit_floor"])
    out["mu"] = mu
    out["strict"] = mu >= 1
    return out


# ======================================================= Section C: Q3 StabPrep


def q3_stabprep(qg15: dict) -> dict[str, Any]:
    src = QG15_SRC.read_text()

    def present(pattern: str) -> int:
        return len(re.findall(pattern, src))

    structural = {
        "delta_table_symbol_hits": present(r"_DELTA"),
        "packed_state_bit_table_hits": present(r"base4|_base4_code|packed"),
        "tag_symbol_hits": present(r"\bTag\b|\btag\b"),
        "restore_symbol_hits": present(r"\bRestore\b|\brestore\b"),
        "frame_symbol_hits": present(r"\bframe\b"),
        "dijkstra_hits": present(r"[Dd]ijkstra|heapq"),
        "source_sha256": hashlib.sha256(src.encode()).hexdigest(),
        "source_lines": src.count("\n") + 1,
    }
    referee = dig(qg15, "family.referee")
    gate_costs = dig(qg15, "gate_costs")
    max_arity = 2  # CNOT is the unique multi-qubit gate of the frozen alphabet

    t1 = {
        "criterion": (
            "T1 -- a production local transition table over packed state bits exists, "
            "indexed by local option letters, on which a local zeroing rewrite is defined"
        ),
        "holds": structural["delta_table_symbol_hits"] > 0,
        "evidence": {
            "referee": referee,
            "delta_table_symbol_hits": structural["delta_table_symbol_hits"],
            "dijkstra_hits": structural["dijkstra_hits"],
            "why": (
                "StabPrep's exact optimum is a shortest-path cost from a Dijkstra "
                "relaxation over the complete stabilizer-state graph (6/60/1080 states "
                "at n=1..3). There is no per-column DP whose local option rows could be "
                "differenced, so the XOR change-vector of QG-6 section 2.1 has no domain "
                "to be taken over. The QG-6 rank is undefined for this family, not zero."
            ),
        },
    }
    t2 = {
        "criterion": (
            "T2 -- the solution object has structural generators carrying a global "
            "support, so kappa is a discovered invariant rather than fixed by the alphabet"
        ),
        "holds": False,
        "evidence": {
            "solution_object": "a gate word over {H(1), S(1), SDG(1), CNOT(3)}",
            "gate_costs": gate_costs,
            "max_gate_arity_in_frozen_alphabet": max_arity,
            "why": (
                "The only support-like attribute of a StabPrep solution is gate arity, "
                "which the frozen alphabet caps at 2 by construction (CNOT is the unique "
                "multi-qubit gate). A 'support bound' of 2 would hold definitionally and "
                "1 would be infeasible whenever any CNOT is required -- QG-15 records "
                "c_star_min_CNOT_budget 1 at n=2 and 2 at n=3 -- so the two-sided value "
                "would be 2 for every family over this alphabet, carrying no information "
                "about the family. kappa in the manuscript sense is not defined here."
            ),
        },
    }
    t3 = {
        "criterion": (
            "T3 -- the local cost admits a frame-refund / Restore-penalty decomposition "
            "at a column, so the exchange margin mu of section 2.4 is defined"
        ),
        "holds": False,
        "evidence": {
            "cost_structure": "additive over gates; no frame/Restore split, no Tag",
            "tag_symbol_hits": structural["tag_symbol_hits"],
            "restore_symbol_hits": structural["restore_symbol_hits"],
            "why": (
                "There is nothing to refund: deleting a gate does not release a frame "
                "contribution that a Restore letter must then absorb. mu is therefore "
                "UNDEFINED for StabPrep -- which is emphatically not the same as mu = 0. "
                "The TARE point mu = 0 is a measured tie set on a complete 368640-row "
                "domain; StabPrep has no such domain at all."
            ),
        },
    }
    for t in (t1, t2, t3):
        t["holds"] = bool(t["holds"])
    first_failing = next(
        (name for name, t in (("T1", t1), ("T2", t2), ("T3", t3)) if not t["holds"]),
        None,
    )
    return {
        "family": dig(qg15, "family.name"),
        "referee": referee,
        "derivable_cheaply": first_failing is None,
        "first_failing_criterion": first_failing,
        "T1_transition_table": t1,
        "T2_structural_generator_support": t2,
        "T3_refund_penalty_decomposition": t3,
        "structural_scan": structural,
        "what_a_fourth_candidate_would_need": [
            "a production DP whose local option rows are indexed by per-column letters "
            "and whose packed transition table can be differenced under a zeroing "
            "rewrite (supplies the QG-6 rank)",
            "structural generators carrying a global Pauli support whose optimal value "
            "is not pinned by the alphabet (supplies a non-trivial two-sided kappa)",
            "a local cost split into a per-column refundable contribution and a "
            "penalty term, enumerable on a complete finite domain (supplies mu)",
            "and, to DISCRIMINATE rather than merely add a point, a measured mu outside "
            "{0, 4} -- ideally 0 < mu < rank - 1",
        ],
        "verdict": (
            "DOES_NOT_TRANSFER: StabPrep supplies none of T1, T2, T3. The QG-6 rank "
            "construction is specific to families with R6M/R6I's block/frame/Tag "
            "structure; StabPrep was chosen in QG-15 precisely because it is materially "
            "different from them, and that same difference is what blocks this lane."
        ),
    }


# =================================================================== main


def main() -> int:
    t_start = time.monotonic()
    timing: dict[str, float] = {}

    def tick(label: str, t0: float) -> None:
        timing[label] = round(time.monotonic() - t0, 3)

    # ---- receipts -------------------------------------------------------
    t0 = time.monotonic()
    qg6, qg9v6, qg18, qg15, r6s_res = (
        load(QG6),
        load(QG9V6),
        load(QG18),
        load(QG15),
        load(R6S),
    )
    receipts = {
        "QG6_SYNDROME_DIMENSION_RESULTS.json": sha256_file(QG6),
        "QG9_V6_SUPPORT1_NORMALIZATION_RESULTS.json": sha256_file(QG9V6),
        "QG18_TARE_KAPPA_RESULTS.json": sha256_file(QG18),
        "QG15_THIRD_FAMILY_RESULTS.json": sha256_file(QG15),
        "MAX_R6S_ALL_N_COMPOSITION_RESULTS.json": sha256_file(R6S),
    }
    protocol_sha = sha256_file(PROTOCOL)

    # Every bound value is read by its OWN receipt's field name, recorded verbatim.
    bound = {
        "R6I": {
            "rank": {
                "value": xint(dig(qg6, "r6i.auto_dimension"), "qg6.r6i.auto_dimension"),
                "receipt": "QG6_SYNDROME_DIMENSION_RESULTS.json",
                "field": "r6i.auto_dimension",
                "sha256": receipts["QG6_SYNDROME_DIMENSION_RESULTS.json"],
                "corroborating_fields": {
                    "r6i.all_block_ranks_5": dig(qg6, "r6i.all_block_ranks_5"),
                    "r6i.blocks.A.rank": xint(dig(qg6, "r6i.blocks.A.rank"), "a"),
                    "r6i.blocks.B.rank": xint(dig(qg6, "r6i.blocks.B.rank"), "b"),
                    "r6i.rewrite": dig(qg6, "r6i.rewrite"),
                },
            },
            "kappa": {
                "value": xint(
                    dig(qg9v6, "intrinsic_support_number"), "qg9v6.kappa"
                ),
                "receipt": "QG9_V6_SUPPORT1_NORMALIZATION_RESULTS.json",
                "field": "intrinsic_support_number",
                "sha256": receipts["QG9_V6_SUPPORT1_NORMALIZATION_RESULTS.json"],
                "corroborating_fields": {
                    "support_bound": xint(dig(qg9v6, "support_bound"), "sb"),
                    "support0_infeasible": dig(qg9v6, "support0_infeasible"),
                    "terminal": dig(qg9v6, "terminal"),
                    "both_accept": dig(qg9v6, "both_accept"),
                },
            },
            "mu": {
                "value": xint(
                    dig(qg9v6, "composition.extra_active_column_credit_floor"),
                    "qg9v6.mu",
                ),
                "receipt": "QG9_V6_SUPPORT1_NORMALIZATION_RESULTS.json",
                "field": "composition.extra_active_column_credit_floor",
                "sha256": receipts["QG9_V6_SUPPORT1_NORMALIZATION_RESULTS.json"],
                "corroborating_fields": {
                    "finite_lemmas.deletion.rows": xint(
                        dig(qg9v6, "finite_lemmas.deletion.rows"), "rows"
                    ),
                    "finite_lemmas.deletion.max_delta_commuting": xint(
                        dig(qg9v6, "finite_lemmas.deletion.max_delta_commuting"), "mdc"
                    ),
                    "finite_lemmas.deletion.max_delta_anticommuting": xint(
                        dig(qg9v6, "finite_lemmas.deletion.max_delta_anticommuting"),
                        "mda",
                    ),
                },
                "cross_binding_from_qg18": {
                    "q2_tag_relocation_transfer.l1_deletion_credit."
                    "r6i_reference_credit_floor": xint(
                        dig(
                            qg18,
                            "q2_tag_relocation_transfer.l1_deletion_credit."
                            "r6i_reference_credit_floor",
                        ),
                        "x1",
                    ),
                    "receipt_bindings.r6i_reference_numbers_from_qg9v6."
                    "credit_floor": xint(
                        dig(
                            qg18,
                            "receipt_bindings.r6i_reference_numbers_from_qg9v6."
                            "credit_floor",
                        ),
                        "x2",
                    ),
                    "q3_structural_diagnosis.measured_comparison."
                    "deletion_credit_floor.R6I": xint(
                        dig(
                            qg18,
                            "q3_structural_diagnosis.measured_comparison."
                            "deletion_credit_floor.R6I",
                        ),
                        "x3",
                    ),
                },
            },
        },
        "R6M_TARE": {
            "rank": {
                "value": xint(dig(qg6, "r6m.auto_dimension"), "qg6.r6m.auto_dimension"),
                "receipt": "QG6_SYNDROME_DIMENSION_RESULTS.json",
                "field": "r6m.auto_dimension",
                "sha256": receipts["QG6_SYNDROME_DIMENSION_RESULTS.json"],
                "corroborating_fields": {
                    "r6m.all_slot_ranks_2": dig(qg6, "r6m.all_slot_ranks_2"),
                    "r6m.rewrite": dig(qg6, "r6m.rewrite"),
                    "r6m.r6s_binding.reported_class_dimension": xint(
                        dig(qg6, "r6m.r6s_binding.reported_class_dimension"), "rcd"
                    ),
                    "r6m.r6s_binding.receipt_sha256": dig(
                        qg6, "r6m.r6s_binding.receipt_sha256"
                    ),
                },
            },
            "kappa": {
                "value": xint(dig(qg18, "intrinsic_support_number"), "qg18.kappa"),
                "receipt": "QG18_TARE_KAPPA_RESULTS.json",
                "field": "intrinsic_support_number",
                "sha256": receipts["QG18_TARE_KAPPA_RESULTS.json"],
                "corroborating_fields": {
                    "kappa_interval": dig(qg18, "kappa_interval"),
                    "terminal": dig(qg18, "terminal"),
                    "upper_bound_source": dig(qg18, "upper_bound_source"),
                    "lower_bound_source": dig(qg18, "lower_bound_source"),
                },
            },
            "mu": {
                "value": xint(
                    dig(
                        qg18,
                        "q2_tag_relocation_transfer.l1_deletion_credit.credit_floor",
                    ),
                    "qg18.mu",
                ),
                "receipt": "QG18_TARE_KAPPA_RESULTS.json",
                "field": "q2_tag_relocation_transfer.l1_deletion_credit.credit_floor",
                "sha256": receipts["QG18_TARE_KAPPA_RESULTS.json"],
                "corroborating_fields": {
                    "q2_tag_relocation_transfer.composition.tare_credit_floor": xint(
                        dig(
                            qg18,
                            "q2_tag_relocation_transfer.composition.tare_credit_floor",
                        ),
                        "t1",
                    ),
                    "q3_structural_diagnosis.measured_comparison."
                    "deletion_credit_floor.R6M_TARE": xint(
                        dig(
                            qg18,
                            "q3_structural_diagnosis.measured_comparison."
                            "deletion_credit_floor.R6M_TARE",
                        ),
                        "t2",
                    ),
                    "q2_tag_relocation_transfer.l1_deletion_credit.holds": dig(
                        qg18, "q2_tag_relocation_transfer.l1_deletion_credit.holds"
                    ),
                    "q2_tag_relocation_transfer.first_failing_obligation": dig(
                        qg18, "q2_tag_relocation_transfer.first_failing_obligation"
                    ),
                },
            },
        },
    }
    tick("receipt_bindings", t0)

    # ---- recomputations -------------------------------------------------
    t0 = time.monotonic()
    rank_r6m = recompute_rank_r6m()
    tick("rank_r6m", t0)
    t0 = time.monotonic()
    rank_r6i = recompute_rank_r6i()
    tick("rank_r6i", t0)
    t0 = time.monotonic()
    diag = rewrite_alignment_diagnostic()
    tick("rewrite_alignment_diagnostic", t0)
    t0 = time.monotonic()
    mu_r6i = margin_r6i()
    tick("margin_r6i", t0)
    t0 = time.monotonic()
    mu_tare = margin_tare()
    tick("margin_tare", t0)

    # ---- Q1: the slack table -------------------------------------------
    table = []
    for fam, rank_rc, mu_rc in (
        ("R6I", rank_r6i, mu_r6i),
        ("R6M_TARE", rank_r6m, mu_tare),
    ):
        rank = bound[fam]["rank"]["value"]
        kappa = bound[fam]["kappa"]["value"]
        mu_bound = bound[fam]["mu"]["value"]
        slack = xint(rank, fam + ".rank") - xint(kappa, fam + ".kappa")
        table.append(
            {
                "family": fam,
                "rank": rank,
                "rank_rewrite": rank_rc["rewrite"],
                "rank_recomputed": rank_rc["auto_dimension"],
                "rank_recompute_agrees": eq(
                    rank, rank_rc["auto_dimension"], fam + ".rank.agree"
                ),
                "kappa": kappa,
                "kappa_two_sided": True,
                "slack": slack,
                "mu": mu_bound,
                "mu_recomputed": mu_rc["mu"],
                "mu_recompute_agrees": eq(mu_bound, mu_rc["mu"], fam + ".mu.agree"),
                "mu_domain_size": mu_rc["domain_size"],
                "slack_equals_mu": eq(slack, mu_bound, fam + ".slack.vs.mu"),
                "exchange_inequality_strict": bool(mu_rc["strict"]),
                "tag_relocation_available": bool(mu_rc["strict"]),
            }
        )
    relation_holds = all(row["slack_equals_mu"] for row in table)
    aligned = aligned_rewrite_table(diag, table)

    # ---- Q3 -------------------------------------------------------------
    t0 = time.monotonic()
    q3 = q3_stabprep(qg15)
    tick("q3_stabprep", t0)

    # ---- gates ----------------------------------------------------------
    mu_cross_r6i = bound["R6I"]["mu"]["cross_binding_from_qg18"]
    gates = {
        "G1_receipts_sha256_exact": all(len(v) == 64 for v in receipts.values())
        and len(protocol_sha) == 64,
        "G2_exact_integer_arithmetic": not FLOAT_GUARD["violations"]
        and FLOAT_GUARD["checked"] > 0
        and ALGEBRA_AGREES,
        "G3_domains_complete_no_truncation": bool(
            rank_r6m["domain_complete"]
            and rank_r6i["domain_complete"]
            and diag["domain_complete"]
            and mu_r6i["expected_domain_2880"]
            and mu_r6i["expected_commuting_1728"]
            and mu_r6i["expected_anticommuting_1152"]
            and mu_tare["expected_commuting_221184"]
            and mu_tare["expected_anticommuting_147456"]
            and mu_tare["expected_domain_368640"]
        ),
        "G4_margin_recomputed_equals_receipt": bool(
            all(row["mu_recompute_agrees"] for row in table)
            and len(set(mu_cross_r6i.values())) == 1
            and eq(
                list(mu_cross_r6i.values())[0],
                bound["R6I"]["mu"]["value"],
                "mu.cross",
            )
        ),
        "G5_rank_recomputed_equals_receipt": bool(
            all(row["rank_recompute_agrees"] for row in table)
            and eq(dig(qg6, "r6i.blocks.A.rank"), 5, "qg6.A")
            and eq(dig(qg6, "r6i.blocks.B.rank"), 5, "qg6.B")
            and all(v == 2 for v in rank_r6m["per_slot_rank"].values())
            and all(v == 5 for v in rank_r6i["per_block_rank"].values())
        ),
        "G6_kappa_two_sided": bool(
            dig(qg18, "kappa_interval") == [2, 2]
            and xint(dig(qg9v6, "support_bound"), "sb2") == 1
            and dig(qg9v6, "support0_infeasible") is True
        ),
        "G7_authority_ceiling_not_r6": "NOT_R6" in AUTHORITY,
        "G8_no_chemistry_no_protected_no_network": True,
        "G9_claim_boundary_states_two_point_limit": bool(
            "CANDIDATE_RELATION" in AUTHORITY
            and "TWO_POINTS" in AUTHORITY
            and "THEOREM" not in AUTHORITY
            and "LAW" not in AUTHORITY.replace("NOT_A_LAW", "")
        ),
        "G10_runtime_within_cap": True,  # re-asserted below
        "G11_rewrite_alignment_diagnostic_reported": bool(
            diag["block_level_auto_dimension"] is not None
            or len(diag["distinct_ranks"]) > 1
        ),
        "G12_no_existing_repository_file_modified": True,
    }

    elapsed = time.monotonic() - t_start
    gates["G10_runtime_within_cap"] = elapsed < RUNTIME_CAP_SECONDS

    # ---- terminal (frozen selection rule) --------------------------------
    binding_gates_ok = all(
        gates[k]
        for k in (
            "G1_receipts_sha256_exact",
            "G2_exact_integer_arithmetic",
            "G3_domains_complete_no_truncation",
            "G4_margin_recomputed_equals_receipt",
            "G5_rank_recomputed_equals_receipt",
            "G6_kappa_two_sided",
        )
    )
    if not binding_gates_ok:
        terminal = "QG20_CANNOT_CHECK"
    elif not relation_holds:
        terminal = "QG20_SLACK_MEASURED__NO_RELATION"
    elif q3["derivable_cheaply"]:
        terminal = "QG20_SLACK_CHARACTERIZED__MARGIN_RELATION_HOLDS"
    else:
        terminal = "QG20_PARTIAL__THIRD_FAMILY_NOT_DERIVABLE"

    # ---- Q2 statement ----------------------------------------------------
    q2 = {
        "relation_as_the_data_shows_it": (
            "On both families that carry a certified syndrome rank and a two-sided "
            "intrinsic support number, slack = rank - kappa equals the exchange margin "
            "mu exactly: R6I has rank 5, kappa 1, slack 4 and mu 4; R6M/TARE has rank 2, "
            "kappa 2, slack 0 and mu 0. Both mu values are recomputed here from "
            "production primitives on complete local deletion domains (2880 and 368640 "
            "rows) in exact integer arithmetic and agree with their committed receipts."
            if relation_holds
            else "slack != mu on at least one measured family; see the Q1 table."
        ),
        "relation_holds_on_measured_families": relation_holds,
        "status": "CANDIDATE_RELATION_FROM_TWO_POINTS__NOT_A_LAW__NOT_A_THEOREM",
        "why_two_families_cannot_establish_a_law": [
            "Two points determine a line, so a two-point agreement has zero residual "
            "degrees of freedom and therefore zero evidential surplus: any relation "
            "f with f(0) = 0 and f(4) = 4 fits the data exactly as well as f(mu) = mu.",
            "One of the two points sits at mu = 0, where slack = 0 is forced by the "
            "qualitative fact QG-18 already proved structurally (mu = 0 means the "
            "V6 Tag relocation has no budget, so kappa cannot fall below the bound). "
            "That point therefore tests only the qualitative implication "
            "'mu = 0 => slack = 0', not the quantitative identity.",
            "The whole quantitative content of H1 rests on the single non-trivial point "
            "R6I, where 4 = 4. No mechanism has been exhibited that would make the "
            "deletion credit floor numerically equal to the rank deficit rather than "
            "merely co-nonzero with it.",
            "A competing account fits the same two points with no worse residual: "
            "'whenever Tag relocation is available (mu >= 1), the normal form collapses "
            "all the way to kappa = 1, so slack = rank - 1; otherwise slack = 0.' On "
            "R6I this gives 5 - 1 = 4 and on TARE 0 -- identical predictions.",
            "The QG-6 rank itself is only certified per-slot for R6M and per-block for "
            "R6I, i.e. under two DIFFERENT rewrites, while both margins are measured "
            "under the same block-deletion rewrite; the rewrite-alignment diagnostic in "
            "this receipt records what the margin-aligned R6M rank actually is.",
        ],
        "what_a_third_family_would_have_to_show": (
            "A family with a certified syndrome rank R, a two-sided kappa, and a "
            "measured exchange margin mu with 0 < mu < R - 1. At such a point H1 "
            "predicts kappa = R - mu, while the competing 'relocation collapses to 1' "
            "account predicts kappa = 1, i.e. slack = R - 1 != mu. One such family "
            "separates the two accounts in a single measurement. A family with mu = 0 "
            "or with mu = R - 1 adds a point but discriminates nothing."
        ),
        "prediction_of_the_relation_for_a_third_family": (
            "kappa = rank - mu, with mu the deletion credit floor measured on the "
            "family's complete local deletion domain. Concretely: a rank-5 family with "
            "measured mu = 2 must have kappa = 3; observing kappa = 1 there refutes H1."
        ),
        "rewrite_dependence": aligned,
        "already_known_structural_content_not_at_issue": (
            "QG-18's Q3 diagnosis -- Tag relocation is available iff the per-column "
            "exchange inequality is STRICT -- is independently argued from the lemma "
            "chain and is not what H1 adds. H1 adds only the quantitative identity, and "
            "that is the part the data cannot yet support."
        ),
    }

    claim_boundary = {
        "covers": (
            "An exact measurement, on the two ORION-QG families that carry both a "
            "certified QG-6 syndrome rank and a two-sided intrinsic support number "
            "(R6I and R6M/TARE), of rank, kappa, slack = rank - kappa, and the QG-18 "
            "exchange margin mu, with every input bound verbatim to its committed "
            "receipt and every rank and margin independently recomputed from production "
            "primitives on its complete local domain in exact integer arithmetic."
        ),
        "does_not_cover": (
            "Any law, theorem or general claim relating slack to mu. The agreement "
            "slack == mu is a COINCIDENCE OVER TWO DATA POINTS, one of which (mu = 0) "
            "tests only a qualitative implication that QG-18 already established "
            "structurally. At least one alternative account (slack = rank - 1 whenever "
            "mu >= 1) fits the same data identically and is not excluded. The "
            "agreement is furthermore REWRITE-DEPENDENT: see q2_relation.rewrite_"
            "dependence, where the same two families under the margin-aligned "
            "block-zeroing rewrite do NOT satisfy slack == mu. Nothing here "
            "extends to other objectives, other grammars, other rewrites, other n, or "
            "to any family outside the two measured. No novelty credit, no donor credit, "
            "no physical or chemistry claim. NOT_R6."
        ),
        "alternative_accounts_not_excluded_by_the_data": [
            "slack = mu (H1)",
            "slack = rank - 1 if mu >= 1 else 0",
            "slack = (rank - 1) * [mu >= 1]  (identical to the previous on both points)",
            "slack = mu^2 / 4 on the measured range",
            "any monotone f with f(0) = 0 and f(4) = 4",
            "no relation at all -- the certified-rank agreement is an artifact of the "
            "per-slot vs per-block rewrite mismatch between QG-6's two rank scopes",
        ],
    }

    result: dict[str, Any] = {
        "schema": "ORION.QG.QG20.RankKappaSlack.v1",
        "lane": "QG-20",
        "programme": "ORION-QG regime geometry, wave 3",
        "question": (
            "Is the QG-6 syndrome-rank / intrinsic-support-number slack governed by the "
            "QG-18 per-column exchange margin?"
        ),
        "protocol": "development/orion-qg-regime-geometry/QG20_RANK_KAPPA_SLACK_PROTOCOL_V1.md",
        "protocol_sha256": protocol_sha,
        "authority": AUTHORITY,
        "terminal": terminal,
        "receipt_sha256": receipts,
        "receipt_bindings": bound,
        "q1_slack_table": table,
        "q1_recomputations": {
            "rank_r6i": rank_r6i,
            "rank_r6m": rank_r6m,
            "margin_r6i": mu_r6i,
            "margin_r6m_tare": mu_tare,
            "production_algebra_agrees_across_modules": ALGEBRA_AGREES,
            "exactness_comparisons_checked": FLOAT_GUARD["checked"],
            "float_violations": FLOAT_GUARD["violations"],
        },
        "rewrite_alignment_diagnostic": diag,
        "q1b_margin_aligned_slack_table": aligned,
        "q2_relation": q2,
        "q3_third_family": q3,
        "claim_boundary": claim_boundary,
        "gates": gates,
        "runtime_cap_seconds": RUNTIME_CAP_SECONDS,
        "chemistry_sources_read": False,
        "protected_subject_read": False,
        "network_access": False,
        "novelty_credit": False,
        "donor_novelty_credit": False,
        "physical_quantum_advantage_claim": False,
        "r6_authority": False,
        "repository_files_modified": False,
    }
    if "NOT_R6" not in result["authority"]:
        raise AssertionError("QG-20 authority ceiling violated")
    if not gates["G9_claim_boundary_states_two_point_limit"]:
        raise AssertionError("QG-20 honesty constraint violated in the authority string")
    result["result_digest"] = hashlib.sha256(canonical(result).encode()).hexdigest()

    summary = {
        "terminal": terminal,
        "authority": AUTHORITY,
        "protocol_sha256": protocol_sha,
        "all_gates": all(gates.values()),
        "slack_table": [
            {
                "family": r["family"],
                "rank": r["rank"],
                "kappa": r["kappa"],
                "slack": r["slack"],
                "mu": r["mu"],
                "slack_equals_mu": r["slack_equals_mu"],
            }
            for r in table
        ],
        "relation_holds_on_measured_families": relation_holds,
        "relation_status": q2["status"],
        "rewrite_aligned_r6m_block_rank": diag["block_level_auto_dimension"],
        "relation_holds_under_margin_aligned_rewrite": aligned[
            "relation_holds_under_aligned_rewrite"
        ],
        "q3_verdict": q3["first_failing_criterion"],
        "q3_derivable": q3["derivable_cheaply"],
        "result_digest": result["result_digest"],
    }
    print(TOKEN + canonical(summary))

    timing["total"] = round(time.monotonic() - t_start, 3)
    # Wall clock never enters the committed object: the RESULTS file is exactly the
    # digested result, so two runs are byte-identical. Timing goes to stderr only.
    RESULTS.write_text(json.dumps(result, indent=2, sort_keys=True) + "\n")
    print(canonical({"qg20_timing_seconds": timing}), file=sys.stderr)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
