#!/usr/bin/env python3
"""P7 necessity-scoping V2 frame verification (revival lane NR-10).

Executes the frozen protocol ``P7_NECESSITY_SCOPING_V2_FRAME_PROTOCOL_V1.md``:
a pure standard-library re-implementation of the registered finite semantic world
(carrier = (discharged set, declared-new set, source, target); composite =
componentwise union with first-source/last-target --- the construction of
``_finite_semantic_world`` in ``src/orion/study/p7/composition_calculus_smt.py``),
swept exhaustively to check N2-A..N2-E2.

No pytest, no suites, no xdist, no cloning. One run, one JSON artifact.
"""

from __future__ import annotations

import itertools
import json
import time
from pathlib import Path

RESULT_PATH = Path(__file__).with_name("P7_NECESSITY_SCOPING_V2_RESULT_V1.json")


# ---------------------------------------------------------------------------
# The frame (frozen by protocol section 2)
# ---------------------------------------------------------------------------


class Frame:
    """A finite instantiation of the registered two-layer frame."""

    def __init__(self, n_obl: int, n_con: int):
        self.n_obl = n_obl
        self.n_con = n_con
        self.obls = tuple(range(n_obl))
        self.contracts = tuple(range(n_con))
        subsets = [
            frozenset(s)
            for r in range(n_obl + 1)
            for s in itertools.combinations(self.obls, r)
        ]
        # Carrier: (discharged, fresh, src, tgt) --- verbatim from the module.
        self.trans = [
            (d, f, s, t)
            for d in subsets
            for f in subsets
            for s in self.contracts
            for t in self.contracts
        ]
        self.index = {elem: i for i, elem in enumerate(self.trans)}

    def comp(self, t: int, u: int) -> int:
        dt, ft, st, _ = self.trans[t]
        du, fu, _, tu = self.trans[u]
        return self.index[(dt | du, ft | fu, st, tu)]

    # -- completions ---------------------------------------------------------

    def all_demands(self):
        for bits in itertools.product((False, True), repeat=self.n_con * self.n_obl):
            yield {
                (c, o): bits[c * self.n_obl + o]
                for c in self.contracts
                for o in self.obls
            }

    def all_tables(self):
        pairs = list(itertools.product(self.contracts, repeat=2))
        for mask in range(1 << len(pairs)):
            yield frozenset(p for i, p in enumerate(pairs) if mask >> i & 1)

    def table_sound(self, demands, table) -> bool:
        # Bridge(a,b) -> forall o. Demands(a,o) == Demands(b,o)
        return all(
            all(demands[(a, o)] == demands[(b, o)] for o in self.obls)
            for (a, b) in table
        )

    def completions(self):
        for demands in self.all_demands():
            for table in self.all_tables():
                if self.table_sound(demands, table):
                    yield demands, table

    def consistent_demands(self, table):
        return [dm for dm in self.all_demands() if self.table_sound(dm, table)]

    # -- semantics -----------------------------------------------------------

    def total(self, demands, ti: int) -> bool:
        d, f, s, t = self.trans[ti]
        return all(
            not demands[(t, o)] or demands[(s, o)] or o in d or o in f
            for o in self.obls
        )

    def containment(self, demands, a: int, b: int) -> bool:
        # every obligation b demands is demanded by a (b = Src u, a = Tgt t)
        return all(not demands[(b, o)] or demands[(a, o)] for o in self.obls)

    def obligation_equal(self, demands, a: int, b: int) -> bool:
        return all(demands[(a, o)] == demands[(b, o)] for o in self.obls)

    @staticmethod
    def match(a: int, b: int, table) -> bool:
        return a == b or (a, b) in table

    @staticmethod
    def components(table, n_con: int):
        """Undirected connected components of the bridge table (reflexive)."""
        parent = list(range(n_con))

        def find(x):
            while parent[x] != x:
                parent[x] = parent[parent[x]]
                x = parent[x]
            return x

        for a, b in table:
            ra, rb = find(a), find(b)
            if ra != rb:
                parent[ra] = rb
        return {c: find(c) for c in range(n_con)}


def fmt_demands(fr: Frame, demands) -> dict:
    return {f"k{c}/o{o}": demands[(c, o)] for c in fr.contracts for o in fr.obls}


