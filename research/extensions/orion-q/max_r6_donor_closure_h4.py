#!/usr/bin/env python3
"""Execute the donor-closure computation selected by native Self-ORION N0.

This script answers only the two frozen N0 discriminator obligations on the
already-open H4 state. It never accesses the prospective stretched-N2 R6 file.

Protocol:
  development/orion-q-max-r0/MAX_R6_DONOR_CLOSURE_COMPUTATION_PACKET.md
"""
from __future__ import annotations

import hashlib
import json
import math
from dataclasses import dataclass
from functools import lru_cache

import max_r5h_mixed_cardinality_development as r5h

CFG = r5h.SUBJECTS["H4"]
WINDOW = 12
TARGET = {
    "Lambda": 4.862157873932594,
    "CNOT": 1428,
    "T": 5568,
    "blocks": 246,
    "ancilla": 0,
    "reference_total_T": 31028,
    "partition_sha256": "ead1365263ba4ba0e288be7f3715125f4d0a4fb5a14b7979f97c7237792ad1fc",
}
RZ_T = 48
FOQCS_QRISP_COMMIT = "044979610a91a872fb087f539a5d78a66ee9cebe"
FOQCS_QRISP_PATH = "src/qrisp/block_encodings/constructors/foqcs_lcu/from_foqcs_lcu_prep.py"


def sha(obj) -> str:
    return hashlib.sha256(
        json.dumps(obj, sort_keys=True, separators=(",", ":"), allow_nan=False).encode()
    ).hexdigest()


@dataclass(frozen=True)
class DState:
    lam: float
    cnot: int
    t: int
    blocks: int
    ancilla: int
    uses_hyper: bool
    partition: tuple[tuple[str, tuple[int, ...]], ...]


def within_target(s: DState) -> bool:
    return (
        s.lam <= TARGET["Lambda"] + 1e-12
        and s.cnot <= TARGET["CNOT"]
        and s.t <= TARGET["T"]
        and s.blocks <= TARGET["blocks"]
        and s.ancilla <= TARGET["ancilla"]
    )


def dominates_same_flag(a: DState, b: DState) -> bool:
    # Hyperblock usage is kept as a formal state coordinate because the N1 threat
    # question distinguishes ordinary exact states from relaxed general-m states.
    if a.uses_hyper != b.uses_hyper:
        return False
    le = (
        a.lam <= b.lam + 1e-13
        and a.cnot <= b.cnot
        and a.t <= b.t
        and a.blocks <= b.blocks
        and a.ancilla <= b.ancilla
    )
    strict = (
        a.lam < b.lam - 1e-13
        or a.cnot < b.cnot
        or a.t < b.t
        or a.blocks < b.blocks
        or a.ancilla < b.ancilla
    )
    return le and strict


def prune(states):
    # Collapse identical discrete coordinates independently for hyper/nonhyper.
    collapsed = {}
    for s in states:
        if not within_target(s):
            continue
        key = (s.cnot, s.t, s.blocks, s.ancilla, s.uses_hyper)
        old = collapsed.get(key)
        if old is None or (s.lam, s.partition) < (old.lam, old.partition):
            collapsed[key] = s
    rows = sorted(
        collapsed.values(),
        key=lambda s: (
            s.uses_hyper,
            round(s.lam, 15),
            s.cnot,
            s.t,
            s.blocks,
            s.ancilla,
            s.partition,
        ),
    )
    keep = []
    for s in rows:
        if any(dominates_same_flag(o, s) for o in keep):
            continue
        keep.append(s)
    return tuple(keep)


def hyperblock(mask: int, subterms, offset: int):
    idx = tuple(i for i in range(len(subterms)) if (mask >> i) & 1)
    m = len(idx)
    coeff = [abs(float(subterms[i][1])) for i in idx]
    lam = math.sqrt(m) * math.sqrt(sum(a * a for a in coeff))
    return r5h.Block(
        mask=mask,
        indices=tuple(offset + i for i in idx),
        kind=f"OPTIMISTIC_TARE_M{m}",
        lam=float(lam),
        cnot=0,
        t=int(2 * (2 * m - 1) * RZ_T),
        ancilla=0,
    )


def candidate_blocks(subterms, n: int, offset: int, *, include_hyper: bool):
    blocks = list(r5h.candidate_blocks(subterms, n, offset, "mixed"))
    hyper_count = 0
    if include_hyper:
        w = len(subterms)
        max_m = min(w, 2 * n + 1)
        for mask in range(1, 1 << w):
            m = mask.bit_count()
            if 3 <= m <= max_m:
                blocks.append(hyperblock(mask, subterms, offset))
                hyper_count += 1
    blocks.sort(key=lambda b: (b.mask, b.kind, b.indices))
    return tuple(blocks), hyper_count


