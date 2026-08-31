#!/usr/bin/env python3
"""Refresh field-level metadata checks for the ORION-03 bibliography."""

from __future__ import annotations

import argparse
import json
import re
import time
import unicodedata
import urllib.parse
import urllib.request


EXPECTED = [
    ("doyle1979", "10.1016/0004-3702(79)90008-0", "a truth maintenance system", 1979, 1),
    ("martins1988", "10.1016/0004-3702(88)90031-8", "a model for belief revision", 1988, 2),
    ("agm1985", "10.2307/2274239", "on the logic of theory change partial meet contraction and revision functions", 1985, 3),
    ("kifer1992", "10.1016/0743-1066(92)90007-p", "theory of generalized annotated logic programming and its applications", 1992, 2),
    ("green2007", "10.1145/1265530.1265535", "provenance semirings", 2007, 3),
    ("cheney2009", "10.1561/1900000006", "provenance in databases why how and where", 2009, 3),
    ("bourgaux2022", "10.24963/kr.2022/10", "revisiting semiring provenance for datalog", 2022, 4),
    ("abokhamis2022", "10.1145/3517804.3524140", "convergence of datalog over pre semirings", 2022, 5),
    ("bonatti2011", "10.1016/j.websem.2011.06.003", "robust and scalable linked data reasoning incorporating provenance and trust annotations", 2011, 4),
    ("buneman2002", "10.1145/543613.543633", "on propagation of deletions and annotations through views", 2002, 3),
    ("meliou2010", "10.14778/1880172.1880176", "the complexity of causality and responsibility for query answers and non answers", 2010, 4),
    ("cutler2024", "10.1145/3649835", "cedar a new language for expressive fast safe and analyzable authorization", 2024, 15),
    ("rfc5280", "10.17487/rfc5280", "internet x 509 public key infrastructure certificate and certificate revocation list crl profile", 2008, 6),
]


def normalize(text: str) -> str:
    text = unicodedata.normalize("NFKD", text).encode("ascii", "ignore").decode("ascii")
    return re.sub(r"[^a-z0-9]+", " ", text.casefold()).strip()


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--output")
    args = parser.parse_args()
    records = []
    errors = []
    for key, doi, expected_title, expected_year, expected_authors in EXPECTED:
        url = "https://api.crossref.org/works/" + urllib.parse.quote(doi, safe="")
        request = urllib.request.Request(
            url,
            headers={"User-Agent": "ORION-reference-verification/2.0 (mailto:sze-chun.yiu@fysik.su.se)"},
        )
        with urllib.request.urlopen(request, timeout=30) as response:
            message = json.load(response)["message"]
        title = message.get("title", [""])[0]
        published = message.get("published-print") or message.get("published") or {}
        year = published.get("date-parts", [[None]])[0][0]
        authors = [
            " ".join(part for part in (author.get("given"), author.get("family")) if part)
            for author in message.get("author", [])
        ]
        normalized_title = normalize(title)
        title_ok = normalize(expected_title) in normalized_title or normalized_title in normalize(expected_title)
        record = {
            "key": key,
            "input_doi": doi,
            "resolved_doi": message.get("DOI"),
            "title": title,
            "authors": authors,
            "year": year,
            "container": (message.get("container-title") or [""])[0],
            "volume": message.get("volume"),
            "issue": message.get("issue"),
            "page": message.get("page"),
            "type": message.get("type"),
            "update_to": message.get("update-to"),
            "checks": {
                "doi_matches": str(message.get("DOI", "")).casefold() == doi.casefold(),
                "title_matches": title_ok,
                "year_matches": year == expected_year,
                "author_count_matches": len(authors) == expected_authors,
                "no_recorded_update": not message.get("update-to"),
            },
        }
        failed = [name for name, passed in record["checks"].items() if not passed]
        if failed:
            errors.append({"key": key, "failed_checks": failed})
        records.append(record)
        time.sleep(0.1)

    output = {
        "schema": "ORION.CitationMetadataVerification.v1",
        "as_of": "2026-08-31",
        "decision": "PASS" if not errors else "BLOCKED",
        "crossref_records": records,
        "non_doi_primary_source": {
            "key": "openssl364",
            "source": "https://github.com/openssl/openssl/tree/openssl-3.6.4",
            "tag": "openssl-3.6.4",
            "commit": "d3c1b1169b3569ff3069e5b399f47b2b28e03d79",
            "status": "official primary software/source release",
        },
        "frontier_sources": [
            {
                "key": "thapa2026minimal",
                "source": "https://arxiv.org/abs/2607.16443v2",
                "title": "Causality and Minimal Supports in Recursive Datalog",
                "authors": ["Ratan Bahadur Thapa", "Steffen Staab"],
                "status": "arXiv v2; author metadata states accepted for RuleML+RR 2026",
            },
            {
                "key": "thapa2026stratified",
                "source": "https://arxiv.org/abs/2608.21141v1",
                "title": "Causal Explanations for Stratified Datalog",
                "authors": ["Ratan Bahadur Thapa", "Steffen Staab"],
                "status": "preprint only; no peer-reviewed version located as of 2026-08-31",
            },
        ],
        "errors": errors,
        "does_not_certify": [
            "full_text_entailment_beyond_the_claim_roles_recorded_in_CITATION_VERIFICATION_V1.md",
            "absence_of_future_corrections_or_retractions",
        ],
    }
    rendered = json.dumps(output, indent=2, ensure_ascii=False, sort_keys=True) + "\n"
    if args.output:
        with open(args.output, "w", encoding="utf-8", newline="\n") as handle:
            handle.write(rendered)
    print(rendered, end="")
    raise SystemExit(0 if not errors else 1)


if __name__ == "__main__":
    main()
