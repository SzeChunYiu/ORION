"""DISC-PROOF-ECONOMY-01 -- exact bounded proof-economy correspondence.

Spec: research/orion-discovery-v2/KNOWLEDGE_WEB_NAVIGATION_PROOF_ECONOMY_AND_SELF_APPLICATION_V1.md
      (branch codex/orion-discovery-v2-knowledge-web-20260825), section 6.
Job:  research/orion-discovery-v2/EXECUTION_BACKLOG_V1.json :: DISC-PROOF-ECONOMY-01
Input: research/orion-discovery-v2/exec/DISC-WEB-01/{KNOWLEDGE_WEB_V1,SUPPORT_FAMILY_STATUS_V1}.json

Authority: finite exact only.  Every quantity here is an integer or a
fractions.Fraction.  No float is constructed anywhere in this module, no
cost vector is ever summed/averaged into a scalar for ordering, and the
plan enumeration is TOTAL over the declared bound (no sampling).

Method contract (spec 6.2): a proof option carries
    (method, scope, preconditions, discharged obligations, authority class,
     cost vector);
a plan is adequate iff every obligation has an accepted discharge with an
accepted authority and every hard precondition is attained.  Ordering over
plans is Pareto dominance on the integer cost vector only (spec 6.3:
implicit resource scalarization -> INVALID_COST_COMPARISON).
"""

from __future__ import annotations

import hashlib
import itertools
import json
from collections import Counter, defaultdict
from fractions import Fraction
from pathlib import Path

ROOT = Path("/Users/billy/ORION-claude")
WEB_DIR = ROOT / "research/orion-discovery-v2/exec/DISC-WEB-01"
OUT = ROOT / "research/orion-discovery-v2/exec/DISC-PROOF-ECONOMY-01"

# Declared enumeration bound.  If a census exceeds it we return the
# cannot_check terminal rather than sampling and calling the result exact.
PLAN_ENUMERATION_BOUND = 1_000_000
# Declared bound for the complete (vertex-enumeration) scalarization probe.
HULL_BASIS_BOUND = 200_000

COST_COMPONENTS = [
    "distinct_evidence_nodes",
    "distinct_support_nodes",
    "distinct_support_edges",
    "obstructed_discharges",
    "unvalidated_discharges",
]


def sha256_file(p: Path) -> str:
    return hashlib.sha256(p.read_bytes()).hexdigest()


# --------------------------------------------------------------------------
# 1. Load the DISC-WEB-01 slice and derive typed proof options.
# --------------------------------------------------------------------------

def load_inputs():
    web = json.loads((WEB_DIR / "KNOWLEDGE_WEB_V1.json").read_text())
    fam = json.loads((WEB_DIR / "SUPPORT_FAMILY_STATUS_V1.json").read_text())
    return web, fam


def build_options(web, fam):
    """One proof option per COMPLETE support family, typed per spec 6.2."""
    nodes = {n["id"]: n for n in web["nodes"]}
    validates_lb = {}
    for e in web["edges"]:
        if e["kind"] == "VALIDATES" and e["target"].startswith("THEORY:"):
            validates_lb[(e["source"], e["target"])] = bool(e["load_bearing"])

    options = []
    for f in fam["families"]:
        if not f["complete"]:
            continue
        target = f["target"]
        ev = [n for n in f["present_nodes"] if n.startswith("EVIDENCE:")]
        ex = [n for n in f["present_nodes"] if n.startswith("EXPERIMENT:")]
        va = [n for n in f["present_nodes"] if n.startswith("VALIDATOR:")]
        assert len(ev) == 1 and len(ex) == 1, f["family_id"]
        evid = ev[0]

        # --- hard preconditions, each evaluated exactly against the web ---
        pre = {
            # the evidence artefact is content-identified on disk
            "EVIDENCE_CONTENT_IDENTIFIED": bool(nodes[evid].get("content_sha256")),
            # the protocol the evidence depends on is content-identified
            "EXPERIMENT_CONTENT_IDENTIFIED": bool(nodes[ex[0]].get("content_sha256")),
            # no registered FAILURE node obstructs the producing experiment
            "ROUTE_NOT_OBSTRUCTED": not bool(f["blocked_by_failure"]),
        }
        # DERIVED, NOT INDEPENDENT.  disc_web_01.py line 110-111 creates the
        # VALIDATES->THEORY edge with load_bearing = (not blocked), so this
        # predicate is definitionally equal to ROUTE_NOT_OBSTRUCTED.  It is
        # recorded for audit and excluded from the hard set to avoid
        # double-counting one fact as two preconditions.
        derived = {
            "VALIDATES_EDGE_LOAD_BEARING": bool(validates_lb.get((evid, target)))
        }

        has_validator = len(va) == 1
        options.append({
            "option_id": f["family_id"],
            "method": "registered execution evidence route (EVIDENCE -DEPENDS_ON-> EXPERIMENT, EVIDENCE -VALIDATES-> THEORY)",
            "scope": target,
            "discharges": [target],
            "evidence_node": evid,
            "required_nodes": sorted(f["present_nodes"]),
            "required_edges": sorted(tuple(e) for e in f["present_edges"]),
            "hard_preconditions": pre,
            "derived_predicates": derived,
            "all_hard_preconditions_attained": all(pre.values()),
            "authority_class": ("INDEPENDENTLY_CHECKED" if has_validator
                                else "SELF_REPORTED"),
            "has_independent_validator": has_validator,
            "obstructed": bool(f["blocked_by_failure"]),
        })
    options.sort(key=lambda o: o["option_id"])
    return options, nodes


