#!/usr/bin/env python3
"""A5 S1a: domain assignment for the PMC OA linked-record reservoirs.

Assigns one of the four frozen A5 domains to each rights-clear harvested
unit in the committed PMC linked-harvest candidate rows (M3 protocol-to-
results, M4 article-to-correction, M8 article-to-licensed-supplement),
using the domain lexicon and the decision procedure frozen in
development/p4-m6-source-provider-successor-v4-2026-08-23/PROTOCOL_V4.json.

Domain assignment ONLY.  Mechanism identities come from the committed
harvest rows and are never reassigned.  No network, no RNG, no outcome
access.  Fail-closed: any unit whose domain is ambiguous, unclassified,
or whose pair sides disagree on the assigned domain is recorded in a
reservoir and counts to no cell.
"""

from __future__ import annotations

import argparse
import hashlib
import html
import json
import re
import sys
import tempfile
from collections import Counter
from pathlib import Path
from typing import Any

DOMAINS = [
    "EARTH_ENVIRONMENT",
    "LIFE_BIOMEDICAL",
    "SCIENTIFIC_SOFTWARE",
    "PHYSICAL_ENGINEERING",
]

INPUT_PINS: dict[str, dict[str, str]] = {
    "m3_candidates": {
        "path": "development/p4-scientific-ascent-2026-08-23/source_binding/pmc-oa-linked-harvest-v1/CANDIDATES_M3_PROTOCOL_TO_RESULTS.jsonl",
        "sha256": "2703b131c791cad8e547ef6f25d885f7e0c216ff0cff01cc477779b081b1f4fe",
        "mechanism": "M3_PROTOCOL_TO_RESULTS",
    },
    "m4_candidates": {
        "path": "development/p4-scientific-ascent-2026-08-23/source_binding/pmc-oa-linked-harvest-v1/CANDIDATES_M4_ARTICLE_TO_CORRECTION.jsonl",
        "sha256": "18022f30e84e8f8810166e68fafdad81635a2b22712d148dc4742f32306b286b",
        "mechanism": "M4_ARTICLE_TO_CORRECTION",
    },
    "m8_candidates": {
        "path": "development/p4-scientific-ascent-2026-08-23/source_binding/pmc-oa-linked-harvest-v1/CANDIDATES_M8_ARTICLE_TO_LICENSED_SUPPLEMENT.jsonl",
        "sha256": "2d8404d49898b29ace9d2d33db647cb4ed83a7eaad37952e258f998408f2ebfa",
        "mechanism": "M8_ARTICLE_TO_LICENSED_SUPPLEMENT",
    },
    "domain_protocol": {
        "path": "development/p4-m6-source-provider-successor-v4-2026-08-23/PROTOCOL_V4.json",
        "sha256": "902d2d7e0efac569f9b4c87d087b560e4039666d5ee13be075fd3adba4bc27f4",
        "mechanism": None,
    },
}

SCHEMA = "ORION.A5.S1a.PMCDomainAssignment.v1"

# The frozen V4 rule matches over "JOSS title/abstract plus GitHub
# description/topics".  The PMC candidate rows expose title and journal
# only; this adaptation is declared in the result artifact and applies
# the SAME lexicon and the SAME decision procedure to those fields.
DOMAIN_TEXT_FIELDS = ["title", "journal"]
V4_RULE_TEXT = (
    "case-insensitive substring matches over JOSS title/abstract plus GitHub "
    "description/topics; assign the unique domain with the greatest number of "
    "distinct matched tokens"
)
ADAPTATION_NOTE = (
    "PMC candidate rows carry title and journal but no abstract; the frozen "
    "lexicon and the frozen unique-max-distinct-token decision procedure are "
    "applied verbatim over the concatenation of plain_text(title) and "
    "plain_text(journal).  No other text source was used and no token was "
    "added, removed, or reweighted."
)

RIGHTS_CLEAR = "CC_BY_40"


def plain_text(value: object) -> str:
    text = " " if value is None else str(value)
    text = re.sub(r"<[^>]+>", " ", html.unescape(text))
    return " ".join(text.split())


