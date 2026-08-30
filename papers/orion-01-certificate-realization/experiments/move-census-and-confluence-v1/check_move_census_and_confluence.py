#!/usr/bin/env python3
"""ORION01.MOVE_CENSUS_AND_CONFLUENCE.v1 -- census, hidden-operation control, confluence.

Extends experiments/contextual-move-completeness-v1 (Theorem A/B/C, controls K1-K4).
Reuses that packet's frozen model verbatim: states 1..n, declared candidate moves are
the strictly resource-decreasing pairs (s, t) with s > t, a registry is any subset.

Three stages, in order:

  S1 CENSUS      source-side (12 pinned production move schemas, five independent
                 frozen counts) and runtime-side (declared moves per domain size,
                 with closed-form cross-checks).
  S2 HOSTILE     can an UNDECLARED operation reproduce the declared observable
                 signature while changing the rewrite relation?
  S3 CONFLUENCE  critical pairs (local peaks) of the declared move system and their
                 joinability, cross-checked by a closed form and by Newman's lemma.

Exit codes -- a CANNOT_CHECK is never reported as a pass:

  0  measured, every control passed, no stage CANNOT_CHECK
  3  CANNOT_CHECK: a control failed, so this packet is not measuring the frozen
     object (model mismatch); no stage result is read either way
  4  measured for the stages that could run, but at least one declared sub-stage
     is CANNOT_CHECK (partial); read the per-stage status fields
  5  self-test failure: a perturbation went undetected, or the unperturbed input
     raised an alarm (--self-test only)

Standard library only. No ORION, no PyZX import. Read-only on every frozen artifact.
"""

import argparse
import hashlib
import itertools
import json
import math
import platform
from collections import defaultdict
from pathlib import Path

# ---------------------------------------------------------------- frozen inputs

HERE = Path(__file__).resolve().parent
PAPER = HERE.parents[1]
REPO = PAPER.parents[1]

R12 = PAPER / "evidence/convergence-v1/REGISTRY_NONIDENTIFIABILITY_R12_RESULTS.json"
PRIOR = PAPER / "experiments/contextual-move-completeness-v1/RESULT_V1.json"
SRCREG = PAPER / "experiments/r11-pyzx-full-reduce/ORION01_R11_PYZX_SOURCE_REGISTRY.json"
R11RES = PAPER / "experiments/r11-pyzx-full-reduce/ORION01_R11_PYZX_RESULTS.json"
R11PR = PAPER / "experiments/r11-pyzx-full-reduce/ORION01_R11_POST_REVIEW_REGISTRY_AUDIT.json"
PR1469 = PAPER / "evidence/convergence-v1/AB_PR1469_PRODUCTION_REGISTRY_AUDIT.json"

# The frozen R12 exhaustive_panel covers exactly n = 2..6. The main panel must not
# leave that range or the histogram cross-check has nothing to compare against.
NS_FULL = list(range(2, 7))
NS_SMOKE = list(range(2, 5))


class CannotCheck(Exception):
    """A frozen input could not be read or does not have the frozen shape."""


def load(path):
    try:
        return json.loads(path.read_text())
    except Exception as exc:                       # noqa: BLE001 - reported verbatim
        raise CannotCheck("cannot read %s: %s" % (path, exc))


def input_bindings():
    """SHA-256 of every frozen artifact this packet reads, recorded so the result is
    independently re-verifiable against the commit those artifacts were frozen at.

    This matters because the checker resolves its inputs by path from the working
    tree. Recording the digests is what lets a reader confirm the measurement was
    taken against the frozen bytes and not a tree that had moved underneath it.
    Follows the R11 audit convention (`frozen_registry_sha256`, `raw_result_sha256`)."""
    out = {}
    for name, path in (("r12_registry_nonidentifiability", R12),
                       ("prior_art_contextual_move_completeness", PRIOR),
                       ("r11_pyzx_source_registry", SRCREG),
                       ("r11_pyzx_results", R11RES),
                       ("r11_post_review_registry_audit", R11PR)):
        try:
            digest = hashlib.sha256(path.read_bytes()).hexdigest()
        except Exception as exc:                   # noqa: BLE001 - reported verbatim
            raise CannotCheck("cannot hash %s: %s" % (path, exc))
        out[name] = {"path": str(path.relative_to(REPO)), "sha256": digest}
    return out


def check_input_bindings_against_frozen_receipts(bindings, r11pr, pr1469):
    """C14: three of the digests above were independently recorded INSIDE other frozen
    artifacts when those artifacts were sealed. Recomputing them here and comparing
    against those receipts proves the bytes measured are the bytes that were frozen,
    which a path-resolved read cannot establish on its own."""
    try:
        expected = [
            ("r11_pyzx_source_registry", r11pr["bindings"]["frozen_registry_sha256"],
             "R11 post-review bindings.frozen_registry_sha256"),
            ("r11_pyzx_results", r11pr["bindings"]["raw_result_sha256"],
             "R11 post-review bindings.raw_result_sha256"),
            ("r12_registry_nonidentifiability", pr1469["json_receipts"][0]["sha256"],
             "PR1469 audit json_receipts[0].sha256"),
        ]
    except Exception as exc:                       # noqa: BLE001 - reported verbatim
        raise CannotCheck("cannot read frozen receipt digests: %s" % exc)
    rows, mismatches = [], []
    for key, want, src in expected:
        got = bindings[key]["sha256"]
        rows.append({"input": key, "recorded_in": src, "matches": got == want})
        if got != want:
            mismatches.append({"input": key, "computed": got, "recorded": want,
                               "recorded_in": src})
    return rows, mismatches


# ------------------------------------------------------- the frozen move system

