#!/usr/bin/env python3
"""VM6 — structural Psi-side enrichment, recorded before outcomes.

REVIVAL_PASS_V1 improvement path #3 (V2 lane): the V4 census recorded only
cost-side and regime fields, so no admissible (cost-independent) structural
enrichment of the vocabulary was ever tested. This driver replays the frozen
enumeration (derivation + canonicalisation only — no outcome search), binds
each replayed instance positionally to the frozen V4 receipt row, computes the
pre-registered family of cost-independent structural features for every
instance, and asks the certificate-explanation-gap-v1 Theorem-1/2 question for
each registered candidate vocabulary Psi: is C_Dxx constant on every Psi-fibre?

Machinery: run_per_panel_v4.py imported unmodified (sha256-asserted). Costs and
all outcome quantities come from the receipt rows; the imported evaluate() is
used only for the 30 registered binding controls, never as a data source for
the constancy analysis.

Protocol: development/orion-10-vm6-structural-enrichment/VM6_STRUCTURAL_ENRICHMENT_PROTOCOL_V1.md
(frozen before any outcome computation).

Authority: finite-population statement over the frozen V4 census (13,458
instances, 10 registered panels, unit-cost R6M grammar at the frozen config).
NOT an all-n statement; no promotion; novelty_authority=false;
physical_quantum_advantage_claim=false.

Exit codes: 0 = separating primitive found; 1 = no registered enrichment
(negative terminal); 3 = CANNOT_CHECK.
"""
from __future__ import annotations

import argparse
import ast
import hashlib
import json
import sys
import time
from collections import defaultdict
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parents[3]
V4_DIR = (
    REPO_ROOT
    / "papers"
    / "orion-10-certified-static-forecasting"
    / "theory"
    / "vocabulary-minimality-v4-per-panel-dedupe"
)
RECEIPT = V4_DIR / "RUN_3561900_RAW.json.gz"
MACHINERY = V4_DIR / "run_per_panel_v4.py"
ORIONQ_DIR = REPO_ROOT / "research" / "extensions" / "orion-q"
ORIONQG_DIR = REPO_ROOT / "research" / "extensions" / "orion-qg"
PROTOCOL = (
    REPO_ROOT
    / "development"
    / "orion-10-vm6-structural-enrichment"
    / "VM6_STRUCTURAL_ENRICHMENT_PROTOCOL_V1.md"
)

#: Frozen at registration. G1.
RECEIPT_SHA256 = "28a760c7b4abb552cb9c4cd66c705bd070c21c4332b5330d7b53191e8ee7857f"
#: run_per_panel_v4.py must be byte-identical to the registration (G0).
MACHINERY_SHA256 = (
    "1525895d75e0a46793425404222b8e1cdd844fadb977d359649132f928dcffd9"
)
#: origin/main commit this study was registered against.
BASE_REVISION = "4f2a223ae383cb7a999c86538befc8bd28d1357d"
SCHEMA_ID = "ORION10.VM6_STRUCTURAL_ENRICHMENT.v1"
EXPECTED_TOTAL_ROWS = 13458

# The frozen module's internal sys.path entry (theory/orion-q) no longer
# exists; the machinery modules now live under research/extensions/. Pre-insert
# those BEFORE importing the module. This is a path fix, not an edit.
sys.path.insert(0, str(ORIONQ_DIR))
sys.path.insert(0, str(ORIONQG_DIR))
sys.path.insert(0, str(V4_DIR))

import run_per_panel_v4 as v4  # noqa: E402

#: Cost-machinery symbols that must not appear inside any feature_* function
#: (G6 anti-instrument gate).
FORBIDDEN_IN_FEATURES = {
    "evaluate", "r6m", "r6o", "r6p", "r6s", "qg5b", "p10", "v4",
    "C_DP", "C_Dxx", "C_Dplus", "f_Bprime", "gap4", "regime",
    "receipt", "rows", "row", "cost",
}


# --------------------------------------------------------------------------
# Receipt loading (pattern imported from check_fibre_constancy_v5.py).
# --------------------------------------------------------------------------

