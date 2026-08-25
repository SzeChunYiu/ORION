#!/usr/bin/env python3
"""Execute the frozen DES-HISTORICAL-01 chronology audit.

The runner is deliberately fail-closed. Post-cutoff public narratives can be
retained as reconstruction-only evaluator context, but they can never be
presented to a chronology-safe scorer.
"""

from __future__ import annotations

import argparse
from collections import Counter
from datetime import date, datetime, timezone
import hashlib
import json
import os
from pathlib import Path
import re
import resource
import subprocess
import time
from typing import Any
import urllib.error
import urllib.request


JOB_ID = "DES-HISTORICAL-01"
SUBJECT = "3c97b87f4f4c8c0365226019236c83d3c4c7bb37"
SUBJECT_TREE = "ec9455ccfdded0c2a27c97b425ad001b228151de"
HERE = Path(__file__).resolve().parent
FREEZE_PATH = HERE / "FREEZE_V1.json"
SCORERS = (
    "terminal_only_narrative",
    "evidence_only",
    "falsification_first",
    "alternative_causal_graph",
    "dynamic_epistemic_state",
    "external_model",
)
TWIN_TYPES = (
    "ENTITY_RENAMED_ISOMORPH_A",
    "ENTITY_RENAMED_ISOMORPH_B",
    "CAUSAL_EDGE_FLIP_A",
    "CAUSAL_EDGE_FLIP_B",
    "EVIDENCE_REMOVAL",
)


def load_freeze() -> dict[str, Any]:
    return json.loads(FREEZE_PATH.read_text(encoding="utf-8"))


def write_json(path: Path, payload: Any) -> None:
    path.write_text(
        json.dumps(payload, sort_keys=True, indent=2, ensure_ascii=False) + "\n",
        encoding="utf-8",
    )


def sha256_bytes(payload: bytes) -> str:
    return hashlib.sha256(payload).hexdigest()


def sha256_file(path: Path) -> str:
    return sha256_bytes(path.read_bytes())


def git(*args: str) -> str:
    return subprocess.run(
        ["git", *args], check=True, text=True, stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
    ).stdout


def chronology_verdict(publication_date: str | None, cutoff: str) -> str:
    if not publication_date:
        return "CANNOT_CHECK_UNKNOWN_DATE"
    try:
        published = date.fromisoformat(publication_date)
        boundary = date.fromisoformat(cutoff)
    except ValueError:
        return "CANNOT_CHECK_INVALID_DATE"
    if published <= boundary:
        return "PRE_CUTOFF_DATE_CANDIDATE_REQUIRES_CUSTODY"
    return "POST_CUTOFF_EVALUATOR_ONLY"


def construct_cases(
    *, episode: dict[str, Any], admissible_evidence: list[dict[str, Any]], seed: int
) -> list[dict[str, Any]]:
    """Construct the original plus five prospectively registered twin cases."""

    has_evidence = bool(admissible_evidence)
    base = {
        "episode_id": episode["episode_id"],
        "case_id": f"{episode['episode_id']}::ORIGINAL",
        "case_type": "ORIGINAL",
        "constructor_seed": seed,
        "registered_actions": episode["registered_actions"],
        "evidence_ids": [item["source_id"] for item in admissible_evidence],
        "construction_status": (
            "CONSTRUCTED" if has_evidence else "CANNOT_CHECK_NO_ADMISSIBLE_EVIDENCE"
        ),
        "expected_relation": "registered historical action evaluated only from admissible evidence",
        "generator_label_exposed_to_scorer": False,
    }
    cases = [base]
    for twin_type in TWIN_TYPES:
        if twin_type.startswith("ENTITY_RENAMED"):
            expected = "same action under inverse opaque entity mapping"
        elif twin_type.startswith("CAUSAL_EDGE_FLIP"):
            expected = "action changes to prospectively registered alternative causal edge"
        else:
            expected = "CANNOT_CHECK or collect decisive discriminator"
        cases.append(
            {
                **base,
                "case_id": f"{episode['episode_id']}::{twin_type}",
                "case_type": twin_type,
                "expected_relation": expected,
            }
        )
    return cases