def declared_moves(n):
    """Declared candidate moves: strictly resource-decreasing pairs. |D_n| = n(n-1)/2."""
    return tuple((s, t) for s in range(2, n + 1) for t in range(1, s))


def outgoing_sources(registry):
    return set(s for s, _ in registry)


def terminal_states(n, registry):
    out = outgoing_sources(registry)
    return set(s for s in range(1, n + 1) if s not in out)


def terminal_complexity(n, registry):
    """The declared completeness metric. None when no state is terminal (undefined)."""
    term = terminal_states(n, registry)
    return max(term) if term else None


def source_complete(n, registry):
    out = outgoing_sources(registry)
    return all(s in out for s in range(2, n + 1))


def successors_map(n, registry):
    succ = dict((s, []) for s in range(1, n + 1))
    for s, t in registry:
        if s in succ:
            succ[s].append(t)
    return succ


def descendants_bfs(n, registry):
    """Reflexive-transitive reachability, by breadth-first closure. Method 1."""
    succ = successors_map(n, registry)
    desc = {}
    for s in range(1, n + 1):
        seen = set([s])
        stack = [s]
        while stack:
            u = stack.pop()
            for v in succ.get(u, ()):
                if v not in seen:
                    seen.add(v)
                    stack.append(v)
        desc[s] = frozenset(seen)
    return desc


def descendants_closure(n, registry):
    """Reflexive-transitive reachability, by iterated relational composition. Method 2."""
    reach = dict((s, set([s])) for s in range(1, n + 1))
    for s, t in registry:
        reach[s].add(t)
    changed = True
    while changed:
        changed = False
        for s in range(1, n + 1):
            add = set()
            for u in reach[s]:
                add |= reach[u]
            if not add <= reach[s]:
                reach[s] |= add
                changed = True
    return dict((s, frozenset(v)) for s, v in reach.items())


def normal_forms(n, registry, desc=None):
    """NF(s) = terminal states reachable from s. Empty set means s never reduces to
    a normal form (only possible once a non-terminating operation is present)."""
    d = desc if desc is not None else descendants_bfs(n, registry)
    term = terminal_states(n, registry)
    return dict((s, frozenset(d[s] & term)) for s in range(1, n + 1))


def critical_pairs(n, registry):
    """Local peaks t1 <- s -> t2 with t1 != t2, counted UNORDERED.

    This is the abstract-rewriting analogue of a critical pair: the move system has
    no terms and no left-hand-side overlap, so the Knuth-Bendix construction does not
    apply literally. Every divergence in this system is a local peak at a single
    source state, and that is what is enumerated here."""
    by_source = defaultdict(list)
    for s, t in registry:
        by_source[s].append(t)
    pairs = []
    for s in sorted(by_source):
        targets = sorted(set(by_source[s]))
        for t1, t2 in itertools.combinations(targets, 2):
            pairs.append((s, t1, t2))
    return pairs


def pair_joins(desc, t1, t2):
    return bool(desc[t1] & desc[t2])


# --------------------------------------------------------- S1 census: runtime

def closed_form_source_complete(n):
    """Prior art Theorem B: prod_{s=2}^{n} (2^(s-1) - 1)."""
    v = 1
    for s in range(2, n + 1):
        v *= (2 ** (s - 1) - 1)
    return v


def closed_form_move_occurrences(n):
    """Total move occurrences summed over all 2^E registries: each of the E declared
    moves is present in exactly half of them, so the total is E * 2^(E-1)."""
    e = n * (n - 1) // 2
    return e * (2 ** (e - 1))


def closed_form_critical_pairs(n):
    """Total unordered local peaks summed over all 2^E registries on n states.

    For source s the targets are the s-1 states below it, each present independently,
    so summing C(d_s, 2) over all registries gives, using
    sum_d C(m,d) C(d,2) = C(m,2) 2^(m-2),
        2^(E-(s-1)) * C(s-1,2) * 2^(s-3) = C(s-1,2) * 2^(E-2).
    Summing over s = 2..n and applying the hockey-stick identity
    sum_{k=1}^{n-1} C(k,2) = C(n,3) gives C(n,3) * 2^(E-2).
    Multiply before dividing so n = 2 (E = 1) stays exact."""
    e = n * (n - 1) // 2
    return (math.comb(n, 3) * (2 ** e)) // 4


def confluent_count_recursion(n):
    """Independent count of confluent registries, without enumerating registries.

    Build states 1..n in increasing order, tracking only the partition of the states
    built so far into normal-form classes (states sharing a unique normal form). When
    state m+1 is added its target set must be either empty (m+1 becomes a new terminal
    and its own class) or a nonempty subset of exactly ONE existing class (2^c - 1
    choices for a class of size c). A target set spanning two classes gives m+1 two
    distinct reachable normal forms, which is precisely non-confluence."""
    states = {(1,): 1}                                    # after state 1
    for _ in range(2, n + 1):
        nxt = defaultdict(int)
        for sizes, cnt in states.items():
            nxt[tuple(sorted(sizes + (1,)))] += cnt       # empty target set
            for i in range(len(sizes)):
                lst = list(sizes)
                lst[i] += 1
                nxt[tuple(sorted(lst))] += cnt * (2 ** sizes[i] - 1)
        states = dict(nxt)
    return sum(states.values())