def _find(obj, key, depth=0):
    if depth > 5:
        return None
    if isinstance(obj, dict):
        if key in obj:
            return obj[key]
        for value in obj.values():
            found = _find(value, key, depth + 1)
            if found is not None:
                return found
    return None


def load_receipt() -> tuple[list[dict], dict]:
    """Return (census_rows, panels) from the frozen receipt, sha-asserted."""
    blob = None
    digest = hashlib.sha256()
    with open(RECEIPT, "rb") as fh:
        blob_compressed = fh.read()
    import gzip

    blob = gzip.decompress(blob_compressed)
    digest = hashlib.sha256(blob).hexdigest()
    if digest != RECEIPT_SHA256:
        raise RuntimeError(
            "G1 FAILED: receipt changed since the protocol was frozen: "
            f"{digest}"
        )
    rows = None
    panels = None
    for line in blob.decode("utf-8").splitlines():
        if "=" in line and line.split("=", 1)[1].lstrip().startswith("{"):
            obj = json.loads(line.split("=", 1)[1])
            rows = _find(obj, "full_census_rows_v2") if rows is None else rows
            panels = _find(obj, "panels") if panels is None else panels
            if rows is not None and panels is not None:
                break
    if rows is None or panels is None:
        raise RuntimeError("G1 FAILED: receipt lacks census rows or panels")
    return rows, panels


# --------------------------------------------------------------------------
# Pre-registered structural features (Psi-side, computed from the canonical
# key only — no cost machinery, enforced by the G6 AST gate).
# --------------------------------------------------------------------------

def _anticommute(a: int, b: int) -> bool:
    """Distinct non-identity single-qubit Pauli letters anticommute."""
    return a != 0 and b != 0 and a != b


def feature_n(key: tuple) -> int:
    return key[0]


def feature_weights(key: tuple) -> tuple:
    cols = key[1:]
    return tuple(
        sum(1 for col in cols if col[i] != 0) for i in range(6)
    )


def feature_column_supports(key: tuple) -> tuple:
    return tuple(sum(1 for c in col if c != 0) for col in key[1:])


def feature_letter_multiset(key: tuple) -> tuple:
    return tuple(sorted(letter for col in key[1:] for letter in col))


def feature_commutation_matrix(key: tuple) -> tuple:
    """Flattened 6x6 commute-bit matrix of the canonical key's target rows.

    Rows i, j commute iff the number of qubits on which their canonical
    letters are distinct non-identity letters is even (letter form of the
    mod-2 symplectic inner product).
    """
    cols = key[1:]
    bits = []
    for i in range(6):
        for j in range(6):
            anticommutes = sum(
                1 for col in cols if _anticommute(col[i], col[j])
            )
            bits.append(0 if anticommutes % 2 else 1)
    return tuple(bits)


def feature_pair_commute(key: tuple) -> tuple:
    m = feature_commutation_matrix(key)
    return (m[0 * 6 + 1], m[2 * 6 + 3], m[4 * 6 + 5])


FEATURE_NAMES = (
    "n",
    "weights",
    "column_supports",
    "letter_multiset",
    "commutation_matrix",
    "pair_commute",
)

FEATURE_FNS = {
    "n": feature_n,
    "weights": feature_weights,
    "column_supports": feature_column_supports,
    "letter_multiset": feature_letter_multiset,
    "commutation_matrix": feature_commutation_matrix,
    "pair_commute": feature_pair_commute,
}


def commutation_from_instance(tp: tuple) -> tuple:
    """Commute-bit matrix computed from a raw (x, z) instance (G4 control)."""
    rows = [t for pair in tp for t in pair]
    bits = []
    for a in rows:
        for b in rows:
            phase = ((a[0] & b[1]) ^ (a[1] & b[0])).bit_count()
            bits.append(0 if phase % 2 else 1)
    return tuple(bits)


# --------------------------------------------------------------------------
# Constancy checker (validated on synthetic data before any real analysis).
# --------------------------------------------------------------------------

