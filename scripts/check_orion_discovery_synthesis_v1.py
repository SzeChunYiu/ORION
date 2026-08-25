from __future__ import annotations

import json
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
RESEARCH = ROOT / "research" / "orion-discovery-v1"


def _load(name: str) -> dict[str, object]:
    path = RESEARCH / name
    with path.open("r", encoding="utf-8") as handle:
        payload = json.load(handle)
    if not isinstance(payload, dict):
        raise ValueError(f"{name} must contain an object")
    return payload


def main() -> int:
    theorem = _load("DISCOVERY_SYNTHESIS_THEOREM_LEDGER_V1.json")
    backlog = _load("DISCOVERY_SYNTHESIS_COMPUTE_BACKLOG_V1.json")
    receipt = _load("DISCOVERY_SYNTHESIS_COMPLETION_RECEIPT_V1.json")

    theorems = theorem.get("theorems")
    if not isinstance(theorems, list) or theorem.get("theorem_count") != len(theorems):
        raise ValueError("synthesis theorem count mismatch")
    ids = [row.get("id") for row in theorems if isinstance(row, dict)]
    if len(ids) != len(theorems) or len(ids) != len(set(ids)):
        raise ValueError("synthesis theorem IDs must be unique and present")
    required_prefixes = {"SYN-T", "NAV-T"}
    if not all(any(str(item).startswith(prefix) for prefix in required_prefixes) for item in ids):
        raise ValueError("unexpected synthesis theorem ID")
    for row in theorems:
        if not isinstance(row, dict):
            raise ValueError("theorem row must be an object")
        for field in (
            "id",
            "title",
            "statement_class",
            "status",
            "assumptions",
            "proof_artifact",
            "falsifier",
            "authority_ceiling",
        ):
            if field not in row or row[field] in (None, "", []):
                raise ValueError(f"theorem {row.get('id')} lacks {field}")
        proof = RESEARCH / str(row["proof_artifact"]).split("#", 1)[0]
        if not proof.exists():
            raise ValueError(f"theorem proof artifact does not exist: {proof}")
        executable = row.get("executable_artifact")
        if executable and not (ROOT / str(executable)).exists():
            raise ValueError(f"executable theorem artifact does not exist: {executable}")

    jobs = backlog.get("jobs")
    if not isinstance(jobs, list) or backlog.get("job_count") != len(jobs):
        raise ValueError("synthesis backlog job count mismatch")
    job_ids = [row.get("job_id") for row in jobs if isinstance(row, dict)]
    if len(job_ids) != len(jobs) or len(job_ids) != len(set(job_ids)):
        raise ValueError("synthesis backlog job IDs must be unique and present")
    for row in jobs:
        if not isinstance(row, dict):
            raise ValueError("backlog row must be an object")
        for field in (
            "job_id",
            "mode",
            "question",
            "reason_compute_needed",
            "frozen_inputs",
            "required_outputs",
            "positive_terminal",
            "negative_terminal",
            "cannot_check_terminal",
        ):
            if field not in row or row[field] in (None, "", []):
                raise ValueError(f"job {row.get('job_id')} lacks {field}")

    if receipt.get("theorem_entries") != len(theorems):
        raise ValueError("completion receipt theorem count mismatch")
    if receipt.get("compute_jobs_frozen") != len(jobs):
        raise ValueError("completion receipt job count mismatch")
    if receipt.get("focused_tests_passed") != 15:
        raise ValueError("completion receipt focused test count mismatch")
    authority = receipt.get("authority")
    if not isinstance(authority, dict) or authority.get("paper_authority_delta") != "NONE":
        raise ValueError("completion receipt authority boundary missing")

    hashes = receipt.get("content_sha256")
    if not isinstance(hashes, dict) or not hashes:
        raise ValueError("completion receipt content manifest missing")
    import hashlib

    for relative, expected in hashes.items():
        path = ROOT / str(relative)
        if not path.is_file():
            raise ValueError(f"completion manifest path missing: {relative}")
        actual = hashlib.sha256(path.read_bytes()).hexdigest()
        if actual != expected:
            raise ValueError(f"completion manifest hash mismatch: {relative}")

    required_files = (
        "COMPOSITION_TRANSFER_COMPLETION_CALCULUS_V1.md",
        "DISCOVERY_EVENT_NORMAL_FORM_V1.md",
        "FRONTIER_MATH_NAVIGATION_PROTOCOL_V1.md",
        "AI_EXECUTOR_PROMPT_SYNTHESIS_V1.md",
        "DISCOVERY_SYNTHESIS_COMPLETION_RECEIPT_V1.json",
    )
    for name in required_files:
        if not (RESEARCH / name).is_file():
            raise ValueError(f"missing synthesis research artifact: {name}")

    print(
        "ORION_DISCOVERY_SYNTHESIS_V1_GREEN "
        f"theorems={len(theorems)} jobs={len(jobs)}"
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