def enumerate_panel(ns, frozen_hist):
    """One exhaustive pass per n. Produces the runtime census, the confluence stage,
    and the control cross-checks that need per-registry data."""
    rows = []
    alarms = []
    for n in ns:
        edges = declared_moves(n)
        e = len(edges)
        total = 1 << e

        sc_count = 0
        cp_total = 0
        cp_joining = 0
        nonjoin_witness = None
        confluent_count = 0
        locally_confluent_count = 0
        newman_disagreements = 0
        reach_method_disagreements = 0
        live_move_total = 0
        dead_move_total = 0
        sc_and_confluent = 0
        confluent_not_sc = 0
        confluent_not_sc_witness = None
        nonjoin_in_source_complete = 0

        for mask in range(total):
            reg = frozenset(edges[i] for i in range(e) if (mask >> i) & 1)
            desc = descendants_bfs(n, reg)

            # C8: second, independent reachability algorithm must agree exactly.
            if descendants_closure(n, reg) != desc:
                reach_method_disagreements += 1

            sc = source_complete(n, reg)
            if sc:
                sc_count += 1

            # live / dead move census: a move (s,t) can only ever fire in a run that
            # starts at the top state n if s is reachable from n.
            from_top = desc[n]
            for (s, _t) in reg:
                if s in from_top:
                    live_move_total += 1
                else:
                    dead_move_total += 1

            pairs = critical_pairs(n, reg)
            cp_total += len(pairs)
            all_join = True
            for (s, t1, t2) in pairs:
                if pair_joins(desc, t1, t2):
                    cp_joining += 1
                else:
                    all_join = False
                    if sc:
                        nonjoin_in_source_complete += 1
                    if nonjoin_witness is None:
                        nonjoin_witness = {
                            "n": n,
                            "registry_source_target_pairs":
                                sorted([list(p) for p in reg]),
                            "peak_source": s, "targets": [t1, t2],
                            "descendants_of_target_1": sorted(desc[t1]),
                            "descendants_of_target_2": sorted(desc[t2]),
                            "source_complete": sc,
                            "terminal_complexity": terminal_complexity(n, reg)}
            if all_join:
                locally_confluent_count += 1

            nf = normal_forms(n, reg, desc)
            glob = all(len(nf[s]) == 1 for s in range(1, n + 1))
            if glob:
                confluent_count += 1
                if not sc:
                    confluent_not_sc += 1
                    # prefer the LARGEST such registry: the empty registry is
                    # confluent for trivial reasons and is a weak exhibit.
                    if (confluent_not_sc_witness is None
                            or len(reg) > confluent_not_sc_witness["move_count"]):
                        confluent_not_sc_witness = {
                            "move_count": len(reg),
                            "n": n,
                            "registry_source_target_pairs":
                                sorted([list(p) for p in reg]),
                            "terminal_complexity": terminal_complexity(n, reg),
                            "normal_form_of_each_state":
                                dict((str(s), sorted(nf[s])) for s in range(1, n + 1))}
                if sc:
                    sc_and_confluent += 1

            # C4 Newman: this system is terminating (every move strictly decreases the
            # state), so local confluence and confluence must coincide exactly.
            if all_join != glob:
                newman_disagreements += 1

        cf_sc = closed_form_source_complete(n)
        cf_cp = closed_form_critical_pairs(n)
        rec_conf = confluent_count_recursion(n)
        frozen_at_1 = int(frozen_hist.get(n, {}).get("1", -1))

        if not (sc_count == cf_sc == frozen_at_1):
            alarms.append({"control": "C2_R12_HISTOGRAM_CROSSCHECK", "n": n,
                           "enumerated": sc_count, "closed_form": cf_sc,
                           "frozen_r12_at_complexity_1": frozen_at_1})
        if cp_total != cf_cp:
            alarms.append({"control": "C3_CRITICAL_PAIR_CLOSED_FORM", "n": n,
                           "enumerated": cp_total, "closed_form": cf_cp})
        if confluent_count != rec_conf:
            alarms.append({"control": "C5_CONFLUENT_COUNT_RECURSION", "n": n,
                           "enumerated": confluent_count, "recursion": rec_conf})
        if newman_disagreements:
            alarms.append({"control": "C4_NEWMAN_AGREEMENT", "n": n,
                           "disagreements": newman_disagreements})
        if reach_method_disagreements:
            alarms.append({"control": "C8_REACHABILITY_TWO_METHODS", "n": n,
                           "disagreements": reach_method_disagreements})
        if sc_and_confluent != sc_count or nonjoin_in_source_complete:
            alarms.append({"control": "C9_SOURCE_COMPLETE_IMPLIES_CONFLUENT", "n": n,
                           "source_complete": sc_count, "of_those_confluent": sc_and_confluent,
                           "non_joinable_pairs_in_source_complete": nonjoin_in_source_complete})
        cf_occ = closed_form_move_occurrences(n)
        if live_move_total + dead_move_total != cf_occ:
            alarms.append({"control": "C13_MOVE_OCCURRENCE_CLOSED_FORM", "n": n,
                           "enumerated": live_move_total + dead_move_total,
                           "closed_form": cf_occ})

        rows.append({
            "n": n,
            "declared_moves": e,
            "registries_total": total,
            "source_complete_count": sc_count,
            "source_complete_closed_form": cf_sc,
            "frozen_r12_count_at_complexity_1": frozen_at_1,
            "critical_pairs_total": cp_total,
            "critical_pairs_closed_form": cf_cp,
            "critical_pairs_joining": cp_joining,
            "critical_pairs_non_joinable": cp_total - cp_joining,
            "non_joinable_pairs_in_source_complete_registries": nonjoin_in_source_complete,
            "locally_confluent_registries": locally_confluent_count,
            "confluent_registries": confluent_count,
            "confluent_registries_recursion": rec_conf,
            "confluent_but_not_source_complete": confluent_not_sc,
            "live_move_occurrences": live_move_total,
            "dead_move_occurrences": dead_move_total,
            "move_occurrences_closed_form": cf_occ,
            "non_joinable_witness": nonjoin_witness,
            "confluent_not_source_complete_witness": confluent_not_sc_witness,
        })
    return rows, alarms