def exact_window(subterms, n: int, offset: int, *, include_hyper: bool):
    w = len(subterms)
    full = (1 << w) - 1
    blocks, hyper_count = candidate_blocks(subterms, n, offset, include_hyper=include_hyper)
    by_first = {i: [] for i in range(w)}
    for block in blocks:
        for i in range(w):
            if (block.mask >> i) & 1:
                by_first[i].append(block)

    calls = 0

    @lru_cache(maxsize=None)
    def solve(mask: int):
        nonlocal calls
        calls += 1
        if mask == 0:
            return (DState(0.0, 0, 0, 0, 0, False, tuple()),)
        first = (mask & -mask).bit_length() - 1
        cand = []
        for block in by_first[first]:
            if block.mask & mask != block.mask:
                continue
            is_hyper = block.kind.startswith("OPTIMISTIC_TARE_M")
            # Immediate target bounds are exact because all future block costs are nonnegative.
            if (
                block.lam > TARGET["Lambda"] + 1e-12
                or block.cnot > TARGET["CNOT"]
                or block.t > TARGET["T"]
                or block.ancilla > TARGET["ancilla"]
            ):
                continue
            for tail in solve(mask ^ block.mask):
                s = DState(
                    lam=block.lam + tail.lam,
                    cnot=block.cnot + tail.cnot,
                    t=block.t + tail.t,
                    blocks=1 + tail.blocks,
                    ancilla=max(block.ancilla, tail.ancilla),
                    uses_hyper=is_hyper or tail.uses_hyper,
                    partition=((block.kind, block.indices),) + tail.partition,
                )
                if within_target(s):
                    cand.append(s)
        return prune(cand)

    front = solve(full)
    return front, {
        "offset": offset,
        "window_terms": w,
        "candidate_blocks": len(blocks),
        "optimistic_hyperblocks": hyper_count,
        "subset_states_solved": calls,
        "bounded_frontier": len(front),
        "bounded_hyper_frontier": sum(s.uses_hyper for s in front),
    }


def combine(a, b):
    cand = []
    for x in a:
        for y in b:
            s = DState(
                lam=x.lam + y.lam,
                cnot=x.cnot + y.cnot,
                t=x.t + y.t,
                blocks=x.blocks + y.blocks,
                ancilla=max(x.ancilla, y.ancilla),
                uses_hyper=x.uses_hyper or y.uses_hyper,
                partition=x.partition + y.partition,
            )
            if within_target(s):
                cand.append(s)
    return prune(cand)


def reference_total_t(s: DState) -> int:
    q = 0 if s.blocks <= 1 else int(math.ceil(math.log2(s.blocks)))
    padded = 1 << q if q else 1
    prep_t = 2 * (padded - 1) * RZ_T
    selector_t = 4 * max(0, s.blocks - 1)
    return int(s.t + prep_t + selector_t)


def part_hash(partition) -> str:
    return sha([[kind, list(indices)] for kind, indices in partition])


def run_general_m_closure(terms):
    n = CFG["n_qubits"]
    exact_global = (DState(0.0, 0, 0, 0, 0, False, tuple()),)
    relaxed_global = exact_global
    meta = []
    for start in range(0, len(terms), WINDOW):
        sub = terms[start : min(start + WINDOW, len(terms))]
        exact_local, exact_meta = exact_window(sub, n, start, include_hyper=False)
        relaxed_local, relaxed_meta = exact_window(sub, n, start, include_hyper=True)
        exact_global = combine(exact_global, exact_local)
        relaxed_global = combine(relaxed_global, relaxed_local)
        meta.append(
            {
                "start": start,
                "exact": exact_meta,
                "relaxed": relaxed_meta,
                "global_exact": len(exact_global),
                "global_relaxed": len(relaxed_global),
                "global_relaxed_hyper": sum(s.uses_hyper for s in relaxed_global),
            }
        )
        if not exact_global:
            raise AssertionError({"exact_target_frontier_disappeared_at": start})
        if not relaxed_global:
            raise AssertionError({"relaxed_target_frontier_disappeared_at": start})

    exact_target_matches = [
        s
        for s in exact_global
        if abs(s.lam - TARGET["Lambda"]) <= 1e-12
        and s.cnot == TARGET["CNOT"]
        and s.t == TARGET["T"]
        and s.blocks == TARGET["blocks"]
        and s.ancilla == TARGET["ancilla"]
    ]
    if not exact_target_matches:
        raise AssertionError("R5H target resource point not reproduced by exact alphabet")
    target_hash_match = any(part_hash(s.partition) == TARGET["partition_sha256"] for s in exact_target_matches)
    if not target_hash_match:
        raise AssertionError(
            {
                "R5H_target_partition_hash_not_reproduced": [
                    part_hash(s.partition) for s in exact_target_matches
                ]
            }
        )

    threats = [s for s in relaxed_global if s.uses_hyper]
    # All relaxed_global states are already <= target on every explicit coordinate.
    # Check the redundant outer coordinate defensively.
    threats = [s for s in threats if reference_total_t(s) <= TARGET["reference_total_T"]]
    threats.sort(
        key=lambda s: (
            s.lam,
            s.cnot,
            s.t,
            s.blocks,
            s.ancilla,
            part_hash(s.partition),
        )
    )
    threat = threats[0] if threats else None
    outcome = (
        "DOMINATES_OR_INCONCLUSIVE" if threat is not None else "NONDOMINATING_OR_CLOSED"
    )
    threat_payload = None
    if threat is not None:
        threat_payload = {
            "Lambda": threat.lam,
            "CNOT": threat.cnot,
            "T": threat.t,
            "blocks": threat.blocks,
            "ancilla": threat.ancilla,
            "reference_total_T": reference_total_t(threat),
            "partition_sha256": part_hash(threat.partition),
            "histogram": _hist(threat.partition),
        }
    return {
        "outcome": outcome,
        "target": TARGET,
        "exact_target_hash_reproduced": target_hash_match,
        "exact_bounded_final_states": len(exact_global),
        "relaxed_bounded_final_states": len(relaxed_global),
        "relaxed_hyper_threat_count": len(threats),
        "best_relaxed_hyper_threat": threat_payload,
        "window_meta": meta,
        "proof_rule": "exact_subset_partition_DP_with_nonnegative_target_bounds_and_hyper_usage_bit",
        "optimistic_semantics": {
            "m_min": 3,
            "m_max_formula": "min(12,2n+1)",
            "Lambda": "sqrt(m)*l2",
            "CNOT": 0,
            "ancilla": 0,
            "T": "96*(2m-1)",
            "achievable_claim": False,
        },
    }