def constancy_analysis(items: list[tuple[tuple, int]]) -> dict:
    """items: [(psi_key, cost)] -> fibre-constancy report for one Psi."""
    grouped: dict[tuple, set] = defaultdict(set)
    members: dict[tuple, list] = defaultdict(list)
    for idx, (psi_key, cost) in enumerate(items):
        grouped[psi_key].add(cost)
        members[psi_key].append((idx, cost))
    mixed = {k: sorted(v) for k, v in grouped.items() if len(v) > 1}
    rows_in_mixed = sum(len(members[k]) for k in mixed)
    worst_key = None
    worst_spread = -1
    for k, costs in mixed.items():
        spread = max(costs) - min(costs)
        if spread > worst_spread:
            worst_spread = spread
            worst_key = k
    return {
        "n_fibres": len(grouped),
        "mixed_fibres": len(mixed),
        "rows_in_mixed_fibres": rows_in_mixed,
        "worst_fibre_key": worst_key,
        "worst_cost_spread": worst_spread if worst_key is not None else 0,
        "mixed_fibre_costs": (
            {repr(k): v for k, v in sorted(mixed.items(), key=lambda x: repr(x[0]))[:5]}
            if mixed
            else {}
        ),
    }


def self_test_constancy_checker() -> None:
    """Verdict tracking on synthetic data: mixed fibre must be flagged,
    constant population must not be. Fails loudly if the checker is blind."""
    # 3 rows, fibres A (costs 5, 5) and B (costs 7, 9): exactly B mixed.
    report = constancy_analysis([(("A",), 5), (("A",), 5), (("B",), 7), (("B",), 9)])
    assert report["n_fibres"] == 2, report
    assert report["mixed_fibres"] == 1, report
    assert report["rows_in_mixed_fibres"] == 2, report
    assert report["worst_cost_spread"] == 2, report
    ok = constancy_analysis([(("A",), 5), (("A",), 5), (("B",), 7)])
    assert ok["mixed_fibres"] == 0 and ok["rows_in_mixed_fibres"] == 0, ok
    print("SELF_TEST_CONSTANCY_CHECKER=PASS", flush=True)


# --------------------------------------------------------------------------
# Replay of the frozen enumeration (derivation + canonicalisation only).
# --------------------------------------------------------------------------

def replay_panel(hname: str, n: int, limit: int | None):
    """Replicate run_per_panel's enumeration loop exactly, minus evaluate().

    Returns (rows, counters) where rows[i] = dict(s_idx, tp_idx, key) for the
    i-th evaluated instance, and counters mirror the receipt summary fields.
    """
    skels = v4.SKELETON_BUILDERS[hname](n)
    cap = v4.CAPS[(hname, n)]
    if limit is not None:
        cap = min(cap, limit)
    if hname == "H5":
        pair_lists = []
        for frames6, s in skels:
            occ = set(v4.qg5b._qubits(v4.qg5b._supp_mask(s)))
            for f in frames6:
                occ |= set(v4.qg5b._qubits(v4.qg5b._supp_mask(f)))
            pair_lists.append(v4.template_pairs_h5(n, occ))
    else:
        shared = v4.template_pairs(n)
        pair_lists = [shared] * len(skels)
    max_tp = max(len(pl) for pl in pair_lists)

    dedupe: set = set()
    raw = zero_skip = dup_skip = 0
    out: list[dict] = []
    cap_hit = False
    for tp_idx in range(max_tp):
        if cap_hit:
            break
        for s_idx, (frames6, s) in enumerate(skels):
            if len(out) >= cap:
                cap_hit = True
                break
            if tp_idx >= len(pair_lists[s_idx]):
                continue
            raw += 1
            tp = v4.derive_instance(frames6, pair_lists[s_idx][tp_idx])
            if tp is None:
                zero_skip += 1
                continue
            key = v4.canonical_key(tp, n)
            if key in dedupe:
                dup_skip += 1
                continue
            dedupe.add(key)
            out.append({"s_idx": s_idx, "tp_idx": tp_idx, "key": key})
        else:
            continue
        break
    counters = {
        "raw_scanned": raw,
        "zero_target_skipped": zero_skip,
        "duplicate_skipped": dup_skip,
        "evaluated": len(out),
        "cap": v4.CAPS[(hname, n)],
        "cap_hit": cap_hit,
    }
    return out, counters, skels, pair_lists


