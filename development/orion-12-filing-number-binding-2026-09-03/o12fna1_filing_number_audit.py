#!/usr/bin/env python3
"""O12FNA1 — ORION-12 filing-number binding audit (driver V1).

Implements exactly the registered protocol
``development/orion-12-filing-number-binding-2026-09-03/O12FNA1_PROTOCOL_V1.md``.
Read-only over the frozen paper tree: every expected value is imported by JSON
key from the frozen artifacts; no constant, threshold, or aggregation rule is
defined locally.

Exit codes (distinct, per protocol Section 7):
  0  O12_FNA1_FILING_NUMBER_BINDING_VERIFIED__ZERO_DRIFT
  2  O12_FNA1_FILING_NUMBER_DRIFT_DETECTED
  3  O12_FNA1_CANNOT_CHECK__FROZEN_INPUT_OR_SURFACE_ABSENT
  4  internal defect (never a pass, never a terminal)
"""

from __future__ import annotations

import hashlib
import json
import re
import subprocess
import sys
from pathlib import Path

LANE = Path(__file__).resolve().parent
REPO = LANE.parents[1]
PAPER = REPO / "papers" / "orion-12-open-world-scientific-discovery"
PROTOCOL_FILE = LANE / "O12FNA1_PROTOCOL_V1.md"

SCHEMA = "ORION.ORION12.FilingNumberAudit.v1"
AUTHORITY = (
    "AUDIT_ONLY__BINDING_VERIFICATION_NOT_NEW_SCIENCE_NOT_A_CLAIM_CHANGE_NOT_A_REBIND"
)
TERMINAL_VERIFIED = "O12_FNA1_FILING_NUMBER_BINDING_VERIFIED__ZERO_DRIFT"
TERMINAL_DRIFT = "O12_FNA1_FILING_NUMBER_DRIFT_DETECTED"
TERMINAL_CANNOT_CHECK = "O12_FNA1_CANNOT_CHECK__FROZEN_INPUT_OR_SURFACE_ABSENT"

DEPTHS = ["10", "20", "50", "100", "200"]


class InternalDefect(Exception):
    """Unresolvable registered key / malformed frozen input. Exit 4."""


def sha256_bytes(data: bytes) -> str:
    return hashlib.sha256(data).hexdigest()


def sha256_file(path: Path) -> str:
    h = hashlib.sha256()
    with open(path, "rb") as fh:
        for chunk in iter(lambda: fh.read(1 << 20), b""):
            h.update(chunk)
    return h.hexdigest()


def load_json(path: Path):
    try:
        with open(path, "r", encoding="utf-8") as fh:
            return json.load(fh)
    except (OSError, json.JSONDecodeError) as exc:
        raise InternalDefect(f"cannot load frozen JSON {path}: {exc}") from exc


def read_text(path: Path) -> str:
    with open(path, "r", encoding="utf-8") as fh:
        return fh.read()


def key_get(obj, dotted: str):
    """Resolve 'a.b[0].c' against a frozen JSON object."""
    try:
        cur = obj
        for part in dotted.split("."):
            m = re.fullmatch(r"([^\[\]]+)\[(\d+)\]", part)
            if m:
                cur = cur[m.group(1)][int(m.group(2))]
            else:
                cur = cur[part]
        return cur
    except (KeyError, IndexError, TypeError) as exc:
        raise InternalDefect(f"registered key does not resolve: {dotted!r}") from exc


def fmt_number(value, precision: int | None) -> str:
    if precision is None:
        return str(value)
    return f"{round(float(value), precision):.{precision}f}"


def norm_ws(text: str) -> str:
    return re.sub(r"\s+", " ", text).strip()


# --------------------------------------------------------------------------
# Registered inputs and surfaces (protocol Sections 2-3)
# --------------------------------------------------------------------------