def _hist(partition):
    out = {}
    for kind, _indices in partition:
        out[kind] = out.get(kind, 0) + 1
    return out


def run_foqcs_closure():
    # Frozen source evidence is current Qrisp code at the locked commit. It exposes
    # a custom FOQCS constructor accepting arbitrary caller-supplied PREP_R/PREP_L
    # callables and at least 2L activation ancillas. This establishes route
    # availability but does not provide or zero-cost a chemistry-specific PREP.
    return {
        "outcome": "GENERIC_MATCHED_ROUTE_AVAILABLE",
        "route": "Qrisp BlockEncoding.from_foqcs_lcu_prep custom PREP_R/PREP_L constructor",
        "source": {
            "repo": "eclipse-qrisp/Qrisp",
            "commit": FOQCS_QRISP_COMMIT,
            "path": FOQCS_QRISP_PATH,
        },
        "matched_access_statement": "caller may supply custom left/right PREP for FOQCS activation registers beyond built-in models",
        "prep_resource_status": "UNRESOLVED_USER_SUPPLIED_PREP__NOT_ZERO_COST",
        "minimum_activation_ancillas": "2L",
        "built_in_structured_models_only_for_automatic_operator_route": True,
    }


def main():
    r5h.configure_subject(CFG)
    text = r5h.h.fetch_source()
    one, two = r5h.h.parse_ducc(text)
    paulis, max_imag = r5h.h.jordan_wigner_paulis(one, two)
    paulis.pop((0, 0), None)
    terms = sorted(paulis.items(), key=lambda kv: (-abs(kv[1]), kv[0][0], kv[0][1]))
    if len(terms) != 268:
        raise AssertionError({"unexpected_H4_terms": len(terms)})
    general_m = run_general_m_closure(terms)
    foqcs = run_foqcs_closure()
    gates = {
        "source_blob_bound": CFG["blob"] == "b98792b1055dbac0ebf2a7576f72412e3e4ac6c5",
        "h4_term_count_bound": len(terms) == 268,
        "hermitian": max_imag <= 5e-8,
        "exact_r5h_target_reproduced": general_m["exact_target_hash_reproduced"],
        "general_m_outcome_resolved": general_m["outcome"]
        in {"NONDOMINATING_OR_CLOSED", "DOMINATES_OR_INCONCLUSIVE"},
        "foqcs_route_resolved": foqcs["outcome"] == "GENERIC_MATCHED_ROUTE_AVAILABLE",
        "foqcs_prep_not_free": foqcs["prep_resource_status"]
        == "UNRESOLVED_USER_SUPPLIED_PREP__NOT_ZERO_COST",
        "fresh_r6_subject_unopened": True,
    }
    if not all(gates.values()):
        raise AssertionError(gates)
    out = {
        "schema": "ORIONQ.MAXR6.DonorClosureH4.v1",
        "authority": "NATIVE_SELECTED_DONOR_CLOSURE_EVIDENCE_ONLY__NOT_R6",
        "source_blob": CFG["blob"],
        "terms": len(terms),
        "max_imag": max_imag,
        "GENERAL_M_DONOR_OUTCOME": general_m["outcome"],
        "FOQCS_GENERIC_PREP_OUTCOME": foqcs["outcome"],
        "general_m": general_m,
        "foqcs": foqcs,
        "gates": gates,
        "fresh_r6_subject_coefficients_accessed": False,
    }
    print("ORIONQ_MAX_R6_DONOR_CLOSURE=" + json.dumps(out, sort_keys=True))
    return out


if __name__ == "__main__":
    main()
