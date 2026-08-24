#!/usr/bin/env python3
"""Run the frozen Europe PMC count-only census without persisting result rows."""

from __future__ import annotations

import datetime as dt
import hashlib
import json
import sys
import urllib.parse
import urllib.request
from pathlib import Path


HERE = Path(__file__).resolve().parent
PROTOCOL_PATH = HERE / "SOURCE_FEASIBILITY_PROTOCOL_V1.json"
OUTPUT_PATH = HERE / "METADATA_COUNT_RECEIPT_V1.json"


def sha256_bytes(payload: bytes) -> str:
    return hashlib.sha256(payload).hexdigest()


def canonical_json_bytes(value: object) -> bytes:
    return (json.dumps(value, indent=2, sort_keys=True) + "\n").encode("utf-8")


def main() -> int:
    protocol_bytes = PROTOCOL_PATH.read_bytes()
    protocol = json.loads(protocol_bytes)
    epmc = protocol["sources"]["EUROPE_PMC"]
    base_url = epmc["metadata_count_route"].removeprefix("GET ")
    frozen_parameters = dict(epmc["count_request_parameters"])

    counts: list[dict[str, object]] = []
    errors: list[dict[str, str]] = []
    for query_spec in epmc["frozen_candidate_queries"]:
        parameters = {"query": query_spec["query"], **frozen_parameters}
        url = f"{base_url}?{urllib.parse.urlencode(parameters)}"
        request = urllib.request.Request(
            url,
            headers={
                "Accept": "application/json",
                "User-Agent": "ORION-P1-source-feasibility-count-only/1.0",
            },
        )
        try:
            with urllib.request.urlopen(request, timeout=60) as response:
                raw = response.read()
                status = int(response.status)
            payload = json.loads(raw)
            # Deliberately extract only count/request metadata. resultList is neither
            # inspected, printed nor serialized to the receipt.
            hit_count = int(payload["hitCount"])
            request_echo = payload.get("request", {})
            counts.append(
                {
                    "id": query_spec["id"],
                    "role": query_spec["role"],
                    "query": query_spec["query"],
                    "request_url": url,
                    "http_status": status,
                    "hit_count": hit_count,
                    "provider_version": payload.get("version"),
                    "provider_query_echo": request_echo.get("queryString"),
                    "raw_response_sha256": sha256_bytes(raw),
                    "result_rows_persisted": False,
                    "result_rows_inspected": False,
                }
            )
            del payload, raw
        except Exception as exc:  # fail closed and retain every query identity
            errors.append(
                {
                    "id": query_spec["id"],
                    "query": query_spec["query"],
                    "error_type": type(exc).__name__,
                    "error": str(exc),
                }
            )

    count_by_id = {str(row["id"]): int(row["hit_count"]) for row in counts}
    notice_total = sum(
        count_by_id.get(key, 0)
        for key in (
            "EPMC_OA_PUBLISHED_ERRATUM",
            "EPMC_OA_CORRECTION",
            "EPMC_OA_RETRACTION_NOTICE",
            "EPMC_OA_EXPRESSION_OF_CONCERN",
        )
    )
    original_count = count_by_id.get("EPMC_OA_RETRACTED_ORIGINAL", 0)
    if errors or len(counts) != len(epmc["frozen_candidate_queries"]):
        terminal = "P1_NATURALISTIC_PUBLIC_PANEL_CANNOT_CHECK_METADATA_CENSUS"
    elif notice_total == 0 or original_count == 0:
        terminal = "P1_NATURALISTIC_PUBLIC_PANEL_NOT_SUPPORTED_ZERO_METADATA_CANDIDATE_CLASS"
    else:
        terminal = (
            "P1_NATURALISTIC_PUBLIC_METADATA_CANDIDATES_PRESENT__"
            "CASE_FEASIBILITY_UNDETERMINED"
        )

    receipt = {
        "schema_version": "orion.p1.naturalistic-public-metadata-count-receipt.v1",
        "identity": "P1.NATURALISTIC.PUBLIC.METADATA.COUNT.V1",
        "generated_at": dt.datetime.now(dt.timezone.utc).isoformat(),
        "authority": "COUNT_ONLY_METADATA_PREFLIGHT__NO_CASE_OR_SCIENTIFIC_AUTHORITY",
        "protocol": {
            "path": str(PROTOCOL_PATH.relative_to(HERE.parents[2])),
            "sha256": sha256_bytes(protocol_bytes),
            "frozen_at": protocol["frozen_at"],
        },
        "provider": epmc["provider_identity"],
        "requests": counts,
        "errors": errors,
        "summary": {
            "frozen_query_count": len(epmc["frozen_candidate_queries"]),
            "completed_query_count": len(counts),
            "notice_class_hit_count_sum_not_deduplicated": notice_total,
            "retracted_original_hit_count": original_count,
            "result_rows_persisted": False,
            "result_rows_inspected": False,
            "article_or_notice_text_accessed": False,
            "pair_relations_assessed": 0,
            "rights_admissible_pairs": 0,
            "eligible_source_clusters": 0,
            "case_execution_authorized": False,
            "terminal": terminal,
        },
        "interpretation": "Counts establish candidate metadata prevalence under the frozen publication-type queries only. They do not establish original-notice joins, rights, typed action gold, anti-leak construct validity, case eligibility, decision-mixed fibres or system performance.",
    }
    OUTPUT_PATH.write_bytes(canonical_json_bytes(receipt))
    print(f"wrote {OUTPUT_PATH}")
    print(f"terminal={terminal}")
    for row in counts:
        print(f"{row['id']}={row['hit_count']}")
    if errors:
        for row in errors:
            print(f"ERROR {row['id']}: {row['error_type']}: {row['error']}", file=sys.stderr)
        return 3
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