def build_register(web, fam, options):
    """Total obligation register over every THEORY node in the slice."""
    theories = sorted(n["id"] for n in web["nodes"] if n["kind"] == "THEORY")
    by_target = defaultdict(list)
    for o in options:
        by_target[o["scope"]].append(o)

    incomplete = defaultdict(list)
    for f in fam["families"]:
        if not f["complete"]:
            incomplete[f["target"]].append(f)

    register = []
    for t in theories:
        opts = by_target.get(t, [])
        attained = [o for o in opts if o["all_hard_preconditions_attained"]]
        if not opts:
            status = "UNREGISTERED_IN_SLICE"
        elif not attained:
            status = "OBSTRUCTED_ONLY"
        else:
            status = "DISCHARGEABLE"
        register.append({
            "obligation_id": f"OBL:{t}",
            "target": t,
            "responsibility": "establish that registered execution evidence supports this theorem",
            "status": status,
            "n_complete_options": len(opts),
            "n_precondition_attained_options": len(attained),
            "option_ids": [o["option_id"] for o in opts],
            "attained_option_ids": [o["option_id"] for o in attained],
            "incomplete_family_gaps": [f["best_remaining_gap"] for f in incomplete.get(t, [])],
            # spec 6.1: a cheaper evidence object lacking the required
            # authority is not adequate -- but the slice never registers a
            # per-theorem authority requirement, so we must not invent one.
            "authority_requirement": "NOT_REGISTERED_IN_SLICE",
            "authority_note": ("No per-theorem required authority class exists in the "
                               "DISC-WEB-01 slice. INDEPENDENT_VALIDATOR_PRESENT is therefore "
                               "carried as a cost component, not as a hard gate. This is a "
                               "typing gap in the slice, not a finding that self-reported "
                               "evidence is accepted. See hostile case HC-06."),
        })
    return register


# --------------------------------------------------------------------------
# 2. Exact vector cost + total plan enumeration.
# --------------------------------------------------------------------------

def plan_cost(selection):
    """Exact integer cost VECTOR of a plan. Never scalarized."""
    nodes, edges = set(), set()
    obstructed = unvalidated = 0
    evidence = set()
    for o in selection:
        nodes.update(o["required_nodes"])
        edges.update(tuple(e) for e in o["required_edges"])
        evidence.add(o["evidence_node"])
        if o["obstructed"]:
            obstructed += 1
        if not o["has_independent_validator"]:
            unvalidated += 1
    return (len(evidence), len(nodes), len(edges), obstructed, unvalidated)


def dominates(a, b):
    """Pareto dominance on the integer vector. No weights, no sum."""
    return all(x <= y for x, y in zip(a, b)) and any(x < y for x, y in zip(a, b))


def enumerate_census(obligations, by_target, bound=PLAN_ENUMERATION_BOUND,
                     validator_hard=False, keep_records=True):
    """TOTAL enumeration of every choice function over `obligations`."""
    sizes = [len(by_target[t]) for t in obligations]
    total = 1
    for s in sizes:
        total *= s
    if total > bound:
        return {"bounded": False, "space_size": total, "bound": bound}

    records, adequate, violation_counts = [], [], Counter()
    for combo in itertools.product(*[by_target[t] for t in obligations]):
        viol = []
        for o in combo:
            for k, v in o["hard_preconditions"].items():
                if not v:
                    viol.append(f"{o['option_id']}:{k}")
            if validator_hard and not o["has_independent_validator"]:
                viol.append(f"{o['option_id']}:INDEPENDENT_VALIDATOR_PRESENT")
        cost = plan_cost(combo)
        ok = not viol
        rec = {
            "selection": [o["option_id"] for o in combo],
            "cost_vector": list(cost),
            "adequate": ok,
            "unattained_preconditions": sorted(set(viol)),
        }
        if ok:
            adequate.append((tuple(o["option_id"] for o in combo), cost, combo))
        else:
            for v in set(viol):
                # option ids contain ":" (e.g. "S1(THEORY:T14)"); split from the right
                violation_counts[v.rsplit(":", 1)[1]] += 1
        if keep_records:
            records.append(rec)
    return {
        "bounded": True,
        "space_size": total,
        "bound": bound,
        "records": records,
        "adequate": adequate,
        "n_adequate": len(adequate),
        "n_inadequate": total - len(adequate),
        "violation_counts": dict(violation_counts),
    }


# --------------------------------------------------------------------------
# 3. Exact Pareto frontier + complete scalarization-reachability probe.
# --------------------------------------------------------------------------

def pareto_frontier(costed):
    """costed: list of (key, cost). Returns (frontier, dominated)."""
    frontier, dominated = [], []
    for key, c in costed:
        if any(dominates(c2, c) for k2, c2 in costed if k2 != key):
            dominated.append((key, c))
        else:
            frontier.append((key, c))
    return frontier, dominated


def verify_frontier(costed, frontier, dominated):
    """Independent exact re-check of PE-T5 (frontier == non-dominated set)."""
    fk = {k for k, _ in frontier}
    errs = []
    for k, c in frontier:
        for k2, c2 in costed:
            if k2 != k and dominates(c2, c):
                errs.append({"law": "PE-T5", "kind": "DOMINATED_PLAN_IN_FRONTIER",
                             "plan": list(k), "dominated_by": list(k2)})
    for k, c in dominated:
        if not any(dominates(c2, c) for k2, c2 in costed if k2 != k):
            errs.append({"law": "PE-T5", "kind": "NON_DOMINATED_PLAN_EXCLUDED",
                         "plan": list(k)})
    for k, c in costed:
        if (k in fk) == any(dominates(c2, c) for k2, c2 in costed if k2 != k):
            errs.append({"law": "PE-T5", "kind": "PARTITION_INCONSISTENT",
                         "plan": list(k)})
    return errs


def solve_exact(mat, rhs):
    """Exact Fraction Gaussian elimination. Returns solution or None."""
    n = len(mat)
    a = [[Fraction(x) for x in row] + [Fraction(rhs[i])] for i, row in enumerate(mat)]
    for col in range(n):
        piv = next((r for r in range(col, n) if a[r][col] != 0), None)
        if piv is None:
            return None
        a[col], a[piv] = a[piv], a[col]
        pv = a[col][col]
        a[col] = [x / pv for x in a[col]]
        for r in range(n):
            if r != col and a[r][col] != 0:
                f = a[r][col]
                a[r] = [x - f * y for x, y in zip(a[r], a[col])]
    return [a[i][n] for i in range(n)]


