#!/usr/bin/env python3
"""Independent checker for ORION05.GLOBAL_OBSTRUCTION_BASIS.v1 census output.

INDEPENDENCE DISCIPLINE
-----------------------
This file does NOT import the campaign runner
(`run_global_obstruction_basis_v1.py`) and does NOT import the paper solver.
Every judgment — Pauli algebra, cost identities, Lemma-E reduction, the
O_ANCHORED / O_PHANTOM / O_COMM_S2 predicates, outcome derivation, and the
campaign terminal decision order — is re-implemented directly from the frozen
text of THEORY.md (D1-D7) and PROTOCOL.json on branch
`science/o05-obstruction-basis-v1` (commit 1404c56cd).

Shared with the paper (mathematics, not runner judgment; see CHECKER_NOTES.md):
  * the production letter convention I=0,X=1,Y=2,Z=3 with binary symplectic
    coordinates ((0,0),(1,0),(1,1),(0,1)) — a frozen definition, restated here;
  * the frozen F_3 Restore rule, frame multipliers m in {2,4}, Tag cost 2w(S);
  * the result-row FIELD NAMES (schema, not judgment), read off the frozen
    runner file.

EXIT CODES
  0  agreement on every checked item
  2  disagreement (bounded report printed; campaign terminal for this state is
     CANNOT_CHECK__CHECKER_DISAGREEMENT — never arbitrated here)
  3  cannot-check (missing/malformed inputs, wrong n, absent required files)
  5  self-test harness failure (only in --self-test)

No tolerances are granted anywhere: every comparison is exact equality.
"""

from __future__ import annotations

import argparse
import hashlib
import json
import sys
import tempfile
from itertools import combinations, product
from pathlib import Path

# ---------------------------------------------------------------------------
# Frozen mathematical conventions (re-derived, standalone)
# ---------------------------------------------------------------------------

CODE_BITS = ((0, 0), (1, 0), (1, 1), (0, 1))  # I, X, Y, Z
BITS_CODE = {bits: code for code, bits in enumerate(CODE_BITS)}


def lsy(a: int, b: int) -> int:
    """Binary local symplectic product of two phase-ignored Pauli letters."""
    ax, az = CODE_BITS[a]
    bx, bz = CODE_BITS[b]
    return (ax & bz) ^ (az & bx)


def lmul(a: int, b: int) -> int:
    """Phase-ignored local Pauli product."""
    ax, az = CODE_BITS[a]
    bx, bz = CODE_BITS[b]
    return BITS_CODE[(ax ^ bx, az ^ bz)]


def f3(a: int, b: int, c: int) -> int:
    """Frozen donor-owned three-way local Restore-factor support cost."""
    if a == b == c != 0:
        return 1
    return int(a != 0) + int(b != 0) + int(c != 0)


def sletter(sparse, q: int) -> int:
    for qq, a in sparse:
        if qq == q:
            return a
    return 0


def ssymp(a, b) -> int:
    coords = {q for q, _ in a} | {q for q, _ in b}
    return sum(lsy(sletter(a, q), sletter(b, q)) for q in coords) % 2


def as_sparse(entries):
    return tuple((int(q), int(a)) for q, a in entries)


# ---------------------------------------------------------------------------
# Census enumeration and input identity (THEORY D1)
# ---------------------------------------------------------------------------