# ------------------------------------------- S1 census: source (pinned registry)

CONTROL_NODES = ("full_reduce", "clifford_simp", "interior_clifford_simp", "spider_simp")


def normalize_symbol(sym):
    """One move is spelled three ways across the three frozen artifacts:
    'BaseGraph.remove_isolated_vertices', 'g.remove_isolated_vertices' and bare
    'remove_isolated_vertices'. Strip a single receiver qualifier so the three
    independent inventories can be compared as sets."""
    return sym.split(".")[-1] if "." in sym else sym


def source_census(srcreg, r11res, r11pr):
    schemas = srcreg["registered_schemas"]
    order = srcreg["registered_symbol_order"]
    declared = set(order)

    by_kind = defaultdict(int)
    for s in schemas:
        by_kind[s["kind"]] += 1
    exact_search = sum(1 for s in schemas if s.get("exact_search_enabled"))

    # reachability of each declared move from the pinned entrypoint, over the frozen
    # control call graph; count DISTINCT symbols, not paths (full_reduce reaches
    # interior_clifford_simp both directly and through clifford_simp).
    ccg = srcreg["control_call_graph"]
    seen, stack = set(), ["full_reduce"]
    while stack:
        u = stack.pop()
        for v in ccg.get(u, ()):
            w = normalize_symbol(v)
            if w not in seen:
                seen.add(w)
                if w in ccg:
                    stack.append(w)
    reachable_moves = sorted(seen & declared)
    unreachable_moves = sorted(declared - seen)

    # five independent frozen counts of the same object
    ra = r11res["registry_audit"]
    counts = {
        "registered_schemas": len(schemas),
        "registered_symbol_order": len(order),
        "r11_discovered_count": int(ra["discovered_count"]),
        "r11_discovered_registered_symbols": len(ra["discovered_registered_symbols"]),
        "r11_hostile_single_omissions": len(ra["hostile_single_omissions"]),
        "r11_hostile_omissions_rejected": int(ra["hostile_omissions_rejected"]),
        "post_review_mutated_registry_omissions": len(r11pr["mutated_registry_omissions"]),
        "post_review_mutated_registry_omissions_rejected":
            int(r11pr["mutated_registry_omissions_rejected"]),
    }

    sets = {
        "registered_schemas": set(s["symbol"] for s in schemas),
        "registered_symbol_order": declared,
        "r11_discovered_registered_symbols": set(ra["discovered_registered_symbols"]),
        "r11_hostile_single_omissions": set(x["omitted"] for x in ra["hostile_single_omissions"]),
        "post_review_mutated_registry_omissions":
            set(x["omitted"] for x in r11pr["mutated_registry_omissions"]),
    }

    def graph_moves(graph, benign=None):
        out = set()
        for caller, callees in graph.items():
            drop = set(benign.get(caller, ())) if benign else set()
            for c in callees:
                if c in drop or not isinstance(c, str):
                    continue
                w = normalize_symbol(c)
                if w in CONTROL_NODES:
                    continue
                out.add(w)
        return out

    graphs = {
        "source_registry_control_call_graph": graph_moves(ccg),
        "r11_observed_control_call_graph": graph_moves(ra["observed_control_call_graph"]),
        "post_review_full_pinned_control_call_inventory": graph_moves(
            r11pr["full_pinned_control_call_inventory"],
            r11pr["explicit_benign_nonmutating_calls"]),
    }

    alarms = []
    if len(set(counts.values())) != 1:
        alarms.append({"control": "C1_SOURCE_FIVEFOLD_COUNT_AGREEMENT", "counts": counts})
    for name, st in sets.items():
        if st != declared:
            alarms.append({"control": "C1_SOURCE_FIVEFOLD_COUNT_AGREEMENT",
                           "set_mismatch": name,
                           "missing": sorted(declared - st), "extra": sorted(st - declared)})
    for name, st in graphs.items():
        if st != declared:
            alarms.append({"control": "C10_CALL_GRAPH_SURFACE_EQUALS_REGISTRY",
                           "graph": name,
                           "missing": sorted(declared - st), "extra": sorted(st - declared)})

    excluded = set(srcreg["excluded_public_pyzx_operations"])
    hostile_ext = set(srcreg["hostile_extension_symbols"])
    if hostile_ext & declared:
        alarms.append({"control": "C11_HOSTILE_EXTENSION_DISJOINT_FROM_REGISTRY",
                       "overlap": sorted(hostile_ext & declared)})
    if not hostile_ext <= excluded:
        alarms.append({"control": "C11_HOSTILE_EXTENSION_DISJOINT_FROM_REGISTRY",
                       "hostile_not_in_excluded": sorted(hostile_ext - excluded)})

    return {
        "declared_move_count": len(order),
        "declared_moves": sorted(order),
        "by_kind": dict(sorted(by_kind.items())),
        "exact_search_enabled_count": exact_search,
        "control_nodes": list(CONTROL_NODES),
        "reachable_from_entrypoint": reachable_moves,
        "unreachable_from_entrypoint": unreachable_moves,
        "independent_frozen_counts": counts,
        "excluded_public_operations_count": len(excluded),
        "hostile_extension_symbols": sorted(hostile_ext),
        "input_domain_complete_word_count": srcreg["input_domain"]["complete_word_count"],
        "input_domain_executed_before_fail_closed":
            r11res["input_domain"]["executed_before_fail_closed_terminal"],
        "frozen_round_terminal": r11res["terminal"],
        "normalization_rule": "strip a single receiver qualifier before the final '.' "
                              "so BaseGraph.X, g.X and X compare equal; drop the four "
                              "control nodes and the frozen benign non-mutating calls",
    }, alarms


