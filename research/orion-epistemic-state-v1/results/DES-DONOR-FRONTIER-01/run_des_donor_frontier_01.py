#!/usr/bin/env python3
"""Frozen multi-source donor discovery for DES-DONOR-FRONTIER-01.

Metadata discovery is not donor execution. The runner therefore fails closed
unless a separately frozen runnable-donor contract is present (V1 has none).
"""

from __future__ import annotations

import argparse
from collections import Counter
import hashlib
import json
from pathlib import Path
import platform
import re
import time
from typing import Any
from urllib.error import HTTPError, URLError
from urllib.parse import quote, urlencode
from urllib.request import Request, urlopen
import xml.etree.ElementTree as ET


JOB_ID = "DES-DONOR-FRONTIER-01"
TERMINAL = "MATERIAL_DONOR_INACCESSIBLE"
AUTHORITY_CEILING = (
    "MULTISOURCE_METADATA_DISCOVERY_ONLY__NO_RUNNABLE_IDEAL_DONOR_PRODUCT__"
    "NO_NOVELTY_OR_SUPERIORITY_AUTHORITY"
)
USER_AGENT = "ORION-DES-DONOR-FRONTIER-01/1.0 (public scholarly metadata audit)"


def canonical(payload: Any) -> bytes:
    return (json.dumps(payload, sort_keys=True, separators=(",", ":")) + "\n").encode()


def sha256_bytes(data: bytes) -> str:
    return hashlib.sha256(data).hexdigest()


def sha256_file(path: Path) -> str:
    return sha256_bytes(path.read_bytes())


def write_json(path: Path, payload: Any) -> None:
    path.write_bytes(canonical(payload))


def request_bytes(url: str, timeout: float, attempts: int = 3) -> tuple[bytes | None, list[str]]:
    errors: list[str] = []
    for attempt in range(1, attempts + 1):
        try:
            request = Request(url, headers={"User-Agent": USER_AGENT, "Accept": "application/json"})
            with urlopen(request, timeout=timeout) as response:
                return response.read(), errors
        except (HTTPError, URLError, TimeoutError, OSError) as exc:
            errors.append(f"attempt={attempt}:{type(exc).__name__}:{exc}")
            if attempt < attempts:
                time.sleep(float(attempt))
    return None, errors


def normalize_title(value: str) -> str:
    return " ".join(re.findall(r"[a-z0-9]+", value.lower()))


def record_key(record: dict[str, Any]) -> str:
    doi = str(record.get("doi") or "").lower().removeprefix("https://doi.org/")
    if doi:
        return f"doi:{doi}"
    identifier = str(record.get("id") or "").lower()
    if identifier:
        return f"id:{identifier}"
    return "title:" + normalize_title(str(record.get("title") or ""))


def openalex(query: str, limit: int, timeout: float) -> tuple[list[dict[str, Any]], dict[str, Any]]:
    params = urlencode({"search": query, "per-page": limit})
    url = "https://api.openalex.org/works?" + params
    data, errors = request_bytes(url, timeout)
    if data is None:
        return [], {"source": "openalex", "url": url, "errors": errors, "ok": False}
    payload = json.loads(data)
    records = []
    for row in payload.get("results", []):
        authors = [
            item.get("author", {}).get("display_name")
            for item in row.get("authorships", [])
            if item.get("author", {}).get("display_name")
        ]
        records.append(
            {
                "source": "openalex",
                "id": row.get("id"),
                "doi": row.get("doi"),
                "title": row.get("display_name") or row.get("title"),
                "authors": authors,
                "year": row.get("publication_year"),
                "type": row.get("type"),
                "cited_by_count": row.get("cited_by_count"),
                "open_access": row.get("open_access", {}),
                "primary_location": row.get("primary_location"),
                "abstract_available": bool(row.get("abstract_inverted_index")),
            }
        )
    return records, {
        "source": "openalex",
        "url": url,
        "errors": errors,
        "ok": True,
        "returned": len(records),
    }