def census_targets(index: int) -> list[list[int]]:
    for i, combo in enumerate(combinations(range(1, 16), 6)):
        if i == index:
            return [[c // 4, c % 4] for c in combo]
    raise IndexError(index)


def input_hash(targets) -> str:
    blob = json.dumps(targets, separators=(",", ":")).encode()
    return hashlib.sha256(blob).hexdigest()


# ---------------------------------------------------------------------------
# Witness recomputation (frozen objective, re-derived)
# ---------------------------------------------------------------------------

def ordered_slots(targets, matching, perm_b, perm_c):
    """Slot order: pairA + pairB(perm) + pairC(perm); A never swapped."""
    pairs = [(targets[i], targets[j]) for i, j in matching]
    a = pairs[0]
    b = pairs[1] if perm_b == 0 else (pairs[1][1], pairs[1][0])
    c = pairs[2] if perm_c == 0 else (pairs[2][1], pairs[2][0])
    return list(a) + list(b) + list(c)


def frame_cost_recompute(frames, centrals) -> int:
    total = 0
    for j in range(3):
        w0, w1 = len(frames[2 * j]), len(frames[2 * j + 1])
        m0, m1 = (2, 4) if centrals[j] == 0 else (4, 2)
        total += m0 * (w0 - 1) + m1 * (w1 - 1)
    return total


def restore_recompute(slots, frames, n) -> int:
    total = 0
    for q in range(n):
        total += f3(
            lmul(slots[0][q], sletter(frames[0], q)),
            lmul(slots[2][q], sletter(frames[2], q)),
            lmul(slots[4][q], sletter(frames[4], q)),
        )
        total += f3(
            lmul(slots[1][q], sletter(frames[1], q)),
            lmul(slots[3][q], sletter(frames[3], q)),
            lmul(slots[5][q], sletter(frames[5], q)),
        )
    return total


def tag_rank_recompute(frames, active) -> int:
    rows = []
    for frame in frames:
        row = 0
        for j, q in enumerate(active):
            fx, fz = CODE_BITS[sletter(frame, q)]
            if fz:
                row |= 1 << (2 * j)
            if fx:
                row |= 1 << (2 * j + 1)
        rows.append(row)
    rank, bit = 0, 2 * len(active) - 1
    while bit >= 0:
        pivot = next((i for i in range(rank, len(rows)) if (rows[i] >> bit) & 1), None)
        if pivot is None:
            bit -= 1
            continue
        rows[rank], rows[pivot] = rows[pivot], rows[rank]
        for i in range(len(rows)):
            if i != rank and ((rows[i] >> bit) & 1):
                rows[i] ^= rows[rank]
        rank += 1
        bit -= 1
    return rank


def min_tag_weight_n2(pairs, orientation) -> int | None:
    """Brute-force exact minimum Tag weight at n=2 (all 16 dense tags)."""
    best = None
    for t0, t1 in product(range(4), repeat=2):
        tag = tuple((q, a) for q, a in ((0, t0), (1, t1)) if a)
        ok = all(
            (ssymp(tag, r0), ssymp(tag, r1)) == tuple(orientation)
            for r0, r1 in pairs
        )
        if ok:
            w = len(tag)
            best = w if best is None or w < best else best
    return best


# ---------------------------------------------------------------------------
# Classification (THEORY D4-D7, re-implemented from the frozen text)
# ---------------------------------------------------------------------------

def branch_roles(pair, tag, orientation):
    r0, r1 = pair
    l0, l1 = ssymp(tag, r0), ssymp(tag, r1)
    if (l0, l1) != tuple(orientation):
        raise ValueError({"labels_disagree_with_orientation": [l0, l1]})
    return (r0, r1) if l0 == 0 else (r1, r0)


def coordinate_classes(frame, partner, tag):
    return [
        (q, (lsy(a, sletter(partner, q)), lsy(sletter(tag, q), a)))
        for q, a in frame
    ]


def classify_block(f0, f1, tag, other_frames):
    """THEORY D6 predicates. Returns dict(shape, failures, pinned, detail)."""
    w0, w1 = len(f0), len(f1)
    supp0 = [q for q, _ in f0]
    supp1 = [q for q, _ in f1]
    union = sorted(set(supp0) | set(supp1))
    occ = sum(
        1
        for q in union
        if lsy(sletter(tag, q), sletter(f0, q)) or lsy(sletter(tag, q), sletter(f1, q))
    )
    failures: list[str] = []
    pinned = False
    detail = {"w0": w0, "w1": w1, "occ": occ}

    def s(q):
        return sletter(tag, q)

    def pin(q):
        return s(q) != 0 and any(
            sletter(g, q) != 0 and lsy(s(q), sletter(g, q)) == 1
            for g in other_frames
        )

    if w0 == 1 and w1 == 1:
        shape = "anchored"
        q0, q1 = supp0[0], supp1[0]
        good = (
            q0 == q1
            and s(q0) == sletter(f0, q0) != 0
            and lsy(s(q0), sletter(f1, q0)) == 1
        )
        if not good:
            failures.append("anchored_structure")
        if occ != 1:
            failures.append("occupancy")
    elif w0 == 1 and w1 == 2:
        shape = "phantom"
        h = supp0[0]
        if h not in supp1:
            return {
                "shape": "UNCLASSIFIED",
                "failures": ["phantom_home_off_anti"],
                "pinned": False,
                "detail": detail,
            }
        b = next(q for q in supp1 if q != h)
        detail |= {"home": h, "borrow": b}
        if s(h) != 0:
            if lsy(s(h), sletter(f1, h)) or lsy(s(h), sletter(f0, h)):
                failures.append("l1_phantom_at_home")
            failures.append("phantom_tagged_home")
        if s(b) == 0 or lsy(s(b), sletter(f1, b)) != 1:
            failures.append("phantom_untagged_borrow")
        if sletter(f0, h) == sletter(f1, h):
            failures.append("phantom_home_commute")
        if occ != 1:
            failures.append("occupancy")
        pinned = pin(b)
    elif w0 == 2 and w1 == 1:
        shape = "comm_s2"
        a = supp1[0]
        if a not in supp0:
            return {
                "shape": "UNCLASSIFIED",
                "failures": ["comm_s2_partner_off"],
                "pinned": False,
                "detail": detail,
            }
        b = next(q for q in supp0 if q != a)
        detail |= {"anchor": a, "borrow": b}
        good = (
            s(b) != 0
            and lsy(s(b), sletter(f0, b)) == 1
            and s(a) != 0
            and lsy(s(a), sletter(f0, a)) == 1
            and sletter(f1, a) not in (0, s(a), sletter(f0, a))
        )
        if not good:
            failures.append("comm_s2_structure")
        if occ != 2:
            failures.append("occupancy")
        pinned = pin(b)
    elif w0 == 2 and w1 == 2:
        shape = "NEEDS_L1_REDUCTION"
        failures.append("NEEDS_L1_REDUCTION")
    else:
        shape = "UNCLASSIFIED"
        failures.append("UNCLASSIFIED")
    return {"shape": shape, "failures": failures, "pinned": pinned, "detail": detail}


def classify_witness(pairs, tag, orientation):
    blocks = []
    all_frames = [f for p in pairs for f in p]
    for pi, pair in enumerate(pairs):
        f0, f1 = branch_roles(pair, tag, orientation)
        others = [
            f for pj, p in enumerate(pairs) if pj != pi for f in p
        ]
        entry = classify_block(f0, f1, tag, others)
        entry["pair_index"] = pi
        blocks.append(entry)
    weight2 = [b for b in blocks if 2 in (b["detail"]["w0"], b["detail"]["w1"])]
    clean = [
        b for b in weight2 if b["shape"] in ("phantom", "comm_s2") and not b["failures"]
    ]
    return {
        "blocks": blocks,
        "weight2_block_count": len(weight2),
        "clean_obstruction_shapes": sorted({b["shape"] for b in clean}),
        "membership": "IN_BASIS" if clean else "NOT_IN_BASIS",
    }


def reduce_pairs(pairs, tag, orientation, slots, centrals, n, baseline_cost):
    """THEORY D5 reduction (checker's own deletion order; see notes A0)."""
    pairs = [tuple(map(as_sparse, p)) for p in pairs]

    def frames_of(ps):
        return [f for p in ps for f in p]

    def total(ps):
        return (
            frame_cost_recompute(frames_of(ps), centrals)
            + 2 * len(tag)
            + restore_recompute(slots, frames_of(ps), n)
        )

    deletions, audit_failures = [], []
    changed = True
    while changed:
        changed = False
        for pi, (r0, r1) in enumerate(pairs):
            for mi, (frame, partner) in enumerate(((r0, r1), (r1, r0))):
                if len(frame) != 2:
                    continue
                for q, a in frame:
                    if (lsy(a, sletter(partner, q)), lsy(sletter(tag, q), a)) != (0, 0):
                        continue
                    new_frame = tuple(e for e in frame if e[0] != q)
                    new_pair = (new_frame, r1) if mi == 0 else (r0, new_frame)
                    trial = list(pairs)
                    trial[pi] = new_pair
                    ok_anti = all(ssymp(p[0], p[1]) == 1 for p in trial)
                    ok_labels = all(
                        (ssymp(tag, p[0]), ssymp(tag, p[1])) == tuple(orientation)
                        for p in trial
                    )
                    ok_cost = total(trial) == baseline_cost
                    if ok_anti and ok_labels and ok_cost:
                        pairs = trial
                        deletions.append({"pair": pi, "member": mi, "q": q})
                        changed = True
                        break
                    audit_failures.append(
                        {"pair": pi, "member": mi, "q": q, "ok_anti": ok_anti,
                         "ok_labels": ok_labels, "ok_cost": ok_cost}
                    )
                if changed:
                    break
            if changed:
                break
    return pairs, deletions, audit_failures


def derive_outcome(gap, reduced_cls):
    if gap == 0:
        return "NO_GAP"
    if reduced_cls["membership"] == "IN_BASIS":
        return "GAP_IN_BASIS"
    if any("NEEDS_L1_REDUCTION" in b["failures"] for b in reduced_cls["blocks"]):
        return "GAP_NEEDS_L1_REDUCTION"
    return "GAP_NOT_IN_BASIS"


# ---------------------------------------------------------------------------
# Row-level checks
# ---------------------------------------------------------------------------

class Report:
    def __init__(self):
        self.disagreements: list[dict] = []
        self.cannot_check: list[dict] = []

    def dis(self, where, field, ours, theirs):
        self.disagreements.append(
            {"where": where, "field": field, "checker": ours, "runner": theirs}
        )

    def cc(self, where, why):
        self.cannot_check.append({"where": where, "why": why})


def check_row(row, protocol, report: Report, is_control_targets=None):
    rid = row.get("instance_id", "<missing-id>")
    where = f"row:{rid}"
    terminal = row.get("terminal")
    if terminal not in ("OK", "TIMEOUT", "ERROR"):
        report.dis(where, "terminal", "one of OK/TIMEOUT/ERROR", terminal)
        return
    if terminal in ("TIMEOUT", "ERROR"):
        # Fail-closed conformance: adverse rows carry no outcome grade.
        if "outcome" in row:
            report.dis(where, "outcome_on_adverse_row", "absent", row["outcome"])
        return

    targets = row.get("targets")
    if targets is None:
        report.cc(where, "missing targets")
        return
    n = len(targets[0])
    if n != 2:
        report.cc(where, f"n={n} not checkable by the n=2 checker")
        return

    # (a) input identity
    if is_control_targets is not None:
        if targets != is_control_targets:
            report.dis(where, "control_targets", is_control_targets, targets)
    elif isinstance(rid, int):
        expected = census_targets(rid)
        if targets != expected:
            report.dis(where, "census_targets", expected, targets)
    else:
        report.cc(where, f"non-integer instance_id {rid!r} outside control panel")
    if row.get("input_sha256") != input_hash(targets):
        report.dis(where, "input_sha256", input_hash(targets), row.get("input_sha256"))
    frozen_hash = protocol["source_bindings"]["support_two_solver"]["sha256"]
    if row.get("solver_sha256") != frozen_hash:
        report.dis(where, "solver_sha256", frozen_hash, row.get("solver_sha256"))

    w = row.get("witness2")
    for field in ("c_d2", "c_d1", "gap", "matching2"):
        if field not in row:
            report.cc(where, f"missing field {field}")
            return
    if w is None:
        report.cc(where, "missing witness2")
        return

    pairs = [tuple(as_sparse(m) for m in p) for p in w["frames"]]
    frames = [f for p in pairs for f in p]
    tag = as_sparse(w["tag"])
    orientation = tuple(w["orientation"])
    centrals = tuple(w["centrals"])
    matching = [tuple(p) for p in row["matching2"]]
    perm_b, perm_c = w["relative_permutation_B"], w["relative_permutation_C"]

    # matching must be a perfect matching of 0..5
    if sorted(i for p in matching for i in p) != list(range(6)):
        report.dis(where, "matching2_perfect_matching", "perm of 0..5", matching)
        return
    slots = ordered_slots(targets, matching, perm_b, perm_c)

    # (b)+(d) witness validity and exact cost identities
    if not all(ssymp(p[0], p[1]) == 1 for p in pairs):
        report.dis(where, "pairs_anticommute", True, False)
    if not all(1 <= len(f) <= 2 for f in frames):
        report.dis(where, "frame_support_cap", "1..2", [len(f) for f in frames])
    try:
        labels_ok = all(
            (ssymp(tag, p[0]), ssymp(tag, p[1])) == orientation for p in pairs
        )
    except Exception as exc:
        report.cc(where, f"label recompute failed: {exc!r}")
        return
    if not labels_ok:
        report.dis(where, "tag_labels_equal_orientation", True, False)
    active = sorted({q for f in frames for q, _ in f})
    if not {q for q, _ in tag}.issubset(set(active)):
        report.dis(where, "tag_confined_to_active_union", True, False)
    if sorted(w.get("active_union", [])) != active:
        report.dis(where, "active_union", active, w.get("active_union"))
    rank = tag_rank_recompute(frames, active)
    if w.get("tag_constraint_rank") != rank:
        report.dis(where, "tag_constraint_rank", rank, w.get("tag_constraint_rank"))
    min_w = min_tag_weight_n2(pairs, orientation)
    if min_w is None:
        report.dis(where, "tag_feasible", "some tag exists", "none")
    elif len(tag) != min_w:
        report.dis(where, "tag_minimum_weight", min_w, len(tag))

    fc = frame_cost_recompute(frames, centrals)
    rc = restore_recompute(slots, frames, n)
    tc = 2 * len(tag)
    if fc != w["frame_cost"]:
        report.dis(where, "frame_cost", fc, w["frame_cost"])
    if tc != w["tag_cost"]:
        report.dis(where, "tag_cost", tc, w["tag_cost"])
    if rc != w["restore_cost"]:
        report.dis(where, "restore_cost", rc, w["restore_cost"])
    if fc + tc + rc != w["cost"]:
        report.dis(where, "cost_identity", fc + tc + rc, w["cost"])
    if row["c_d2"] != w["cost"]:
        report.dis(where, "c_d2_equals_witness_cost", w["cost"], row["c_d2"])

    # (b) gap classification
    gap = row["c_d1"] - row["c_d2"]
    if row["gap"] != gap:
        report.dis(where, "gap_arithmetic", gap, row["gap"])
    if gap < 0:
        report.dis(where, "gap_nonnegative", ">=0", gap)
        return

    # (c) basis membership through OUR predicates
    try:
        red_pairs, _dels, _audit = reduce_pairs(
            pairs, tag, orientation, slots, centrals, n, w["cost"]
        )
        red_cls = classify_witness([tuple(p) for p in red_pairs], tag, orientation)
    except Exception as exc:
        report.cc(where, f"classification failed: {exc!r}")
        return
    ours = derive_outcome(gap, red_cls)
    theirs = row.get("outcome")
    if ours != theirs:
        report.dis(where, "outcome", ours, theirs)
    rec_mem = (row.get("classification_reduced") or {}).get("membership")
    if gap > 0 and rec_mem is not None and rec_mem != red_cls["membership"]:
        report.dis(where, "reduced_membership", red_cls["membership"], rec_mem)
    return ours


# ---------------------------------------------------------------------------
# Campaign-level checks
# ---------------------------------------------------------------------------

def decide_terminal(outcomes, expected_count, controls_passed, any_cc_rows):
    """Frozen decision order (PROTOCOL.decision_rule_order)."""
    if not controls_passed:
        return "CANNOT_CHECK_CONTROL_FAILURE"
    if any_cc_rows or len(outcomes) != expected_count:
        return "CANNOT_CHECK_INCOMPLETE_CENSUS"
    gaps = [o for o in outcomes if o != "NO_GAP"]
    if not gaps:
        return "T4_NO_GAPS_IN_CENSUS"
    if any(o == "GAP_NOT_IN_BASIS" for o in gaps):
        return "T2_NEW_OBSTRUCTION_CLASS_FOUND"
    if any(o == "GAP_NEEDS_L1_REDUCTION" for o in gaps):
        return "T3_BASIS_INCOMPLETE_NO_PATTERN"
    return "T1_BASIS_COMPLETE"


def check_control_gate(gate, protocol, report: Report):
    controls = gate.get("controls", [])
    by_id = {c.get("control"): c for c in controls}
    all_expected_pass = True
    for cid, spec in protocol.get("controls", {}).items():
        if not isinstance(spec, dict) or "targets_dense" not in spec:
            continue  # rule-text entries (C_NEG_CORRUPT etc.)
        # Runner naming convention (frozen runner CONTROLS_POS): C_POS_R6O_16
        # -> "control:r6o-16". A synthetic protocol may override via control_id.
        default_rid = "control:" + cid.lower().replace("c_pos_", "").replace("_", "-")
        rid = spec.get("control_id", default_rid)
        entry = by_id.get(rid) or by_id.get(cid)
        if entry is None:
            report.cc(f"control:{cid}", "control record missing from CONTROL_GATE")
            all_expected_pass = False
            continue
        rec = entry.get("record", {})
        exp = spec["expected"]
        where = f"control:{cid}"
        if rec.get("terminal") != "OK":
            report.dis(where, "terminal", "OK", rec.get("terminal"))
        exp_costs = exp.get("recorded_costs", {})
        if exp_costs:
            if rec.get("c_d2") != exp_costs.get("C_unrestricted_dp"):
                report.dis(where, "c_d2", exp_costs.get("C_unrestricted_dp"), rec.get("c_d2"))
            if rec.get("c_d1") != exp_costs.get("C_Dplus"):
                report.dis(where, "c_d1", exp_costs.get("C_Dplus"), rec.get("c_d1"))
        if exp.get("gap_positive") and not (rec.get("gap", 0) > 0):
            report.dis(where, "gap_positive", True, rec.get("gap"))
        ours = check_row(rec, protocol, report, is_control_targets=spec["targets_dense"])
        if exp.get("membership") == "IN_BASIS" and ours not in (None, "GAP_IN_BASIS"):
            report.dis(where, "membership", "IN_BASIS", ours)
        if not entry.get("corrupted_basis_fired", False):
            report.dis(where, "corrupted_basis_fired", True,
                       entry.get("corrupted_basis_fired"))
        if not entry.get("passed", False):
            all_expected_pass = False
    gate_flag = gate.get("control_gate_passed")
    # Recompute the gate verdict from what we verified above: it passed iff no
    # control-scoped disagreement/cannot-check was recorded.
    control_issues = [
        d for d in report.disagreements if str(d["where"]).startswith("control:")
    ] + [c for c in report.cannot_check if str(c["where"]).startswith("control:")]
    ours_gate = all_expected_pass and not control_issues
    if gate_flag != ours_gate:
        report.dis("control_gate", "control_gate_passed", ours_gate, gate_flag)
    return ours_gate


def check_campaign(out_dir: Path, protocol, report: Report, aggregate_path=None):
    inst_dir = out_dir / "instances"
    if not inst_dir.is_dir():
        report.cc("campaign", f"missing instances dir {inst_dir}")
        return None
    outcomes = []
    input_defect = False  # unreadable/malformed inputs: checker cannot grade
    adverse_rows = False  # readable TIMEOUT/ERROR rows: faithful recompute
    rows = sorted(inst_dir.glob("inst_*.json"))
    for path in rows:
        try:
            row = json.loads(path.read_text())
        except json.JSONDecodeError as exc:
            report.cc(str(path.name), f"malformed JSON: {exc}")
            input_defect = True
            continue
        before = len(report.cannot_check)
        ours = check_row(row, protocol, report)
        if len(report.cannot_check) > before:
            input_defect = True
        term = row.get("terminal")
        if term in ("TIMEOUT", "ERROR"):
            adverse_rows = True
        elif ours is not None:
            outcomes.append(ours)

    gate_path = out_dir / "CONTROL_GATE.json"
    if gate_path.exists():
        try:
            gate = json.loads(gate_path.read_text())
            controls_passed = check_control_gate(gate, protocol, report)
        except json.JSONDecodeError as exc:
            report.cc("CONTROL_GATE", f"malformed JSON: {exc}")
            controls_passed = False
    else:
        report.cc("CONTROL_GATE", "CONTROL_GATE.json missing")
        controls_passed = False

    expected_count = protocol["instance_family"]["count"]
    terminal = decide_terminal(
        outcomes, expected_count, controls_passed, input_defect or adverse_rows
    )

    if aggregate_path is None and (out_dir / "RESULT.json").exists():
        aggregate_path = out_dir / "RESULT.json"
    if input_defect:
        # With unreadable inputs the checker cannot faithfully grade the
        # terminal; comparison is cannot-check, never a disagreement.
        report.cc("campaign", "aggregate terminal not compared: malformed or "
                              "unreadable inputs present")
    elif aggregate_path is not None and Path(aggregate_path).exists():
        try:
            agg = json.loads(Path(aggregate_path).read_text())
            if agg.get("terminal") != terminal:
                report.dis("campaign", "terminal", terminal, agg.get("terminal"))
        except json.JSONDecodeError as exc:
            report.cc("aggregate", f"malformed JSON: {exc}")
    else:
        print(json.dumps({"note": "no aggregate to compare",
                          "recomputed_terminal": terminal}))
    return terminal


# ---------------------------------------------------------------------------
# Entry
# ---------------------------------------------------------------------------

MAX_PRINTED = 20


def run_check(out_dir: Path, protocol_path: Path, aggregate=None) -> int:
    try:
        protocol = json.loads(Path(protocol_path).read_text())
    except (OSError, json.JSONDecodeError) as exc:
        print(json.dumps({"fatal": "cannot-check", "why": f"protocol: {exc}"}))
        return 3
    report = Report()
    terminal = check_campaign(Path(out_dir), protocol, report, aggregate)
    summary = {
        "recomputed_terminal": terminal,
        "disagreements": len(report.disagreements),
        "cannot_check": len(report.cannot_check),
    }
    print(json.dumps(summary))
    for d in report.disagreements[:MAX_PRINTED]:
        print(json.dumps({"DISAGREEMENT": d}, default=str))
    if len(report.disagreements) > MAX_PRINTED:
        print(json.dumps({"suppressed_disagreements":
                          len(report.disagreements) - MAX_PRINTED}))
    for c in report.cannot_check[:MAX_PRINTED]:
        print(json.dumps({"CANNOT_CHECK": c}, default=str))
    if report.disagreements:
        print(json.dumps({
            "verdict": "DISAGREEMENT",
            "campaign_terminal_for_this_state":
                "CANNOT_CHECK__CHECKER_DISAGREEMENT",
        }))
        return 2
    if report.cannot_check:
        print(json.dumps({"verdict": "CANNOT_CHECK"}))
        return 3
    print(json.dumps({"verdict": "AGREE"}))
    return 0


# ---------------------------------------------------------------------------
# Self-test: synthetic result sets with planted defects (no solver, no repo)
# ---------------------------------------------------------------------------

def _mk_row(instance_id, targets, pairs, tag, orientation, centrals,
            matching, perm_b, perm_c, c_d1_delta, outcome):
    frames = [f for p in pairs for f in p]
    slots = ordered_slots(targets, matching, perm_b, perm_c)
    fc = frame_cost_recompute(frames, centrals)
    rc = restore_recompute(slots, frames, 2)
    cost = fc + 2 * len(tag) + rc
    active = sorted({q for f in frames for q, _ in f})
    row = {
        "schema": "ORION.ORION05.GLOBAL_OBSTRUCTION_BASIS.InstanceResult.v1",
        "instance_id": instance_id,
        "targets": targets,
        "input_sha256": input_hash(targets),
        "solver_sha256": "SELFTEST_SOLVER_HASH",
        "terminal": "OK",
        "c_d2": cost,
        "c_d1": cost + c_d1_delta,
        "gap": c_d1_delta,
        "matching2": [list(p) for p in matching],
        "witness2": {
            "cost": cost,
            "frames": [[[list(e) for e in p[0]], [list(e) for e in p[1]]]
                       for p in pairs],
            "tag": [list(e) for e in tag],
            "orientation": list(orientation),
            "centrals": list(centrals),
            "relative_permutation_B": perm_b,
            "relative_permutation_C": perm_c,
            "frame_cost": fc,
            "tag_cost": 2 * len(tag),
            "restore_cost": rc,
            "active_union": active,
            "tag_constraint_rank": tag_rank_recompute(frames, active),
        },
        "witness2_checks_all": True,
        "witness1_checks_all": True,
        "outcome": outcome,
    }
    if c_d1_delta > 0:
        row["classification_reduced"] = {
            "membership": "IN_BASIS" if outcome == "GAP_IN_BASIS" else "NOT_IN_BASIS"
        }
    return row


def _selftest_fixtures(base: Path):
    """Build clean + three planted-defect result sets. Returns scenario dirs."""
    X, Y, Z = 1, 2, 3
    anchored_pair = (((0, Y),), ((0, X),))          # roles f0=Y@0, f1=X@0
    comm_pair = (((0, X), (1, X)), ((0, Z),))        # comm_s2 block
    tag1 = ((0, Y),)                                 # for all-anchored witness
    tag2 = ((0, Y), (1, Z))                          # for comm_s2 witness
    orientation = (0, 1)
    matching = [(0, 1), (2, 3), (4, 5)]

    row_a = _mk_row(0, census_targets(0), [anchored_pair] * 3, tag1,
                    orientation, (0, 0, 0), matching, 0, 0, 0, "NO_GAP")
    row_b = _mk_row(1, census_targets(1), [comm_pair, anchored_pair,
                    anchored_pair], tag2, orientation, (0, 0, 0), matching,
                    0, 0, 1, "GAP_IN_BASIS")
    # Synthetic protocol: same schema/logic, self-test expectations and count.
    proto = {
        "instance_family": {"count": 2},
        "source_bindings": {"support_two_solver": {"sha256": "SELFTEST_SOLVER_HASH"}},
        "controls": {
            "C_POS_SYNTH": {
                "control_id": "control:synth",
                "targets_dense": census_targets(1),
                "expected": {
                    "gap_positive": True,
                    "membership": "IN_BASIS",
                    "recorded_costs": {
                        "C_unrestricted_dp": row_b["c_d2"],
                        "C_Dplus": row_b["c_d1"],
                    },
                },
            }
        },
    }
    ctrl_rec = dict(row_b)
    ctrl_rec["instance_id"] = "control:synth"
    gate = {
        "control_gate_passed": True,
        "controls": [{
            "control": "control:synth",
            "passed": True,
            "positive_ok": True,
            "corrupted_basis_fired": True,
            "record": ctrl_rec,
        }],
    }
    result = {"terminal": "T1_BASIS_COMPLETE"}

    def write(name, rows, gate_obj, result_obj, corrupt_file=False):
        d = base / name
        (d / "instances").mkdir(parents=True)
        for r in rows:
            rid = r["instance_id"]
            fname = f"inst_{rid:04d}.json" if isinstance(rid, int) else f"inst_{rid}.json"
            (d / "instances" / fname).write_text(json.dumps(r))
        (d / "CONTROL_GATE.json").write_text(json.dumps(gate_obj))
        (d / "RESULT.json").write_text(json.dumps(result_obj))
        if corrupt_file:
            (d / "instances" / "inst_9999.json").write_text("{not json")
        (d / "PROTOCOL.json").write_text(json.dumps(proto))
        return d

    clean = write("clean", [row_a, row_b], gate, result)

    bad_row = json.loads(json.dumps(row_b))
    bad_row["outcome"] = "GAP_NOT_IN_BASIS"          # (i) corrupted outcome
    bad_row["classification_reduced"] = {"membership": "NOT_IN_BASIS"}
    s1 = write("corrupt-row", [row_a, bad_row], gate, result)

    s2 = write("corrupt-terminal", [row_a, row_b], gate,
               {"terminal": "T4_NO_GAPS_IN_CENSUS"})  # (ii) mis-graded terminal

    bad_gate = json.loads(json.dumps(gate))
    bad_gate["controls"][0]["corrupted_basis_fired"] = False  # (iii) bad control
    s3 = write("corrupt-control", [row_a, row_b], bad_gate, result)

    s4 = write("malformed", [row_a, row_b], gate, result, corrupt_file=True)
    return [("clean", clean, 0), ("corrupt-row", s1, 2),
            ("corrupt-terminal", s2, 2), ("corrupt-control", s3, 2),
            ("malformed", s4, 3)]


def self_test() -> int:
    ok = True
    with tempfile.TemporaryDirectory() as td:
        for name, d, expected in _selftest_fixtures(Path(td)):
            print(f"--- self-test scenario: {name} (expect exit {expected}) ---")
            code = run_check(d, d / "PROTOCOL.json")
            print(json.dumps({"scenario": name, "exit": code,
                              "expected": expected, "ok": code == expected}))
            ok = ok and code == expected
    print(json.dumps({"self_test_passed": ok}))
    return 0 if ok else 5


def main() -> int:
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument("--out-dir", type=Path, help="campaign output dir to check")
    ap.add_argument("--protocol", type=Path, help="frozen PROTOCOL.json path")
    ap.add_argument("--aggregate", type=Path, default=None)
    ap.add_argument("--self-test", action="store_true")
    args = ap.parse_args()
    if args.self_test:
        return self_test()
    if not args.out_dir or not args.protocol:
        print(json.dumps({"fatal": "cannot-check",
                          "why": "--out-dir and --protocol required"}))
        return 3
    return run_check(args.out_dir, args.protocol, args.aggregate)


if __name__ == "__main__":
    sys.exit(main())