# ------------------------------------------------- S2 hidden-operation control

def frozen_hidden_edge_reproduction(rows):
    """C6: reproduce every frozen hidden_edge_controls row from the model alone.

    Each frozen row is the empty registry against the single-edge registry {(n,1)}."""
    mismatches = []
    for r in rows:
        n = int(r["n"])
        absent = terminal_complexity(n, frozenset())
        src, tgt = int(r["unresolved_edge_source"]), int(r["unresolved_edge_target"])
        present = terminal_complexity(n, frozenset([(src, tgt)]))
        if (absent != int(r["terminal_complexity_if_absent"])
                or present != int(r["terminal_complexity_if_present"])):
            mismatches.append({"n": n, "recomputed_absent": absent,
                               "recomputed_present": present, "frozen": r})
    return len(rows), mismatches


def hidden_operation_control(ns):
    """Can an UNDECLARED operation change the rewrite relation without moving the
    declared observable?

    Weak observable  -- the R12 direct optimizer signature. Frozen as constant over
      every registry (`same_optimizer_signature_for_every_registry: true`), so it is
      blind to every change, declared or hidden. Recorded as VACUOUS_BY_CONSTRUCTION
      and carries no weight here.
    Strong observable -- terminal_complexity, which R12 shows IS sensitive
      (`one_unresolved_edge_changes_terminal_complexity: true`, 31 frozen rows).

    Ground truth is the normal-form map s |-> NF(s). Classification per (registry,
    hidden op):
      BENIGN             semantics unchanged and strong observable unchanged
      HONESTLY_DETECTED  semantics changed and strong observable changed
      MIMIC              semantics changed, strong observable UNCHANGED
      FALSE_IMPROVEMENT  strong observable falls to EXACTLY 1 while some state loses
                         its normal form -- the metric reads perfectly complete while
                         the system reduces strictly less. This is deliberately the
                         strict `-> 1` subset, so the count is a LOWER BOUND on
                         metric-misleading cases: a hidden op driving tc from 6 to 2
                         while destroying a normal form is counted HONESTLY_DETECTED,
                         because the metric did at least move.
      OBSERVABLE_UNDEFINED  no state is terminal, so the declared metric is undefined
    """
    tally = defaultdict(int)
    witnesses = {}
    per_class = defaultdict(lambda: defaultdict(int))

    for n in ns:
        edges = declared_moves(n)
        e = len(edges)
        for mask in range(1 << e):
            reg = frozenset(edges[i] for i in range(e) if (mask >> i) & 1)
            base_desc = descendants_bfs(n, reg)
            base_nf = normal_forms(n, reg, base_desc)
            base_tc = terminal_complexity(n, reg)

            hidden = []
            for s in range(1, n + 1):
                hidden.append(("SELF_LOOP", (s, s)))               # identity effect
            for t in range(1, n + 1):
                for s in range(t + 1, n + 1):
                    hidden.append(("ASCENDING", (t, s)))           # resource-increasing
            for (s, t) in edges:
                if (s, t) not in reg and t in base_desc[s]:
                    hidden.append(("TRANSITIVE_COMPOSITE", (s, t)))  # already reachable

            for kind, op in hidden:
                ext = frozenset(set(reg) | set([op]))
                ext_desc = descendants_bfs(n, ext)
                ext_nf = normal_forms(n, ext, ext_desc)
                ext_tc = terminal_complexity(n, ext)

                sem_changed = ext_nf != base_nf
                obs_changed = ext_tc != base_tc

                if ext_tc is None:
                    label = "OBSERVABLE_UNDEFINED"
                elif (base_tc is not None and ext_tc == 1 and base_tc != 1
                      and any(len(ext_nf[s]) == 0 for s in range(1, n + 1))):
                    label = "FALSE_IMPROVEMENT"
                elif sem_changed and not obs_changed:
                    label = "MIMIC"
                elif sem_changed and obs_changed:
                    label = "HONESTLY_DETECTED"
                else:
                    label = "BENIGN"

                tally[label] += 1
                per_class[kind][label] += 1

                # keep the SHARPEST witness of each class, not merely the first one:
                # for a false improvement the severity is how far the declared metric
                # wrongly falls; for a mimic it is how many states silently lose their
                # normal form while the metric does not move at all.
                if label == "FALSE_IMPROVEMENT":
                    severity = (base_tc or 0) - (ext_tc or 0)
                elif label == "MIMIC":
                    severity = sum(1 for s in range(1, n + 1)
                                   if len(ext_nf[s]) == 0 and len(base_nf[s]) > 0)
                else:
                    severity = 0
                if label not in witnesses or severity > witnesses[label]["severity"]:
                    witnesses[label] = {
                        "severity": severity,
                        "n": n, "hidden_operation_kind": kind,
                        "hidden_operation_source_target": list(op),
                        "declared_registry_source_target_pairs":
                            sorted([list(p) for p in reg]),
                        "terminal_complexity_before": base_tc,
                        "terminal_complexity_after": ext_tc,
                        "normal_forms_before":
                            dict((str(s), sorted(base_nf[s])) for s in range(1, n + 1)),
                        "normal_forms_after":
                            dict((str(s), sorted(ext_nf[s])) for s in range(1, n + 1)),
                        "weak_observable_before": {"feasible_state_count": n,
                                                   "optimum_value": 1, "optimum_witness": 1},
                        "weak_observable_after": {"feasible_state_count": n,
                                                  "optimum_value": 1, "optimum_witness": 1},
                    }

    alarms = []
    # C7 discrimination: a control that fires on everything, or on nothing, has not
    # been shown to separate a harmful hidden operation from a harmless one.
    for needed in ("BENIGN", "HONESTLY_DETECTED"):
        if tally.get(needed, 0) == 0:
            alarms.append({"control": "C7_HOSTILE_CONTROL_DISCRIMINATES",
                           "missing_class": needed,
                           "reason": "control never produced this class, so it has not "
                                     "been shown to discriminate"})
    return {
        "classification_totals": dict(sorted(tally.items())),
        "by_hidden_operation_kind":
            dict((k, dict(sorted(v.items()))) for k, v in sorted(per_class.items())),
        "witnesses": witnesses,
        "weak_observable_status": "VACUOUS_BY_CONSTRUCTION",
        "weak_observable_citation":
            "REGISTRY_NONIDENTIFIABILITY_R12_RESULTS.json controls."
            "same_optimizer_signature_for_every_registry = true",
    }, alarms