def run_frame(n_obl: int, n_con: int, *, leg_level_e: bool):
    fr = Frame(n_obl, n_con)
    n_trans = len(fr.trans)
    counts = {
        "transformations": n_trans,
        "leg_pairs": n_trans ** 2,
        "completions": 0,
        "leg_checks": 0,
        "observations_checked": 0,
        "leg_level_e_instances": 0,
        "match_sound_violations": 0,
        "containment_sound_violations": 0,
    }
    exhibits = {
        "witness": None,
        "containment_failure": None,
        "conflation": None,
    }

    completions = list(fr.completions())
    counts["completions"] = len(completions)

    # -- N2-B (conditional theorem re-verified) + N2-A + N2-C exhibits -------
    for demands, table in completions:
        tot = [fr.total(demands, i) for i in range(n_trans)]
        for t in range(n_trans):
            if not tot[t]:
                continue
            for u in range(n_trans):
                if not tot[u]:
                    continue
                counts["leg_checks"] += 1
                a, b = fr.trans[t][3], fr.trans[u][2]
                comp_total = tot[fr.comp(t, u)]
                if fr.match(a, b, table) and not comp_total:
                    counts["match_sound_violations"] += 1
                if fr.containment(demands, a, b) and not comp_total:
                    counts["containment_sound_violations"] += 1
                tgt_u = fr.trans[u][3]
                if (
                    exhibits["witness"] is None
                    and comp_total
                    and any(demands[(tgt_u, o)] for o in fr.obls)
                    and fr.obligation_equal(demands, a, b)
                    and not fr.match(a, b, table)
                ):
                    exhibits["witness"] = {
                        "frame": [n_obl, n_con],
                        "legs": [list(map(sorted, fr.trans[t][:2])) + [fr.trans[t][2], fr.trans[t][3]],
                                 list(map(sorted, fr.trans[u][:2])) + [fr.trans[u][2], fr.trans[u][3]]],
                        "handoff_contracts": [a, b],
                        "bridge_table": sorted(table),
                        "demands": fmt_demands(fr, demands),
                        "composite_total": True,
                        "refused_by_match": True,
                    }
                if (
                    exhibits["containment_failure"] is None
                    and not comp_total
                    and not fr.containment(demands, a, b)
                ):
                    exhibits["containment_failure"] = {
                        "frame": [n_obl, n_con],
                        "handoff_contracts": [a, b],
                        "bridge_table": sorted(table),
                        "demands": fmt_demands(fr, demands),
                        "composite_total": False,
                    }

    # -- N2-D: opacity conflation, constructed then verified -----------------
    # Empty registry: k0 and k1 in different singleton components. Identity legs
    # are total under every completion. Two completions differing only in
    # Demands (unobservable in the opaque scope) share the observation
    # (k0, k1, {}) and the same legs, yet the composite is total in one and not
    # in the other.
    empty_table = frozenset()
    comp_of = fr.components(empty_table, fr.n_con)
    a, b = fr.contracts[0], fr.contracts[1]
    o0 = fr.obls[0]
    t_id = fr.index[(frozenset(), frozenset(), a, a)]
    u_id = fr.index[(frozenset(), frozenset(), b, b)]
    dm_equivalent = {key: False for key in itertools.product(fr.contracts, fr.obls)}
    dm_equivalent[(a, o0)] = True
    dm_equivalent[(b, o0)] = True
    dm_failing = {key: False for key in itertools.product(fr.contracts, fr.obls)}
    dm_failing[(b, o0)] = True
    conflation_facts = {
        "different_components": comp_of[a] != comp_of[b],
        "legs_total_both_completions": all(
            fr.total(dm, t_id) and fr.total(dm, u_id) for dm in (dm_equivalent, dm_failing)
        ),
        "match_false_both": not fr.match(a, b, empty_table),
        "tables_sound": all(
            fr.table_sound(dm, empty_table) for dm in (dm_equivalent, dm_failing)
        ),
        "composite_total_witness_side": fr.total(dm_equivalent, fr.comp(t_id, u_id)),
        "composite_total_failure_side": fr.total(dm_failing, fr.comp(t_id, u_id)),
        "same_observation": True,
        "same_legs": True,
        "witness_side_demands_something": dm_equivalent[(b, o0)],
    }
    exhibits["conflation"] = {
        "frame": [n_obl, n_con],
        "handoff_contracts": [a, b],
        "bridge_table": [],
        "witness_side": {"demands": fmt_demands(fr, dm_equivalent)},
        "failure_side": {"demands": fmt_demands(fr, dm_failing)},
        "facts": conflation_facts,
    }

    # -- N2-E1 / N2-E2: observation-level characterization --------------------
    e1_mismatches = []
    leg_level_disagreements = 0
    e2_separating = None
    e2_iff_violations = 0
    for table in fr.all_tables():
        comp_of = fr.components(table, fr.n_con)
        consistent = fr.consistent_demands(table)
        symmetric = all((bb, aa) in table for (aa, bb) in table)
        transitive = all(
            (aa, cc) in table
            for (aa, bb) in table
            for (bb2, cc) in table
            if bb == bb2
        )
        # exact condition for match == connectivity: every ordered pair of
        # distinct same-component contracts is registered (self-pairs are
        # covered by match's first disjunct). Symmetric-transitive registries
        # are component-complete; the converse fails only on self-pairs.
        component_complete = all(
            (x, y) in table
            for x in fr.contracts
            for y in fr.contracts
            if x != y and comp_of[x] == comp_of[y]
        )
        for a in fr.contracts:
            for b in fr.contracts:
                counts["observations_checked"] += 1
                licenseable = all(fr.containment(dm, a, b) for dm in consistent)
                connected = comp_of[a] == comp_of[b]
                matched = fr.match(a, b, table)
                if licenseable != connected or (matched and not licenseable):
                    e1_mismatches.append(
                        {"a": a, "b": b, "table": sorted(table),
                         "licenseable": licenseable, "connected": connected,
                         "matched": matched}
                    )
                if e2_separating is None and licenseable and not matched:
                    e2_separating = {"a": a, "b": b, "table": sorted(table)}
                if (matched != connected) != (not component_complete):
                    e2_iff_violations += 1
                # second implementation: leg-level enumeration, both directions
                if leg_level_e:
                    failing_instance = None
                    for dm in consistent:
                        tot = [fr.total(dm, i) for i in range(n_trans)]
                        for t in range(n_trans):
                            if not tot[t] or fr.trans[t][3] != a:
                                continue
                            for u in range(n_trans):
                                if not tot[u] or fr.trans[u][2] != b:
                                    continue
                                counts["leg_level_e_instances"] += 1
                                if not tot[fr.comp(t, u)]:
                                    failing_instance = {
                                        "demands": fmt_demands(fr, dm),
                                        "legs": [t, u],
                                    }
                    if failing_instance is not None and licenseable:
                        leg_level_disagreements += 1
                    if failing_instance is None and not licenseable:
                        leg_level_disagreements += 1

    return {
        "frame": {"obligations": n_obl, "contracts": n_con},
        "counts": counts,
        "exhibits": exhibits,
        "verdicts": {
            "N2_A_witness_preserved": exhibits["witness"] is not None,
            "N2_B_match_sound": counts["match_sound_violations"] == 0,
            "N2_B_containment_sound": counts["containment_sound_violations"] == 0,
            "N2_C_containment_necessary": exhibits["containment_failure"] is not None,
            "N2_D_conflation": all(
                v for k, v in conflation_facts.items() if k != "composite_total_failure_side"
            ) and not conflation_facts["composite_total_failure_side"],
            "N2_E1_exact_characterization": not e1_mismatches,
            "N2_E1_leg_level_agreement": leg_level_disagreements == 0,
            "N2_E2_match_separated": e2_separating is not None,
            "N2_E2_closure_complete_iff_match": e2_iff_violations == 0,
        },
        "e1_mismatches": e1_mismatches[:10],
        "e2_separating_example": e2_separating,
    }


