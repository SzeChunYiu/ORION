#!/usr/bin/env python3
"""Build the ORION-14 double-blind review supplement from bound safe results.

The output is deliberately *not* a copy of the repository tree.  It exports a
small set of result objects under neutral filenames, removes explicitly
operational identity fields, fails closed on repository/development leakage,
and emits a deterministic ZIP plus checksums.

It does not export protected per-case gold, raw traces, secret seeds,
credentials, or candidate-hidden fields.
"""

from __future__ import annotations

import argparse
import hashlib
import json
import re
import shutil
import stat
import zipfile
from pathlib import Path
from typing import Any

ROOT = Path(__file__).resolve().parents[3]
PAPER = ROOT / "papers" / "orion-14-verified-scientific-discovery"
P4X = ROOT / "research" / "claim_expansion" / "p4"

SOURCES = {
    "v2_publication_metrics.json": PAPER / "evidence" / "protected_v2" / "PUBLICATION_METRICS_V2.json",
    "v2_family_contrasts.json": PAPER / "evidence" / "protected_v2" / "FAMILY_CONTRAST_V2.json",
    "v3_identifiability.json": PAPER / "evidence" / "protected_v3" / "IDENTIFIABILITY_V3.json",
    "v3_panel.json": PAPER / "evidence" / "protected_v3" / "PANEL_V3.json",
    "p4x_exact_result.json": P4X / "P4_X_PROTECTED_RESULT_V1.json",
    "p4x_independent_verification.json": P4X / "P4_X_INDEPENDENT_VERIFICATION_V1.json",
}

# These fields bind repository execution/custody history but are not needed to
# evaluate the released scientific numbers in a double-blind supplement.  The
# canonical repository retains them unchanged.
DROP_KEYS = {
    "artifact",
    "campaign_run_id",
    "subject_commit",
    "freeze_document",
    "protocol_merge",
    "outcome_access_receipt_commit",
    "verification_implementation_commit",
}

FORBIDDEN_TEXT = [
    re.compile(pattern, re.IGNORECASE)
    for pattern in (
        r"SzeChunYiu",
        r"github\.com/",
        r"api\.github\.com",
        r"GitHub Actions",
        r"workflow run",
        r"pull request",
        r"development/",
        r"papers/orion-14-verified-scientific-discovery/",
        r"/Users/",
        r"/home/",
    )
]

README = """# Anonymous review artifact

This supplement supports the bounded results reported in the accompanying
manuscript.  It contains safe aggregate result objects for the protected V2
battery, the distinct V3 identifiability/interface battery, and the P4-X exact
scientific-promotion contracts, together with a small verifier for the headline
counts.

## Evidence identities

The three empirical layers are separate experiments and must not be pooled.

- **V2**: finite protected false-promotion / clean-coverage experiment.  Its
  registered H3 comparison is saturated and remains `NOT_SUPPORTED`.
- **V3**: distinct shortcut-resistant exact-axis experiment.  Its positive H3
  result is interpreted only as terminal/interface attainability under the
  frozen gate lattice, not general scientific judgement.
- **P4-X**: 400 heterogeneous exact scientific-promotion contracts comparing a
  target-bound non-compensatory relation with donor-complete generic,
  compensatory, and information-equivalent typed products.  The typed product
  ties exactly, so no centralization or unique-expressivity claim is licensed.

## What is deliberately absent

Protected per-case gold, raw protected execution traces, secret seeds,
credentials, candidate-hidden fields, author identity, public repository URLs,
and operational history are not included.  Their absence is part of
blind review and protected-evaluation custody; it is not presented as full
external reproduction.

Run `python verify_headlines.py` from this directory to verify the headline
counts and retained boundaries from the packaged JSON objects.
"""

VERIFY = r'''#!/usr/bin/env python3
from __future__ import annotations

import json
from pathlib import Path

HERE = Path(__file__).resolve().parent
load = lambda name: json.loads((HERE / name).read_text())

v2 = load("v2_publication_metrics.json")
v3 = load("v3_panel.json")
x = load("p4x_exact_result.json")
xv = load("p4x_independent_verification.json")

assert v2["case_count"] == 420
assert v2["hypotheses"]["H1"]["status"] == "PASS"
assert v2["hypotheses"]["H2"]["status"] == "PASS"
assert v2["hypotheses"]["H3"]["status"] == "NOT_SUPPORTED"
assert v2["systems"]["ORION"]["false_promotion_rate"] == 0.0
strongest = v2["strongest_frozen_comparator"]
assert v2["systems"][strongest]["false_promotion_rate"] == 0.5
assert v2["systems"]["ORION"]["clean_coverage"] == 1.0
assert v2["systems"][strongest]["clean_coverage"] == 1.0
assert len(v2["ablations"]) == 8

assert v3["case_count"] == 420
assert v3["H3"]["status"] == "SUPPORTED"
cc = v3["cannot_check_family_summary"]
assert cc["ORION"]["correct_terminal"] == 30
assert cc["provenai-citation-fidelity-influence"]["correct_terminal"] == 0
assert cc["deepsciverify-abstract-to-full-escalation"]["correct_terminal"] == 15

assert x["case_count"] == 400
assert x["counts_correct"] == {
    "P4_X": 400,
    "B1_GENERIC_AUTHORIZATION_PRODUCT": 250,
    "B2_COMPENSATORY_PRODUCT": 50,
    "B3_IDEAL_TYPED_PRODUCT": 400,
}
assert x["p4x_minus_b1"] == 0.375
assert x["bootstrap_95_ci"] == [0.3275, 0.4225]
assert x["b3_p4x_decision_mismatches"] == 0
assert xv["imports_original_execution_module"] is False
assert xv["canonical_rows_sha256"] == x["canonical_rows_sha256"]
assert xv["counts_correct"] == x["counts_correct"]

print("ANONYMOUS_REVIEW_HEADLINES_VERIFIED")
'''