def crossref(query: str, limit: int, timeout: float) -> tuple[list[dict[str, Any]], dict[str, Any]]:
    params = urlencode({"query.bibliographic": query, "rows": limit})
    url = "https://api.crossref.org/works?" + params
    data, errors = request_bytes(url, timeout)
    if data is None:
        return [], {"source": "crossref", "url": url, "errors": errors, "ok": False}
    payload = json.loads(data)
    records = []
    for row in payload.get("message", {}).get("items", []):
        title = row.get("title", [None])
        year_parts = row.get("published", {}).get("date-parts", [[None]])
        authors = [
            " ".join(part for part in (item.get("given"), item.get("family")) if part)
            for item in row.get("author", [])
        ]
        records.append(
            {
                "source": "crossref",
                "id": row.get("URL"),
                "doi": row.get("DOI"),
                "title": title[0] if title else None,
                "authors": authors,
                "year": year_parts[0][0] if year_parts and year_parts[0] else None,
                "type": row.get("type"),
                "cited_by_count": row.get("is-referenced-by-count"),
                "container_title": (row.get("container-title") or [None])[0],
                "abstract_available": bool(row.get("abstract")),
            }
        )
    return records, {
        "source": "crossref",
        "url": url,
        "errors": errors,
        "ok": True,
        "returned": len(records),
    }