# --------------------------------------------------------------------------
# Anti-instrument AST gate (G6a).
# --------------------------------------------------------------------------

def anti_instrument_gate() -> None:
    tree = ast.parse(Path(__file__).read_text())
    checked = 0
    for node in ast.walk(tree):
        if isinstance(node, ast.FunctionDef) and node.name.startswith("feature_"):
            checked += 1
            for sub in ast.walk(node):
                if isinstance(sub, ast.Name) and sub.id in FORBIDDEN_IN_FEATURES:
                    raise RuntimeError(
                        f"G6a FAILED: feature function {node.name} references "
                        f"forbidden symbol {sub.id}"
                    )
                if isinstance(sub, ast.Attribute) and sub.attr in FORBIDDEN_IN_FEATURES:
                    raise RuntimeError(
                        f"G6a FAILED: feature function {node.name} references "
                        f"forbidden attribute {sub.attr}"
                    )
    assert checked == len(FEATURE_FNS), (
        f"G6a FAILED: expected {len(FEATURE_FNS)} feature functions, "
        f"AST-gated {checked}"
    )
    print(f"G6_ANTI_INSTRUMENT=PASS (feature functions gated: {checked})", flush=True)


# --------------------------------------------------------------------------
# Main.
# --------------------------------------------------------------------------

def canonical_json(value) -> str:
    return json.dumps(value, sort_keys=True, separators=(",", ":"))


