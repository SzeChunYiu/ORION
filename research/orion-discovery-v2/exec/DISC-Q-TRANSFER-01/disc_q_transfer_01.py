"""DISC-Q-TRANSFER-01 -- ORION-Q structural navigation transfer under
target-native validation and matched resources.

Spec: research/orion-discovery-v2/KNOWLEDGE_WEB_NAVIGATION_PROOF_ECONOMY_AND_SELF_APPLICATION_V1.md
      sections 8.3/8.5 (branch codex/orion-discovery-v2-knowledge-web-20260825)
Job:  research/orion-discovery-v2/EXECUTION_BACKLOG_V1.json :: DISC-Q-TRANSFER-01
Donor source: papers/candidates/qg-paper-03-stub/MANUSCRIPT_V1.md
Target input: research/orion-discovery-v2/exec/DISC-PROOF-ECONOMY-01/PROOF_OBLIGATION_REGISTER.json

AUTHORITY. This module may license a TARGET-DOMAIN result only. The target
domain is the OSTC evidence-selection problem: a finite, non-quantum,
exactly-enumerable set-cover instance over registered execution-evidence jobs.
NO quantum authority is transferred. Nothing computed here is a physical claim,
a hardware claim, or a quantum-advantage claim of any kind; the donor is used
only as a source of STRUCTURAL METHOD (a definition and a proof technique),
per spec section 8.5 and theorem QX-T1 (method may transfer, source scientific
authority may not).

Arithmetic: integers only. No float is constructed in this module.
Enumeration: total over the declared bound, or the cannot_check terminal.
"""

from __future__ import annotations

import hashlib
import itertools
import json
from collections import Counter, defaultdict
from pathlib import Path

ROOT = Path("/Users/billy/ORION-claude")
PE_DIR = ROOT / "research/orion-discovery-v2/exec/DISC-PROOF-ECONOMY-01"
WEB_DIR = ROOT / "research/orion-discovery-v2/exec/DISC-WEB-01"
DONOR = ROOT / "papers/candidates/qg-paper-03-stub/MANUSCRIPT_V1.md"
OUT = ROOT / "research/orion-discovery-v2/exec/DISC-Q-TRANSFER-01"

# Declared total-enumeration bound. Exceeding it returns the cannot_check
# terminal rather than sampling and calling the result exact.
ENUMERATION_BOUND = 1_000_000
# Declared cap for the exchange-relation scan (relation R5).
EXCHANGE_SCAN_CAP = 2_000_000

COST_COMPONENTS = ["distinct_support_nodes", "distinct_support_edges",
                   "unvalidated_jobs", "obstructed_jobs"]
RESOURCE_COMPONENTS = ["subsets_enumerated", "coverage_evaluations",
                       "cost_vector_evaluations", "dominance_comparisons",
                       "oracle_subsets_enumerated"]


def sha256_file(p: Path) -> str:
    return hashlib.sha256(p.read_bytes()).hexdigest()


def popcount(x: int) -> int:
    return bin(x).count("1")


def dominates(a, b):
    """Pareto dominance on integer vectors. No weights, no scalar collapse."""
    return all(x <= y for x, y in zip(a, b)) and any(x < y for x, y in zip(a, b))


# --------------------------------------------------------------------------
# 1. Target instance: OSTC evidence-selection as a finite subset lattice.
# --------------------------------------------------------------------------

def build_target():
    reg = json.loads((PE_DIR / "PROOF_OBLIGATION_REGISTER.json").read_text())
    web = json.loads((WEB_DIR / "KNOWLEDGE_WEB_V1.json").read_text())
    options = reg["proof_options"]

    jobs = sorted({o["evidence_node"] for o in options})
    job_ix = {j: i for i, j in enumerate(jobs)}

    # a job covers obligation t only through an option whose hard
    # preconditions are ALL attained (DISC-PROOF-ECONOMY-01 semantics)
    covers = defaultdict(set)
    nodes_of = defaultdict(set)
    edges_of = defaultdict(set)
    unvalidated, obstructed = set(), set()
    for o in options:
        j = o["evidence_node"]
        nodes_of[j].update(o["required_nodes"])
        edges_of[j].update(tuple(e) for e in o["required_edges"])
        if not o["has_independent_validator"]:
            unvalidated.add(j)
        if o["obstructed"]:
            obstructed.add(j)
        if o["all_hard_preconditions_attained"]:
            covers[j].add(o["scope"])

    obligations = sorted(set().union(*covers.values()))
    obl_ix = {t: i for i, t in enumerate(obligations)}

    all_nodes = sorted(set().union(*nodes_of.values()))
    all_edges = sorted(set().union(*edges_of.values()))
    node_ix = {n: i for i, n in enumerate(all_nodes)}
    edge_ix = {e: i for i, e in enumerate(all_edges)}

    cov_mask, node_mask, edge_mask = [], [], []
    for j in jobs:
        cov_mask.append(sum(1 << obl_ix[t] for t in covers[j]))
        node_mask.append(sum(1 << node_ix[n] for n in nodes_of[j]))
        edge_mask.append(sum(1 << edge_ix[e] for e in edges_of[j]))
    unval_mask = sum(1 << job_ix[j] for j in unvalidated)
    obstr_mask = sum(1 << job_ix[j] for j in obstructed)
    full_cov = (1 << len(obligations)) - 1

    return {
        "jobs": jobs, "job_ix": job_ix, "obligations": obligations,
        "cov_mask": cov_mask, "node_mask": node_mask, "edge_mask": edge_mask,
        "unval_mask": unval_mask, "obstr_mask": obstr_mask,
        "full_cov": full_cov, "n_jobs": len(jobs),
        "covers": {j: sorted(covers[j]) for j in jobs},
        "ballast_jobs": sorted(j for j in jobs if not covers[j]),
        "web_counts": web["counts"],
    }


class Resources:
    """Exact integer resource counters, incremented at the real work sites."""

    def __init__(self):
        self.c = Counter()

    def vec(self):
        return tuple(self.c[k] for k in RESOURCE_COMPONENTS)