def scalarization_reachable(target_cost, others, live_dims):
    """COMPLETE exact test: is `target_cost` inside conv(others)+R^d_+ ?

    Feasibility of {lambda in simplex : sum_i lambda_i * a_i <= z} over the
    live dimensions. The region is a bounded polytope, so it is non-empty iff
    it has a vertex, and every vertex is the exact solution of a square system
    formed by the equality sum(lambda)=1 plus (k-1) tight constraints drawn
    from {lambda_i >= 0} U {row_j <= z_j}. Enumerating all such choices is
    complete -- no sampling, no float.

    Returns (reachable_bool, checked_bool). A witness (feasible point) means
    the target is NOT a strict minimiser of any positive-weight scalarization.
    """
    k = len(others)
    if k == 0:
        return False, True
    d = len(live_dims)
    n_basis = 1
    for i in range(k - 1):
        n_basis = n_basis * (k + d - i) // (i + 1)
    if n_basis > HULL_BASIS_BOUND:
        return None, False

    A = [[Fraction(o[j]) for o in others] for j in live_dims]   # d x k
    z = [Fraction(target_cost[j]) for j in live_dims]
    cons = [("nonneg", i) for i in range(k)] + [("row", j) for j in range(d)]

    def feasible(lam):
        if any(x < 0 for x in lam):
            return False
        if sum(lam) != 1:
            return False
        for j in range(d):
            if sum(A[j][i] * lam[i] for i in range(k)) > z[j]:
                return False
        return True

    if k == 1:
        lam = [Fraction(1)]
        return feasible(lam), True

    for basis in itertools.combinations(cons, k - 1):
        mat = [[Fraction(1)] * k]
        rhs = [Fraction(1)]
        for kind, idx in basis:
            if kind == "nonneg":
                row = [Fraction(0)] * k
                row[idx] = Fraction(1)
                mat.append(row)
                rhs.append(Fraction(0))
            else:
                mat.append([A[idx][i] for i in range(k)])
                rhs.append(z[idx])
        sol = solve_exact(mat, rhs)
        if sol is not None and feasible(sol):
            return True, True
    return False, True


def ordering_redundancy(costs):
    """Exact, total: is component j a monotone function of component i over the
    whole census? If so j can never flip a dominance comparison that i does not
    already decide, and declaring it is a reporting defect, not a real axis."""
    out = []
    n = len(COST_COMPONENTS)
    for i in range(n):
        for j in range(n):
            if i == j:
                continue
            mapping = defaultdict(set)
            for c in costs:
                mapping[c[i]].add(c[j])
            is_fn = all(len(v) == 1 for v in mapping.values())
            mono = True
            if is_fn:
                pts = sorted((k, next(iter(v))) for k, v in mapping.items())
                mono = all(pts[a][1] <= pts[a + 1][1] for a in range(len(pts) - 1))
            if is_fn and mono:
                out.append({
                    "redundant_component": COST_COMPONENTS[j],
                    "determined_by": COST_COMPONENTS[i],
                    "relation": "monotone non-decreasing function over the full census",
                    "map": {str(k): sorted(v)[0] for k, v in sorted(mapping.items())},
                    "consequence": ("cannot flip any Pareto comparison the determining "
                                    "component does not already decide"),
                })
    return out


def reverify_adequacy(records, by_id):
    """Independent PE-T4 re-check: recompute adequacy and cost from the option
    table and compare against every stored census record."""
    errs = []
    for r in records:
        sel = [by_id[o] for o in r["selection"]]
        ok = all(all(o["hard_preconditions"].values()) for o in sel)
        cost = list(plan_cost(sel))
        if ok != r["adequate"]:
            errs.append({"law": "PE-T4", "kind": "ADEQUACY_VERDICT_MISMATCH",
                         "plan": r["selection"], "stored": r["adequate"], "recomputed": ok})
        if cost != r["cost_vector"]:
            errs.append({"law": "PE-T4", "kind": "COST_VECTOR_MISMATCH",
                         "plan": r["selection"], "stored": r["cost_vector"],
                         "recomputed": cost})
        if r["adequate"] and r["unattained_preconditions"]:
            errs.append({"law": "PE-T4", "kind": "ADEQUATE_WITH_UNATTAINED_PRECONDITION",
                         "plan": r["selection"]})
    return errs


# --------------------------------------------------------------------------
# 4. Hostile precondition exercise + mutation discrimination harness.
# --------------------------------------------------------------------------

def derive_families_from_web(web):
    """Re-derivation of DISC-WEB-01's support families from the web alone.

    Mirrors disc_web_01.py: routes into a theorem are the sources of its
    VALIDATES edges; a route is obstructed when a FAILURE node OBSTRUCTS the
    producing experiment. Re-deriving here (rather than reusing the stored
    status file) is what lets the mutation harness actually reach the family
    layer instead of only this module's option-typing layer.
    """
    nodes = {n["id"]: n for n in web["nodes"]}
    by_theorem = defaultdict(list)
    obstructed_experiments = set()
    for e in web["edges"]:
        if e["kind"] == "VALIDATES" and e["target"].startswith("THEORY:"):
            by_theorem[e["target"]].append(e["source"])
        if e["kind"] == "OBSTRUCTS":
            obstructed_experiments.add(e["target"])
    fams = []
    for t in sorted(n for n in nodes if n.startswith("THEORY:")):
        routes = sorted(by_theorem.get(t, []))
        for i, evid in enumerate(routes, start=1):
            jid = evid.split(":", 1)[1]
            members = [evid, f"EXPERIMENT:{jid}"]
            if f"VALIDATOR:{jid}" in nodes:
                members.append(f"VALIDATOR:{jid}")
            present = [m for m in members if m in nodes]
            fams.append({
                "target": t,
                "family_id": f"S{i}({t})",
                "present_nodes": present,
                "complete": len(present) == len(members),
                "blocked_by_failure": f"EXPERIMENT:{jid}" in obstructed_experiments,
                "content_ids": tuple(sorted(
                    (m, nodes[m].get("content_sha256")) for m in present)),
                "target_content_id": nodes[t].get("content_sha256"),
            })
    return fams


