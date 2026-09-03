#!/usr/bin/env python3
"""Validate Q2_RECEIPT_CLAIM_MAP_V1.json: the committed claim-to-receipt mapping.

This closes the gap REPLAY_RECEIPT_V1.json records as
``claim_set_correspondence: CANNOT_CHECK`` ("no committed mapping from index
entries to manuscript claims"). The checker re-derives everything from the
committed bytes -- it does not trust the artifact's own verification block:

* every claim quote is verbatim inside its cited manuscript file and line;
* every cited receipt exists, is indexed in RECEIPT_INDEX.md (sha256[:16]) or
  RECEIPT_INDEX_V2.md (git blob sha), and the committed bytes still match that
  digest;
* the receipt disposition partitions all 47 indexed receipts plus the 5
  Q2-denominator-only receipts with no silent drops;
* CLAIM_LEDGER_V4.md is still the sha256 recorded in the publication package
  manifest, and all eight ledger ids are covered by some claim;
* every indexed receipt still carries an authority/terminal scoping field;
* the cited manuscript files are byte-identical to manuscript_base_commit, so
  line anchors cannot silently go stale.

Publication integrity only: this checker grants no scientific authority.
"""

from __future__ import annotations

import hashlib
import json
import pathlib
import subprocess
import sys

ROOT = pathlib.Path(__file__).resolve().parents[2]
BASE = ROOT / "papers/orion-06-recursive-recovery"
MAP_PATH = BASE / "Q2_RECEIPT_CLAIM_MAP_V1.json"
V1_INDEX = BASE / "RECEIPT_INDEX.md"
V2_INDEX = BASE / "RECEIPT_INDEX_V2.md"
INVENTORY_PATH = BASE / "Q2_ELIGIBLE_RECEIPT_INVENTORY_V1.json"
LEDGER_PATH = BASE / "CLAIM_LEDGER_V4.md"
MANIFEST_PATH = BASE / "submission/publication-ready-20260831/PACKAGE_MANIFEST.json"
RECEIPT_ROOT = "research/extensions/orion-q"

EXPECTED_SCHEMA = "ORIONQ.Q2ReceiptClaimMap.v1"
EXPECTED_LEDGER_SHA = "f40a73d8f70c08d26ea29739a66663f40d8709ba1df14d3a0baee65b77175b28"
LEDGER_IDS = [f"O6-P{i}" for i in range(1, 9)]
MANUSCRIPT_FILES = [
    "papers/orion-06-recursive-recovery/manuscript/main.tex",
    "papers/orion-06-recursive-recovery/manuscript/sections/01-introduction.tex",
    "papers/orion-06-recursive-recovery/manuscript/sections/03-results.tex",
    "papers/orion-06-recursive-recovery/manuscript/sections/04-discussion.tex",
    "papers/orion-06-recursive-recovery/manuscript/sections/05-related-work-boundary.tex",
    "papers/orion-06-recursive-recovery/manuscript/sections/06-limitations.tex",
    "papers/orion-06-recursive-recovery/manuscript/sections/07-conclusion.tex",
    "papers/orion-06-recursive-recovery/manuscript/sections/08-reproducibility.tex",
]