def main() -> int:
    t_start = time.monotonic()
    parser = argparse.ArgumentParser()
    parser.add_argument(
        "--panel-limit", type=int, default=None,
        help="smoke mode: truncate each panel's replay to N rows",
    )
    parser.add_argument(
        "--probe-span", type=int, default=None,
        help="smoke mode: probe every N-th row instead of the registered set",
    )
    args = parser.parse_args()
    smoke = args.panel_limit is not None

    # ---- G0: machinery byte-identical to registration ----------------------
    machinery_sha = hashlib.sha256(MACHINERY.read_bytes()).hexdigest()
    assert machinery_sha == MACHINERY_SHA256, (
        f"G0 FAILED: run_per_panel_v4.py differs from registration: {machinery_sha}"
    )
    print(f"G0_MACHINERY_SHA=PASS ({machinery_sha})", flush=True)

    # ---- G6a: anti-instrument ---------------------------------------------
    anti_instrument_gate()

    # ---- G1: receipt integrity --------------------------------------------
    rows, panels = load_receipt()
    assert len(rows) == EXPECTED_TOTAL_ROWS, (
        f"G1 FAILED: expected {EXPECTED_TOTAL_ROWS} rows, got {len(rows)}"
    )
    print(f"G1_RECEIPT_SHA=PASS ({len(rows)} rows)", flush=True)

    # ---- G7: population fact C_DP == C_Dxx on every receipt row -----------
    dp_xx_violations = sum(1 for r in rows if r["C_DP"] != r["C_Dxx"])
    assert dp_xx_violations == 0, (
        f"G7 FAILED: C_DP != C_Dxx on {dp_xx_violations} receipt rows"
    )
    print("G7_DP_EQ_XX=PASS (13458/13458)", flush=True)

    # ---- self-test of the constancy checker -------------------------------
    self_test_constancy_checker()

    # receipt rows grouped by panel, in local_index order
    by_panel: dict[str, list[dict]] = defaultdict(list)
    for r in rows:
        by_panel[r["panel"]].append(r)
    for pname in by_panel:
        by_panel[pname].sort(key=lambda r: r["local_index"])

    feature_rows: list[dict] = []
    probe_count = 0
    sample_checks = 0
    roundtrips = 0
    global_row_idx = 0

    for hname, n in v4.PANEL_ORDER:
        pname = f"{hname}_n{n}"
        replayed, counters, skels, pair_lists = replay_panel(
            hname, n, args.panel_limit
        )
        receipt_rows = by_panel[pname]
        summary = panels[pname]

        # ---- G2: replay counters + row-sequence alignment -----------------
        if not smoke:
            for field in (
                "evaluated", "raw_scanned", "zero_target_skipped",
                "duplicate_skipped", "cap_hit",
            ):
                assert counters[field] == summary[field], (
                    f"G2 FAILED: {pname} {field}: replay {counters[field]} "
                    f"vs receipt {summary[field]}"
                )
        assert len(replayed) <= len(receipt_rows)
        for lidx, rrow in enumerate(replayed):
            rr = receipt_rows[lidx]
            assert rr["local_index"] == lidx
            # feature computation BEFORE any constancy analysis (G6b staged)
            key = rrow["key"]
            feats = {name: fn(key) for name, fn in FEATURE_FNS.items()}
            feature_rows.append({
                "panel": pname,
                "local_index": lidx,
                "global_index": global_row_idx,
                "key": key,
                "features": feats,
                "receipt": {
                    "f_Bprime": rr["f_Bprime"],
                    "C_DP": rr["C_DP"],
                    "C_Dxx": rr["C_Dxx"],
                    "C_Dplus": rr["C_Dplus"],
                    "gap4": rr["gap4"],
                    "regime": rr["regime"],
                },
            })
            global_row_idx += 1

        # ---- G4 (sampled): canonical round-trip + commutation invariance --
        span = args.probe_span or 500
        for lidx, rrow in enumerate(replayed):
            if lidx % span and lidx not in (0, len(replayed) // 2, len(replayed) - 1):
                continue
            key = rrow["key"]
            inst = v4.instance_from_key(key)
            assert v4.canonical_key(inst, n) == key, (
                f"G4 FAILED: round-trip broken at {pname}[{lidx}]"
            )
            roundtrips += 1
            tp = v4.derive_instance(
                skels[rrow["s_idx"]][0], pair_lists[rrow["s_idx"]][rrow["tp_idx"]]
            )
            assert tp is not None
            assert commutation_from_instance(tp) == feature_commutation_matrix(key), (
                f"G4 FAILED: commutation matrix not canonical-invariant at "
                f"{pname}[{lidx}]"
            )
            sample_checks += 1

        # ---- G3 (registered probe set): exact evaluate() binding ----------
        probes = sorted(
            {0, len(replayed) // 2, len(replayed) - 1}
            & set(range(len(replayed)))
        )
        if smoke:
            probes = sorted(set(range(0, len(replayed), max(1, args.probe_span or 25))))
        for lidx in probes:
            rrow = replayed[lidx]
            rr = receipt_rows[lidx]
            tp = v4.derive_instance(
                skels[rrow["s_idx"]][0], pair_lists[rrow["s_idx"]][rrow["tp_idx"]]
            )
            v4._clear_instance_caches()
            ev = v4.evaluate(tp, n)
            for field in ("C_DP", "C_Dxx", "C_Dplus", "f_Bprime", "gap4", "regime"):
                assert ev[field] == rr[field], (
                    f"G3 FAILED: {pname}[{lidx}] {field}: evaluate() "
                    f"{ev[field]} vs receipt {rr[field]}"
                )
            probe_count += 1
        print(
            f"PANEL_REPLAY={pname} rows={len(replayed)} "
            f"counters={canonical_json(counters)} probes={probe_count} "
            f"g4_checks={sample_checks}",
            flush=True,
        )

    # ---- G6b: staged output — feature table frozen before constancy -------
    features_digest = hashlib.sha256(
        canonical_json(
            [
                {
                    "panel": fr["panel"],
                    "local_index": fr["local_index"],
                    "features": {
                        k: (list(v) if isinstance(v, tuple) else v)
                        for k, v in fr["features"].items()
                    },
                    "key": [list(c) for c in fr["key"][1:]],
                    "key_n": fr["key"][0],
                }
                for fr in feature_rows
            ]
        ).encode()
    ).hexdigest()
    print(f"FEATURE_TABLE_SHA256={features_digest}", flush=True)
    print(
        f"STAGE=FEATURES_FROZEN rows={len(feature_rows)} — constancy analysis "
        "starts only now (G6b)",
        flush=True,
    )

    # ---- G5: cross-panel canonical-key cost consistency --------------------
    key_costs: dict[tuple, set] = defaultdict(set)
    key_hits: dict[tuple, list] = defaultdict(list)
    for fr in feature_rows:
        k = fr["key"]
        key_costs[k].add(
            (fr["receipt"]["C_DP"], fr["receipt"]["C_Dxx"],
             fr["receipt"]["C_Dplus"], fr["receipt"]["f_Bprime"])
        )
        key_hits[k].append(
            {"panel": fr["panel"], "local_index": fr["local_index"]}
        )
    inconsistent = {k: v for k, v in key_costs.items() if len(v) > 1}
    assert not inconsistent, (
        f"G5 FAILED: {len(inconsistent)} canonical keys carry inconsistent "
        "costs across panels"
    )
    cross_panel_keys = sum(1 for k, h in key_hits.items() if len(h) > 1)
    print(
        f"G5_CROSS_PANEL_KEY_CONSISTENCY=PASS "
        f"(distinct_keys={len(key_costs)}, cross_panel_keys={cross_panel_keys})",
        flush=True,
    )

    # ---- constancy analysis over registered vocabularies -------------------
    def vocab_key(fr: dict, names: tuple) -> tuple:
        parts = [fr["receipt"]["f_Bprime"]]
        for name in names:
            value = fr["features"][name]
            parts.append(value)
        return tuple(parts)

    vocab_reports: dict[str, dict] = {}
    candidate_ids = {
        "B0": (),
        "S1": ("n",),
        "S2": ("weights",),
        "S3": ("column_supports",),
        "S4": ("letter_multiset",),
        "S5": ("commutation_matrix",),
        "S6": ("pair_commute",),
        "C": FEATURE_NAMES[:5],  # n, weights, supports, letters, commutation
    }
    for vid, names in candidate_ids.items():
        items = [(vocab_key(fr, names), fr["receipt"]["C_Dxx"]) for fr in feature_rows]
        vocab_reports[vid] = constancy_analysis(items)
        vocab_reports[vid]["features"] = list(names)
        print(
            f"VOCAB={vid} fibres={vocab_reports[vid]['n_fibres']} "
            f"mixed={vocab_reports[vid]['mixed_fibres']} "
            f"rows_in_mixed={vocab_reports[vid]['rows_in_mixed_fibres']}",
            flush=True,
        )

    # diagnostics: each single feature alone (Q2, no terminal weight)
    for name in FEATURE_NAMES:
        items = [((fr["features"][name],), fr["receipt"]["C_Dxx"]) for fr in feature_rows]
        report = constancy_analysis(items)
        vocab_reports[f"DIAG_{name}"] = report
        vocab_reports[f"DIAG_{name}"]["features"] = [name]
        print(
            f"DIAG={name} fibres={report['n_fibres']} "
            f"mixed={report['mixed_fibres']} "
            f"rows_in_mixed={report['rows_in_mixed_fibres']}",
            flush=True,
        )

    # CONTROL: canonical key itself (constant by G5 construction)
    control_items = [
        ((tuple(list(fr["key"])),), fr["receipt"]["C_Dxx"]) for fr in feature_rows
    ]
    vocab_reports["CONTROL"] = constancy_analysis(control_items)
    vocab_reports["CONTROL"]["features"] = ["canonical_key"]

    # ---- terminal determination -------------------------------------------
    b0 = vocab_reports["B0"]
    if b0["mixed_fibres"] == 0:
        print(
            "STATUS=CANNOT_CHECK__V5_REPRODUCTION_FAILED "
            "(B0 shows no mixed fibre on the same receipt V5 refuted)",
            flush=True,
        )
        return 3

    candidates = {vid: vocab_reports[vid] for vid in ("S1", "S2", "S3", "S4", "S5", "S6", "C")}
    exact_vocabs = [vid for vid, rep in candidates.items() if rep["mixed_fibres"] == 0]

    # worst surviving pair under C (finest registered vocabulary)
    worst_pair = None
    if candidates["C"]["mixed_fibres"] > 0:
        by_c: dict[tuple, list] = defaultdict(list)
        for fr in feature_rows:
            by_c[vocab_key(fr, candidate_ids["C"])].append(fr)
        best_spread = -1
        for ck, members in by_c.items():
            if len(members) < 2:
                continue
            costs = {m["receipt"]["C_Dxx"] for m in members}
            if len(costs) < 2:
                continue
            spread = max(costs) - min(costs)
            if spread > best_spread:
                lo = min(
                    (m for m in members if m["receipt"]["C_Dxx"] == min(costs)),
                    key=lambda m: (m["panel"], m["local_index"]),
                )
                hi = min(
                    (m for m in members if m["receipt"]["C_Dxx"] == max(costs)),
                    key=lambda m: (m["panel"], m["local_index"]),
                )
                best_spread = spread
                worst_pair = {
                    "c_fibre_key": ck,
                    "cost_spread": spread,
                    "low": _witness(lo),
                    "high": _witness(hi),
                }

    protocol_sha = hashlib.sha256(PROTOCOL.read_bytes()).hexdigest()
    runtime = round(time.monotonic() - t_start, 3)

    if exact_vocabs:
        terminal = "STRUCTURAL_ENRICHMENT_EXACT__SEPARATING_PRIMITIVE_FOUND"
        exit_code = 0
    else:
        terminal = "NO_REGISTERED_STRUCTURAL_ENRICHMENT__BPRIME_MIXING_SURVIVES_ALL"
        exit_code = 1

    result = {
        "schema": SCHEMA_ID,
        "study": "VM6_STRUCTURAL_ENRICHMENT",
        "base_revision": BASE_REVISION,
        "protocol_sha256": protocol_sha,
        "receipt_sha256": RECEIPT_SHA256,
        "machinery_sha256": MACHINERY_SHA256,
        "machinery": "run_per_panel_v4.py (imported unmodified)",
        "smoke_mode": smoke,
        "terminal": terminal,
        "exact_vocabularies": exact_vocabs,
        "vocabularies": vocab_reports,
        "worst_pair_under_C": worst_pair,
        "gates": {
            "G0_machinery_sha256": True,
            "G1_receipt_sha256": True,
            "G2_replay_counters_and_sequence": not smoke,
            "G3_binding_probes": probe_count,
            "G4_feature_welldefinedness_checks": sample_checks,
            "G5_cross_panel_key_consistency": True,
            "G6_anti_instrument_and_staging": True,
            "G7_dp_eq_xx": True,
        },
        "row_count": len(feature_rows),
        "features_table_sha256": features_digest,
        "runtime_seconds": runtime,
        "authority": (
            "Finite-population statement over the frozen V4 census (13,458 "
            "instances, 10 registered panels, unit-cost R6M grammar at the "
            "frozen config). Not an all-n statement; no promotion of any "
            "strategy or deployment; nothing about physical implementations."
        ),
        "novelty_authority": False,
        "physical_quantum_advantage_claim": False,
    }
    if smoke:
        result["terminal"] = "SMOKE_MECHANICS_ONLY__NO_TERMINAL"
        exit_code = 0
    result["result_digest"] = hashlib.sha256(
        canonical_json(result).encode()
    ).hexdigest()
    print("VM6_RESULT=" + canonical_json(result), flush=True)
    print(
        f"VM6_RUNTIME_SECONDS={runtime} terminal={result['terminal']} "
        f"digest={result['result_digest']}",
        flush=True,
    )
    return exit_code


def _witness(fr: dict) -> dict:
    return {
        "panel": fr["panel"],
        "local_index": fr["local_index"],
        "canonical_key": [list(col) for col in fr["key"][1:]],
        "n": fr["key"][0],
        "features": {
            k: (list(v) if isinstance(v, tuple) else v)
            for k, v in fr["features"].items()
        },
        "receipt": fr["receipt"],
    }


if __name__ == "__main__":
    sys.exit(main())