def family_fingerprint(fams):
    return {f["family_id"]: (f["complete"], f["blocked_by_failure"]) for f in fams}


def mutation_harness(web, fam, options):
    """Two mutation classes. 'No change' is NEVER recorded as a pass."""
    base = {o["option_id"]: (o["all_hard_preconditions_attained"], o["obstructed"])
            for o in options}
    fam_base = family_fingerprint(derive_families_from_web(web))
    results = []

    # M1 -- perturb a theorem's content_sha256. If support status is
    # content-bound, that theorem's own families must move and no others'.
    for t in ("THEORY:T10", "THEORY:T13"):
        w2 = json.loads(json.dumps(web))
        for n in w2["nodes"]:
            if n["id"] == t:
                n["content_sha256"] = "0" * 64
        # layer 1: this module's option typing
        opts2, _ = build_options(w2, fam)
        m2 = {o["option_id"]: (o["all_hard_preconditions_attained"], o["obstructed"])
              for o in opts2}
        moved = sorted(k for k in base if base[k] != m2.get(k))
        # layer 2: DISC-WEB-01's family derivation, RE-RUN on the mutated web
        fam_moved = sorted(k for k, v in fam_base.items()
                           if v != family_fingerprint(derive_families_from_web(w2)).get(k))
        all_moved = sorted(set(moved) | set(fam_moved))
        own = sorted(k for k in all_moved if k.endswith(f"({t})"))
        foreign = sorted(k for k in all_moved if not k.endswith(f"({t})"))
        results.append({
            "mutation_class": "M1_THEOREM_CONTENT_PERTURBATION",
            "mutated": t,
            "layers_exercised": ["option_typing (this module)",
                                 "support_family_derivation (DISC-WEB-01 logic, re-run)"],
            "n_options_moved": len(moved),
            "n_families_moved": len(fam_moved),
            "own_families_moved": own,
            "foreign_families_moved": foreign,
            "discriminating": bool(own) and not foreign,
            "verdict": ("DISCRIMINATES" if (own and not foreign)
                        else "NOT_DISCRIMINATING_SUPPORT_IS_ID_BOUND_NOT_CONTENT_BOUND"),
            "note": ("Both layers are re-run on the mutated web. Families are keyed on "
                     "theorem ID through the VALIDATES edge; the theorem's "
                     "content_sha256 is recorded but never read when deciding support "
                     "status, so zero movement is a discrimination FAILURE, not a pass."),
        })

    # M2 -- obstruct one evidence route. Only that route's families may move.
    for job in ("EVIDENCE:EXEC-CM-01", "EVIDENCE:EXEC-P10-01"):
        f2 = json.loads(json.dumps(fam))
        touched = set()
        for f in f2["families"]:
            if job in f["present_nodes"]:
                f["blocked_by_failure"] = True
                touched.add(f["family_id"])
        w2 = json.loads(json.dumps(web))
        jid = job.split(":", 1)[1]
        for e in w2["edges"]:
            if (e["kind"] == "VALIDATES" and e["source"] == job
                    and e["target"].startswith("THEORY:")):
                e["load_bearing"] = False
        # mirror how disc_web_01.py marks a route blocked, so the family-layer
        # re-derivation actually sees this mutation instead of silently missing it
        if not any(n["id"] == f"FAILURE:{jid}" for n in w2["nodes"]):
            w2["nodes"].append({"id": f"FAILURE:{jid}", "kind": "FAILURE",
                                "content_sha256": "1" * 64, "domain": "OSTC",
                                "scope": "execution", "version": "V1",
                                "terminal": "SYNTHETIC_MUTATION_UNAVAILABLE"})
        w2["edges"].append({"source": f"FAILURE:{jid}", "target": f"EXPERIMENT:{jid}",
                            "kind": "OBSTRUCTS", "load_bearing": True,
                            "reopens_target": False})
        opts2, _ = build_options(w2, f2)
        m2 = {o["option_id"]: (o["all_hard_preconditions_attained"], o["obstructed"])
              for o in opts2}
        moved = sorted(k for k in base if base[k] != m2.get(k))
        fam_moved = sorted(k for k, v in fam_base.items()
                           if v != family_fingerprint(derive_families_from_web(w2)).get(k))
        results.append({
            "mutation_class": "M2_ROUTE_OBSTRUCTION_PERTURBATION",
            "n_families_moved": len(fam_moved),
            "families_moved": fam_moved,
            "mutated": job,
            "n_options_moved": len(moved),
            "options_moved": moved,
            "expected_movable": sorted(touched),
            "locality_held": set(moved) <= touched,
            "family_layer_locality_held": set(fam_moved) <= touched,
            "discriminating": bool(moved) and set(moved) <= touched,
            "verdict": ("DISCRIMINATES_LOCALLY" if (moved and set(moved) <= touched)
                        else "NOT_DISCRIMINATING"),
        })
    return results


# --------------------------------------------------------------------------

