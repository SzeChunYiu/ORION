#!/usr/bin/env python3
"""Frozen exact-pair evaluator for P3 V20.

This file is frozen before the BERTMap attempt.  It refuses to open the public
reference until the BERTMap native and typed-decoder result is itself frozen.
The primary estimand is the finite class-to-class opportunity shared by AML
and BERTMap; the full equivalence-pair table is secondary.  One OAEI case is
one analysis unit, so no population inference, confidence interval or p value
is produced.
"""

from __future__ import annotations

import csv
import hashlib
import json
from fractions import Fraction
from pathlib import Path
from xml.etree import ElementTree as ET


ROOT = Path(__file__).resolve().parent
PROTOCOL = ROOT / "PROTOCOL_V20.json"
BERTMAP_RESULT = ROOT / "BERTMAP_RESULT_V20.json"
REFERENCE = ROOT / "inputs/REFERENCE_FROZEN_V20.rdf"
AML = ROOT.parent / "p3-aml-java8-prospective-comparator-v16-2026-08-23/AML_ALIGNMENT_V16.rdf"
AML_RESULT = ROOT.parent / "p3-aml-java8-prospective-comparator-v16-2026-08-23/RESULT_V16.json"
UNIVERSE = ROOT / "UNIVERSE_MANIFEST_V20.json"
OUT_JSON = ROOT / "COMMON_PAIR_METRICS_V20.json"
OUT_MD = ROOT / "COMMON_PAIR_METRICS_V20.md"

EXPECTED_REFERENCE_SHA = "0afb0f2c9764201d91c226c5fb60d4b25425168acf6c2604fb191be906e9ec16"
EXPECTED_AML_SHA = "994c74c3749543205d89ef7daea0c3156d267410e35c1687f55601768b3db934"
EXPECTED_AML_RESULT_SHA = "8045631b720ac9d0c612c418b853efb6b45951257972604923dcf1d9f9a253ce"
RDF_RESOURCE = "{http://www.w3.org/1999/02/22-rdf-syntax-ns#}resource"


def sha256(path: Path) -> str:
    h = hashlib.sha256()
    with path.open("rb") as handle:
        for block in iter(lambda: handle.read(1024 * 1024), b""):
            h.update(block)
    return h.hexdigest()


def local(tag: str) -> str:
    return tag.rsplit("}", 1)[-1]


def alignment_cells(path: Path) -> list[tuple[str, str, str]]:
    cells: list[tuple[str, str, str]] = []
    for cell in ET.parse(path).getroot().iter():
        if local(cell.tag) != "Cell":
            continue
        src = tgt = relation = None
        for child in cell:
            name = local(child.tag)
            if name == "entity1":
                src = child.attrib.get(RDF_RESOURCE)
            elif name == "entity2":
                tgt = child.attrib.get(RDF_RESOURCE)
            elif name == "relation":
                relation = (child.text or "").strip()
        if not src or not tgt or relation is None:
            raise RuntimeError(f"malformed alignment cell in {path}")
        cells.append((src, tgt, relation))
    return cells


def bertmap_pairs(path: Path) -> tuple[set[tuple[str, str]], int]:
    with path.open(newline="") as handle:
        rows = list(csv.reader(handle, delimiter="\t", strict=True))
    if not rows or rows[0] != ["SrcEntity", "TgtEntity", "Score"]:
        raise RuntimeError("BERTMap decoded table header mismatch")
    pairs = [(src, tgt) for src, tgt, _score in rows[1:]]
    return set(pairs), len(pairs) - len(set(pairs))


def rational(value: Fraction) -> dict[str, object]:
    return {
        "numerator": value.numerator,
        "denominator": value.denominator,
        "fraction": f"{value.numerator}/{value.denominator}",
        "decimal": float(value),
    }