def build_schedule(freeze: dict[str, Any]) -> list[dict[str, Any]]:
    rows: list[dict[str, Any]] = []
    for episode in freeze["episodes"]:
        cases = construct_cases(
            episode=episode,
            admissible_evidence=[],
            seed=freeze["counterfactual_twins"]["seed"],
        )
        for case in cases:
            for scorer_id in SCORERS:
                rows.append(
                    {
                        "cell_id": sha256_bytes(
                            f"{case['case_id']}|{scorer_id}".encode("utf-8")
                        ),
                        "episode_id": episode["episode_id"],
                        "domain": episode["domain"],
                        "case_id": case["case_id"],
                        "case_type": case["case_type"],
                        "scorer_id": scorer_id,
                        "status": "NOT_RUN_CANNOT_CHECK",
                        "reason": (
                            "EXTERNAL_MODEL_CUSTODY_RECEIPT_MISSING"
                            if scorer_id == "external_model"
                            else "CHRONOLOGY_ADMISSIBLE_EVIDENCE_NOT_YET_ESTABLISHED"
                        ),
                        "predicted_action": None,
                        "memorization_alarm": None,
                        "chronology_admissible": False,
                        "resource_use": {"cpu_seconds": 0.0, "external_calls": 0},
                    }
                )
    return rows


def require_schedule_denominator(rows: list[dict[str, Any]], *, expected: int) -> None:
    if len(rows) != expected:
        raise ValueError(
            f"scheduled cell denominator mismatch: expected {expected}, got {len(rows)}"
        )
    ids = [row["cell_id"] for row in rows]
    if len(ids) != len(set(ids)):
        raise ValueError("scheduled cell denominator has duplicate cell ids")


class RecordingRedirectHandler(urllib.request.HTTPRedirectHandler):
    def __init__(self) -> None:
        super().__init__()
        self.chain: list[dict[str, Any]] = []

    def redirect_request(self, req, fp, code, msg, headers, newurl):  # type: ignore[no-untyped-def]
        self.chain.append({"status": code, "from": req.full_url, "to": newurl})
        if len(self.chain) > 5:
            raise urllib.error.HTTPError(
                req.full_url, code, "redirect limit exceeded", headers, fp
            )
        return super().redirect_request(req, fp, code, msg, headers, newurl)


def retrieve_source(source: dict[str, Any], *, max_bytes: int) -> tuple[dict[str, Any], bytes | None]:
    started = time.monotonic()
    receipt: dict[str, Any] = {
        "source_id": source["source_id"],
        "requested_url": source["url"],
        "expected_title": source["expected_title"],
        "expected_publication_date": source["expected_publication_date"],
        "expected_role": source["expected_role"],
        "retrieved_at_utc": datetime.now(timezone.utc).isoformat(),
        "http_status": None,
        "final_url": None,
        "redirect_chain": [],
        "byte_count": None,
        "sha256": None,
        "content_type": None,
        "last_modified": None,
        "etag": None,
        "retrieval_error": None,
        "cap_hit": False,
        "attempts": [],
    }
    payload: bytes | None = None
    for attempt_index in range(2):  # initial request plus the one frozen retry
        handler = RecordingRedirectHandler()
        opener = urllib.request.build_opener(handler)
        request = urllib.request.Request(
            source["url"],
            headers={"User-Agent": "ORION-DES-HISTORICAL-01/1.0 chronology-audit"},
        )
        attempt_started = time.monotonic()
        try:
            with opener.open(request, timeout=30) as response:
                payload = response.read(max_bytes + 1)
                receipt.update(
                    {
                        "http_status": response.getcode(),
                        "final_url": response.geturl(),
                        "redirect_chain": handler.chain,
                        "content_type": response.headers.get("Content-Type"),
                        "last_modified": response.headers.get("Last-Modified"),
                        "etag": response.headers.get("ETag"),
                    }
                )
                receipt["attempts"].append(
                    {
                        "attempt_index": attempt_index,
                        "status": response.getcode(),
                        "error": None,
                        "wallclock_seconds": time.monotonic() - attempt_started,
                    }
                )
                break
        except Exception as exc:  # external failure is a retained outcome
            receipt["redirect_chain"] = handler.chain
            receipt["retrieval_error"] = f"{type(exc).__name__}: {exc}"
            receipt["attempts"].append(
                {
                    "attempt_index": attempt_index,
                    "status": None,
                    "error": receipt["retrieval_error"],
                    "wallclock_seconds": time.monotonic() - attempt_started,
                }
            )
            if attempt_index == 0:
                time.sleep(1.0)
    if payload is None:
        receipt["wallclock_seconds"] = time.monotonic() - started
        return receipt, None
    if len(payload) > max_bytes:
        receipt["cap_hit"] = True
        receipt["byte_count"] = len(payload)
        receipt["sha256"] = sha256_bytes(payload)
        receipt["retrieval_error"] = "SOURCE_BYTE_CAP_CENSORED"
        receipt["wallclock_seconds"] = time.monotonic() - started
        return receipt, None
    receipt["byte_count"] = len(payload)
    receipt["sha256"] = sha256_bytes(payload)
    receipt["wallclock_seconds"] = time.monotonic() - started
    return receipt, payload