def sha256_bytes(data: bytes) -> str:
    return hashlib.sha256(data).hexdigest()


def sanitized(obj: Any) -> Any:
    if isinstance(obj, dict):
        return {k: sanitized(v) for k, v in obj.items() if k not in DROP_KEYS}
    if isinstance(obj, list):
        return [sanitized(v) for v in obj]
    return obj


def scan_text(label: str, text: str) -> None:
    for pattern in FORBIDDEN_TEXT:
        if pattern.search(text):
            raise SystemExit(f"identity/development leakage in {label}: {pattern.pattern}")


def write_text(path: Path, text: str, executable: bool = False) -> None:
    scan_text(path.name, text)
    path.write_text(text, encoding="utf-8", newline="\n")
    if executable:
        path.chmod(path.stat().st_mode | stat.S_IXUSR)


def deterministic_zip(source_dir: Path, zip_path: Path) -> None:
    with zipfile.ZipFile(zip_path, "w", compression=zipfile.ZIP_DEFLATED, compresslevel=9) as zf:
        for path in sorted(p for p in source_dir.rglob("*") if p.is_file()):
            rel = path.relative_to(source_dir).as_posix()
            info = zipfile.ZipInfo(rel, date_time=(1980, 1, 1, 0, 0, 0))
            info.compress_type = zipfile.ZIP_DEFLATED
            info.external_attr = (0o644 & 0xFFFF) << 16
            zf.writestr(info, path.read_bytes(), compress_type=zipfile.ZIP_DEFLATED, compresslevel=9)


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--out-dir", type=Path, default=PAPER / "submission" / "_build")
    args = parser.parse_args()

    out = args.out_dir.resolve()
    bundle = out / "anonymous_review"
    zip_path = out / "orion14_anonymous_review.zip"
    if out.exists():
        shutil.rmtree(out)
    bundle.mkdir(parents=True)

    manifest: dict[str, Any] = {
        "schema": "AnonymousReviewArtifact.v1",
        "scientific_scope": "bounded V2, V3 and P4-X results only",
        "protected_gold_exported": False,
        "raw_protected_traces_exported": False,
        "author_identity_exported": False,
        "files": {},
    }

    write_text(bundle / "README.md", README)
    write_text(bundle / "verify_headlines.py", VERIFY, executable=True)

    for neutral_name, source in SOURCES.items():
        raw = source.read_bytes()
        obj = json.loads(raw)
        clean = sanitized(obj)
        encoded = (json.dumps(clean, indent=2, sort_keys=True) + "\n").encode("utf-8")
        scan_text(neutral_name, encoded.decode("utf-8"))
        (bundle / neutral_name).write_bytes(encoded)
        manifest["files"][neutral_name] = {
            "sha256": sha256_bytes(encoded),
            "canonical_source_sha256": sha256_bytes(raw),
        }

    manifest_text = json.dumps(manifest, indent=2, sort_keys=True) + "\n"
    write_text(bundle / "MANIFEST.json", manifest_text)

    # Verify the package itself before it can be archived.
    namespace: dict[str, Any] = {"__name__": "__main__", "__file__": str(bundle / "verify_headlines.py")}
    exec(compile(VERIFY, str(bundle / "verify_headlines.py"), "exec"), namespace)

    # Hash every member except SHA256SUMS, then write the member list.
    sums = []
    for path in sorted(p for p in bundle.iterdir() if p.is_file() and p.name != "SHA256SUMS"):
        sums.append(f"{sha256_bytes(path.read_bytes())}  {path.name}")
    write_text(bundle / "SHA256SUMS", "\n".join(sums) + "\n")

    # Final identity scan over the exact member bytes.
    for path in sorted(p for p in bundle.iterdir() if p.is_file()):
        scan_text(path.name, path.read_text(encoding="utf-8"))

    deterministic_zip(bundle, zip_path)
    print(f"ANONYMOUS_REVIEW_ARCHIVE={zip_path}")
    print(f"ANONYMOUS_REVIEW_ARCHIVE_SHA256={sha256_bytes(zip_path.read_bytes())}")
    print(f"ANONYMOUS_REVIEW_FILE_COUNT={sum(1 for p in bundle.iterdir() if p.is_file())}")


if __name__ == "__main__":
    main()