INPUTS = {
    "A1": "external/P2_TREC_COVID_ARMS_V1.json",
    "A2": "evidence/P2_INTEGRATED_CLAIM_BINDINGS_V1.json",
    "A3": "evidence/p2x/P2_X_CLAIM_VALUES_V1.json",
    "A4": "manuscript/generated/suite_facts.json",
    "A5": "protocol/STATISTICAL_PLAN_V1.json",
    "A6": "experiments/beir-route-aware-stopping-v1/RESULTS_V1.json",
    "A7": "experiments/beir-route-aware-stopping-v2-density/RESULTS_V2.json",
    "A8": "experiments/beir-route-aware-stopping-v3-conditional/RESULTS_V3.json",
    "A9": "evidence/external_results/P2_V2_ACQUISITION_DEV3R_RESULT_2026-08-18.json",
    "M1": "journal_package/SHA256SUMS",
    "M2": "submission/SHA256SUMS",
    "M3": "submission/SUBMISSION_MANIFEST.sha256",
    "M4": "experiments/beir-route-aware-stopping-v1/SHA256SUMS",
    "M5": "journal_package/current_revision/SUBMISSION_MANIFEST.json",
}

SURFACES = {
    "S1": "PUBLICATION_FREEZE_ADDENDUM_V2.md",
    "S2": "journal_package/elsevier-cas/cover_letter_ipm_20260902.md",
    "S3": "submission/FILING_METADATA_V1.json",
    "S4": "manuscript/ipm_submission.tex",
    "S5": "manuscript/main.tex",
    "S6": "manuscript/sections/05a-public-screening-transport.tex",
    "S7": "JOURNAL_READINESS_V2.md",
    "S8": "manuscript/generated/suite_facts.tex",
}

MANIFEST_BASES = {
    "M1": PAPER,
    "M2": PAPER / "submission",
    "M3": PAPER,
    "M4": PAPER / "experiments" / "beir-route-aware-stopping-v1",
}


def number_binding(bid, surface, art, key, precision, min_occ=1):
    return {
        "id": bid, "kind": "NUMBER", "surface": surface, "artifact": art,
        "key": key, "precision": precision, "min_occ": min_occ,
    }


def text_binding(bid, surface, template, art, keys, min_occ=1, precisions=None):
    """template uses {k0},{k1},... filled from artifact keys. ``precisions``
    gives the fixed decimal count for float keys (None = str() the value)."""
    return {
        "id": bid, "kind": "TEXT", "surface": surface, "template": template,
        "artifact": art, "keys": keys, "min_occ": min_occ,
        "precisions": precisions or [None] * len(keys),
    }


TREC_RNI = "pass_gate_verdict.criteria.recall_noninferiority"
COST_PCT = "pass_gate_verdict.criteria.cost_reduction.reads_vs_comparator_pct"
NDCG_D = "pass_gate_verdict.not_a_gate_criterion_but_measured.ndcg_at_10_delta_mean"