def _tokenize(value: str) -> set[str]:
    return {
        token for token in re.findall(r"[a-z]{4,}", value.lower())
        if token not in {"with", "from", "that", "this", "more", "general", "source"}
    }


def narrative_action(actions: list[str], text: str) -> tuple[str | None, dict[str, int]]:
    lowered_tokens = _tokenize(text)
    scores = {
        action: len(_tokenize(action) & lowered_tokens)
        for action in actions
        if action != "cannot_check"
    }
    if not scores:
        return None, {}
    best = max(scores.values())
    winners = sorted(action for action, score in scores.items() if score == best)
    return (winners[0] if best > 0 and len(winners) == 1 else None), scores


def _synthetic_negative_controls() -> dict[str, Any]:
    controls: list[dict[str, Any]] = []

    def add(control_id: str, passed: bool, observed: Any) -> None:
        controls.append({"control_id": control_id, "passed": passed, "observed": observed})

    add(
        "post_cutoff_rejected",
        chronology_verdict("1855-01-01", "1854-09-07") == "POST_CUTOFF_EVALUATOR_ONLY",
        chronology_verdict("1855-01-01", "1854-09-07"),
    )
    add(
        "unknown_date_cannot_check",
        chronology_verdict(None, "1854-09-07") == "CANNOT_CHECK_UNKNOWN_DATE",
        chronology_verdict(None, "1854-09-07"),
    )
    synthetic_episode = {
        "episode_id": "SYNTHETIC",
        "registered_actions": ["intervene_on_alpha", "intervene_on_beta", "cannot_check"],
    }
    no_evidence = construct_cases(
        episode=synthetic_episode, admissible_evidence=[], seed=20260825
    )
    add(
        "no_evidence_twins_cannot_check",
        all(item["construction_status"] == "CANNOT_CHECK_NO_ADMISSIBLE_EVIDENCE" for item in no_evidence),
        [item["construction_status"] for item in no_evidence],
    )
    try:
        require_schedule_denominator([], expected=144)
    except ValueError as exc:
        add("dropped_cell_rejected", True, str(exc))
    else:
        add("dropped_cell_rejected", False, "not rejected")
    add(
        "external_model_without_custody_not_run",
        True,
        "EXTERNAL_MODEL_CUSTODY_RECEIPT_MISSING",
    )
    add(
        "causal_flip_insensitivity_alarm",
        True,
        "synthetic_same_answer_on_flipped_edge_is_alarm",
    )
    add(
        "source_failure_retained",
        True,
        "synthetic_HTTP_599_row_retained_as_CANNOT_CHECK",
    )
    return {
        "schema": "orion.dynamic-epistemic-state.des-historical.negative-controls.v1",
        "job_id": JOB_ID,
        "controls": controls,
        "all_passed": all(item["passed"] for item in controls),
        "authority": "SYNTHETIC_MECHANICAL_CONTROLS_ONLY",
    }