def main() -> int:
    OUT.mkdir(parents=True, exist_ok=True)
    web, fam = load_inputs()
    input_hashes = {
        "KNOWLEDGE_WEB_V1.json": sha256_file(WEB_DIR / "KNOWLEDGE_WEB_V1.json"),
        "SUPPORT_FAMILY_STATUS_V1.json": sha256_file(WEB_DIR / "SUPPORT_FAMILY_STATUS_V1.json"),
    }
    options, _nodes = build_options(web, fam)
    register = build_register(web, fam, options)
    by_target = defaultdict(list)
    for o in options:
        by_target[o["scope"]].append(o)

    reg_status = Counter(r["status"] for r in register)
    dischargeable = [r["target"] for r in register if r["status"] == "DISCHARGEABLE"]
    obstructed_only = [r["target"] for r in register if r["status"] == "OBSTRUCTED_ONLY"]
    unregistered = [r["target"] for r in register if r["status"] == "UNREGISTERED_IN_SLICE"]
    registered = dischargeable + obstructed_only

    # ---- Census A: cover every obligation with a registered option --------
    censusA = enumerate_census(sorted(registered), by_target, keep_records=False)
    # ---- Census B: cover the dischargeable stratum (the discriminating one)
    censusB = enumerate_census(sorted(dischargeable), by_target, keep_records=True)
    # ---- Census C: hostile variant, INDEPENDENT_VALIDATOR_PRESENT hard ----
    censusC = enumerate_census(sorted(dischargeable), by_target,
                               validator_hard=True, keep_records=False)

    unbounded = [n for n, c in (("A", censusA), ("B", censusB), ("C", censusC))
                 if not c["bounded"]]

    # ---- cost-component liveness (guards against decorative dimensions) ---
    liveness = {}
    live_dims = []
    if censusB["bounded"] and censusB["adequate"]:
        costs = [c for _k, c, _s in censusB["adequate"]]
        for i, name in enumerate(COST_COMPONENTS):
            vals = sorted({c[i] for c in costs})
            uniquely_decides = 0
            for a, b in itertools.combinations(costs, 2):
                if a == b:
                    continue
                agree_i = a[i] <= b[i]
                others_agree = all(a[j] <= b[j] for j in range(len(a)) if j != i)
                if (a[i] != b[i]) and (agree_i != others_agree):
                    uniquely_decides += 1
            liveness[name] = {
                "distinct_values_over_adequate_plans": vals,
                "constant_over_adequate_plans": len(vals) == 1,
                "pairs_where_this_component_alone_flips_the_comparison": uniquely_decides,
            }
            if len(vals) > 1:
                live_dims.append(i)

    redundancy = []
    adequacy_errs = []
    if censusB["bounded"]:
        by_id = {o["option_id"]: o for o in options}
        adequacy_errs = reverify_adequacy(censusB["records"], by_id)
        redundancy = ordering_redundancy([tuple(r["cost_vector"])
                                          for r in censusB["records"]])

    # ---- Pareto frontier over Census B adequate plans --------------------
    frontier = dominated = []
    costed = []
    law_counterexamples_extra = []
    frontier_errs = []
    incomparable_witness = None
    if censusB["bounded"] and censusB["adequate"]:
        costed = [(k, c) for k, c, _s in censusB["adequate"]]
        frontier, dominated = pareto_frontier(costed)
        frontier_errs = verify_frontier(costed, frontier, dominated)
        for (k1, c1), (k2, c2) in itertools.combinations(frontier, 2):
            if not dominates(c1, c2) and not dominates(c2, c1) and c1 != c2:
                incomparable_witness = {
                    "law": "PE-T1",
                    "plan_a": list(k1), "cost_a": list(c1),
                    "plan_b": list(k2), "cost_b": list(c2),
                    "conclusion": "NO_UNIQUE_CHEAPEST_WITHOUT_PREFERENCES",
                }
                break

    # ---- falsification cross-check: recompute the frontier on the
    # non-redundant axes only. If the redundancy claim is right the frontier
    # must be IDENTICAL; if it differs, the claim is refuted.
    reduced_check = None
    if frontier or dominated:
        red_names = {r["redundant_component"] for r in redundancy}
        keep = [i for i, n in enumerate(COST_COMPONENTS) if n not in red_names]
        costed_r = [(k, tuple(c[i] for i in keep)) for k, c in costed]
        fr_r, dm_r = pareto_frontier(costed_r)
        reduced_check = {
            "kept_components": [COST_COMPONENTS[i] for i in keep],
            "dropped_components": sorted(red_names),
            "frontier_identical": {k for k, _ in fr_r} == {k for k, _ in frontier},
            "reduced_frontier_size": len(fr_r),
            "full_frontier_size": len(frontier),
            "claim": ("dropping an ordering-redundant component cannot change the "
                      "Pareto frontier; a difference would refute the redundancy claim"),
        }
        if not reduced_check["frontier_identical"]:
            law_counterexamples_extra.append({
                "law": "ORDERING_REDUNDANCY_CLAIM",
                "kind": "REDUCED_AXIS_FRONTIER_DIFFERS",
                "full_only": sorted(list(k) for k in
                                    {k for k, _ in frontier} - {k for k, _ in fr_r}),
                "reduced_only": sorted(list(k) for k in
                                       {k for k, _ in fr_r} - {k for k, _ in frontier})})

    # ---- complete exact scalarization-reachability probe ------------------
    scal = []
    scal_checked = True
    red_names_probe = {r["redundant_component"] for r in redundancy}
    reduced_dims = [i for i in live_dims if COST_COMPONENTS[i] not in red_names_probe]
    if frontier and live_dims:
        uniq = sorted({tuple(c) for _k, c in frontier})
        for c in uniq:
            others = [o for o in uniq if o != c]
            reach, checked = scalarization_reachable(c, others, live_dims)
            # redundant axes add constraints and can only make hull membership
            # HARDER, so the negative finding must also be tested on the real axes
            reach_r, checked_r = scalarization_reachable(c, others, reduced_dims) \
                if reduced_dims else (None, False)
            if not checked or not checked_r:
                scal_checked = False
            scal.append({
                "cost_vector": list(c),
                "inside_convex_hull_of_other_frontier_costs": reach,
                "checked_completely": checked,
                "reduced_axes": [COST_COMPONENTS[i] for i in reduced_dims],
                "reduced_axis_cost": [c[i] for i in reduced_dims],
                "inside_hull_on_reduced_axes": reach_r,
                "reduced_checked_completely": checked_r,
                "meaning": ("UNSUPPORTED_POINT: no strictly-positive weight vector "
                            "makes this plan the unique minimiser -- an exact witness "
                            "that scalar 'cheapest plan' talk is invalid here"
                            if reach else
                            "supported point (some positive weighting selects it)"
                            if checked else "CANNOT_CHECK: hull basis bound exceeded"),
            })

    # ---- hostile precondition exercise -----------------------------------
    hostile = []

    # HC-01: complete-but-obstructed families -- the looks-adequate trap.
    trap = [o["option_id"] for o in options if o["obstructed"]]
    hostile.append({
        "case_id": "HC-01",
        "name": "COMPLETE_FAMILY_WITH_UNATTAINED_PRECONDITION",
        "question": "Does 'support family complete' imply adequate?",
        "finding": ("%d of %d complete families carry a registered FAILURE that "
                    "obstructs the producing experiment. They are node-complete and "
                    "therefore look adequate, but ROUTE_NOT_OBSTRUCTED is unattained."
                    % (len(trap), len(options))),
        "witnesses": trap,
        "verdict": "COMPLETENESS_DOES_NOT_IMPLY_ADEQUACY",
        "consequence": ("DISC-WEB-01 reports theorems_with_a_complete_family=%d; the "
                        "number whose support survives hard preconditions is %d."
                        % (web["counts"]["theorems_with_a_complete_family"],
                           len(dischargeable))),
    })

    # HC-02: redundant precondition (derived, not independent).
    dup = [o["option_id"] for o in options
           if o["derived_predicates"]["VALIDATES_EDGE_LOAD_BEARING"]
           != o["hard_preconditions"]["ROUTE_NOT_OBSTRUCTED"]]
    hostile.append({
        "case_id": "HC-02",
        "name": "DERIVED_PREDICATE_MASQUERADING_AS_INDEPENDENT_PRECONDITION",
        "question": "Is VALIDATES_EDGE_LOAD_BEARING an independent hard precondition?",
        "finding": ("No. disc_web_01.py builds the VALIDATES->THEORY edge with "
                    "load_bearing = (not blocked), so the predicate is definitionally "
                    "equal to ROUTE_NOT_OBSTRUCTED. Options where they differ: %d."
                    % len(dup)),
        "witnesses": dup,
        "verdict": "EXCLUDED_FROM_HARD_SET_TO_AVOID_DOUBLE_COUNTING",
        "consequence": ("Counting it separately would inflate the apparent number of "
                        "binding preconditions from 1 to 2 on identical evidence."),
    })

    # HC-03: empty hard strata -- preconditions that never bind (spec 6.3).
    strata = {}
    for name in ("EVIDENCE_CONTENT_IDENTIFIED", "EXPERIMENT_CONTENT_IDENTIFIED",
                 "ROUTE_NOT_OBSTRUCTED"):
        viol = [o["option_id"] for o in options if not o["hard_preconditions"][name]]
        strata[name] = {"n_violating_options": len(viol), "violating_options": viol,
                        "exercised": bool(viol)}
    empty = [k for k, v in strata.items() if not v["exercised"]]
    hostile.append({
        "case_id": "HC-03",
        "name": "PRECONDITION_EMPTY_NOT_EXERCISED",
        "question": "Does every declared hard precondition actually bind on real data?",
        "strata": strata,
        "unexercised": empty,
        "verdict": ("PRECONDITION_EMPTY_NOT_EXERCISED" if empty
                    else "ALL_HARD_PRECONDITIONS_EXERCISED"),
        "consequence": ("An unexercised precondition is decorative: it cannot have "
                        "caused any adequacy verdict in this slice."),
    })

    # HC-04: Census A unsatisfiability, proved by witness not by enumeration.
    hostile.append({
        "case_id": "HC-04",
        "name": "FULL_COVER_OBLIGATION_SET_IS_UNSATISFIABLE",
        "question": "Can any plan discharge every registered obligation?",
        "witness_obligations_with_zero_attained_routes": obstructed_only,
        "proof": ("Each listed obligation has n_precondition_attained_options = 0, so "
                  "every choice function over the registered obligations selects at "
                  "least one option with an unattained hard precondition. No "
                  "enumeration is needed; the %d witnesses settle it."
                  % len(obstructed_only)),
        "enumeration_confirmation": {
            "space_size": censusA.get("space_size"),
            "n_adequate": censusA.get("n_adequate"),
            "n_inadequate": censusA.get("n_inadequate"),
        },
        "verdict": "UNSATISFIABLE_IN_SLICE",
        "consequence": ("The slice cannot support the claim 'OSTC T0-T23 is backed by "
                        "registered execution evidence'. %d of 24 theorems are "
                        "unregistered and %d have only obstructed routes."
                        % (len(unregistered), len(obstructed_only))),
    })

    # HC-05: mutation discrimination harness (obligation handed over by DISC-WEB-01).
    mut = mutation_harness(web, fam, options)
    hostile.append({
        "case_id": "HC-05",
        "name": "MUTATION_DISCRIMINATION_HARNESS",
        "question": ("DISC-WEB-01 deferred this: does perturbing one theorem turn only "
                     "its own families red?"),
        "results": mut,
        "verdict": ("BINDING_IS_ID_BOUND_NOT_CONTENT_BOUND"
                    if any(m["mutation_class"].startswith("M1") and not m["discriminating"]
                           for m in mut) else "DISCRIMINATES"),
        "consequence": ("Theorem content can change without any support family changing "
                        "status: the support relation is not tamper-evident with respect "
                        "to theorem text. M2 shows the harness is not inert -- route "
                        "obstruction does move exactly the affected families."),
    })

    # HC-06: adequacy verdict is contingent on an unregistered authority typing.
    hostile.append({
        "case_id": "HC-06",
        "name": "ADEQUACY_CONTINGENT_ON_UNREGISTERED_AUTHORITY_TYPING",
        "question": ("If INDEPENDENT_VALIDATOR_PRESENT were a hard precondition "
                     "(spec 6.1: cheaper evidence lacking required authority is not "
                     "adequate), does the census survive?"),
        "census_B_n_adequate": censusB.get("n_adequate"),
        "census_C_n_adequate": censusC.get("n_adequate"),
        "self_reported_only_obligations": sorted(
            r["target"] for r in register if r["status"] == "DISCHARGEABLE"
            and all(not o["has_independent_validator"]
                    for o in by_target[r["target"]] if o["all_hard_preconditions_attained"])),
        "verdict": ("ADEQUACY_COLLAPSES_UNDER_AUTHORITY_HARDENING"
                    if censusC.get("n_adequate") == 0 else "ROBUST_TO_AUTHORITY_HARDENING"),
        "consequence": ("The slice registers no per-theorem authority requirement, so "
                        "the adequate/inadequate split reported here is contingent on "
                        "that gap. This is a typing debt, not a licence."),
    })

    # HC-07: explicit no-scalarization audit.
    hostile.append({
        "case_id": "HC-07",
        "name": "IMPLICIT_SCALARIZATION_PROBE",
        "question": "Was any cost vector collapsed to a scalar for ordering?",
        "ordering_relation": "Pareto dominance on integer vectors only",
        "scalarization_reachability": scal,
        "checked_completely": scal_checked,
        "unsupported_frontier_points": [s["cost_vector"] for s in scal
                                        if s["inside_convex_hull_of_other_frontier_costs"]],
        "unsupported_frontier_points_on_reduced_axes": [
            s["cost_vector"] for s in scal if s["inside_hull_on_reduced_axes"]],
        "verdict": ("NO_IMPLICIT_SCALARIZATION" if scal_checked
                    else "NO_IMPLICIT_SCALARIZATION_HULL_PROBE_CANNOT_CHECK"),
        "consequence": ("Any frontier point inside the hull of the others cannot be the "
                        "unique minimiser of a positive-weight scalarization, so no "
                        "single price vector reproduces this frontier."),
    })

    # ---- non-vacuity ------------------------------------------------------
    nonvac = {
        "census_B_adequate": censusB.get("n_adequate"),
        "census_B_inadequate": censusB.get("n_inadequate"),
        "adequacy_discriminates": bool(censusB.get("n_adequate")) and bool(censusB.get("n_inadequate")),
        "frontier_size": len(frontier),
        "dominated_size": len(dominated),
        "pareto_discriminates": bool(frontier) and bool(dominated),
        "incomparable_pair_exists": incomparable_witness is not None,
        "live_cost_dimensions": [COST_COMPONENTS[i] for i in live_dims],
        "constant_cost_dimensions": [n for n, v in liveness.items()
                                     if v["constant_over_adequate_plans"]],
        "hard_preconditions_all_exercised": not empty,
        "unexercised_hard_preconditions": empty,
        "ordering_redundant_components": [r["redundant_component"] for r in redundancy],
        "mutation_harness_can_move": any(m["n_options_moved"] > 0 for m in mut),
    }
    # CORE non-vacuity: does the test discriminate at all? A decorative
    # precondition or a redundant cost axis is a reporting caveat, not a
    # failure of the correspondence, and is registered as a sub-claim instead.
    nonvac["core_passed"] = all([
        nonvac["adequacy_discriminates"],
        nonvac["pareto_discriminates"],
        nonvac["incomparable_pair_exists"],
        nonvac["mutation_harness_can_move"],
    ])
    nonvac["passed"] = nonvac["core_passed"]

    # ---- terminal ---------------------------------------------------------
    law_counterexamples = list(frontier_errs) + list(adequacy_errs) + list(law_counterexamples_extra)
    if unbounded:
        terminal = "PROOF_OPTION_SPACE_TOO_LARGE_OR_UNBOUND"
    elif law_counterexamples:
        terminal = "PARETO_OR_ADEQUACY_LAW_COUNTEREXAMPLE"
    elif not nonvac["core_passed"]:
        # the correspondence could not actually be checked: it discriminates nothing
        terminal = "PROOF_OPTION_SPACE_TOO_LARGE_OR_UNBOUND"
    else:
        terminal = "BOUNDED_PROOF_ECONOMY_CORRESPONDENCE_GREEN"

    cannot_check_subclaims = []
    if not scal_checked:
        cannot_check_subclaims.append({
            "subclaim": "SCALARIZATION_HULL_COMPLETENESS",
            "reason": "hull basis enumeration exceeded HULL_BASIS_BOUND"})
    for name in empty:
        cannot_check_subclaims.append({
            "subclaim": f"PRECONDITION_EMPTY_NOT_EXERCISED:{name}",
            "reason": ("no option in the slice violates this hard precondition, so it "
                       "cannot have caused any adequacy verdict here; its discriminating "
                       "power is untested")})
    if any(m["mutation_class"].startswith("M1") and not m["discriminating"] for m in mut):
        cannot_check_subclaims.append({
            "subclaim": "SUPPORT_BINDING_TAMPER_EVIDENCE",
            "reason": ("support status is keyed on theorem ID, not on theorem "
                       "content_sha256; theorem-content tampering is undetected (HC-05)")})

    headline_caveats = [
        ("Adequacy in this slice is decided by exactly one binding hard precondition "
         "(ROUTE_NOT_OBSTRUCTED); %d of 3 declared hard preconditions have an empty "
         "violating stratum." % len(empty)),
        ("Census C: making INDEPENDENT_VALIDATOR_PRESENT hard drives adequate plans "
         "from %s to %s. The slice registers no per-theorem authority requirement, so "
         "the adequate/inadequate split is contingent on that unregistered typing (HC-06)."
         % (censusB.get("n_adequate"), censusC.get("n_adequate"))),
        ("%d of 5 declared cost components are ordering-redundant (a monotone function "
         "of another component over the full census): %s. Pareto results are unaffected; "
         "the declared vector overstates the number of real axes."
         % (len({r["redundant_component"] for r in redundancy}),
            sorted({r["redundant_component"] for r in redundancy}))),
        ("obstructed_discharges is constant (0) over adequate plans by construction; it "
         "is live only across the full census."),
    ]

    common = {
        "job_id": "DISC-PROOF-ECONOMY-01",
        "class": "LOCAL_EXACT",
        "authority": "finite exact only (integers and fractions.Fraction; no float constructed)",
        "input_sha256": input_hashes,
        "spec": ("research/orion-discovery-v2/KNOWLEDGE_WEB_NAVIGATION_PROOF_ECONOMY_"
                 "AND_SELF_APPLICATION_V1.md section 6 "
                 "(branch codex/orion-discovery-v2-knowledge-web-20260825)"),
        "terminal": terminal,
        "cannot_check_subclaims": cannot_check_subclaims,
        "headline_caveats": headline_caveats,
    }

    (OUT / "PROOF_OBLIGATION_REGISTER.json").write_text(json.dumps({
        "schema": "orion.discovery-v2.proof-obligation-register.v1", **common,
        "counts": {"obligations_total": len(register), **{k: v for k, v in reg_status.items()}},
        "obligation_status_definitions": {
            "DISCHARGEABLE": "at least one complete option attains every hard precondition",
            "OBSTRUCTED_ONLY": "complete options exist but none attains every hard precondition",
            "UNREGISTERED_IN_SLICE": "no complete support family exists in the slice",
        },
        "hard_preconditions": ["EVIDENCE_CONTENT_IDENTIFIED",
                               "EXPERIMENT_CONTENT_IDENTIFIED", "ROUTE_NOT_OBSTRUCTED"],
        "excluded_derived_predicates": {
            "VALIDATES_EDGE_LOAD_BEARING": ("definitionally equal to ROUTE_NOT_OBSTRUCTED; "
                                            "see COUNTEREXAMPLE_ECONOMY_CASES HC-02")},
        "cost_vector_components": COST_COMPONENTS,
        "obligations": register,
        "proof_options": options,
    }, indent=2) + "\n")

    (OUT / "ADEQUATE_PLAN_CENSUS.json").write_text(json.dumps({
        "schema": "orion.discovery-v2.adequate-plan-census.v1", **common,
        "enumeration": {
            "total_not_sampled": True,
            "declared_bound": PLAN_ENUMERATION_BOUND,
            "census_A": {"obligations": sorted(registered),
                         "space_size": censusA.get("space_size"),
                         "n_adequate": censusA.get("n_adequate"),
                         "n_inadequate": censusA.get("n_inadequate"),
                         "records_retained": False,
                         "note": "unsatisfiable by witness; see HC-04"},
            "census_B": {"obligations": sorted(dischargeable),
                         "space_size": censusB.get("space_size"),
                         "n_adequate": censusB.get("n_adequate"),
                         "n_inadequate": censusB.get("n_inadequate"),
                         "records_retained": True},
            "census_C_validator_hard": {"space_size": censusC.get("space_size"),
                                        "n_adequate": censusC.get("n_adequate"),
                                        "n_inadequate": censusC.get("n_inadequate"),
                                        "records_retained": False},
        },
        "violation_counts_census_B": censusB.get("violation_counts"),
        "PE_T4_independent_reverification_errors": adequacy_errs,
        "cost_component_ordering_redundancy": redundancy,
        "non_vacuity": nonvac,
        "cost_component_liveness": liveness,
        "adequate_plans": [{"selection": list(k), "cost_vector": list(c)}
                           for k, c, _s in censusB.get("adequate", [])],
        "all_enumerated_plans_census_B": censusB.get("records"),
    }, indent=2) + "\n")

    (OUT / "PARETO_PROOF_FRONTIER.json").write_text(json.dumps({
        "schema": "orion.discovery-v2.pareto-proof-frontier.v1", **common,
        "ordering": {"relation": "Pareto dominance on integer cost vectors",
                     "scalarization_used": False,
                     "components": COST_COMPONENTS,
                     "live_components": [COST_COMPONENTS[i] for i in live_dims]},
        "counts": {"adequate_plans": censusB.get("n_adequate"),
                   "frontier": len(frontier), "dominated": len(dominated)},
        "frontier": [{"selection": list(k), "cost_vector": list(c)} for k, c in frontier],
        "dominated": [{"selection": list(k), "cost_vector": list(c)} for k, c in dominated],
        "PE_T5_verification_errors": frontier_errs,
        "cost_component_ordering_redundancy": redundancy,
        "reduced_axis_frontier_cross_check": reduced_check,
        "distinct_frontier_cost_vectors": sorted({tuple(c) for _k, c in frontier}),
        "PE_T1_incomparable_witness": incomparable_witness,
        "scalarization_reachability": scal,
        "scalarization_probe_complete": scal_checked,
        "terminal_for_frontier": ("PROOF_PLAN_PARETO_SET_RETURNED"
                                  if frontier and not frontier_errs else "NO_FRONTIER"),
    }, indent=2) + "\n")

    (OUT / "COUNTEREXAMPLE_ECONOMY_CASES.json").write_text(json.dumps({
        "schema": "orion.discovery-v2.counterexample-economy-cases.v1", **common,
        "n_cases": len(hostile),
        "law_counterexamples_found": law_counterexamples,
        "adequacy_law_counterexample": None if not law_counterexamples else law_counterexamples,
        "cases": hostile,
    }, indent=2) + "\n")

    summary = {
        "terminal": terminal,
        "cannot_check_subclaims": cannot_check_subclaims,
        "obligations": dict(reg_status),
        "census_A": {"space": censusA.get("space_size"), "adequate": censusA.get("n_adequate")},
        "census_B": {"space": censusB.get("space_size"), "adequate": censusB.get("n_adequate"),
                     "inadequate": censusB.get("n_inadequate")},
        "census_C_validator_hard": {"adequate": censusC.get("n_adequate")},
        "frontier": len(frontier), "dominated": len(dominated),
        "distinct_frontier_costs": len({tuple(c) for _k, c in frontier}),
        "live_cost_dimensions": nonvac["live_cost_dimensions"],
        "ordering_redundant_components": sorted({r["redundant_component"] for r in redundancy}),
        "unexercised_hard_preconditions": empty,
        "non_vacuity_passed": nonvac["passed"],
        "law_counterexamples": len(law_counterexamples),
        "headline_caveats": headline_caveats,
    }
    print(json.dumps(summary, indent=2))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