def sha256_file(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as handle:
        for block in iter(lambda: handle.read(1 << 20), b""):
            digest.update(block)
    return digest.hexdigest()


def load_lexicon(protocol: dict[str, Any]) -> dict[str, list[str]]:
    source = protocol.get("domain_lexicon")
    if not isinstance(source, dict):
        raise RuntimeError("domain_lexicon missing from pinned V4 protocol")
    lexicon = {}
    for domain in DOMAINS:
        terms = source.get(domain)
        if not isinstance(terms, list) or not terms:
            raise RuntimeError(f"domain_lexicon missing domain {domain}")
        lexicon[domain] = [str(term) for term in terms]
    return lexicon


def classify_domain(text: str, lexicon: dict[str, list[str]]) -> dict[str, Any]:
    """Verbatim decision procedure from harvest_v4.classify_domain."""
    folded = text.casefold()
    scores: dict[str, int] = {}
    matches: dict[str, list[str]] = {}
    for domain in DOMAINS:
        hits = sorted({token for token in lexicon[domain] if token.casefold() in folded})
        scores[domain] = len(hits)
        matches[domain] = hits
    maximum = max(scores.values())
    winners = [d for d, score in scores.items() if score == maximum]
    if maximum == 0:
        status, assigned = "CANNOT_CHECK_DOMAIN_UNCLASSIFIED", None
    elif len(winners) != 1:
        status, assigned = "CANNOT_CHECK_DOMAIN_AMBIGUOUS", None
    else:
        status, assigned = "PASS", winners[0]
    return {"status": status, "assigned_domain": assigned, "scores": scores, "matched_tokens": matches}


def domain_text(row: dict[str, Any]) -> str:
    return " ".join(plain_text(row.get(field)) for field in DOMAIN_TEXT_FIELDS)


def side_class(side: dict[str, Any], lexicon: dict[str, list[str]]) -> dict[str, Any]:
    result = classify_domain(domain_text(side), lexicon)
    result["domain_text_sha256"] = hashlib.sha256(domain_text(side).encode("utf-8")).hexdigest()
    return result


def unit_verdict(row: dict[str, Any], mechanism: str, lexicon: dict[str, list[str]]) -> dict[str, Any]:
    """Fail-closed unit rule per mechanism; never reassigns mechanism."""
    article = side_class(row, lexicon)
    verdict: dict[str, Any] = {
        "mechanism": mechanism,
        "article_classification": article,
        "unit_status": None,
        "assigned_domain": None,
        "reservoir": None,
        "bytes_and_rights": None,
    }
    if mechanism in ("M3_PROTOCOL_TO_RESULTS", "M4_ARTICLE_TO_CORRECTION"):
        partner = row.get("partner")
        if not isinstance(partner, dict):
            verdict["unit_status"] = "RESERVOIR_NO_PARTNER_OBJECT"
            verdict["reservoir"] = "no_partner_object"
            return verdict
        partner_class = side_class(partner, lexicon)
        verdict["partner_classification"] = partner_class
        verdict["bytes_and_rights"] = {
            "article_rights_class": row.get("rights_class"),
            "partner_rights_class": partner.get("rights_class"),
            "article_nxml_sha256": row.get("nxml_sha256"),
            "partner_nxml_sha256": partner.get("nxml_sha256"),
            "article_license_urls": row.get("license_urls"),
            "partner_license_urls": partner.get("license_urls"),
            "pair_status": row.get("pair_status"),
        }
        rights_clear = (
            row.get("rights_class") == RIGHTS_CLEAR
            and partner.get("rights_class") == RIGHTS_CLEAR
            and bool(row.get("nxml_sha256"))
            and bool(partner.get("nxml_sha256"))
        )
        if not rights_clear:
            verdict["unit_status"] = "RESERVOIR_RIGHTS_OR_BYTES_NOT_CLEAR"
            verdict["reservoir"] = "rights_or_bytes_not_clear"
            return verdict
        if article["status"] != "PASS":
            verdict["unit_status"] = f"RESERVOIR_ARTICLE_{article['status']}"
            verdict["reservoir"] = "article_" + article["status"].removeprefix("CANNOT_CHECK_DOMAIN_").lower()
            return verdict
        if partner_class["status"] != "PASS":
            verdict["unit_status"] = f"RESERVOIR_PARTNER_{partner_class['status']}"
            verdict["reservoir"] = "partner_" + partner_class["status"].removeprefix("CANNOT_CHECK_DOMAIN_").lower()
            return verdict
        if article["assigned_domain"] != partner_class["assigned_domain"]:
            verdict["unit_status"] = "RESERVOIR_PAIR_DOMAIN_DISAGREEMENT"
            verdict["reservoir"] = "pair_domain_disagreement"
            return verdict
        verdict["unit_status"] = "DOMAIN_ASSIGNED_UNIT"
        verdict["assigned_domain"] = article["assigned_domain"]
        return verdict

    if mechanism == "M8_ARTICLE_TO_LICENSED_SUPPLEMENT":
        supplements = row.get("supplement_files") or []
        hashed = [
            item
            for item in supplements
            if isinstance(item, dict)
            and item.get("sha256")
            and item.get("bytes")
            and item.get("http_status") == 200
        ]
        verdict["bytes_and_rights"] = {
            "article_rights_class": row.get("rights_class"),
            "article_nxml_sha256": row.get("nxml_sha256"),
            "article_license_urls": row.get("license_urls"),
            "supplementary_material_elements_n": row.get("supplementary_material_elements_n"),
            "supplement_files_total": len(supplements),
            "supplement_files_hashed_with_200": len(hashed),
        }
        rights_clear = row.get("rights_class") == RIGHTS_CLEAR and bool(row.get("nxml_sha256"))
        elements = row.get("supplementary_material_elements_n")
        if not rights_clear:
            verdict["unit_status"] = "RESERVOIR_RIGHTS_OR_BYTES_NOT_CLEAR"
            verdict["reservoir"] = "rights_or_bytes_not_clear"
            return verdict
        if not isinstance(elements, int) or elements <= 0 or not hashed:
            verdict["unit_status"] = "RESERVOIR_NO_HASHED_SUPPLEMENT_FILE"
            verdict["reservoir"] = "no_hashed_supplement_file"
            return verdict
        if article["status"] != "PASS":
            verdict["unit_status"] = f"RESERVOIR_ARTICLE_{article['status']}"
            verdict["reservoir"] = "article_" + article["status"].removeprefix("CANNOT_CHECK_DOMAIN_").lower()
            return verdict
        verdict["unit_status"] = "DOMAIN_ASSIGNED_UNIT"
        verdict["assigned_domain"] = article["assigned_domain"]
        return verdict

    raise RuntimeError(f"unknown mechanism {mechanism}")


def run(repo_root: Path, rows_path: Path, result_path: Path, check_digests: bool = True) -> dict[str, Any]:
    # --- pinned inputs -----------------------------------------------------
    pinned = {}
    for key, spec in INPUT_PINS.items():
        path = repo_root / spec["path"]
        if not path.is_file():
            raise RuntimeError(f"missing pinned input {key}: {path}")
        digest = sha256_file(path)
        if check_digests and digest != spec["sha256"]:
            raise RuntimeError(f"CANNOT_CHECK_S1A_INPUT_DIGEST_MISMATCH {key}: {digest}")
        pinned[key] = {"path": spec["path"], "sha256": digest}

    lexicon = load_lexicon(json.loads((repo_root / INPUT_PINS["domain_protocol"]["path"]).read_text(encoding="utf-8")))

    all_rows: list[dict[str, Any]] = []
    per_mechanism: dict[str, Any] = {}

    for key in ("m3_candidates", "m4_candidates", "m8_candidates"):
        spec = INPUT_PINS[key]
        raw_rows = [json.loads(line) for line in (repo_root / spec["path"]).read_text(encoding="utf-8").splitlines() if line.strip()]
        mechanism = spec["mechanism"]
        cell_counts: Counter = Counter()
        reservoirs: Counter = Counter()
        for index, row in enumerate(raw_rows):
            verdict = unit_verdict(row, mechanism, lexicon)
            verdict_row = {
                "schema_version": SCHEMA,
                "input": key,
                "row_index": index,
                "mechanism": mechanism,
                "pmcid": row.get("pmcid"),
                "doi": row.get("doi"),
                "title_plain": plain_text(row.get("title")),
                "unit_status": verdict["unit_status"],
                "assigned_domain": verdict["assigned_domain"],
                "reservoir": verdict["reservoir"],
                "article_classification": verdict["article_classification"],
                "bytes_and_rights": verdict["bytes_and_rights"],
            }
            if "partner_classification" in verdict:
                verdict_row["partner_classification"] = verdict["partner_classification"]
            all_rows.append(verdict_row)
            if verdict["unit_status"] == "DOMAIN_ASSIGNED_UNIT":
                cell_counts[(mechanism, verdict["assigned_domain"])] += 1
            else:
                reservoirs[verdict["unit_status"]] += 1
        per_mechanism[mechanism] = {
            "input": pinned[key],
            "input_rows": len(raw_rows),
            "domain_assigned_units": {
                domain: cell_counts.get((mechanism, domain), 0) for domain in DOMAINS
            },
            "domain_assigned_units_total": sum(cell_counts.values()),
            "reservoir_breakdown": dict(sorted(reservoirs.items())),
            "reservoir_total": sum(reservoirs.values()),
        }

    units_by_cell = {
        f"{domain}__{mechanism}": per_mechanism[mechanism]["domain_assigned_units"][domain]
        for mechanism in per_mechanism
        for domain in DOMAINS
    }
    rows_path.write_text("".join(json.dumps(row, sort_keys=True) + "\n" for row in all_rows), encoding="utf-8")

    result = {
        "schema_version": SCHEMA,
        "date": "2026-09-03",
        "identity": "A5_S1A_PMC_DOMAIN_ASSIGNMENT_V1",
        "authority_boundary": {
            "authority": "COMMITTED_PUBLIC_METADATA_DOMAIN_ASSIGNMENT_ONLY",
            "grants_scientific_authority": False,
            "protected_outcomes_accessed": False,
            "comparator_outputs_accessed": False,
            "terminal_gold_accessed": False,
            "mechanism_reassignment_performed": False,
            "domain_assignment_only": True,
            "counts_are_not_eligible_pair_counts": True,
            "interpretation": (
                "A domain-assigned unit is a rights-clear (both-sides CC BY 4.0) harvested "
                "pair/record whose bytes receipts are present in the committed harvest and "
                "whose assigned domain is the unique frozen-lexicon winner on BOTH sides "
                "(M3/M4) or the article side (M8).  Natural-pair eligibility, target-claim "
                "adjudication and external screening remain open and can only reduce counts."
            ),
        },
        "inputs": pinned,
        "domain_lexicon": {
            "source_path": pinned["domain_protocol"]["path"],
            "source_sha256": pinned["domain_protocol"]["sha256"],
            "rule_text_frozen_v4": V4_RULE_TEXT,
            "decision_procedure": "verbatim harvest_v4.classify_domain over plain-text-concatenated candidate fields",
            "domain_text_fields_used": DOMAIN_TEXT_FIELDS,
            "adaptation_disclosure": ADAPTATION_NOTE,
            "lexicon_terms": {d: lexicon[d] for d in DOMAINS},
        },
        "per_mechanism": per_mechanism,
        "units_by_cell": units_by_cell,
        "total_domain_assigned_units": sum(units_by_cell.values()),
        "determinism": {"no_network": True, "no_rng": True, "input_sha256_pinned": True},
        "rows_jsonl_sha256": sha256_file(rows_path),
        "rows": len(all_rows),
        "execution_boundary": {
            "host": "billy-old",
            "committed_artifacts": "rows jsonl + this result json only",
            "raw_harvest_bytes": "already committed upstream in pmc-oa-linked-harvest-v1",
        },
        "forbidden_claims": [
            "natural-pair eligibility",
            "mechanism reassignment",
            "domain authority beyond the frozen lexicon",
            "case resolution",
            "scientific performance",
            "confirmation",
            "ORION superiority",
        ],
        "scientific_authority_delta": "NONE__DOMAIN_LABELLING_OF_COMMITTED_HARVEST_ROWS_ONLY",
    }
    result_path.write_text(json.dumps(result, sort_keys=True, indent=2) + "\n", encoding="utf-8")
    return result


def self_test(repo_root: Path) -> int:
    """Tamper assertions; returns 0 only if every forgery is rejected."""
    with tempfile.TemporaryDirectory() as tmp:
        tmp_path = Path(tmp)
        rows_path = tmp_path / "rows.jsonl"
        result_path = tmp_path / "result.json"
        result = run(repo_root, rows_path, result_path)
        base_m4_lb = result["per_mechanism"]["M4_ARTICLE_TO_CORRECTION"]["domain_assigned_units"]["LIFE_BIOMEDICAL"]
        assert base_m4_lb > 0, "self-test fixture lost its LIFE_BIOMEDICAL units"

        # Tamper 1: strip CC BY 4.0 from one counted M4 LIFE unit -> count drops.
        m4_spec = INPUT_PINS["m4_candidates"]
        raw = (repo_root / m4_spec["path"]).read_text(encoding="utf-8").splitlines()
        parsed = [json.loads(line) for line in raw if line.strip()]
        dropped = False
        for row in parsed:
            if (
                row.get("rights_class") == RIGHTS_CLEAR
                and isinstance(row.get("partner"), dict)
                and row["partner"].get("rights_class") == RIGHTS_CLEAR
            ):
                article = side_class(row, load_lexicon(json.loads((repo_root / INPUT_PINS["domain_protocol"]["path"]).read_text(encoding="utf-8"))))
                if article["status"] == "PASS" and article["assigned_domain"] == "LIFE_BIOMEDICAL":
                    row["rights_class"] = "CC_BY_NC_40"
                    dropped = True
                    break
        assert dropped, "self-test could not build tamper 1 fixture"
        tampered_inputs = tmp_path / "inputs"
        (tampered_inputs / "development" / "x").mkdir(parents=True, exist_ok=True)
        fake_root = _fake_root(repo_root, tampered_inputs, {m4_spec["path"]: parsed})
        tampered_rows = tampered_inputs / "rows.jsonl"
        tampered_result = tampered_inputs / "result.json"
        tamper1 = run(fake_root, tampered_rows, tampered_result, check_digests=False)
        assert (
            tamper1["per_mechanism"]["M4_ARTICLE_TO_CORRECTION"]["domain_assigned_units"]["LIFE_BIOMEDICAL"]
            == base_m4_lb - 1
        ), "tamper 1 (rights stripped) was NOT rejected by the unit rule"

        # Tamper 2: corrupt the lexicon input bytes -> digest refusal.
        fake_root2 = _fake_root(repo_root, tmp_path / "inputs2", {}, corrupt="domain_protocol")
        try:
            run(fake_root2, tmp_path / "rows2.jsonl", tmp_path / "result2.json")
        except RuntimeError as exc:
            assert "INPUT_DIGEST_MISMATCH" in str(exc), f"unexpected refusal: {exc}"
        else:
            raise AssertionError("tamper 2 (lexicon byte corruption) was NOT refused")

        # Tamper 3: forge an ambiguous title -> must land in reservoir, never a cell.
        lexicon = load_lexicon(json.loads((repo_root / INPUT_PINS["domain_protocol"]["path"]).read_text(encoding="utf-8")))
        ambiguous = classify_domain("climate genomics software physics climate genomics software physics", lexicon)
        assert ambiguous["status"] == "CANNOT_CHECK_DOMAIN_AMBIGUOUS" and ambiguous["assigned_domain"] is None
        unclassified = classify_domain("A study of nothing in particular", lexicon)
        assert unclassified["status"] == "CANNOT_CHECK_DOMAIN_UNCLASSIFIED" and unclassified["assigned_domain"] is None
    print(json.dumps({"self_test": "PASS", "schema": SCHEMA}, sort_keys=True))
    return 0


def _fake_root(repo_root: Path, base: Path, replacements: dict[str, list[dict[str, Any]]], corrupt: str | None = None) -> Path:
    """Materialise a private copy of the pinned inputs (optionally tampered)."""
    for key, spec in INPUT_PINS.items():
        target = base / spec["path"]
        target.parent.mkdir(parents=True, exist_ok=True)
        source = repo_root / spec["path"]
        if key == corrupt:
            data = json.loads(source.read_text(encoding="utf-8"))
            data["domain_lexicon"]["LIFE_BIOMEDICAL"] = ["zzz-no-such-token"]
            target.write_text(json.dumps(data, indent=2), encoding="utf-8")
        elif spec["path"] in replacements:
            target.write_text("".join(json.dumps(row, sort_keys=True) + "\n" for row in replacements[spec["path"]]), encoding="utf-8")
        else:
            target.write_bytes(source.read_bytes())
    return base


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--repo-root", type=Path, default=Path(__file__).resolve().parents[2])
    parser.add_argument("--rows", type=Path, default=Path(__file__).resolve().parent / "A5_S1A_PMC_DOMAIN_ASSIGNMENT_ROWS_V1.jsonl")
    parser.add_argument("--result", type=Path, default=Path(__file__).resolve().parent / "A5_S1A_PMC_DOMAIN_ASSIGNMENT_RESULT_V1.json")
    parser.add_argument("--self-test", action="store_true")
    args = parser.parse_args()
    if args.self_test:
        return self_test(args.repo_root)
    result = run(args.repo_root, args.rows, args.result)
    summary = {
        "identity": result["identity"],
        "total_domain_assigned_units": result["total_domain_assigned_units"],
        "units_by_cell": result["units_by_cell"],
        "rows_jsonl_sha256": result["rows_jsonl_sha256"],
    }
    print(json.dumps(summary, sort_keys=True, indent=2))
    return 0


if __name__ == "__main__":
    sys.exit(main())