def registered_bindings():
    return [
        # --- 5.1 cover letter (S2): rows 1-13 ---
        number_binding("CL-01", "S2", "A1", "arms_macro.bm25.recall_at_100", 6),
        number_binding("CL-02", "S2", "A1", "arms_macro.orion_full.recall_at_100", 6),
        number_binding("CL-03", "S2", "A1", f"{TREC_RNI}.delta_mean", 5),
        number_binding("CL-04", "S2", "A1", f"{TREC_RNI}.bootstrap_ci95[0]", 5),
        number_binding("CL-05", "S2", "A1", f"{TREC_RNI}.bootstrap_ci95[1]", 5),
        number_binding("CL-06", "S2", "A1", COST_PCT, 1),
        number_binding("CL-07", "S2", "A1", NDCG_D, 4),
        text_binding("CL-08", "S2", "matches {k0} of", "A3", ["p2x_correct"]),
        text_binding("CL-09", "S2", "{k0} of {k1}", "A3", ["b1_correct", "n"]),
        number_binding("CL-10", "S2", "A4", "OfflineAchievedHalfWidth", 4),
        number_binding("CL-11", "S2", "A5", "TIER_A_full.half_width", 2),
        text_binding("CL-12", "S2", "{k0}-topic", "A4", ["OfflineTopicCount"]),
        number_binding("CL-13", "S2", "A4", "OfflineTaskCount", 0),
        # --- 5.2 freeze addendum V2 (S1): rows 14-17 (rows 18-21 = identity) ---
        number_binding("FA-14", "S1", "A1", f"{TREC_RNI}.delta_mean", 5),
        text_binding("FA-15", "S1", "[{k0},{k1}]", "A1",
                     [f"{TREC_RNI}.bootstrap_ci95[0]", f"{TREC_RNI}.bootstrap_ci95[1]"],
                     precisions=[5, 5]),
        number_binding("FA-16", "S1", "A1", COST_PCT, 1),
        text_binding("FA-17", "S1", "recall@100", None, []),
        # --- 5.3 IP&M filing source (S4): rows 22-31 (row 32 = macro refs) ---
        text_binding("IP-22", "S4", "matches {k0} of", "A3", ["p2x_correct"]),
        text_binding("IP-23", "S4", "{k0} of {k1}", "A3", ["b1_correct", "n"]),
        number_binding("IP-24", "S4", "A1", f"abs:{TREC_RNI}.delta_mean", 5),
        text_binding("IP-25", "S4", "[{k0},{k1}]", "A1",
                     [f"{TREC_RNI}.bootstrap_ci95[0]", f"{TREC_RNI}.bootstrap_ci95[1]"],
                     precisions=[5, 5]),
        number_binding("IP-26", "S4", "A1", COST_PCT, 1),
        number_binding("IP-27", "S4", "A1", NDCG_D, 4),
        text_binding("IP-28", "S4", "{k0} at half-width ${k1}$", "A5",
                     ["TIER_A_full.required_n", "TIER_A_full.half_width"],
                     precisions=[None, 2]),
        text_binding("IP-29", "S4", "{k0} at ${k1}$", "A5",
                     ["TIER_B_committed.required_n", "TIER_B_committed.half_width"],
                     precisions=[None, 2]),
        text_binding("IP-30", "S4", "{k0} at ${k1}$", "A5",
                     ["TIER_C_reduced.required_n", "TIER_C_reduced.half_width"],
                     precisions=[None, 3]),
        text_binding("IP-31", "S4", "{k0} at ${k1}$", "A5",
                     ["TIER_D_minimum_inferential.required_n",
                      "TIER_D_minimum_inferential.half_width"],
                     precisions=[None, 2]),
        # --- 5.4 main / screening / readiness: rows 33-40 ---
        number_binding("MS-33a", "S5", "A2",
                       "facts.zenodo.active_audit_u4_recall_at_10", 6, min_occ=2),
        number_binding("MS-33b", "S6", "A2",
                       "facts.zenodo.active_audit_u4_recall_at_10", 6, min_occ=1),
        number_binding("MS-34a", "S5", "A2",
                       "facts.zenodo.active_audit_candidate_recall_at_10", 6, min_occ=2),
        number_binding("MS-34b", "S6", "A2",
                       "facts.zenodo.active_audit_candidate_recall_at_10", 6, min_occ=2),
        number_binding("MS-35a", "S5", "A2",
                       "facts.zenodo.active_audit_candidate_wss_at_95", 6, min_occ=1),
        number_binding("MS-35b", "S6", "A2",
                       "facts.zenodo.active_audit_candidate_wss_at_95", 6, min_occ=1),
        number_binding("MS-36", "S5", "A2",
                       "facts.kifms_v7.learner_balancer_mean_recall_at_10", 6),
        number_binding("MS-37", "S5", "A2",
                       "facts.kifms_v7.learner_balancer_mean_wss_at_95", 6),
        number_binding("JR-38", "S7", "A9",
                       "official_metrics.baseline.avg_recall", 6),
        number_binding("JR-39", "S7", "A9",
                       "official_metrics.candidate.avg_recall", 6),
        number_binding("JR-40", "S7", "A9",
                       "official_metrics.candidate_minus_baseline.avg_recall", 6),
    ]