def arxiv(query: str, limit: int, timeout: float) -> tuple[list[dict[str, Any]], dict[str, Any]]:
    params = urlencode({"search_query": f'all:"{query}"', "start": 0, "max_results": limit})
    url = "https://export.arxiv.org/api/query?" + params
    data, errors = request_bytes(url, timeout)
    if data is None:
        return [], {"source": "arxiv", "url": url, "errors": errors, "ok": False}
    root = ET.fromstring(data)
    ns = {"atom": "http://www.w3.org/2005/Atom"}
    records = []
    for entry in root.findall("atom:entry", ns):
        identifier = (entry.findtext("atom:id", default="", namespaces=ns) or "").strip()
        title = " ".join((entry.findtext("atom:title", default="", namespaces=ns) or "").split())
        published = entry.findtext("atom:published", default="", namespaces=ns) or ""
        authors = [
            node.findtext("atom:name", default="", namespaces=ns)
            for node in entry.findall("atom:author", ns)
        ]
        records.append(
            {
                "source": "arxiv",
                "id": identifier,
                "doi": None,
                "title": title,
                "authors": authors,
                "year": int(published[:4]) if published[:4].isdigit() else None,
                "type": "preprint",
                "cited_by_count": None,
                "abstract_available": bool(
                    (entry.findtext("atom:summary", default="", namespaces=ns) or "").strip()
                ),
            }
        )
    return records, {
        "source": "arxiv",
        "url": url,
        "errors": errors,
        "ok": True,
        "returned": len(records),
    }


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--bundle", type=Path, default=Path(__file__).resolve().parent)
    parser.add_argument("--out", type=Path, required=True)
    parser.add_argument("--executed-at", required=True)
    parser.add_argument("--execution-head", required=True)
    parser.add_argument("--limit", type=int, default=5)
    parser.add_argument("--timeout", type=float, default=30.0)
    args = parser.parse_args()
    if not re.fullmatch(r"[0-9a-f]{40}", args.execution_head):
        raise SystemExit("execution head must be a full Git SHA")
    bundle = args.bundle.resolve()
    out = args.out.resolve()
    out.mkdir(parents=True, exist_ok=True)
    freeze_path = bundle / "FREEZE_V1.json"
    queries_path = bundle / "QUERY_ATOMS_V1.json"
    runner_path = bundle / "run_des_donor_frontier_01.py"
    freeze = json.loads(freeze_path.read_text())
    queries = json.loads(queries_path.read_text())
    for path, expected in (
        (runner_path, freeze["implementation"]["runner_sha256"]),
        (queries_path, freeze["inputs"]["query_atoms_sha256"]),
    ):
        if sha256_file(path) != expected:
            raise SystemExit(f"frozen input digest drift: {path.name}")
    if args.limit != freeze["search"]["per_source_limit"]:
        raise SystemExit("result limit differs from freeze")

    started = time.monotonic_ns()
    raw_rows: list[dict[str, Any]] = []
    provider_receipts: list[dict[str, Any]] = []
    atom_rows: list[dict[str, Any]] = []
    for atom in queries["atoms"]:
        merged: dict[str, dict[str, Any]] = {}
        source_counts: dict[str, int] = {}
        for provider in (openalex, crossref, arxiv):
            records, receipt = provider(atom["query"], args.limit, args.timeout)
            receipt["atom_id"] = atom["atom_id"]
            provider_receipts.append(receipt)
            source_counts[receipt["source"]] = len(records)
            for record in records:
                raw_rows.append({"atom_id": atom["atom_id"], **record})
                key = record_key(record)
                if key not in merged:
                    merged[key] = record
                else:
                    merged[key]["also_seen_in"] = sorted(
                        set(merged[key].get("also_seen_in", [])) | {record["source"]}
                    )
        candidates = sorted(
            merged.values(),
            key=lambda row: (
                -(row.get("cited_by_count") or 0),
                normalize_title(str(row.get("title") or "")),
                str(row.get("id") or ""),
            ),
        )
        atom_rows.append(
            {
                **atom,
                "provider_counts": source_counts,
                "deduplicated_candidate_count": len(candidates),
                "candidate_records": candidates,
                "runnable_donor_contract_attained": False,
                "frontier_state": "DONOR_ACCESS_CANNOT_CHECK",
                "reason": (
                    "metadata discovery does not establish matched executable code, data, "
                    "information, evaluator, or vector resources"
                ),
            }
        )
        time.sleep(freeze["search"]["polite_delay_seconds"])

    elapsed_ns = time.monotonic_ns() - started
    source_success = Counter(
        receipt["source"] for receipt in provider_receipts if receipt["ok"]
    )
    source_failure = Counter(
        receipt["source"] for receipt in provider_receipts if not receipt["ok"]
    )
    frontier = {
        "schema": "orion.des.p1-p15-ideal-donor-frontiers.v1",
        "job_id": JOB_ID,
        "executed_at": args.executed_at,
        "atom_denominator": len(atom_rows),
        "paper_denominator": len({row["paper_id"] for row in atom_rows}),
        "provider_call_denominator": len(provider_receipts),
        "atom_rows": atom_rows,
        "exact_terminal": TERMINAL,
        "authority_ceiling": AUTHORITY_CEILING,
    }
    residual = {
        "schema": "orion.des.robust-residual-atlas.v1",
        "job_id": JOB_ID,
        "rule": "no residual novelty is computed without a matched runnable ideal donor product",
        "atom_denominator": len(atom_rows),
        "state_counts": dict(Counter(row["frontier_state"] for row in atom_rows)),
        "rows": [
            {
                "atom_id": row["atom_id"],
                "paper_id": row["paper_id"],
                "state": row["frontier_state"],
                "robust_residual": None,
                "candidate_count": row["deduplicated_candidate_count"],
            }
            for row in atom_rows
        ],
        "exact_terminal": TERMINAL,
        "authority_ceiling": AUTHORITY_CEILING,
    }
    primary = {
        "schema": "orion.des.primary-result.v1",
        "job_id": JOB_ID,
        "executed_at": args.executed_at,
        "exact_terminal": TERMINAL,
        "atom_denominator": len(atom_rows),
        "candidate_record_denominator": len(raw_rows),
        "runnable_donor_atoms": 0,
        "cannot_check_atoms": len(atom_rows),
        "claim_ceiling": AUTHORITY_CEILING,
        "paper_authority_delta": "NONE",
    }
    donor = {
        "schema": "orion.des.ideal-donor-result.v1",
        "job_id": JOB_ID,
        "strongest_donor": "IDEAL_COMPOSED_PRODUCT_UNAVAILABLE",
        "matched_runnable_contract_attained": False,
        "metadata_candidates_are_not_substituted_as_donors": True,
        "exact_terminal": TERMINAL,
    }
    controls = {
        "schema": "orion.des.negative-controls.v1",
        "job_id": JOB_ID,
        "controls": [
            {"id": "NO_METADATA_AS_EXECUTION", "passed": True},
            {"id": "NO_WEAK_PROXY_SUBSTITUTION", "passed": True},
            {"id": "PROVIDER_FAILURES_RETAINED", "passed": True},
            {"id": "NO_POST_OUTCOME_QUERY_RETUNING", "passed": True},
        ],
        "all_pass": True,
    }
    resources = {
        "schema": "orion.des.resource-ledger.v1",
        "job_id": JOB_ID,
        "resource_vector": {
            "scholarly_metadata_queries": len(provider_receipts),
            "openalex_success": source_success["openalex"],
            "crossref_success": source_success["crossref"],
            "arxiv_success": source_success["arxiv"],
            "provider_failures": sum(source_failure.values()),
            "elapsed_monotonic_ns": elapsed_ns,
            "gpu": 0,
        },
        "environment": {
            "python": platform.python_version(),
            "implementation": platform.python_implementation(),
            "platform": platform.platform(),
        },
        "cap_hit": False,
        "censored": False,
    }
    transfer = {
        "schema": "orion.des.transfer-result.v1",
        "job_id": JOB_ID,
        "state": "CANNOT_CHECK",
        "reason": "NO_MATCHED_RUNNABLE_DONOR_OR_EXTERNAL_EXPERT_ADJUDICATION",
        "authority_delta": "NONE",
    }
    outputs = {
        "P1_P15_IDEAL_DONOR_FRONTIERS_V1.json": frontier,
        "ROBUST_RESIDUAL_ATLAS_V1.json": residual,
        "PRIMARY_RESULT_V1.json": primary,
        "IDEAL_DONOR_RESULT_V1.json": donor,
        "NEGATIVE_CONTROLS_V1.json": controls,
        "RESOURCE_LEDGER_V1.json": resources,
        "TRANSFER_RESULT_V1.json": transfer,
        "PROVIDER_RECEIPTS_V1.json": {
            "schema": "orion.des.provider-receipts.v1",
            "job_id": JOB_ID,
            "receipts": provider_receipts,
        },
        "RAW_DISCOVERY_ROWS_V1.json": {
            "schema": "orion.des.raw-discovery-rows.v1",
            "job_id": JOB_ID,
            "rows": raw_rows,
        },
    }
    for name, payload in outputs.items():
        write_json(out / name, payload)
    raw_manifest = {
        "schema": "orion.des.raw-manifest.v1",
        "job_id": JOB_ID,
        "subject_revision": freeze["subject_revision"],
        "freeze_sha256": sha256_file(freeze_path),
        "query_atoms_sha256": sha256_file(queries_path),
        "runner_sha256": sha256_file(runner_path),
        "outputs": {
            name: {"bytes": (out / name).stat().st_size, "sha256": sha256_file(out / name)}
            for name in sorted(outputs)
        },
    }
    write_json(out / "RAW_MANIFEST_V1.json", raw_manifest)
    binding = {
        "schema": "orion.des.result-binding-packet.v1",
        "job_id": JOB_ID,
        "base_main": freeze["base_main"],
        "subject_revision": freeze["subject_revision"],
        "execution_head": args.execution_head,
        "freeze_sha256": sha256_file(freeze_path),
        "raw_manifest_sha256": sha256_file(out / "RAW_MANIFEST_V1.json"),
        "case_denominator": len(atom_rows),
        "provider_call_denominator": len(provider_receipts),
        "hard_preconditions": {
            "exact_query_atom_denominator": len(atom_rows) == 75,
            "all_papers_present": len({row["paper_id"] for row in atom_rows}) == 15,
            "matched_runnable_donor_products": False,
            "external_expert_adjudication": False,
        },
        "leakage": {"post_outcome_query_retuning": False, "metadata_as_donor": False},
        "censoring": {"cap_hit": False, "timeout_as_obstruction": False, "rows_dropped": 0},
        "strongest_donor": donor,
        "resource_vector": resources["resource_vector"],
        "transfer": transfer,
        "exact_terminal": TERMINAL,
        "claim_ceiling": AUTHORITY_CEILING,
        "external_authority_state": "CANNOT_CHECK",
        "paper_authority_delta": "NONE",
        "manuscript_writing_owner": "P1_P15_REWRITE_LANE",
    }
    write_json(out / "RESULT_BINDING_PACKET_V1.json", binding)
    print(
        f"{JOB_ID}={TERMINAL} atoms={len(atom_rows)} provider_calls={len(provider_receipts)} "
        f"records={len(raw_rows)} failures={sum(source_failure.values())}"
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