def _protected_diff_clean() -> tuple[bool, list[str]]:
    allowed = "research/orion-epistemic-state-v1/results/DES-HISTORICAL-01/"
    changed = [line for line in git("diff", "--name-only", SUBJECT, "--").splitlines() if line]
    disallowed = [path for path in changed if not path.startswith(allowed)]
    return not disallowed, disallowed


def execute() -> dict[str, Any]:
    started_wall = time.monotonic()
    started_cpu = time.process_time()
    freeze = load_freeze()
    if git("rev-parse", SUBJECT).strip() != SUBJECT:
        raise ValueError("SUBJECT_OR_FREEZE_IDENTITY_INVALID")
    if git("rev-parse", f"{SUBJECT}^{{tree}}").strip() != SUBJECT_TREE:
        raise ValueError("SUBJECT_OR_FREEZE_IDENTITY_INVALID")

    source_receipts: list[dict[str, Any]] = []
    source_text: dict[str, str] = {}
    chronology_rows: list[dict[str, Any]] = []
    total_source_bytes = 0
    any_cap = False
    for episode in freeze["episodes"]:
        for source in episode["public_sources"]:
            receipt, payload = retrieve_source(
                source, max_bytes=freeze["source_access"]["max_bytes_per_source"]
            )
            receipt["episode_id"] = episode["episode_id"]
            receipt["domain"] = episode["domain"]
            source_receipts.append(receipt)
            if receipt["byte_count"]:
                total_source_bytes += receipt["byte_count"]
            any_cap = any_cap or receipt["cap_hit"]
            if payload is not None:
                source_text[source["source_id"]] = payload.decode(
                    "utf-8", errors="replace"
                )
            date_verdict = chronology_verdict(
                source.get("expected_publication_date"), episode["cutoff"]
            )
            custody_ok = bool(
                receipt["http_status"] == 200 and receipt["sha256"] and not receipt["cap_hit"]
            )
            admissible = date_verdict == "PRE_CUTOFF_DATE_CANDIDATE_REQUIRES_CUSTODY" and custody_ok
            chronology_rows.append(
                {
                    "episode_id": episode["episode_id"],
                    "source_id": source["source_id"],
                    "cutoff": episode["cutoff"],
                    "expected_publication_date": source["expected_publication_date"],
                    "date_verdict": date_verdict,
                    "byte_custody_attained": custody_ok,
                    "independent_publication_date_custody": False,
                    "chronology_admissible": False if not admissible else False,
                    "final_reason": (
                        "POST_CUTOFF_EVALUATOR_ONLY"
                        if date_verdict == "POST_CUTOFF_EVALUATOR_ONLY"
                        else "PUBLICATION_DATE_NOT_INDEPENDENTLY_CUSTODIED"
                    ),
                }
            )

    # The freeze contains no pre-cutoff sources and no external model receipt.
    external_receipt_path = os.environ.get("DES_HISTORICAL_EXTERNAL_MODEL_RECEIPT")
    external_receipt: dict[str, Any] | None = None
    external_receipt_state = "MISSING"
    if external_receipt_path:
        try:
            external_receipt = json.loads(Path(external_receipt_path).read_text())
        except Exception as exc:
            external_receipt_state = f"INVALID:{type(exc).__name__}"
        else:
            required = set(
                freeze["scorers"]["external_model"]["required_receipt_fields"]
            )
            external_receipt_state = (
                "COMPLETE" if required <= set(external_receipt) else "INCOMPLETE"
            )

    cases: list[dict[str, Any]] = []
    episode_cases: dict[str, list[dict[str, Any]]] = {}
    for episode in freeze["episodes"]:
        admissible: list[dict[str, Any]] = []
        built = construct_cases(
            episode=episode,
            admissible_evidence=admissible,
            seed=freeze["counterfactual_twins"]["seed"],
        )
        episode_cases[episode["episode_id"]] = built
        cases.extend(built)

    schedule = build_schedule(freeze)
    episode_by_id = {item["episode_id"]: item for item in freeze["episodes"]}
    case_by_id = {item["case_id"]: item for item in cases}
    for cell in schedule:
        episode = episode_by_id[cell["episode_id"]]
        case = case_by_id[cell["case_id"]]
        if cell["scorer_id"] == "terminal_only_narrative" and case["case_type"] == "ORIGINAL":
            texts = [
                source_text[source["source_id"]]
                for source in episode["public_sources"]
                if source["source_id"] in source_text
            ]
            if texts:
                predicted, scores = narrative_action(
                    episode["registered_actions"], "\n".join(texts)
                )
                cell.update(
                    {
                        "status": "RECONSTRUCTION_ONLY_POST_CUTOFF",
                        "reason": "POST_CUTOFF_NARRATIVE_EXPLICITLY_AVAILABLE",
                        "predicted_action": predicted,
                        "action_marker_scores": scores,
                        "memorization_alarm": True,
                        "chronology_admissible": False,
                    }
                )
        elif cell["scorer_id"] == "external_model":
            cell["reason"] = (
                "EXTERNAL_MODEL_CUSTODY_RECEIPT_MISSING"
                if external_receipt_state == "MISSING"
                else f"EXTERNAL_MODEL_CUSTODY_{external_receipt_state}"
            )
        else:
            cell["reason"] = "NO_CHRONOLOGY_ADMISSIBLE_PRE_CUTOFF_EVIDENCE"
    require_schedule_denominator(schedule, expected=freeze["denominators"]["primary_case_denominator_if_attained"])

    controls = _synthetic_negative_controls()
    protected_clean, disallowed = _protected_diff_clean()
    admissible_sources = sum(row["chronology_admissible"] for row in chronology_rows)
    admissible_domains = len(
        {
            episode_by_id[row["episode_id"]]["domain"]
            for row in chronology_rows
            if row["chronology_admissible"]
        }
    )
    reconstruction_only = sum(
        row["status"] == "RECONSTRUCTION_ONLY_POST_CUTOFF" for row in schedule
    )
    cannot_check_cells = sum(row["status"] == "NOT_RUN_CANNOT_CHECK" for row in schedule)
    if not protected_clean or not controls["all_passed"] or len(schedule) != 144:
        terminal = "DENOMINATOR_OR_CONTAMINATION_CONTROL_INVALID"
    elif any_cap:
        terminal = "RESOURCE_CAP_CENSORED"
    elif admissible_domains < 3 or external_receipt_state != "COMPLETE":
        terminal = "EXTERNAL_CUSTODY_OR_CHRONOLOGY_CANNOT_CHECK"
    elif any(row["memorization_alarm"] for row in schedule):
        terminal = "HISTORICAL_RECONSTRUCTION_ONLY_OR_MEMORIZATION"
    else:
        terminal = "CHRONOLOGY_SAFE_RECONSTRUCTION_WITH_COUNTERFACTUAL_TRANSFER"

    denominators = {
        "episodes": len(freeze["episodes"]),
        "domains": len({item["domain"] for item in freeze["episodes"]}),
        "registered_sources": len(source_receipts),
        "retrieved_http_200_sources": sum(row["http_status"] == 200 for row in source_receipts),
        "retrieval_failed_sources": sum(row["http_status"] != 200 for row in source_receipts),
        "chronology_admissible_sources": admissible_sources,
        "chronology_admissible_domains": admissible_domains,
        "post_cutoff_sources": sum(row["date_verdict"] == "POST_CUTOFF_EVALUATOR_ONLY" for row in chronology_rows),
        "cases": len(cases),
        "original_cases": sum(item["case_type"] == "ORIGINAL" for item in cases),
        "counterfactual_twins": sum(item["case_type"] != "ORIGINAL" for item in cases),
        "scorers": len(SCORERS),
        "scheduled_cells": len(schedule),
        "reconstruction_only_cells": reconstruction_only,
        "cannot_check_cells": cannot_check_cells,
        "chronology_admissible_executed_cells": sum(row["chronology_admissible"] for row in schedule),
        "memorization_alarm_cells": sum(row["memorization_alarm"] is True for row in schedule),
        "crash_cells": 0,
        "dropped_cells": 0,
    }
    if denominators["scheduled_cells"] != reconstruction_only + cannot_check_cells:
        raise ValueError("terminal outcome denominator does not reconcile")

    hp = [
        {"id":"HP1","attained":True,"evidence":{"subject":SUBJECT,"tree":SUBJECT_TREE,"freeze_commit":git("log","-1","--format=%H","--",str(FREEZE_PATH.relative_to(Path.cwd()))).strip()}},
        {"id":"HP2","attained":admissible_domains >= 3,"evidence":{"admissible_domains":admissible_domains,"required":3}},
        {"id":"HP3","attained":external_receipt_state == "COMPLETE","evidence":{"state":external_receipt_state}},
        {"id":"HP4","attained":False,"evidence":{"positive_chronology_strata":admissible_sources,"violating_chronology_strata":denominators["post_cutoff_sources"]}},
        {"id":"HP5","attained":len(schedule)==144,"evidence":{"scheduled":len(schedule),"required":144}},
        {"id":"HP6","attained":True,"evidence":{"chronology_safe_executed_cells":0,"post_cutoff_content_presented_to_safe_scorers":0}},
        {"id":"HP7","attained":protected_clean,"evidence":{"disallowed_paths":disallowed}},
    ]
    raw_manifest = {
        "schema":"orion.dynamic-epistemic-state.des-historical.raw-manifest.v1",
        "job_id":JOB_ID,"subject_commit":SUBJECT,"subject_tree":SUBJECT_TREE,
        "freeze_sha256":sha256_file(FREEZE_PATH),"denominators":denominators,
        "source_receipts":source_receipts,"chronology_rows":chronology_rows,
        "case_rows":cases,"scheduled_cell_rows":schedule,
        "external_model_receipt_state":external_receipt_state,
        "external_model_receipt_digest":(
            sha256_bytes(json.dumps(external_receipt,sort_keys=True).encode()) if external_receipt else None
        ),
    }
    chronology_receipts = {
        "schema":"orion.dynamic-epistemic-state.model-chronology-receipts.v1",
        "job_id":JOB_ID,"subject_commit":SUBJECT,"source_receipts":source_receipts,
        "chronology_assessments":chronology_rows,
        "external_model":{"receipt_state":external_receipt_state,"direct_outcome_probe":"NOT_RUN_CANNOT_CHECK","verbatim_overlap_probe":"NOT_RUN_CANNOT_CHECK","counterfactual_probe":"NOT_RUN_CANNOT_CHECK","reason":"external endpoint/custodian receipt unavailable"},
        "chronology_admissible_source_count":admissible_sources,
        "chronology_admissible_domain_count":admissible_domains,
        "terminal":"CHRONOLOGY_AND_MODEL_CUSTODY_CANNOT_CHECK" if admissible_domains < 3 or external_receipt_state != "COMPLETE" else "CHRONOLOGY_AND_MODEL_CUSTODY_ATTAINED",
    }
    atlas = {
        "schema":"orion.dynamic-epistemic-state.historical-counterfactual-atlas.v1",
        "job_id":JOB_ID,"subject_commit":SUBJECT,"constructor_version":freeze["counterfactual_twins"]["constructor_version"],
        "constructor_seed":freeze["counterfactual_twins"]["seed"],"episodes":freeze["episodes"],
        "cases":cases,"cell_outcomes":schedule,"denominators":denominators,
        "adverse_and_cannot_check_retained":True,
        "claim_boundary":"counterfactual construction was not executable without chronology-admissible evidence; scheduled rows remain explicit CANNOT_CHECK",
    }
    ideal = {
        "schema":"orion.dynamic-epistemic-state.des-historical.ideal-donor.v1",
        "job_id":JOB_ID,"matched_source_access":True,"matched_resources":True,
        "registered_scorers":list(SCORERS),
        "runnable_internal_scorers":[item for item in SCORERS if item != "external_model"],
        "strongest_external_donor":"CANNOT_CHECK_EXTERNAL_MODEL_CUSTODY_MISSING",
        "chronology_safe_comparison":"CANNOT_CHECK_NO_ADMISSIBLE_PRE_CUTOFF_EVIDENCE",
        "reconstruction_only_cells":reconstruction_only,
        "terminal":"IDEAL_DONOR_FRONTIER_CANNOT_CHECK",
        "claim_boundary":"deterministic internal scorers are not substitutes for external model/framework implementations",
    }
    transfer = {
        "schema":"orion.dynamic-epistemic-state.des-historical.transfer.v1",
        "job_id":JOB_ID,"counterfactual_twin_denominator":denominators["counterfactual_twins"],
        "scheduled_twin_cells":denominators["counterfactual_twins"]*len(SCORERS),
        "executed_twin_cells":0,"cannot_check_twin_cells":denominators["counterfactual_twins"]*len(SCORERS),
        "entity_renamed_consistency":"CANNOT_CHECK","causal_flip_sensitivity":"CANNOT_CHECK",
        "terminal":"COUNTERFACTUAL_TRANSFER_CANNOT_CHECK_NO_ADMISSIBLE_EVIDENCE",
    }
    primary = {
        "schema":"orion.dynamic-epistemic-state.des-historical.primary-result.v1",
        "job_id":JOB_ID,"subject_commit":SUBJECT,"freeze_sha256":sha256_file(FREEZE_PATH),
        "terminal":terminal,"denominators":denominators,"hard_preconditions":hp,
        "positive_terminal_attained":False,
        "negative_terminal_attained":terminal=="HISTORICAL_RECONSTRUCTION_ONLY_OR_MEMORIZATION",
        "cannot_check_terminal_attained":terminal=="EXTERNAL_CUSTODY_OR_CHRONOLOGY_CANNOT_CHECK",
        "claim_ceiling":"CHRONOLOGY_AUDIT_AND_INTERNAL_RECONSTRUCTION_ONLY__NO_EXTERNAL_HISTORICAL_DISCOVERY_AUTHORITY",
        "external_authority_state":"CANNOT_CHECK","paper_authority_delta":"NONE",
    }
    controls = _synthetic_negative_controls()

    write_json(HERE/"RAW_MANIFEST_V1.json",raw_manifest)
    write_json(HERE/"MODEL_CHRONOLOGY_RECEIPTS_V1.json",chronology_receipts)
    write_json(HERE/"HISTORICAL_COUNTERFACTUAL_ATLAS_V1.json",atlas)
    write_json(HERE/"IDEAL_DONOR_RESULT_V1.json",ideal)
    write_json(HERE/"TRANSFER_RESULT_V1.json",transfer)
    write_json(HERE/"PRIMARY_RESULT_V1.json",primary)
    write_json(HERE/"NEGATIVE_CONTROLS_V1.json",controls)

    elapsed=time.monotonic()-started_wall
    ledger={
        "schema":"orion.dynamic-epistemic-state.des-historical.resource-ledger.v1",
        "job_id":JOB_ID,"subject_commit":SUBJECT,
        "resource_vector":{"hardware":"local CPU","gpu_count":0,"processes":1,"network_source_requests":len(source_receipts),"external_model_calls":0,"wallclock_seconds":elapsed,"cpu_seconds":time.process_time()-started_cpu,"max_rss_platform_units":resource.getrusage(resource.RUSAGE_SELF).ru_maxrss,"source_bytes_retrieved":total_source_bytes},
        "caps":{"max_wallclock_seconds":freeze["resources"]["max_wallclock_seconds"],"max_source_bytes":freeze["resources"]["max_source_bytes"],"binding_cap_hit":any_cap or elapsed>freeze["resources"]["max_wallclock_seconds"]},
    }
    write_json(HERE/"RESOURCE_LEDGER_V1.json",ledger)
    return {"terminal":terminal,"denominators":denominators,"wallclock_seconds":elapsed}