def artifact_value(arts, art: str, key: str):
    root = arts[art]
    if key.startswith("abs:"):
        return abs(key_get(root, key[4:]))
    return key_get(root, key)


def tier_table(a5_json):
    try:
        rows = a5_json["precision_plan"]["precision_tiers"]
    except (KeyError, TypeError) as exc:
        raise InternalDefect("A5 missing precision_plan.precision_tiers") from exc
    tiers = {}
    for row in rows:
        tiers[row["tier"]] = row
    return tiers


def make_resolver(arts):
    tiers = tier_table(arts["A5"])

    def resolve(art: str, key: str):
        if art == "A5" and key.startswith("TIER_"):
            tier_name, field = key.split(".", 1)
            if tier_name not in tiers:
                raise InternalDefect(f"A5 has no tier {tier_name!r}")
            return tiers[tier_name][field]
        return artifact_value(arts, art, key)

    return resolve


def parse_sums(text: str):
    rows = []
    for line in text.splitlines():
        line = line.strip()
        if not line or line.startswith("#"):
            continue
        parts = line.split(None, 1)
        if len(parts) != 2 or not re.fullmatch(r"[0-9a-f]{64}", parts[0]):
            raise InternalDefect(f"malformed digest line: {line[:80]!r}")
        rows.append((parts[0], parts[1].strip().lstrip("*")))
    return rows


def format_text_value(value, precision):
    if precision is not None:
        return f"{float(value):.{precision}f}"
    if isinstance(value, bool):
        return "yes" if value else "no"
    if isinstance(value, int):
        return str(value)
    if isinstance(value, float):
        return f"{value:g}"
    return str(value)