def main() -> int:
    started = time.time()
    results = [
        run_frame(1, 2, leg_level_e=True),
        run_frame(2, 2, leg_level_e=True),
        run_frame(1, 3, leg_level_e=False),
    ]
    all_verdicts = {}
    for r in results:
        for k, v in r["verdicts"].items():
            all_verdicts[k] = all_verdicts.get(k, True) and v
    payload = {
        "schema": "orion.p7.necessity-scoping-v2.v1",
        "protocol": "P7_NECESSITY_SCOPING_V2_FRAME_PROTOCOL_V1.md",
        "lane": "NR-10",
        "source_frame_module": "src/orion/study/p7/composition_calculus_smt.py",
        "source_mechanized_artifact": (
            "papers/paper-07-epistemic-navigation-open-worlds/formal/mechanized/"
            "P7_COMPOSITION_CALCULUS_MECHANIZED_2026-08-21.json"
        ),
        "verdicts": all_verdicts,
        "frames": results,
        "runtime_seconds": round(time.time() - started, 3),
    }
    RESULT_PATH.write_text(json.dumps(payload, indent=1, default=str) + "\n")
    print(
        json.dumps(
            {"verdicts": all_verdicts, "runtime_seconds": payload["runtime_seconds"]},
            indent=1,
        )
    )
    ok = all(all_verdicts.values())
    print("ALL_PRE_REGISTERED_CLAIMS_HOLD" if ok else "SOME_CLAIM_REFUTED_OR_UNDECIDED")
    return 0 if ok else 1


if __name__ == "__main__":
    raise SystemExit(main())