def enumerate_bounded(T, max_support, res):
    """GENUINE support-bounded certified search: enumerates only the
    support-<=d configurations, as the donor's search-cost corollary describes.

    This does NOT walk the full lattice. Using the lattice DP and then filtering
    would leave every arm with the same subsets_enumerated count and make the
    resource comparison meaningless.
    """
    n = T["n_jobs"]
    cm, nm, em = T["cov_mask"], T["node_mask"], T["edge_mask"]
    full = T["full_cov"]
    uv, ob = T["unval_mask"], T["obstr_mask"]
    best = {}
    n_adequate = 0
    for k in range(1, max_support + 1):
        for combo in itertools.combinations(range(n), k):
            res.c["subsets_enumerated"] += 1
            cov = 0
            for b in combo:
                cov |= cm[b]
            res.c["coverage_evaluations"] += 1
            if cov != full:
                continue
            n_adequate += 1
            nod = edg = mask = 0
            for b in combo:
                nod |= nm[b]
                edg |= em[b]
                mask |= 1 << b
            res.c["cost_vector_evaluations"] += 1
            cost = (popcount(nod), popcount(edg),
                    popcount(mask & uv), popcount(mask & ob))
            cur = best.get(cost)
            if cur is None or k < cur:
                best[cost] = k
    return best, {"bounded": True, "space_size": sum(
        len(list(itertools.combinations(range(n), k)))
        for k in range(1, max_support + 1)) if n <= 24 else None,
        "n_adequate": n_adequate, "n_distinct_costs": len(best)}


def enumerate_lattice(T, max_support=None, res=None):
    """TOTAL enumeration of the subset lattice (optionally support-bounded).

    Returns cost-vector -> minimum support attaining it, over ADEQUATE plans.
    Support (|subset|) is deliberately NOT a cost component: in the donor,
    kappa constrains the support of optima under a SEPARATE objective.
    """
    n = T["n_jobs"]
    total = 1 << n
    if total > ENUMERATION_BOUND:
        return None, {"bounded": False, "space_size": total}

    cov = [0] * total
    nod = [0] * total
    edg = [0] * total
    cm, nm, em = T["cov_mask"], T["node_mask"], T["edge_mask"]
    full = T["full_cov"]
    unval_mask, obstr_mask = T["unval_mask"], T["obstr_mask"]

    best = {}                      # cost vector -> min support
    n_adequate = 0
    for mask in range(1, total):
        low = mask & -mask
        rest = mask ^ low
        b = low.bit_length() - 1
        cov[mask] = cov[rest] | cm[b]
        nod[mask] = nod[rest] | nm[b]
        edg[mask] = edg[rest] | em[b]
        if res is not None:
            res.c["subsets_enumerated"] += 1
        sup = popcount(mask)
        if max_support is not None and sup > max_support:
            continue
        if res is not None:
            res.c["coverage_evaluations"] += 1
        if cov[mask] != full:
            continue
        n_adequate += 1
        if res is not None:
            res.c["cost_vector_evaluations"] += 1
        cost = (popcount(nod[mask]), popcount(edg[mask]),
                popcount(mask & unval_mask), popcount(mask & obstr_mask))
        cur = best.get(cost)
        if cur is None or sup < cur:
            best[cost] = sup
    return best, {"bounded": True, "space_size": total,
                  "n_adequate": n_adequate, "n_distinct_costs": len(best)}


def frontier_of(best, res=None):
    """Exact Pareto frontier over distinct cost vectors. No scalarization."""
    costs = sorted(best)
    front = []
    for c in costs:
        dom = False
        for c2 in costs:
            if c2 == c:
                continue
            if res is not None:
                res.c["dominance_comparisons"] += 1
            if dominates(c2, c):
                dom = True
                break
        if not dom:
            front.append(c)
    return front


def kappa_of(best, front):
    """kappa = least B such that every optimum is attained at support <= B.

    Two-sided by construction here: B = max over optima of the minimum
    attaining support, so B-1 provably fails on the witness attaining the max.
    """
    if not front:
        return None, None
    k = max(best[z] for z in front)
    witness = [z for z in front if best[z] == k]
    return k, witness


# --------------------------------------------------------------------------
# 2. Relational correspondence checks (relational vs surface).
# --------------------------------------------------------------------------

def collect_attaining(T, front_costs, cap=EXCHANGE_SCAN_CAP):
    """Second pass: every adequate plan attaining an optimal cost vector."""
    n = T["n_jobs"]
    total = 1 << n
    if total > cap:
        return None
    cov = [0] * total
    nod = [0] * total
    edg = [0] * total
    cm, nm, em = T["cov_mask"], T["node_mask"], T["edge_mask"]
    full = T["full_cov"]
    uv, ob = T["unval_mask"], T["obstr_mask"]
    want = set(front_costs)
    out = defaultdict(list)
    for mask in range(1, total):
        low = mask & -mask
        rest = mask ^ low
        b = low.bit_length() - 1
        cov[mask] = cov[rest] | cm[b]
        nod[mask] = nod[rest] | nm[b]
        edg[mask] = edg[rest] | em[b]
        if cov[mask] != full:
            continue
        cost = (popcount(nod[mask]), popcount(edg[mask]),
                popcount(mask & uv), popcount(mask & ob))
        if cost in want:
            out[cost].append(mask)
    return out


def cost_of(T, mask):
    nod = edg = 0
    for b in range(T["n_jobs"]):
        if mask >> b & 1:
            nod |= T["node_mask"][b]
            edg |= T["edge_mask"][b]
    return (popcount(nod), popcount(edg),
            popcount(mask & T["unval_mask"]), popcount(mask & T["obstr_mask"]))


def covers_all(T, mask):
    c = 0
    for b in range(T["n_jobs"]):
        if mask >> b & 1:
            c |= T["cov_mask"][b]
    return c == T["full_cov"]


def exchange_scan(T, attaining, best):
    """Relation R5 -- the descent-ladder precondition.

    A descent ladder pushes an optimum DOWN in support by local edits that keep
    it an optimum. Test exactly: for an adequate plan attaining optimal cost z
    at support s > min-support(z), is there a single-element removal or a
    single-element swap giving an adequate plan with the SAME cost z and
    strictly smaller support?
    """
    found, checked, above = [], 0, 0
    for z, masks in sorted(attaining.items()):
        mn = best[z]
        for m in masks:
            s = popcount(m)
            if s <= mn:
                continue
            above += 1
            # single-element removal
            for b in range(T["n_jobs"]):
                if not (m >> b & 1):
                    continue
                m2 = m ^ (1 << b)
                checked += 1
                if covers_all(T, m2) and cost_of(T, m2) == z:
                    found.append({"optimal_cost": list(z), "from_support": s,
                                  "to_support": popcount(m2), "edit": "REMOVE",
                                  "job_index": b})
                    break
            if found and found[-1]["optimal_cost"] == list(z):
                continue
            # single-element swap
            for b in range(T["n_jobs"]):
                if not (m >> b & 1):
                    continue
                for c in range(T["n_jobs"]):
                    if m >> c & 1:
                        continue
                    m2 = (m ^ (1 << b)) | (1 << c)
                    checked += 1
                    if popcount(m2) < s and covers_all(T, m2) and cost_of(T, m2) == z:
                        found.append({"optimal_cost": list(z), "from_support": s,
                                      "to_support": popcount(m2), "edit": "SWAP"})
                        break
    exercised = above > 0
    return {"exchanges_found": len(found), "witnesses": found[:10],
            "plans_above_min_support": above, "edits_checked": checked,
            "exercised": exercised,
            "exists": (bool(found) if exercised else None),
            "verdict": ("EXCHANGE_EXISTS" if found else
                        "NO_EXCHANGE_EXISTS" if exercised else
                        "NOT_EXERCISED_PREMISE_CLASS_EMPTY"),
            "note": ("" if exercised else
                     "Every optimum is attained exactly at the coverage floor, so the "
                     "set of optimum-attaining configurations ABOVE minimum support is "
                     "empty. A descent ladder has nothing to descend. This is "
                     "vacuity, not refutation, and must not be recorded as a "
                     "failed relation.")}