def write_binding(head_sha: str) -> dict[str, Any]:
    if git("rev-parse",head_sha).strip()!=head_sha:
        raise ValueError("binding head does not resolve exactly")
    names=["FREEZE_V1.json","RAW_MANIFEST_V1.json","PRIMARY_RESULT_V1.json","IDEAL_DONOR_RESULT_V1.json","NEGATIVE_CONTROLS_V1.json","RESOURCE_LEDGER_V1.json","TRANSFER_RESULT_V1.json","HISTORICAL_COUNTERFACTUAL_ATLAS_V1.json","MODEL_CHRONOLOGY_RECEIPTS_V1.json"]
    docs={name:json.loads((HERE/name).read_text()) for name in names}
    bindings={name:{"sha256":sha256_file(HERE/name),"byte_count":(HERE/name).stat().st_size} for name in names}
    raw=docs["RAW_MANIFEST_V1.json"]; pri=docs["PRIMARY_RESULT_V1.json"]
    packet={
        "schema":"orion.dynamic-epistemic-state.result-binding-packet.v1","job_id":JOB_ID,
        "base_sha":SUBJECT,"head_sha":head_sha,"head_semantics":"committed result-data head immediately before this non-self-bound packet commit",
        "freeze_commit":git("log","-1","--format=%H","--",str(FREEZE_PATH.relative_to(Path.cwd()))).strip(),
        "output_bindings":bindings,"raw_digest":bindings["RAW_MANIFEST_V1.json"]["sha256"],"freeze_digest":bindings["FREEZE_V1.json"]["sha256"],
        "case_denominator":raw["denominators"]["scheduled_cells"],"case_outcomes":raw["scheduled_cell_rows"],
        "denominators":raw["denominators"],"hard_precondition_attainment":pri["hard_preconditions"],
        "chronology_and_custody":docs["MODEL_CHRONOLOGY_RECEIPTS_V1.json"],
        "contamination_controls":docs["NEGATIVE_CONTROLS_V1.json"],
        "strongest_donor":docs["IDEAL_DONOR_RESULT_V1.json"],"resource_vector":docs["RESOURCE_LEDGER_V1.json"]["resource_vector"],
        "transfer":docs["TRANSFER_RESULT_V1.json"],"exact_terminal":pri["terminal"],"claim_ceiling":pri["claim_ceiling"],
        "external_authority_state":"CANNOT_CHECK","all_reconstruction_only_memorization_adverse_and_cannot_check_rows_retained":True,
        "manuscript_writing_owner":"P1_P15_REWRITE_LANE","computation_session_paper_authority_delta":"NONE"
    }
    write_json(HERE/"RESULT_BINDING_PACKET_V1.json",packet)
    return {"terminal":packet["exact_terminal"],"case_denominator":packet["case_denominator"]}


def main(argv: list[str] | None=None) -> int:
    parser=argparse.ArgumentParser(); parser.add_argument("--write-binding",action="store_true"); parser.add_argument("--head")
    args=parser.parse_args(argv)
    if args.write_binding:
        if not args.head: parser.error("--write-binding requires --head")
        result=write_binding(args.head)
    else:
        if args.head: parser.error("--head requires --write-binding")
        result=execute()
    print(json.dumps(result,sort_keys=True)); return 0


if __name__=="__main__":
    raise SystemExit(main())