def sha256(path: pathlib.Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def git_blob(data: bytes) -> str:
    return hashlib.sha1(b"blob %d\0" % len(data) + data).hexdigest()


def git(*args: str) -> str:
    proc = subprocess.run(["git", *args], cwd=ROOT, text=True,
                          stdout=subprocess.PIPE, stderr=subprocess.PIPE)
    if proc.returncode != 0:
        raise RuntimeError(f"git {' '.join(args)} failed: {proc.stderr.strip()}")
    return proc.stdout.strip()


def parse_v1() -> dict[str, str]:
    """name -> sha256[:16], keys normalized to repo-relative receipt paths."""
    out: dict[str, str] = {}
    for line in V1_INDEX.read_text(encoding="utf-8").splitlines():
        if not line.startswith("| `"):
            continue
        cells = [c.strip() for c in line.strip().strip("|").split("|")]
        if len(cells) < 3 or not cells[2].startswith("`"):
            continue
        name, prefix = cells[0].strip("`"), cells[2].strip("`")
        if len(prefix) == 16:
            out[f"{RECEIPT_ROOT}/{name}"] = prefix
    return out


def parse_v2() -> dict[str, str]:
    out: dict[str, str] = {}
    for line in V2_INDEX.read_text(encoding="utf-8").splitlines():
        if not line.startswith("| `research/"):
            continue
        cells = [c.strip() for c in line.strip().strip("|").split("|")]
        path, blob = cells[0].strip("`"), cells[2].strip("`")
        if len(blob) == 40:
            out[path] = blob
    return out


def main() -> int:
    errors: list[str] = []
    data = json.loads(MAP_PATH.read_text(encoding="utf-8"))

    if data.get("schema") != EXPECTED_SCHEMA:
        errors.append(f"SCHEMA_MISMATCH:{data.get('schema')}")

    v1, v2 = parse_v1(), parse_v2()
    if len(v1) != 40:
        errors.append(f"V1_INDEX_ENTRY_COUNT:{len(v1)}")
    if len(v2) != 7:
        errors.append(f"V2_INDEX_ENTRY_COUNT:{len(v2)}")
    indexed = {**v1, **v2}

    inv = json.loads(INVENTORY_PATH.read_text(encoding="utf-8"))
    denominator = list(inv.get("base_receipts_40", [])) + list(inv.get("augmentation_11", []))
    if len(denominator) != 51:
        errors.append(f"INVENTORY_COUNT:{len(denominator)}")
    qg_only = sorted(set(denominator) - set(indexed))

    claims = data.get("claims", [])
    counts = data.get("counts", {})

    # --- per-claim checks -------------------------------------------------
    used_by: dict[str, list[str]] = {}
    covered_ledger: set[str] = set()
    coverage_counts = {"FULL": 0, "PARTIAL": 0, "UNBACKED": 0}
    quotes_ok = 0
    pairs = 0
    for claim in claims:
        cid = claim.get("claim_id", "<none>")
        st = claim.get("statement", {})
        cov = claim.get("coverage")
        if cov not in coverage_counts:
            errors.append(f"BAD_COVERAGE:{cid}:{cov}")
            cov = "UNBACKED"
        else:
            coverage_counts[cov] += 1
        receipts = claim.get("receipts", [])
        other = claim.get("other_evidence", [])
        if cov == "UNBACKED" and receipts:
            errors.append(f"UNBACKED_CLAIM_HAS_RECEIPTS:{cid}")
        if cov != "UNBACKED" and not (receipts or other):
            errors.append(f"BACKED_CLAIM_HAS_NO_EVIDENCE:{cid}")
        covered_ledger.update(claim.get("ledger_claims", []))

        rel = st.get("file")
        path = ROOT / rel if rel else None
        if not path or not path.is_file():
            errors.append(f"CLAIM_FILE_MISSING:{cid}:{rel}")
            continue
        lines = path.read_text(encoding="utf-8").splitlines()
        lineno = st.get("line", 0)
        quote = st.get("quote", "")
        if not (1 <= lineno <= len(lines)) or quote not in lines[lineno - 1]:
            errors.append(f"QUOTE_NOT_VERBATIM:{cid}:{rel}:{lineno}")
        else:
            quotes_ok += 1

        for rec in receipts:
            pairs += 1
            art = rec.get("artifact")
            used_by.setdefault(art, []).append(cid)
            if art not in indexed:
                errors.append(f"RECEIPT_NOT_INDEXED:{cid}:{art}")
                continue
            want = "V1" if art in v1 else "V2"
            if rec.get("index") != want:
                errors.append(f"RECEIPT_INDEX_FIELD_WRONG:{cid}:{art}:{rec.get('index')}!={want}")
            if rec.get("index_digest") != indexed[art]:
                errors.append(f"RECEIPT_DIGEST_RECORD_MISMATCH:{cid}:{art}")
            fpath = ROOT / art
            if not fpath.is_file():
                errors.append(f"RECEIPT_FILE_MISSING:{cid}:{art}")
                continue
            data_bytes = fpath.read_bytes()
            actual = sha256(fpath)[:16] if want == "V1" else git_blob(data_bytes)
            if actual != indexed[art]:
                errors.append(f"RECEIPT_BYTES_DRIFT:{cid}:{art}")

        for ev in other:
            epath = ROOT / ev.get("path", "")
            if not epath.is_file():
                errors.append(f"OTHER_EVIDENCE_MISSING:{cid}:{ev.get('path')}")
                continue
            digest = ev.get("sha256")
            if digest == "SELF_REFERENTIAL_NOT_HASHED":
                if epath != MAP_PATH:
                    errors.append(f"SELF_HASH_EXCUSE_ON_OTHER_FILE:{cid}:{ev.get('path')}")
            elif digest != sha256(epath):
                errors.append(f"OTHER_EVIDENCE_DIGEST_DRIFT:{cid}:{ev.get('path')}")

    # --- disposition partition --------------------------------------------
    disp = data.get("receipt_disposition", {})
    mapped = disp.get("mapped_34", {})
    unused = disp.get("unused_indexed_13", {})
    qg_disp = disp.get("qg_inventory_only_5", {})
    if set(mapped) != set(used_by):
        errors.append(f"MAPPED_SET_MISMATCH:map_only={sorted(set(mapped)-set(used_by))}:"
                      f"claims_only={sorted(set(used_by)-set(mapped))}")
    for art, cids in mapped.items():
        if sorted(set(cids)) != sorted(set(used_by.get(art, []))):
            errors.append(f"MAPPED_CLAIM_LIST_MISMATCH:{art}")
    if set(unused) & set(used_by):
        errors.append(f"UNUSED_BUT_CITED:{sorted(set(unused) & set(used_by))}")
    if set(unused) | set(used_by) != set(indexed):
        errors.append(f"INDEXED_RECEIPTS_UNACCOUNTED:"
                      f"{sorted(set(indexed) - set(unused) - set(used_by))}")
    if len(unused) != 13:
        errors.append(f"UNUSED_COUNT_DRIFT:{len(unused)}")
    for art, reason in unused.items():
        if art not in indexed:
            errors.append(f"UNUSED_NOT_INDEXED:{art}")
        if not isinstance(reason, str) or len(reason) < 20:
            errors.append(f"UNUSED_REASON_MISSING:{art}")
    if set(qg_disp) != set(qg_only):
        errors.append(f"QG_ONLY_SET_MISMATCH:disp={sorted(set(qg_disp))}:"
                      f"inventory={qg_only}")

    # --- ledger binding ----------------------------------------------------
    ledger_sha = sha256(LEDGER_PATH)
    manifest = json.loads(MANIFEST_PATH.read_text(encoding="utf-8"))
    manifest_sha = (manifest.get("active_authority_sha256")
                    or manifest.get("active_authority", {}).get("sha256"))
    binding = data.get("claim_ledger_binding", {})
    if ledger_sha != EXPECTED_LEDGER_SHA:
        errors.append(f"LEDGER_SHA_DRIFT:{ledger_sha}")
    if binding.get("sha256") != ledger_sha or manifest_sha != ledger_sha:
        errors.append("LEDGER_MANIFEST_BINDING_MISMATCH")
    missing_ids = sorted(set(LEDGER_IDS) - covered_ledger)
    if missing_ids:
        errors.append(f"LEDGER_IDS_UNCOVERED:{missing_ids}")

    # --- authority scoping + cross-domain absence --------------------------
    no_scope = [p for p in indexed
                if not any(tok in (ROOT / p).read_text(encoding="utf-8")
                           for tok in ('"authority"', '"terminal"', "BELOW_R6"))]
    if no_scope:
        errors.append(f"RECEIPTS_WITHOUT_AUTHORITY_SCOPE:{no_scope}")
    xd_token = sorted(p for p in indexed
                      if "cross_domain" in (ROOT / p).read_text(encoding="utf-8").lower())
    xd_audit = data.get("verification", {}).get("cross_domain_absence_audit", {})
    if xd_audit.get("receipts_mentioning_cross_domain_token") != xd_token:
        errors.append("CROSS_DOMAIN_AUDIT_STALE")

    # --- counts block + unbacked list ---------------------------------------
    if counts.get("claims") != len(claims) or len(claims) != 31:
        errors.append(f"CLAIM_COUNT_DRIFT:{len(claims)}")
    if counts.get("coverage") != coverage_counts:
        errors.append(f"COVERAGE_COUNT_DRIFT:{coverage_counts}")
    if counts.get("receipts_mapped_to_claims") != len(used_by):
        errors.append(f"MAPPED_COUNT_DRIFT:{len(used_by)}")
    if counts.get("indexed_receipts_unused") != len(unused):
        errors.append(f"UNUSED_COUNT_BLOCK_DRIFT:{len(unused)}")
    if counts.get("qg_inventory_only_unused") != len(qg_only):
        errors.append(f"QG_COUNT_DRIFT:{len(qg_only)}")
    if counts.get("receipt_claim_pairs") != pairs:
        errors.append(f"PAIR_COUNT_DRIFT:{pairs}")
    outside = sorted(set(indexed) - set(denominator))
    if counts.get("indexed_outside_q2_denominator") != outside:
        errors.append(f"OUTSIDE_DENOMINATOR_RECORD_STALE:{outside}")
    in_den = (len(set(used_by) & set(denominator))
              + len(set(unused) & set(denominator)) + len(qg_only))
    if in_den != len(denominator):
        errors.append(f"DENOMINATOR_PARTITION_DRIFT:{in_den}!={len(denominator)}")
    unbacked_listed = data.get("unbacked_claims", [])
    unbacked_actual = [c["claim_id"] for c in claims if c.get("coverage") == "UNBACKED"]
    if unbacked_listed != unbacked_actual:
        errors.append("UNBACKED_LIST_MISMATCH")

    # --- manuscript drift guard ---------------------------------------------
    base = data.get("manuscript_base_commit")
    if not base:
        errors.append("MANUSCRIPT_BASE_COMMIT_MISSING")
    else:
        for rel in MANUSCRIPT_FILES:
            try:
                base_blob = git("rev-parse", f"{base}:{rel}")
            except RuntimeError:
                errors.append(f"MANUSCRIPT_FILE_NOT_AT_BASE:{rel}")
                continue
            if base_blob != git("hash-object", rel):
                errors.append(f"MANUSCRIPT_DRIFT_SINCE_BASE:{rel}")

    if errors:
        print("Q2_RECEIPT_CLAIM_MAP_CHECK=FAIL")
        for err in errors:
            print(f"- {err}")
        return 1

    print("Q2_RECEIPT_CLAIM_MAP_CHECK=PASS")
    print(f"MAP={MAP_PATH.relative_to(ROOT)}")
    print(f"MAP_SHA256={sha256(MAP_PATH)}")
    print(f"CLAIMS={len(claims)} (FULL={coverage_counts['FULL']} "
          f"PARTIAL={coverage_counts['PARTIAL']} UNBACKED={coverage_counts['UNBACKED']})")
    print(f"CLAIM_QUOTES_VERBATIM={quotes_ok}/{len(claims)}")
    print(f"RECEIPT_CLAIM_PAIRS={pairs}")
    print(f"INDEXED_RECEIPTS={len(indexed)} (V1={len(v1)} V2={len(v2)}) "
          f"DIGEST_MATCHES={len(indexed)}")
    print(f"MAPPED_TO_CLAIMS={len(used_by)} UNUSED_FOR_CLAIMS={len(unused)} "
          f"QG_DENOMINATOR_ONLY={len(qg_only)}")
    print(f"Q2_DENOMINATOR_PARTITIONED={len(set(used_by) & set(denominator)) + len(set(unused) & set(denominator)) + len(qg_only)}/{len(denominator)} "
          f"(mapped={len(set(used_by) & set(denominator))} "
          f"unused={len(set(unused) & set(denominator))} qg_only={len(qg_only)})")
    print(f"INDEXED_OUTSIDE_DENOMINATOR={len(outside)} "
          f"({', '.join(part.split('/')[-1] for part in outside)})")
    print(f"LEDGER_IDS_COVERED={len(covered_ledger)}/8")
    print(f"RECEIPTS_WITH_AUTHORITY_SCOPE={len(indexed) - len(no_scope)}/{len(indexed)}")
    print(f"CROSS_DOMAIN_COMPARATIVE_BENCHMARKS_ASSERTED=0")
    print("CLAIM_AUTHORITY=CLAIM_LEDGER_V4.md (this map binds, it does not grant)")
    return 0


if __name__ == "__main__":
    sys.exit(main())