def exchange_scan_scalar(T, comp_index, cap=200000):
    """Non-vacuity control running the SAME detector under a scalar objective.

    Under a scalar objective the optimum is a single value with a tie class, so
    optimum-attaining configurations above minimum support can exist. Running
    the real detector there shows it is not inert.
    """
    n = T["n_jobs"]
    total = 1 << n
    cov = [0] * total
    nod = [0] * total
    edg = [0] * total
    cm, nm, em = T["cov_mask"], T["node_mask"], T["edge_mask"]
    full = T["full_cov"]
    uv, ob = T["unval_mask"], T["obstr_mask"]
    vals = {}
    for mask in range(1, total):
        low = mask & -mask
        rest = mask ^ low
        b = low.bit_length() - 1
        cov[mask] = cov[rest] | cm[b]
        nod[mask] = nod[rest] | nm[b]
        edg[mask] = edg[rest] | em[b]
        if cov[mask] != full:
            continue
        c = (popcount(nod[mask]), popcount(edg[mask]),
             popcount(mask & uv), popcount(mask & ob))[comp_index]
        vals.setdefault(c, []).append(mask)
    mn = min(vals)
    opt_masks = vals[mn]
    min_sup = min(popcount(m) for m in opt_masks)
    above = [m for m in opt_masks if popcount(m) > min_sup]
    found, checked = [], 0
    for m in above[:cap]:
        s0 = popcount(m)
        hit = False
        for b in range(n):
            if not (m >> b & 1):
                continue
            m2 = m ^ (1 << b)
            checked += 1
            if covers_all(T, m2) and cost_of(T, m2)[comp_index] == mn:
                found.append({"from_support": s0, "to_support": popcount(m2),
                              "edit": "REMOVE"})
                hit = True
                break
        if hit:
            continue
    return {"objective": f"scalar_min_{COST_COMPONENTS[comp_index]}",
            "optimal_value": mn, "min_support": min_sup,
            "plans_above_min_support": len(above), "edits_checked": checked,
            "exercised": bool(above), "exchanges_found": len(found),
            "exists": bool(found) if above else None}


def scalar_exchange_control(T, best):
    """Non-vacuity control for the R5 detector, on the SAME real instance.

    Under a scalar objective the optimum is an argmin with ties, so a
    cost-preserving support-reducing exchange CAN exist. Running the detector
    on each single-component objective shows it is not inert, and it makes the
    donor's objective-indexing claim testable in the target.
    """
    out = []
    for i, name in enumerate(COST_COMPONENTS):
        proj = {}
        for z, sup in best.items():
            key = (z[i],)
            if key not in proj or sup < proj[key]:
                proj[key] = sup
        mn = min(k[0] for k in proj)
        opt_costs = [z for z in best if z[i] == mn]
        # Under a SCALAR objective the optimum is one VALUE, attained as soon as
        # some configuration reaches it, so kappa is the minimum attaining
        # support. Under the PARTIAL order every non-dominated vector is a
        # separate optimum that must each be attained, so kappa is the maximum
        # over optima of the minimum attaining support. The two readings are
        # recorded explicitly because they are not the same quantity.
        k_scalar = min(best[z] for z in opt_costs)
        # cost-preserving here means: same scalar objective value
        supports = sorted({best[z] for z in opt_costs})
        out.append({
            "objective": f"scalar_min_{name}",
            "optimal_value": mn,
            "kappa_scalar": k_scalar,
            "n_optimum_cost_vectors": len(opt_costs),
            "attaining_supports": supports,
            "tie_class_nontrivial": len(opt_costs) > 1,
            "support_reducing_move_available_within_optimum_class":
                len(supports) > 1,
        })
    return out


# --------------------------------------------------------------------------