# ------------------------------------------------------------------ self-test

def self_test(ns, frozen_hist, hidden_rows):
    """Exercise the failure paths against perturbed input AND assert the no-alarm
    case on unperturbed input. Returns (ok, report)."""
    results = []

    # P0 control: unperturbed input must raise no alarm at all.
    rows, alarms = enumerate_panel(ns, frozen_hist)
    results.append({"perturbation": "P0_none_unperturbed", "expect": "no alarms",
                    "alarms": len(alarms), "detected": len(alarms) == 0,
                    "note": "no-alarm assertion, not a failure path"})

    # P1: corrupt the frozen histogram -> C2 must fire. The corrupted row must be one
    # this run actually enumerates, or nothing can fire and the perturbation proves
    # nothing (the first version of this test corrupted n=6 while running n=2..4).
    bad = dict((n, dict(v)) for n, v in frozen_hist.items())
    k = ns[-1]
    bad[k] = dict(bad[k])
    bad[k]["1"] = int(bad[k]["1"]) + 1
    _r, a1 = enumerate_panel(ns, bad)
    fired = [x for x in a1 if x["control"] == "C2_R12_HISTOGRAM_CROSSCHECK"]
    results.append({"perturbation": "P1_frozen_histogram_off_by_one",
                    "expect": "C2 fires", "alarms": len(a1), "detected": bool(fired)})

    # P2: off-by-one in the critical-pair closed form -> C3 must fire.
    real = closed_form_critical_pairs
    try:
        globals()["closed_form_critical_pairs"] = lambda n: real(n) + 1
        _r, a2 = enumerate_panel(ns, frozen_hist)
    finally:
        globals()["closed_form_critical_pairs"] = real
    fired = [x for x in a2 if x["control"] == "C3_CRITICAL_PAIR_CLOSED_FORM"]
    results.append({"perturbation": "P2_critical_pair_closed_form_off_by_one",
                    "expect": "C3 fires", "alarms": len(a2), "detected": bool(fired)})

    # P3: break the confluent-count recursion -> C5 must fire.
    realrec = confluent_count_recursion
    try:
        globals()["confluent_count_recursion"] = lambda n: realrec(n) - 1
        _r, a3 = enumerate_panel(ns, frozen_hist)
    finally:
        globals()["confluent_count_recursion"] = realrec
    fired = [x for x in a3 if x["control"] == "C5_CONFLUENT_COUNT_RECURSION"]
    results.append({"perturbation": "P3_confluent_recursion_off_by_one",
                    "expect": "C5 fires", "alarms": len(a3), "detected": bool(fired)})

    # P4: declare a joinable pair non-joinable -> C4 (Newman) must fire.
    realjoin = pair_joins
    try:
        globals()["pair_joins"] = lambda desc, t1, t2: False
        _r, a4 = enumerate_panel(ns, frozen_hist)
    finally:
        globals()["pair_joins"] = realjoin
    fired = [x for x in a4 if x["control"] == "C4_NEWMAN_AGREEMENT"]
    results.append({"perturbation": "P4_injected_fake_non_joinable_pair",
                    "expect": "C4 fires", "alarms": len(a4), "detected": bool(fired)})

    # P5: corrupt one reachability method -> C8 must fire.
    realcl = descendants_closure
    try:
        globals()["descendants_closure"] = lambda n, r: dict(
            (s, frozenset([s])) for s in range(1, n + 1))
        _r, a5 = enumerate_panel(ns, frozen_hist)
    finally:
        globals()["descendants_closure"] = realcl
    fired = [x for x in a5 if x["control"] == "C8_REACHABILITY_TWO_METHODS"]
    results.append({"perturbation": "P5_second_reachability_method_corrupted",
                    "expect": "C8 fires", "alarms": len(a5), "detected": bool(fired)})

    # P6: corrupt a frozen hidden-edge row -> C6 must report a mismatch.
    tampered = [dict(r) for r in hidden_rows]
    tampered[0] = dict(tampered[0])
    tampered[0]["terminal_complexity_if_present"] = \
        int(tampered[0]["terminal_complexity_if_present"]) + 7
    _cnt, mism = frozen_hidden_edge_reproduction(tampered)
    results.append({"perturbation": "P6_frozen_hidden_edge_row_tampered",
                    "expect": "C6 mismatch", "alarms": len(mism), "detected": bool(mism)})

    # P7: unperturbed frozen hidden-edge rows must reproduce with zero mismatch.
    _cnt, mism0 = frozen_hidden_edge_reproduction(hidden_rows)
    results.append({"perturbation": "P7_none_frozen_hidden_edge_unperturbed",
                    "expect": "no mismatch", "alarms": len(mism0),
                    "detected": len(mism0) == 0,
                    "note": "no-alarm assertion, not a failure path"})

    # P8: a source-census set mismatch must fire C1.
    src = load(SRCREG)
    res = load(R11RES)
    pr = load(R11PR)
    broken = json.loads(json.dumps(res))
    broken["registry_audit"]["discovered_registered_symbols"] = \
        broken["registry_audit"]["discovered_registered_symbols"][:-1]
    _c, a8 = source_census(src, broken, pr)
    fired = [x for x in a8 if x["control"] == "C1_SOURCE_FIVEFOLD_COUNT_AGREEMENT"]
    results.append({"perturbation": "P8_source_census_symbol_dropped",
                    "expect": "C1 fires", "alarms": len(a8), "detected": bool(fired)})

    # P9: unperturbed source census must raise no alarm.
    _c, a9 = source_census(src, res, pr)
    results.append({"perturbation": "P9_none_source_census_unperturbed",
                    "expect": "no alarms", "alarms": len(a9), "detected": len(a9) == 0,
                    "note": "no-alarm assertion, not a failure path"})

    # P10: tamper a frozen receipt digest -> C14 must report a mismatch.
    bindings = input_bindings()
    pr1469 = load(PR1469)
    bad_pr = json.loads(json.dumps(pr))
    bad_pr["bindings"]["raw_result_sha256"] = "0" * 64
    _rows, mm = check_input_bindings_against_frozen_receipts(bindings, bad_pr, pr1469)
    results.append({"perturbation": "P10_frozen_receipt_digest_tampered",
                    "expect": "C14 mismatch", "alarms": len(mm), "detected": bool(mm)})

    # P11: unperturbed receipts must match with zero mismatch.
    _rows, mm0 = check_input_bindings_against_frozen_receipts(bindings, pr, pr1469)
    results.append({"perturbation": "P11_none_frozen_receipts_unperturbed",
                    "expect": "no mismatch", "alarms": len(mm0),
                    "detected": len(mm0) == 0,
                    "note": "no-alarm assertion, not a failure path"})

    ok = all(r["detected"] for r in results)
    return ok, results