def metrics(predicted: set[tuple[str, str]], gold: set[tuple[str, str]]) -> dict[str, object]:
    tp = len(predicted & gold)
    fp = len(predicted - gold)
    fn = len(gold - predicted)
    precision = Fraction(tp, len(predicted)) if predicted else Fraction(0, 1)
    recall = Fraction(tp, len(gold)) if gold else Fraction(0, 1)
    f1 = Fraction(2 * tp, 2 * tp + fp + fn) if 2 * tp + fp + fn else Fraction(0, 1)
    return {
        "predicted_pairs": len(predicted),
        "gold_pairs": len(gold),
        "true_positive": tp,
        "false_positive": fp,
        "false_negative": fn,
        "precision": rational(precision),
        "recall": rational(recall),
        "f1": rational(f1),
    }


def main() -> int:
    if OUT_JSON.exists() or OUT_MD.exists():
        raise SystemExit("REFUSE_RERUN_OR_STALE_COMMON_SCORING_ARTIFACT")
    protocol = json.loads(PROTOCOL.read_text())
    if sha256(Path(__file__)) != protocol["frozen_code"]["common_pair_evaluator_v20.py"]:
        raise SystemExit("EVALUATOR_IDENTITY_DRIFT")
    if sha256(REFERENCE) != EXPECTED_REFERENCE_SHA:
        raise SystemExit("REFERENCE_IDENTITY_DRIFT")
    if sha256(AML) != EXPECTED_AML_SHA or sha256(AML_RESULT) != EXPECTED_AML_RESULT_SHA:
        raise SystemExit("AML_IDENTITY_DRIFT")

    bert_result = json.loads(BERTMAP_RESULT.read_text())
    if not bert_result.get("native_success") or not bert_result.get("typed_decoder_pass"):
        raise SystemExit("BERTMAP_OUTPUT_NOT_FROZEN_FOR_COMMON_SCORING")
    decoded_path = Path(bert_result["decoded_repaired_artifact"]["path"])
    if sha256(decoded_path) != bert_result["decoded_repaired_artifact"]["sha256"]:
        raise SystemExit("BERTMAP_DECODED_OUTPUT_DRIFT")

    # The first semantic access to the reference in this successor occurs here,
    # after both system outputs and the evaluator identity are frozen.
    ref_cells = alignment_cells(REFERENCE)
    aml_cells = alignment_cells(AML)
    if len(ref_cells) != 91 or len(aml_cells) != 46:
        raise SystemExit(f"ALIGNMENT_CELL_COUNT_DRIFT:{len(ref_cells)}:{len(aml_cells)}")
    reference_pairs = {(src, tgt) for src, tgt, rel in ref_cells if rel == "="}
    aml_pairs = {(src, tgt) for src, tgt, rel in aml_cells if rel == "="}
    bert_pairs, bert_duplicates = bertmap_pairs(decoded_path)
    universe = json.loads(UNIVERSE.read_text())
    source_classes = set(universe["expected_source_iris"])
    target_classes = set(universe["expected_target_iris"])

    def class_only(pairs: set[tuple[str, str]]) -> set[tuple[str, str]]:
        return {(src, tgt) for src, tgt in pairs if src in source_classes and tgt in target_classes}

    estimands: dict[str, object] = {}
    for name, gold, aml_pred, bert_pred in [
        ("primary_common_class_pair", class_only(reference_pairs), class_only(aml_pairs), class_only(bert_pairs)),
        ("secondary_full_equivalence_pair", reference_pairs, aml_pairs, bert_pairs),
    ]:
        aml_metric = metrics(aml_pred, gold)
        bert_metric = metrics(bert_pred, gold)
        aml_f1 = Fraction(aml_metric["f1"]["numerator"], aml_metric["f1"]["denominator"])
        bert_f1 = Fraction(bert_metric["f1"]["numerator"], bert_metric["f1"]["denominator"])
        delta = bert_f1 - aml_f1
        winner = "BERTMAP" if delta > 0 else "AML" if delta < 0 else "TIE"
        estimands[name] = {
            "gold_scope": "exact directed equivalence pairs; duplicates collapsed",
            "AML_V3_2": aml_metric,
            "BERTMAP_V20": bert_metric,
            "bertmap_minus_aml_f1": rational(delta),
            "finite_case_f1_winner": winner,
        }

    primary_winner = estimands["primary_common_class_pair"]["finite_case_f1_winner"]
    terminal = (
        "P3_V20_SAME_UNIVERSE_COMMON_SCORING_PASS__PRIMARY_COMMON_CLASS_PAIR_"
        f"{primary_winner}__ONE_PUBLIC_OAEI_CASE_DESCRIPTIVE_ONLY__NO_POPULATION_OR_GENERAL_SUPERIORITY_AUTHORITY"
    )
    result = {
        "schema_version": "orion.p3.same-universe-common-pair-metrics.v20",
        "protocol_id": protocol["protocol_id"],
        "authority": "ONE_PROVIDER_NATIVE_PUBLIC_CASE_EXACT_DESCRIPTIVE_PAIR_METRICS_ONLY",
        "analysis_unit": "one frozen OAEI 2004 test-103 case",
        "inference": {
            "population_estimand": False,
            "p_values": False,
            "confidence_intervals": False,
            "reason": "the finite pair table is enumerated, while there is only one case and pair cells are not treated as independent samples",
        },
        "identities": {
            "reference": {"cells": len(ref_cells), "equivalence_cells": len(reference_pairs), "sha256": sha256(REFERENCE)},
            "aml": {"cells": len(aml_cells), "equivalence_pairs": len(aml_pairs), "sha256": sha256(AML)},
            "bertmap": {"decoded_rows": len(bert_pairs) + bert_duplicates, "unique_pairs": len(bert_pairs), "duplicate_rows": bert_duplicates, "sha256": sha256(decoded_path)},
        },
        "estimands": estimands,
        "claim_boundary": [
            "a finite-case F1 difference is not a population or current-SOTA superiority claim",
            "OAEI test 103 belongs to one historical bibliographic seed family",
            "the primary estimand is class-to-class because BERTMap V20 has no property-matching opportunity",
            "the secondary full-pair estimand exposes task-coverage differences rather than hiding them",
            "public same-workspace execution is not protected or independent confirmation",
        ],
        "reference_first_semantically_opened_after_both_outputs_frozen": True,
        "terminal": terminal,
    }
    OUT_JSON.write_text(json.dumps(result, indent=2, sort_keys=True) + "\n")
    p = estimands["primary_common_class_pair"]
    s = estimands["secondary_full_equivalence_pair"]
    OUT_MD.write_text(
        "# P3 V20 same-universe common scoring\n\n"
        f"Terminal: `{terminal}`\n\n"
        "The independent analysis unit is one frozen public OAEI 2004 test-103 case. "
        "All pair cells are enumerated; no p value, confidence interval or population claim is reported.\n\n"
        "| Estimand | AML precision | AML recall | AML F1 | BERTMap precision | BERTMap recall | BERTMap F1 | Winner |\n"
        "|---|---:|---:|---:|---:|---:|---:|---|\n"
        f"| Primary common class pair | {p['AML_V3_2']['precision']['decimal']:.6f} | {p['AML_V3_2']['recall']['decimal']:.6f} | {p['AML_V3_2']['f1']['decimal']:.6f} | {p['BERTMAP_V20']['precision']['decimal']:.6f} | {p['BERTMAP_V20']['recall']['decimal']:.6f} | {p['BERTMAP_V20']['f1']['decimal']:.6f} | {p['finite_case_f1_winner']} |\n"
        f"| Secondary full equivalence pair | {s['AML_V3_2']['precision']['decimal']:.6f} | {s['AML_V3_2']['recall']['decimal']:.6f} | {s['AML_V3_2']['f1']['decimal']:.6f} | {s['BERTMAP_V20']['precision']['decimal']:.6f} | {s['BERTMAP_V20']['recall']['decimal']:.6f} | {s['BERTMAP_V20']['f1']['decimal']:.6f} | {s['finite_case_f1_winner']} |\n\n"
        "These are exact descriptive metrics for one historical public case, not general superiority, protected confirmation or naturalistic transport.\n"
    )
    print(terminal)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