def main() -> int:
    OUT.mkdir(parents=True, exist_ok=True)
    T = build_target()

    inputs = {
        "PROOF_OBLIGATION_REGISTER.json": sha256_file(PE_DIR / "PROOF_OBLIGATION_REGISTER.json"),
        "KNOWLEDGE_WEB_V1.json": sha256_file(WEB_DIR / "KNOWLEDGE_WEB_V1.json"),
        "QG-paper-03 MANUSCRIPT_V1.md": sha256_file(DONOR),
    }

    # ---- ARM D1: donor, total enumeration (target-native validator) -------
    res_donor = Resources()
    best, stats = enumerate_lattice(T, None, res_donor)
    if best is None:
        payload = {"terminal": "TARGET_VALIDATOR_OR_CORRESPONDENCE_CANNOT_CHECK",
                   "reason": "subset lattice exceeds ENUMERATION_BOUND",
                   "space_size": stats["space_size"], "bound": ENUMERATION_BOUND}
        (OUT / "TARGET_NATIVE_VALIDATION_RECEIPT.json").write_text(
            json.dumps(payload, indent=2) + "\n")
        print(json.dumps(payload, indent=2))
        return 0
    front = frontier_of(best, res_donor)
    kappa, kappa_witness = kappa_of(best, front)
    donor_vec = res_donor.vec()

    # ---- classical a-priori bound, no enumeration (donor D2) --------------
    # Every frontier plan is an irredundant cover: if a job could be removed
    # with the cover preserved, the smaller plan's node/edge unions are subsets
    # so its cost vector is <= and the larger plan would be dominated. In an
    # irredundant cover every member holds a private obligation, so
    # support <= |obligations|. This needs no enumeration at all.
    classical_bound = len(T["obligations"])
    attaining = collect_attaining(T, front)
    irredundant_check = None
    if attaining is not None:
        viol = []
        for z, masks in attaining.items():
            for m in masks:
                if popcount(m) != best[z]:
                    continue
                for b in range(T["n_jobs"]):
                    if m >> b & 1 and covers_all(T, m ^ (1 << b)):
                        viol.append({"cost": list(z), "removable_job":
                                     T["jobs"][b]})
        irredundant_check = {
            "claim": "every minimum-support frontier plan is an irredundant cover",
            "violations": viol[:10], "n_violations": len(viol),
            "holds": not viol}

    # ---- does kappa collapse to the classical covering number? ------------
    # The minimum cardinality of a covering subset is the textbook minimum
    # set-cover optimum -- a donor discipline QG-paper-03 explicitly disclaims
    # novelty over. If kappa equals it, the transferred QUANTITY is not even a
    # new quantity in this target.
    min_cover_size = min(best.values()) if best else None
    kappa_is_covering_number = (kappa == min_cover_size)

    # Independent route to the covering number: the smallest k for which a
    # support-bounded search finds ANY adequate plan. Checked separately from
    # min(best.values()) because the collapse claim is the headline finding.
    probe_k = None
    for k in range(1, T["n_jobs"] + 1):
        rp = Resources()
        bk, _ = enumerate_bounded(T, k, rp)
        if bk:
            probe_k = k
            break
    covering_number_cross_check = {
        "via_min_of_cost_keyed_minima": min_cover_size,
        "via_smallest_feasible_support_bound": probe_k,
        "agree": probe_k == min_cover_size,
    }

    # ---- can ANY objective exhibit objective indexing on this instance? ---
    # A minimiser of any strictly monotone objective is Pareto non-dominated.
    # So every such objective's optimum lies in the frontier. If every frontier
    # cost is attained at the same minimum support, no objective can yield a
    # different kappa: the instance is saturated at the coverage floor and
    # objective indexing is UNTESTABLE here, not refuted.
    frontier_min_supports = sorted({best[z] for z in front})
    objective_indexing_testable = len(frontier_min_supports) > 1
    objective_indexing_argument = (
        "Every strictly monotone objective attains its optimum at a Pareto "
        "non-dominated cost vector. All %d frontier costs here are attained at "
        "minimum support %s, so kappa = %s for every such objective. The instance "
        "is saturated at the coverage floor; objective indexing cannot be exercised "
        "on it." % (len(front), frontier_min_supports, kappa))

    # ---- ARM T1: transferred method, support-bounded certified search -----
    res_tr = Resources()
    best_t, stats_t = enumerate_bounded(T, kappa, res_tr)
    front_t = frontier_of(best_t, res_tr)
    transfer_vec = res_tr.vec()
    frontier_recovered = set(front_t) == set(front)

    # ---- ARM T1-oracle-charged: kappa came FROM the total enumeration -----
    # kappa is not available a priori. It was produced by the donor's total
    # enumeration, so that enumeration is charged to this arm. An oracle call
    # that enumerates subsets consumes the SAME physical resource as
    # enumerating subsets, so it is folded into subsets_enumerated rather than
    # parked on a separate axis: splitting it out would let the arm hide its
    # true cost in a different dimension, which is laundering by axis-split.
    res_or = Resources()
    res_or.c.update(res_tr.c)
    for k in ("subsets_enumerated", "coverage_evaluations",
              "cost_vector_evaluations", "dominance_comparisons"):
        res_or.c[k] += res_donor.c[k]
    oracle_vec = res_or.vec()
    # the rejected split-axis variant, reported for transparency
    res_split = Resources()
    res_split.c.update(res_tr.c)
    res_split.c["oracle_subsets_enumerated"] = res_donor.c["subsets_enumerated"]
    split_vec = res_split.vec()

    # ---- ARM D2: classical bound, no oracle ------------------------------
    res_cl = Resources()
    best_c, _ = enumerate_bounded(T, classical_bound, res_cl)
    front_c = frontier_of(best_c, res_cl)
    classical_vec = res_cl.vec()
    classical_recovers = set(front_c) == set(front)

    # ---- relational correspondence checks --------------------------------
    exch = exchange_scan(T, attaining, best) if attaining is not None else None
    control = scalar_exchange_control(T, best)
    # run the SAME detector where the premise class is non-empty
    scalar_exch = [exchange_scan_scalar(T, i) for i in (2, 3)]

    kappa_by_objective = [{"objective": "pareto_vector", "kappa": kappa,
                           "n_optima": len(front)}]
    for c in control:
        kappa_by_objective.append({"objective": c["objective"],
                                   "kappa": c["kappa_scalar"],
                                   "n_optima": c["n_optimum_cost_vectors"]})
    objective_indexed = len({k["kappa"] for k in kappa_by_objective}) > 1

    relations = [
        {"id": "R1", "name": "GRADED_SUPPORT_ON_A_LATTICE",
         "donor_side": "global support of structural generators in a configuration",
         "target_side": "cardinality of the selected evidence-job subset",
         "preserved": True, "load_bearing": True,
         "evidence": ("support is a grading on the subset lattice and "
                      "{P : |P| <= B} is downward closed, as in the donor"),
         "check": "structural"},
        {"id": "R2", "name": "OPTIMUM_ATTAINMENT_AT_BOUNDED_SUPPORT",
         "donor_side": "every instance optimum attained at support <= kappa",
         "target_side": "every Pareto-optimal cost vector attained at support <= kappa",
         "preserved": bool(kappa is not None and all(best[z] <= kappa for z in front)),
         "load_bearing": True,
         "evidence": {"kappa": kappa, "max_min_support": (max(best[z] for z in front)
                                                          if front else None)},
         "check": "exact"},
        {"id": "R3", "name": "TWO_SIDEDNESS",
         "donor_side": "kappa valid and kappa-1 invalid, lower bound needs an infeasibility witness",
         "target_side": "kappa valid and kappa-1 invalid, witnessed by the optimum forcing the max",
         "preserved": bool(kappa_witness), "load_bearing": True,
         "evidence": {"witness_costs": [list(z) for z in (kappa_witness or [])]},
         "caveat": ("two-sidedness is FREE here because the instance is totally "
                    "enumerated; in the donor it requires a separate lower-bound "
                    "witness over an infinite family. The discipline transfers, "
                    "the difficulty does not."),
         "check": "exact"},
        {"id": "R4", "name": "OBJECTIVE_INDEXING",
         "donor_side": "kappa takes two arguments; bounds are objective-scoped",
         "target_side": "kappa differs across the Pareto order and scalar projections",
         "preserved": (objective_indexed if objective_indexing_testable else None),
         "load_bearing": True,
         "evidence": kappa_by_objective,
         "check": ("exact" if objective_indexing_testable else "NOT_EXERCISED"),
         "testable_on_this_instance": objective_indexing_testable,
         "note": objective_indexing_argument,
         "caveat": ("Reporting R4 as REFUTED would overstate what a floor-saturated "
                    "instance can show. It rests on the same coverage-floor fact that "
                    "empties R5's premise class, and is carried as NOT_EXERCISED for "
                    "the same reason.")},
        {"id": "R5", "name": "COST_PRESERVING_SUPPORT_REDUCING_EXCHANGE",
         "donor_side": ("descent-ladder edit grammar: local edits push an optimum "
                        "down in support while it stays an optimum; each rung "
                        "consumes the previous obstruction census"),
         "target_side": ("single-element removal or swap keeping the plan adequate "
                         "AND preserving its exact cost vector"),
         "preserved": (exch["exists"] if (exch and exch["exercised"]) else None),
         "load_bearing": True,
         "evidence": exch,
         "check": ("exact" if (exch and exch["exercised"]) else "NOT_EXERCISED"),
         "control_same_detector_under_scalar_objectives": scalar_exch,
         "note": ("This is the precondition that makes kappa a METHOD rather than "
                  "a notion. Without it the ladder has nothing to descend.")},
        {"id": "R6", "name": "FAMILY_UNIVERSALITY",
         "donor_side": "kappa(F, C) quantifies over every instance of an infinite family (all n)",
         "target_side": "the slice supplies ONE finite instance, not an instance family",
         "preserved": None, "load_bearing": True,
         "evidence": {"target_instances": 1},
         "check": "CANNOT_CHECK",
         "note": ("A per-instance support number is a strictly weaker object than a "
                  "family-intrinsic one. No instance family exists in the target "
                  "slice, and manufacturing one would be fabrication.")},
    ]
    preserved_lb = [r for r in relations if r["load_bearing"] and r["preserved"] is True]
    broken_lb = [r for r in relations if r["load_bearing"] and r["preserved"] is False]
    unchecked_lb = [r for r in relations if r["load_bearing"] and r["preserved"] is None]

    correspondence_type = ("RELATIONAL" if not broken_lb and not unchecked_lb
                           else "PARTIAL_RELATIONAL_WITH_BROKEN_LOAD_BEARING_RELATIONS"
                           if broken_lb else "PARTIAL_RELATIONAL_UNRESOLVED")

    # ---- matched-resource accounting -------------------------------------
    arms = {
        "D1_donor_total_enumeration": donor_vec,
        "D2_donor_classical_support_bound": classical_vec,
        "T1_transfer_support_bounded_kappa": transfer_vec,
        "T1_oracle_charged": oracle_vec,
    }
    # ordering redundancy over the resource vector (carried from DISC-PROOF-ECONOMY-01)
    vecs = list(arms.values())
    res_redundant = []
    for i in range(len(RESOURCE_COMPONENTS)):
        for j in range(len(RESOURCE_COMPONENTS)):
            if i == j:
                continue
            m = defaultdict(set)
            for v in vecs:
                m[v[i]].add(v[j])
            if all(len(s) == 1 for s in m.values()):
                pts = sorted((k, next(iter(s))) for k, s in m.items())
                if all(pts[a][1] <= pts[a + 1][1] for a in range(len(pts) - 1)):
                    res_redundant.append({"redundant": RESOURCE_COMPONENTS[j],
                                          "determined_by": RESOURCE_COMPONENTS[i]})
    res_constant = [RESOURCE_COMPONENTS[i] for i in range(len(RESOURCE_COMPONENTS))
                    if len({v[i] for v in vecs}) == 1]

    matched = {
        "same_target_instance": True,
        "same_obligation_set": True,
        "same_adequacy_predicate": True,
        "same_objective": True,
        "same_validator": True,
        "difference_is_only_the_search_restriction": True,
    }
    # strict vector comparison: no scalarization anywhere
    t_vs_d = {"transfer_dominates_donor": dominates(transfer_vec, donor_vec),
              "donor_dominates_transfer": dominates(donor_vec, transfer_vec),
              "incomparable": not dominates(transfer_vec, donor_vec)
              and not dominates(donor_vec, transfer_vec)}
    o_vs_d = {"oracle_charged_dominates_donor": dominates(oracle_vec, donor_vec),
              "donor_dominates_oracle_charged": dominates(donor_vec, oracle_vec),
              "incomparable": not dominates(oracle_vec, donor_vec)
              and not dominates(donor_vec, oracle_vec)}
    c_vs_d = {"classical_dominates_donor": dominates(classical_vec, donor_vec)}

    # ---- donor subtraction -----------------------------------------------
    residual = {
        "donor_D1_total_enumeration_yields_frontier": True,
        "donor_D1_yields_kappa": True,
        "donor_D2_classical_bound_without_enumeration": classical_bound,
        "donor_D2_recovers_frontier": classical_recovers,
        "transferred_kappa": kappa,
        "tightening_over_classical_bound": (classical_bound - kappa
                                            if kappa is not None else None),
        "tightening_obtainable_without_the_donor_oracle": False,
        "kappa_equals_classical_minimum_cover_size": kappa_is_covering_number,
        "minimum_cover_size": min_cover_size,
        "kappa_collapse_note": (
            "kappa_t = %s equals the minimum cardinality of a covering subset, i.e. the "
            "classical minimum set-cover optimum. In this target the transferred "
            "quantity is not a new quantity: it coincides with a covering number, and "
            "QG-paper-03 disclaims novelty for support sparsification. The donor "
            "discipline owns the value itself, not merely the means of computing it."
            % kappa) if kappa_is_covering_number else
            "kappa_t is strictly larger than the minimum cover size; it is not a covering number.",
        "residual_capability_credited_to_transfer": "NONE",
        "residual_discipline_credited_to_transfer": [
            "two-sided claim typing (support bound vs intrinsic support number)",
            "explicit objective indexing of the bound",
        ],
        "explanation": ("The tighter value kappa=%s is real in the target, but it was "
                        "obtained only from the total enumeration that the donor arm "
                        "already performs. Charging that oracle call makes the "
                        "transferred arm cost at least as much as the donor on every "
                        "resource component. What survives subtraction is a claim-typing "
                        "discipline, not a search capability." % kappa),
    }

    # ---- non-vacuity ------------------------------------------------------
    nonvac = {
        "adequate_vs_inadequate": {"adequate": stats["n_adequate"],
                                   "inadequate": stats["space_size"] - 1 - stats["n_adequate"]},
        "adequacy_discriminates": 0 < stats["n_adequate"] < stats["space_size"] - 1,
        "frontier_vs_dominated": {"frontier": len(front),
                                  "dominated": stats["n_distinct_costs"] - len(front)},
        "pareto_discriminates": 0 < len(front) < stats["n_distinct_costs"],
        "R5_detector_exercised_under_scalar": [
            {"objective": c["objective"], "plans_above_min_support":
             c["plans_above_min_support"], "exchanges_found": c["exchanges_found"]}
            for c in scalar_exch],
        "R5_detector_fires_somewhere": any(c["exchanges_found"] > 0 for c in scalar_exch),
        "R5_premise_class_under_pareto_is_empty": bool(exch and not exch["exercised"]),
        "detector_shows_both_outcomes": (
            any(c["exchanges_found"] > 0 for c in scalar_exch)
            and any(c["exercised"] and not c["exists"] for c in scalar_exch)),
        "detector_not_inert": any(c["exchanges_found"] > 0 for c in scalar_exch),
        "ballast_jobs_present": T["ballast_jobs"],
        "resource_vector_live_components": [
            RESOURCE_COMPONENTS[i] for i in range(len(RESOURCE_COMPONENTS))
            if len({v[i] for v in vecs}) > 1],
        "resource_vector_constant_components": res_constant,
    }
    # core non-vacuity: adequacy and Pareto must discriminate, and the R5
    # detector must be demonstrably capable of firing on this real instance.
    nonvac["passed"] = all([nonvac["adequacy_discriminates"],
                            nonvac["pareto_discriminates"],
                            nonvac["detector_not_inert"]])

    # ---- terminal ---------------------------------------------------------
    cannot_check = []
    if unchecked_lb:
        for r in unchecked_lb:
            reason = r.get("note", "") or ""
            if r["id"] == "R4":
                reason = "NOT_EXERCISED_INSTANCE_SATURATED_AT_COVERAGE_FLOOR -- " + reason
            if r["id"] == "R5" and exch:
                reason = exch["verdict"] + " -- " + exch["note"]
            cannot_check.append({"subclaim": f"RELATION_{r['id']}_{r['name']}",
                                 "reason": reason})
    # The R5 detector's ABSENCE branch is itself unexercised on this instance:
    # everywhere it ran it found an exchange, so its ability to correctly report
    # "no exchange exists" is untested here. Carried as cannot_check rather than
    # counted as a validated detector.
    if scalar_exch and all(c["exercised"] and c["exists"] for c in scalar_exch):
        cannot_check.append({
            "subclaim": "R5_DETECTOR_NEGATIVE_BRANCH_UNEXERCISED",
            "reason": ("In every objective where the R5 premise class was non-empty the "
                       "detector found an exchange, so no run exercised its "
                       "no-exchange verdict. Its positive branch is demonstrated; its "
                       "negative branch is not.")})
    if attaining is None:
        cannot_check.append({"subclaim": "R5_EXCHANGE_SCAN",
                             "reason": "exchange scan exceeded EXCHANGE_SCAN_CAP"})

    apparent_advantage = bool(frontier_recovered and dominates(transfer_vec, donor_vec))
    advantage_survives_charging = bool(dominates(oracle_vec, donor_vec))
    resource_advantage_only = bool(apparent_advantage and not advantage_survives_charging)
    donor_subtraction_residual_empty = (
        residual["residual_capability_credited_to_transfer"] == "NONE")

    gate = {
        "survives_donor_subtraction": not donor_subtraction_residual_empty,
        "survives_matched_resource_accounting": advantage_survives_charging,
        "relational_correspondence_complete": not broken_lb and not unchecked_lb,
        "passed": (not donor_subtraction_residual_empty
                   and advantage_survives_charging
                   and not broken_lb and not unchecked_lb),
    }

    disjuncts_fired = []
    if broken_lb:
        disjuncts_fired.append(
            "BROKEN_LOAD_BEARING_RELATIONS: " + ", ".join(r["id"] for r in broken_lb))
    if resource_advantage_only:
        disjuncts_fired.append("RESOURCE_ADVANTAGE_DOES_NOT_SURVIVE_ORACLE_CHARGING")
    if donor_subtraction_residual_empty:
        disjuncts_fired.append("DONOR_SUBTRACTION_RESIDUAL_CAPABILITY_EMPTY")

    if not nonvac["passed"]:
        terminal = "TARGET_VALIDATOR_OR_CORRESPONDENCE_CANNOT_CHECK"
    elif disjuncts_fired:
        terminal = "SURFACE_ANALOGY_OR_RESOURCE_ADVANTAGE_ONLY"
    elif unchecked_lb:
        terminal = "TARGET_VALIDATOR_OR_CORRESPONDENCE_CANNOT_CHECK"
    else:
        terminal = "ORION_Q_STRUCTURAL_METHOD_TRANSFER_SUPPORTED"

    # The terminal name is a disjunction. Record precisely which disjunct fired,
    # and state plainly that the correspondence was NOT merely nominal: R1-R3
    # are structural relations that were checked and preserved.
    terminal_reading = {
        "disjuncts_fired": disjuncts_fired,
        "correspondence_was_surface_only": bool(not preserved_lb),
        "structurally_preserved_relations": [r["id"] for r in preserved_lb],
        "clarification": (
            "The negative terminal here is reached through the donor-subtraction and "
            "resource disjuncts, NOT because the correspondence was mere vocabulary. "
            "R1-R3 are structural relations that were checked and hold. What fails is "
            "that nothing the transfer supplies survives subtraction of the donor, and "
            "the apparent search saving does not survive charging the oracle that "
            "produced kappa."),
    }

    common = {
        "job_id": "DISC-Q-TRANSFER-01",
        "class": "EXACT_CROSS_DOMAIN_TRANSFER",
        "authority": "TARGET_DOMAIN_RESULT_ONLY",
        "quantum_authority_transferred": False,
        "physical_or_quantum_advantage_claim": False,
        "arithmetic": "integers only; no float constructed",
        "input_sha256": inputs,
        "terminal": terminal,
        "terminal_reading": terminal_reading,
        "gate": gate,
        "cannot_check_subclaims": cannot_check,
    }

    (OUT / "Q_TRANSFER_CONTRACT_V1.json").write_text(json.dumps({
        "schema": "orion.discovery-v2.q-transfer-contract.v1", **common,
        "source_domain": {
            "name": "ORION-Q compilation regime geometry",
            "donor_artifact": "papers/candidates/qg-paper-03-stub/MANUSCRIPT_V1.md",
            "transferred_object": "intrinsic support number kappa(F, C) and the descent-ladder proof technique",
            "donor_definition_verbatim": (
                "For a compilation family F under a fixed objective C, kappa(F, C) is the "
                "least B such that every instance's exact optimum is attained by a "
                "configuration whose structural generators all have global support <= B. "
                "Equivalently: B is a valid support bound and B-1 is not."),
            "authority_not_transferred": [
                "quantum or physical advantage", "hardware performance",
                "compilation-resource novelty (R6)", "priority over any donor discipline"],
        },
        "target_domain": {
            "name": "OSTC evidence-selection (non-quantum finite set cover)",
            "instance": "DISC-WEB-01 registered execution-evidence slice, subset-lattice form",
            "ground_set_jobs": T["jobs"],
            "obligations": T["obligations"],
            "ballast_jobs_covering_nothing": T["ballast_jobs"],
            "space_size": stats["space_size"],
            "enumeration_bound": ENUMERATION_BOUND,
        },
        "contract_elements_required_by_spec_8_5": {
            "relational_correspondence": correspondence_type,
            "strongest_parent_donor_first_refusal": "DONOR_FIRST_REFUSAL.md",
            "target_native_validator": "total exact enumeration of the subset lattice",
            "matched_vector_resource_contract": "MATCHED_RESOURCE_RECEIPT.json",
            "explicit_non_transfer_of_scientific_authority": True,
        },
        "theorem_bindings": {
            "QX-T1": "method may transfer, source scientific authority may not -- honoured",
            "QX-T2": "target-native validator supplied and run",
            "QX-T3": "matched vector resource accounting supplied",
            "NAV-T3": "relational correspondence required, not surface similarity",
        },
    }, indent=2) + "\n")

    (OUT / "RELATIONAL_CORRESPONDENCE_WITNESS.json").write_text(json.dumps({
        "schema": "orion.discovery-v2.relational-correspondence-witness.v1", **common,
        "structure_preserving_map": {
            "compilation family F": "obligation set O (13 OSTC theorems)",
            "structural generator": "registered execution-evidence job",
            "configuration": "subset of evidence jobs",
            "global support": "cardinality of the selected subset",
            "objective C": "integer cost vector " + str(COST_COMPONENTS),
            "exact optimum": "Pareto non-dominated cost vector among adequate plans",
            "kappa(F, C)": "kappa_t = max over optima of the minimum attaining support",
        },
        "preserved_relations": relations,
        "counts": {"load_bearing_preserved": len(preserved_lb),
                   "load_bearing_broken": len(broken_lb),
                   "load_bearing_cannot_check": len(unchecked_lb)},
        "correspondence_type": correspondence_type,
        "surface_only_carryover": ["the words support, optimum, bound"] if broken_lb else [],
        "kappa_by_objective": kappa_by_objective,
        "objective_indexing_confirmed_in_target": objective_indexed,
        "objective_indexing_testable_on_this_instance": objective_indexing_testable,
        "objective_indexing_argument": objective_indexing_argument,
        "scalar_objective_control": control,
        "non_vacuity": nonvac,
    }, indent=2) + "\n")

    (OUT / "TARGET_NATIVE_VALIDATION_RECEIPT.json").write_text(json.dumps({
        "schema": "orion.discovery-v2.target-native-validation-receipt.v1", **common,
        "validator": {
            "name": "total exact enumeration of the OSTC evidence-selection subset lattice",
            "native_to_target": True,
            "uses_donor_machinery": False,
            "uses_quantum_input": False,
            "total_not_sampled": True,
            "space_size": stats["space_size"],
            "declared_bound": ENUMERATION_BOUND,
        },
        "results": {
            "n_adequate_plans": stats["n_adequate"],
            "n_distinct_cost_vectors": stats["n_distinct_costs"],
            "frontier_size": len(front),
            "frontier": [{"cost_vector": list(z), "min_support": best[z]} for z in front],
            "kappa_t": kappa,
            "kappa_two_sided_witness": [list(z) for z in (kappa_witness or [])],
            "minimum_cover_size": min_cover_size,
            "kappa_equals_classical_minimum_cover_size": kappa_is_covering_number,
            "covering_number_cross_check": covering_number_cross_check,
            "irredundant_cover_check": irredundant_check,
        },
        "transferred_method_reproduces_validator": {
            "support_bounded_search_recovers_frontier": frontier_recovered,
            "classical_bound_search_recovers_frontier": classical_recovers,
        },
    }, indent=2) + "\n")

    (OUT / "MATCHED_RESOURCE_RECEIPT.json").write_text(json.dumps({
        "schema": "orion.discovery-v2.matched-resource-receipt.v1", **common,
        "components": RESOURCE_COMPONENTS,
        "scalarization_used": False,
        "ordering_relation": "Pareto dominance on integer resource vectors",
        "matched_conditions": matched,
        "arms": {k: {"resource_vector": list(v),
                     "as_dict": dict(zip(RESOURCE_COMPONENTS, v))}
                 for k, v in arms.items()},
        "comparisons": {
            "transfer_vs_donor_uncharged": t_vs_d,
            "transfer_vs_donor_oracle_charged": o_vs_d,
            "classical_bound_vs_donor": c_vs_d,
        },
        "rejected_split_axis_accounting": {
            "resource_vector": list(split_vec),
            "as_dict": dict(zip(RESOURCE_COMPONENTS, split_vec)),
            "donor_dominates": dominates(donor_vec, split_vec),
            "incomparable": not dominates(donor_vec, split_vec)
            and not dominates(split_vec, donor_vec),
            "why_rejected": (
                "Parking the oracle's enumeration on its own axis makes the arms "
                "Pareto-incomparable and leaves the comparison undecidable without a "
                "preference vector. But an oracle call that enumerates subsets spends "
                "the same physical resource as enumerating subsets, so it belongs in "
                "subsets_enumerated. Axis-splitting here would manufacture "
                "incomparability and hide the cost."),
        },
        "resource_vector_ordering_redundancy": res_redundant,
        "resource_vector_constant_components": res_constant,
        "anti_laundering_note": (
            "kappa is not available a priori in the target. It was produced by the "
            "same total enumeration the donor arm performs, so the transferred arm is "
            "charged oracle_subsets_enumerated = %d. Reporting only the uncharged arm "
            "would be answer laundering through preprocessing (spec 8.2)."
            % res_donor.c["subsets_enumerated"]),
        "verdict": ("APPARENT_ADVANTAGE_DISAPPEARS_UNDER_ORACLE_CHARGING"
                    if not dominates(oracle_vec, donor_vec) else "ADVANTAGE_SURVIVES"),
    }, indent=2) + "\n")

    md = []
    md.append("# DONOR-FIRST REFUSAL -- DISC-Q-TRANSFER-01\n")
    md.append("Authority: **target-domain result only**. No quantum authority is "
              "transferred; nothing below is a physical, hardware, or "
              "quantum-advantage claim.\n")
    md.append("## 1. The donor names its own donors\n")
    md.append("QG-paper-03 (`papers/candidates/qg-paper-03-stub/"
              "MANUSCRIPT_V1.md`, sha256 `%s`) states, in its own words, that it\n"
              % inputs["QG-paper-03 MANUSCRIPT_V1.md"])
    md.append("> claims no novelty for finite-field dependence, support "
              "sparsification, Pauli symplectic representations, or "
              "parametric/polyhedral optimization\n")
    md.append("Support sparsification is therefore a **donor discipline, not a "
              "transferred contribution**. Any target result that classical "
              "sparsification or minimum set cover already delivers must be "
              "credited to that donor.\n")
    md.append("## 2. What the strongest donor achieves WITHOUT the transfer\n")
    md.append("**D1 -- total exact enumeration.** Enumerating all %d subsets returns "
              "the exact Pareto frontier (%d optima) and, as a by-product, the exact "
              "value kappa_t = %s. The donor alone answers the entire question.\n"
              % (stats["space_size"], len(front), kappa))
    md.append("**D2 -- classical irredundant-cover sparsity, no enumeration at all.** "
              "Every frontier plan is an irredundant cover: if a job could be dropped "
              "with coverage preserved, the smaller plan's node and edge unions are "
              "subsets, so its cost vector is componentwise <= and the larger plan "
              "would be dominated. In an irredundant cover each member holds a private "
              "obligation, so support <= |obligations| = %d. This is textbook set-cover "
              "reasoning and needs zero search. Verified on the frontier: %s.\n"
              % (classical_bound,
                 "holds, 0 violations" if (irredundant_check or {}).get("holds")
                 else "VIOLATED -- see receipt"))
    md.append("## 3. Residual after subtraction\n")
    md.append("| Object | Donor alone | With Q transfer | Residual |\n|---|---|---|---|\n")
    md.append("| Exact frontier | yes (D1) | same | none |\n")
    md.append("| Support bound | <= %d (D2, free) | kappa_t = %s | %s tighter, but "
              "only via the D1 oracle |\n"
              % (classical_bound, kappa, classical_bound - kappa if kappa else "n/a"))
    md.append("| Two-sided typing | not asked | asked and answered | **discipline only** |\n")
    md.append("| Objective indexing | not asked | asked, NOT EXERCISABLE | **question only** |\n\n")
    md.append("The objective-indexing phenomenon cannot be exercised here, and it would "
              "overstate the evidence to call it refuted. kappa_t = %s under the Pareto "
              "order and under every single-component objective, because support %s is "
              "forced by COVERAGE -- a combinatorial floor independent of the objective "
              "-- and every frontier cost is attained at that floor. Since any strictly "
              "monotone objective attains its optimum at a non-dominated cost vector, no "
              "objective whatsoever can yield a different kappa on this instance "
              "(relation R4, NOT_EXERCISED).\n\n" % (kappa, kappa))
    md.append("The tightening from %d to %s is a real target-domain fact, but it is not "
              "a capability the transfer supplies: kappa_t is knowable only after the "
              "same total enumeration D1 performs. Charged honestly, the transferred "
              "arm costs at least as much as the donor on every resource component.\n"
              % (classical_bound, kappa))
    if kappa_is_covering_number:
        md.append("## 3b. The transferred quantity collapses to a covering number\n")
        md.append("kappa_t = %s is exactly the minimum cardinality of a covering "
                  "subset -- the classical minimum set-cover optimum. So in this "
                  "target the transfer does not even contribute a new QUANTITY: it "
                  "renames one the donor disciplines already own, and QG-paper-03 "
                  "itself disclaims novelty for support sparsification. This is the "
                  "sharpest reason the residual is empty.\n" % kappa)
    md.append("## 4. Refusal\n")
    md.append("The transfer claim is **refused** for: computing the frontier, computing "
              "kappa_t, and any search-cost advantage. The objective-indexing "
              "phenomenon is neither credited nor refuted: this instance cannot "
              "exercise it. It is **credited "
              "only** with one thing: the two-sided claim-typing discipline that "
              "distinguishes a one-sided support bound from an intrinsic support "
              "number, and the habit of asking whether a bound is objective-indexed. "
              "That discipline changed what was ASKED in the target; it did not change "
              "what could be computed, and on this instance both questions came back "
              "answerable by the donor alone.\n")
    md.append("## 5. Where the donor wins, stated plainly\n")
    md.append("On this instance the donor wins outright. D1 answers everything; D2 "
              "supplies a sound bound for free. The honest verdict is that ORION-Q "
              "contributed a QUESTION here, not a METHOD.\n")
    (OUT / "DONOR_FIRST_REFUSAL.md").write_text("".join(md))

    summary = {
        "terminal": terminal,
        "correspondence_type": correspondence_type,
        "load_bearing_relations": {"preserved": [r["id"] for r in preserved_lb],
                                   "broken": [r["id"] for r in broken_lb],
                                   "cannot_check": [r["id"] for r in unchecked_lb]},
        "target": {"space": stats["space_size"], "adequate": stats["n_adequate"],
                   "distinct_costs": stats["n_distinct_costs"],
                   "frontier": len(front), "kappa_t": kappa,
                   "classical_bound": classical_bound,
                   "min_cover_size": min_cover_size,
                   "kappa_is_classical_covering_number": kappa_is_covering_number,
                   "covering_number_cross_check": covering_number_cross_check},
        "resources": {k: dict(zip(RESOURCE_COMPONENTS, v)) for k, v in arms.items()},
        "transfer_vs_donor_oracle_charged": o_vs_d,
        "gate": gate,
        "disjuncts_fired": disjuncts_fired,
        "frontier_recovered_by_transfer_arm": frontier_recovered,
        "non_vacuity_passed": nonvac["passed"],
        "cannot_check_subclaims": cannot_check,
    }
    print(json.dumps(summary, indent=2))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