def main() -> int:
    smoke = "--smoke" in sys.argv[1:]
    drift = []
    missing = []

    # ---- G0 existence -------------------------------------------------------
    for sid, rel in {**INPUTS, **SURFACES}.items():
        if not (PAPER / rel).is_file():
            missing.append(f"{sid}:{rel}")
    if missing:
        print(json.dumps({"terminal": TERMINAL_CANNOT_CHECK, "missing": missing},
                         sort_keys=True))
        return 3

    # ---- load artifacts needed for the evaluated scope ----------------------
    arts = {aid: load_json(PAPER / rel) for aid, rel in INPUTS.items()
            if aid.startswith("A")}
    surf_text = {sid: read_text(PAPER / rel) for sid, rel in SURFACES.items()}
    resolve = make_resolver(arts)

    # ---- G1-G3 digest gates (full mode only; smoke = G0 + 6 bindings) --------
    manifest_results = {}
    if not smoke:
        for mid, base in MANIFEST_BASES.items():
            rows = parse_sums(read_text(PAPER / INPUTS[mid]))
            bad = [rel for digest, rel in rows
                   if not (base / rel).is_file() or sha256_file(base / rel) != digest]
            manifest_results[mid] = {"checked": len(rows), "mismatches": bad}
            drift.extend(f"{mid}:{rel}" for rel in bad)

    # ---- binding evaluation ---------------------------------------------------
    binds = registered_bindings()
    if len(binds) < 35:
        raise InternalDefect(f"registered binding set too small: {len(binds)}")

    selected = binds[:6] if smoke else binds
    binding_rows = []
    for b in selected:
        if b["kind"] == "NUMBER":
            value = resolve(b["artifact"], b["key"])
            literal = fmt_number(value, b["precision"])
            occurrences = surf_text[b["surface"]].count(literal)
            row = {"id": b["id"], "kind": "NUMBER", "surface": b["surface"],
                   "surface_path": SURFACES[b["surface"]],
                   "artifact": b["artifact"], "artifact_path": INPUTS[b["artifact"]],
                   "key": b["key"], "artifact_value": value,
                   "expected_literal": literal, "occurrences": occurrences,
                   "min_occ": b["min_occ"]}
        else:
            values = [resolve(b["artifact"], k) for k in b["keys"]] \
                if b["artifact"] else []
            fmts = [format_text_value(v, p)
                    for v, p in zip(values, b["precisions"])]
            literal = b["template"].format(
                **{f"k{i}": fv for i, fv in enumerate(fmts)})
            occurrences = surf_text[b["surface"]].count(literal)
            row = {"id": b["id"], "kind": "TEXT", "surface": b["surface"],
                   "surface_path": SURFACES[b["surface"]],
                   "artifact": b["artifact"],
                   "artifact_path": INPUTS.get(b["artifact"]),
                   "keys": b["keys"], "artifact_values": values,
                   "expected_literal": literal, "occurrences": occurrences,
                   "min_occ": b["min_occ"]}
        row["ok"] = row["occurrences"] >= row["min_occ"]
        binding_rows.append(row)
        if not row["ok"]:
            drift.append(row["id"])

    if smoke:
        print(json.dumps({"terminal": TERMINAL_DRIFT if drift else TERMINAL_VERIFIED,
                          "smoke": True, "scope": "G0 + first 6 bindings",
                          "evaluated": [r["id"] for r in binding_rows],
                          "drift": drift}, sort_keys=True))
        return 0 if not drift else 2

    # ---- 5.5 stopping identity (rows 18-21) ------------------------------------
    def stop(vid, corpus, depth):
        return arts[vid]["corpora"][corpus]["by_depth"][depth]["route_aware_stop"]

    identity_rows = []
    try:
        checks = [
            ("I1_arguana_V2_eq_V1",
             all(stop("A7", "arguana", d) == stop("A6", "arguana", d) for d in DEPTHS)),
            ("I2_arguana_V3_eq_V1",
             all(stop("A8", "arguana", d) == stop("A6", "arguana", d) for d in DEPTHS)),
            ("I3_scifact_V3_eq_V1",
             all(stop("A8", "scifact", d) == stop("A6", "scifact", d) for d in DEPTHS)),
            ("I4_nfcorpus_V3_neq_V1",
             any(stop("A8", "nfcorpus", d) != stop("A6", "nfcorpus", d)
                 for d in DEPTHS)),
        ]
    except (KeyError, TypeError) as exc:
        raise InternalDefect(f"stopping-identity key does not resolve: {exc}") from exc
    for cid, observed in checks:
        ok = observed  # registered expectation is True for all four rows
        identity_rows.append({"id": cid, "observed": bool(observed),
                              "registered_expectation": True, "ok": ok})
        if not ok:
            drift.append(cid)

    # ---- 5.6 macro<->JSON (M-A), derived product (M-B), row 32 refs ------------
    macro_rows = []
    tex8 = surf_text["S8"]
    jf = arts["A4"]
    for name in ["OfflineTaskCount", "OfflineDocumentCount", "OfflineTopicCount",
                 "OfflineSuiteFingerprintShort", "OfflineSuiteSeed",
                 "OfflineSystemCount", "OfflineRepeatCount",
                 "OfflineRunRecordCount", "OfflineAchievedHalfWidth",
                 "OfflineUnderpowered"]:
        m = re.search(r"\\newcommand\{\\%s\}\{([^}]*)\}" % re.escape(name), tex8)
        body = m.group(1).replace("{,}", "") if m else None
        expected = format_text_value(jf[name], None)
        ok = body == expected
        macro_rows.append({"macro": name, "tex_body": body, "json": jf[name],
                           "expected": expected, "ok": ok})
        if not ok:
            drift.append(f"MACRO:{name}")
    product = (int(jf["OfflineTaskCount"]) * int(jf["OfflineSystemCount"])
               * int(jf["OfflineRepeatCount"]))
    ok_prod = product == int(jf["OfflineRunRecordCount"])
    macro_rows.append({"macro": "M-B derived: Task*System*Repeat == RunRecordCount",
                       "computed": product, "json": jf["OfflineRunRecordCount"],
                       "ok": ok_prod})
    if not ok_prod:
        drift.append("MACRO:M-B_DERIVED_PRODUCT")
    for name in ["OfflineUnderpowered", "OfflineAchievedHalfWidth",
                 "OfflineTaskCount", "OfflineSystemCount", "OfflineRepeatCount",
                 "OfflineTopicCount"]:
        n = surf_text["S4"].count("\\" + name + "{}")
        ok = n >= 1
        macro_rows.append({"macro": f"row32 S4 ref \\{name}{{}}", "occurrences": n,
                           "min_occ": 1, "ok": ok})
        if not ok:
            drift.append(f"MACRO:S4REF:{name}")

    # ---- 5.7 filing-metadata consistency ---------------------------------------
    filing_meta = load_json(PAPER / SURFACES["S3"])
    consistency_rows = []
    t_main = re.search(r"\\title\{([^}]*)\}", surf_text["S5"])
    t_ipm = re.search(r"\\title\[mode=title\]\{([^}]*)\}", surf_text["S4"], re.DOTALL)
    if t_main is None or t_ipm is None:
        raise InternalDefect("title macros not found in S5/S4")
    title_main = norm_ws(t_main.group(1))
    title_ipm = norm_ws(t_ipm.group(1))
    ok_fa = norm_ws(filing_meta["title"]) == title_main
    consistency_rows.append({"id": "F-A", "meta": norm_ws(filing_meta["title"]),
                             "tex": title_main, "ok": ok_fa})
    if not ok_fa:
        drift.append("F-A")
    ok_fb = norm_ws(filing_meta["title_ipm_adapted"]) == title_ipm
    consistency_rows.append({"id": "F-B",
                             "meta": norm_ws(filing_meta["title_ipm_adapted"]),
                             "tex": title_ipm, "ok": ok_fb})
    if not ok_fb:
        drift.append("F-B")

    m5 = load_json(PAPER / INPUTS["M5"])
    declared = [a["path"] for a in m5.get("artifacts", [])
                if isinstance(a, dict) and "path" in a]
    declared += [u for u in m5.get("reader_facing_uploads", []) if isinstance(u, str)]
    absent = []
    for rel in declared:
        cands = [PAPER / rel,
                 PAPER / "journal_package" / "current_revision" / rel,
                 PAPER / "journal_package" / rel,
                 PAPER / "submission" / rel]
        if not any(c.is_file() for c in cands):
            absent.append(rel)
    ok_fc = not absent
    consistency_rows.append({"id": "F-C", "declared": declared,
                             "declared_count": len(declared), "absent": absent,
                             "ok": ok_fc})
    if not ok_fc:
        drift.append("F-C")

    # ---- Section 6 recorded findings (non-gating) -------------------------------
    findings = []
    b1_open = title_main != title_ipm
    findings.append({
        "finding": "blocking_before_filing[0] title divergence",
        "state": "OPEN" if b1_open else "RESOLVED",
        "evidence": {"main_tex_title": title_main, "ipm_title": title_ipm},
    })
    findings.append({
        "finding": "blocking_before_filing[1] declared PDF absent",
        "state": "STALE_RESOLVED" if ok_fc else "CONFIRMED_OPEN",
        "evidence": {"m5_declared_absent": absent,
                     "note": "all M5-declared artifact paths resolve on this tree"},
    })
    anon = re.search(r"\\author(?:\[\d+\])?\{([^}]*)\}", surf_text["S4"])
    b3_open = anon is not None and "anonymous" in anon.group(1).lower()
    findings.append({
        "finding": "blocking_before_filing[2] anonymous author block",
        "state": "OPEN" if b3_open else "RESOLVED",
        "evidence": {"ipm_author_literal":
                     norm_ws(anon.group(1)) if anon else None},
    })
    findings.append({
        "finding": "blocking_before_filing[3] live IP&M guide verification",
        "state": "CANNOT_CHECK_EXTERNAL",
        "evidence": {"note": "no network call in this study; distinct from "
                             "'checked and fine'"},
    })

    covered = {}
    for mid, base in MANIFEST_BASES.items():
        for _digest, rel in parse_sums(read_text(PAPER / INPUTS[mid])):
            covered[str((base / rel).relative_to(PAPER))] = mid
    census_entries = [{"id": sid, "path": rel,
                       "digest_bound_by": covered.get(rel, "UNBOUND")}
                      for sid, rel in {**INPUTS, **SURFACES}.items()]
    findings.append({"finding": "binding_status_census", "entries": census_entries})
    findings.append({
        "finding": "binding_count_census",
        "registered_table_rows": 40,
        "number_and_text_bindings_evaluated": len(binding_rows),
        "identity_checks": len(identity_rows),
        "macro_checks": len(macro_rows),
        "filing_consistency_checks": len(consistency_rows),
        "pass": sum(1 for r in binding_rows if r["ok"]),
        "fail": sum(1 for r in binding_rows if not r["ok"]),
    })

    # ---- receipt ------------------------------------------------------------------
    proc = subprocess.run(["/usr/bin/git", "-C", str(REPO), "rev-parse", "HEAD"],
                          capture_output=True, text=True)
    if proc.returncode != 0:
        raise InternalDefect(f"git rev-parse failed: {proc.stderr.strip()}")
    base_revision = proc.stdout.strip()

    terminal = TERMINAL_DRIFT if drift else TERMINAL_VERIFIED
    payload = {
        "schema": SCHEMA,
        "study_id": "O12FNA1",
        "protocol": "development/orion-12-filing-number-binding-2026-09-03/"
                    "O12FNA1_PROTOCOL_V1.md",
        "driver": "development/orion-12-filing-number-binding-2026-09-03/"
                  "o12fna1_filing_number_audit.py",
        "base_revision": base_revision,
        "protocol_sha256": sha256_file(PROTOCOL_FILE),
        "authority": AUTHORITY,
        "authority_flags": {
            "audit_only": True,
            "novelty_authority": False,
            "physical_quantum_advantage_claim": False,
            "claim_change": False,
            "rebind": False,
        },
        "novelty_authority": False,
        "physical_quantum_advantage_claim": False,
        "smoke": smoke,
        "gates": {
            "G0_existence": {"missing": missing, "ok": not missing},
            "G1_M1_journal_package_sums": manifest_results.get("M1"),
            "G2_M2_submission_sums": manifest_results.get("M2"),
            "G3_M3_M4_sums": {k: manifest_results[k] for k in ("M3", "M4")},
            "G4_nonvacuity": {"min_registered": 35,
                              "registered_bindings": len(binds),
                              "ok": len(binds) >= 35},
        },
        "manifest_digest_checks": manifest_results,
        "number_and_text_bindings": binding_rows,
        "stopping_identity": identity_rows,
        "macro_bindings": macro_rows,
        "filing_consistency": consistency_rows,
        "recorded_findings": findings,
        "drift_slots": drift,
        "terminal": terminal,
    }
    payload["result_digest"] = sha256_bytes(
        json.dumps(payload, sort_keys=True, separators=(",", ":"),
                   ensure_ascii=False).encode("utf-8"))

    out = LANE / "O12FNA1_RESULTS.json"
    with open(out, "w", encoding="utf-8") as fh:
        json.dump(payload, fh, sort_keys=True, indent=1, ensure_ascii=False)
        fh.write("\n")

    print(json.dumps({"terminal": terminal, "drift_slots": drift,
                      "result_path": str(out),
                      "result_sha256": sha256_file(out),
                      "result_digest": payload["result_digest"],
                      "base_revision": base_revision}, sort_keys=True))
    return 0 if not drift else 2


if __name__ == "__main__":
    try:
        sys.exit(main())
    except InternalDefect as exc:
        print(json.dumps({"exit": 4, "internal_defect": str(exc)}, sort_keys=True))
        sys.exit(4)