# ---------------------------------------------------------------------- main

def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--smoke", action="store_true",
                    help="fast mode: n = 2..4 instead of 2..6")
    ap.add_argument("--self-test", action="store_true",
                    help="validate the checker against perturbed inputs and assert "
                         "the no-alarm case; exit 5 if any perturbation is undetected")
    args = ap.parse_args()
    ns = NS_SMOKE if args.smoke else NS_FULL

    try:
        r12 = load(R12)
        prior = load(PRIOR)
        srcreg = load(SRCREG)
        r11res = load(R11RES)
        r11pr = load(R11PR)
        frozen_hist = dict((int(r["n"]), r["terminal_complexity_histogram"])
                           for r in r12["exhaustive_panel"])
        hidden_rows = r12["hidden_edge_controls"]
        bindings = input_bindings()
        pr1469 = load(PR1469)
        binding_rows, binding_mismatches = check_input_bindings_against_frozen_receipts(
            bindings, r11pr, pr1469)
    except CannotCheck as exc:
        print(json.dumps({"schema": "ORION.ORION01.MoveCensusAndConfluence.Result.v1",
                          "terminal": "T4_CANNOT_CHECK_FROZEN_INPUT",
                          "reason": str(exc)}, indent=2))
        return 3

    if args.self_test:
        ok, report = self_test(ns, frozen_hist, hidden_rows)
        print(json.dumps({"schema": "ORION.ORION01.MoveCensusAndConfluence.SelfTest.v1",
                          "interpreter": platform.python_version(),
                          "domain_sizes": ns, "all_perturbations_detected": ok,
                          "perturbations": report,
                          "exit_code": 0 if ok else 5}, indent=2, sort_keys=True))
        return 0 if ok else 5

    alarms = []
    census_src, a = source_census(srcreg, r11res, r11pr)
    alarms += a
    rows, a = enumerate_panel(ns, frozen_hist)
    alarms += a
    hidden_count, hidden_mismatch = frozen_hidden_edge_reproduction(hidden_rows)
    if hidden_mismatch:
        alarms.append({"control": "C6_FROZEN_HIDDEN_EDGE_REPRODUCTION",
                       "mismatches": hidden_mismatch})
    hostile, a = hidden_operation_control(ns)
    alarms += a
    if binding_mismatches:
        alarms.append({"control": "C14_INPUT_BINDINGS_MATCH_FROZEN_RECEIPTS",
                       "mismatches": binding_mismatches})

    # prior-art continuity: our source-complete counts must equal the already-read
    # values in contextual-move-completeness-v1 for every n they share.
    prior_sc = dict((int(p["n"]), int(p["source_complete_count"])) for p in prior["panel"])
    prior_mismatch = [{"n": r["n"], "here": r["source_complete_count"],
                       "prior_art": prior_sc[r["n"]]}
                      for r in rows if r["n"] in prior_sc
                      and prior_sc[r["n"]] != r["source_complete_count"]]
    if prior_mismatch:
        alarms.append({"control": "C12_PRIOR_ART_CONTINUITY", "mismatches": prior_mismatch})

    cannot_check = [{
        "stage": "S3b_live_production_confluence",
        "status": "CANNOT_CHECK",
        "reason": "confluence of the twelve pinned PyZX macro operations on real ZX "
                  "graphs cannot be decided here: this packet is standard-library "
                  "only by protocol, and `import pyzx` fails on all three "
                  "interpreters present on this host (/usr/bin/python3 3.9.6, "
                  "miniforge 3.13.12, homebrew 3.14.6). The confluence result below "
                  "is about the frozen abstract move system only.",
    }, {
        "stage": "S2b_hidden_operation_in_production",
        "status": "CANNOT_CHECK",
        "reason": "whether the pinned PyZX build actually contains an operation of "
                  "the mimicking shape is not decided here. What is decided is that "
                  "the frozen abstract model admits the witness, and that the pinned "
                  "registry declares move kinds of that shape "
                  "(whole_graph_normalization, whole_graph_cleanup, saturating_*).",
    }]

    if alarms:
        terminal, rc = "T4_CANNOT_CHECK_CONTROL_FAILED", 3
    else:
        nonjoin = any(r["critical_pairs_non_joinable"] > 0 for r in rows)
        mimic = (hostile["classification_totals"].get("FALSE_IMPROVEMENT", 0)
                 + hostile["classification_totals"].get("MIMIC", 0)) > 0
        if mimic and nonjoin:
            terminal = "T1_CENSUS_COMPLETE__HIDDEN_OP_WITNESS_FOUND__CONFLUENCE_PARTIAL"
        elif mimic:
            terminal = "T2_CENSUS_COMPLETE__HIDDEN_OP_WITNESS_FOUND__ALL_PAIRS_JOIN"
        elif nonjoin:
            terminal = "T3_CENSUS_COMPLETE__NO_HIDDEN_OP_WITNESS__CONFLUENCE_PARTIAL"
        else:
            terminal = "T5_CENSUS_COMPLETE__NO_HIDDEN_OP_WITNESS__ALL_PAIRS_JOIN"
        rc = 4                                     # declared CANNOT_CHECK sub-stages

    print(json.dumps({
        "schema": "ORION.ORION01.MoveCensusAndConfluence.Result.v1",
        "protocol_identity": "ORION01.MOVE_CENSUS_AND_CONFLUENCE.v1",
        "paper_id": "ORION-01",
        "authority": "MEASUREMENT_AND_PROOF_ONLY",
        "scientific_authority_delta": "NONE",
        "submission_authority": False,
        "extends": "ORION01.CONTEXTUAL_MOVE_COMPLETENESS.v1",
        "interpreter": platform.python_version(),
        "domain_sizes": ns,
        "mode": "smoke" if args.smoke else "full",
        "input_bindings": bindings,
        "S1_census_source": census_src,
        "S1_census_runtime": rows,
        "S2_hidden_operation_control": hostile,
        "S2_frozen_hidden_edge_rows_reproduced": hidden_count,
        "S2_frozen_hidden_edge_mismatches": hidden_mismatch,
        "controls": {
            "C1_SOURCE_FIVEFOLD_COUNT_AGREEMENT": {"passed": not any(
                x["control"] == "C1_SOURCE_FIVEFOLD_COUNT_AGREEMENT" for x in alarms)},
            "C2_R12_HISTOGRAM_CROSSCHECK": {"passed": not any(
                x["control"] == "C2_R12_HISTOGRAM_CROSSCHECK" for x in alarms)},
            "C3_CRITICAL_PAIR_CLOSED_FORM": {"passed": not any(
                x["control"] == "C3_CRITICAL_PAIR_CLOSED_FORM" for x in alarms)},
            "C4_NEWMAN_AGREEMENT": {"passed": not any(
                x["control"] == "C4_NEWMAN_AGREEMENT" for x in alarms),
                "scope": "declared move system only; it is terminating, which is the "
                         "precondition for Newman's lemma. The hostile stage "
                         "deliberately breaks termination and is excluded."},
            "C5_CONFLUENT_COUNT_RECURSION": {"passed": not any(
                x["control"] == "C5_CONFLUENT_COUNT_RECURSION" for x in alarms)},
            "C6_FROZEN_HIDDEN_EDGE_REPRODUCTION": {"passed": not hidden_mismatch,
                                                   "rows": hidden_count},
            "C7_HOSTILE_CONTROL_DISCRIMINATES": {"passed": not any(
                x["control"] == "C7_HOSTILE_CONTROL_DISCRIMINATES" for x in alarms)},
            "C8_REACHABILITY_TWO_METHODS": {"passed": not any(
                x["control"] == "C8_REACHABILITY_TWO_METHODS" for x in alarms)},
            "C9_SOURCE_COMPLETE_IMPLIES_CONFLUENT": {"passed": not any(
                x["control"] == "C9_SOURCE_COMPLETE_IMPLIES_CONFLUENT" for x in alarms)},
            "C10_CALL_GRAPH_SURFACE_EQUALS_REGISTRY": {"passed": not any(
                x["control"] == "C10_CALL_GRAPH_SURFACE_EQUALS_REGISTRY" for x in alarms)},
            "C11_HOSTILE_EXTENSION_DISJOINT_FROM_REGISTRY": {"passed": not any(
                x["control"] == "C11_HOSTILE_EXTENSION_DISJOINT_FROM_REGISTRY"
                for x in alarms)},
            "C12_PRIOR_ART_CONTINUITY": {"passed": not prior_mismatch},
            "C13_MOVE_OCCURRENCE_CLOSED_FORM": {"passed": not any(
                x["control"] == "C13_MOVE_OCCURRENCE_CLOSED_FORM" for x in alarms)},
            "C14_INPUT_BINDINGS_MATCH_FROZEN_RECEIPTS": {
                "passed": not binding_mismatches, "checked": binding_rows},
        },
        "alarms": alarms,
        "cannot_check": cannot_check,
        "terminal": terminal,
        "exit_code": rc,
    }, indent=2, sort_keys=True))
    return rc


if __name__ == "__main__":
    raise SystemExit(main())
