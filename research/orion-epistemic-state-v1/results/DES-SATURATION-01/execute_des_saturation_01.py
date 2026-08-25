#!/usr/bin/env python3
"""Execute frozen DES-SATURATION-01 on the bound four-case local panel."""
from __future__ import annotations

import dataclasses
from fractions import Fraction
import hashlib
import inspect
import json
from pathlib import Path
import platform
import re
import resource
import subprocess
import sys
import time
from typing import Any, Callable, Iterable, Sequence


HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[3]
FREEZE_PATH = HERE / "FREEZE_V1.json"
RAW_PATH = HERE / "RAW_CASES_V1.jsonl"
PANEL_PATH = ROOT / "papers/paper-02-open-world-scientific-discovery/structural_extension/HISTORICAL_PANEL_V1.json"
SUMMARY_PATH = ROOT / "papers/paper-02-open-world-scientific-discovery/structural_extension/HISTORICAL_PILOT_SUMMARY_V1.json"
SUBJECT_COMMIT = "3c97b87f4f4c8c0365226019236c83d3c4c7bb37"
TOKEN = re.compile(r"[a-z0-9]+")
SEEDS = tuple(202608250601 + index for index in range(64))
POLICY_IDS = ("nearest-neighbour", "diversified", "random-remote", "analogy", "structural-jump")
HIGHER_IS_BETTER = (
    "validated_transfer_gain",
    "coordinate_gain",
    "obligation_gain",
    "support_gain",
    "remote_method_gain",
    "frontier_gain",
)
LOWER_IS_BETTER = ("false_analogy_harm",)

sys.path.insert(0, str(ROOT / "src"))
from orion.transfer.v2.canonical import content_digest  # noqa: E402
from orion.transfer.v2.p2_structure import (  # noqa: E402
    CandidateMethodSignature,
    StructuralCandidateStatus,
    StructuralNeed,
    assess_structural_candidate,
    structural_match_score,
)


def canonical_bytes(value: Any) -> bytes:
    return (json.dumps(value, sort_keys=True, separators=(",", ":")) + "\n").encode()


def sha256_bytes(payload: bytes) -> str:
    return hashlib.sha256(payload).hexdigest()


def write_json(path: Path, value: Any) -> None:
    path.write_bytes(canonical_bytes(value))


def file_receipt(path: Path) -> dict[str, Any]:
    payload = path.read_bytes()
    return {"path": str(path.relative_to(ROOT)), "bytes": len(payload), "sha256": sha256_bytes(payload)}


def fraction_text(value: Fraction) -> str:
    return f"{value.numerator}/{value.denominator}"


def normalize(value: Any) -> Any:
    if isinstance(value, Fraction):
        return fraction_text(value)
    if dataclasses.is_dataclass(value):
        return {field.name: normalize(getattr(value, field.name)) for field in dataclasses.fields(value)}
    if isinstance(value, dict):
        return {str(key): normalize(item) for key, item in sorted(value.items(), key=lambda pair: str(pair[0]))}
    if isinstance(value, (set, frozenset, tuple, list)):
        sequence = sorted(value) if isinstance(value, (set, frozenset)) else value
        return [normalize(item) for item in sequence]
    if hasattr(value, "value"):
        return normalize(value.value)
    return value


def tokens(*values: str) -> frozenset[str]:
    output: set[str] = set()
    for value in values:
        output.update(TOKEN.findall(value.lower()))
    return frozenset(output)


def jaccard(left: frozenset[str], right: frozenset[str]) -> Fraction:
    if not left and not right:
        return Fraction(1)
    if not left or not right:
        return Fraction(0)
    return Fraction(len(left & right), len(left | right))


def candidate_public_content(raw: dict[str, Any]) -> dict[str, Any]:
    return {
        "surface_text": str(raw["surface_text"]),
        "domain": str(raw["domain"]),
        "assumptions": sorted(str(item) for item in raw.get("assumptions", [])),
        "invariants": sorted(str(item) for item in raw.get("invariants", [])),
        "effects": sorted(str(item) for item in raw.get("effects", [])),
        "reconstruction": None if raw.get("reconstruction") is None else str(raw["reconstruction"]),
    }


def candidate_key(raw: dict[str, Any]) -> str:
    return sha256_bytes(canonical_bytes(candidate_public_content(raw)))


POLICY_CASE_KEYS = frozenset({"target_text", "target_domain", "need", "candidates"})
CANDIDATE_KEYS = frozenset({"content_key", "surface_text", "domain", "assumptions", "invariants", "effects", "reconstruction"})


def sanitize_case(raw: dict[str, Any]) -> dict[str, Any]:
    candidates = []
    for item in raw["candidates"]:
        public = candidate_public_content(item)
        public["content_key"] = candidate_key(item)
        candidates.append(public)
    return {
        "target_text": str(raw["target_text"]),
        "target_domain": str(raw["target_domain"]),
        "need": {
            key: normalize(raw["need"].get(key, [] if key != "reconstruction" else None))
            for key in ("assumptions", "invariants", "effects", "failure_signature", "representation_signature", "reconstruction")
        },
        "candidates": candidates,
    }


def validate_policy_payload(case: dict[str, Any]) -> None:
    if frozenset(case) != POLICY_CASE_KEYS:
        raise ValueError("policy payload contains forbidden or missing case fields")
    if not isinstance(case["candidates"], list) or len(case["candidates"]) != 4:
        raise ValueError("policy payload candidate count invalid")
    for candidate in case["candidates"]:
        if frozenset(candidate) != CANDIDATE_KEYS:
            raise ValueError("policy payload contains forbidden or missing candidate fields")
    keys = [candidate["content_key"] for candidate in case["candidates"]]
    if len(keys) != len(set(keys)):
        raise ValueError("policy payload candidate public content is not unique")


def tie_key(candidate: dict[str, Any]) -> str:
    return str(candidate["content_key"])


def nearest_policy(case: dict[str, Any]) -> tuple[list[str], dict[str, int]]:
    validate_policy_payload(case)
    target = tokens(case["target_text"])
    rows = [(jaccard(target, tokens(item["surface_text"])), tie_key(item)) for item in case["candidates"]]
    ranking = [key for _, key in sorted(rows, key=lambda row: (-row[0], row[1]))]
    return ranking, {"candidate_score_evaluations": 4, "pairwise_similarity_evaluations": 0}


def diversified_policy(case: dict[str, Any]) -> tuple[list[str], dict[str, int]]:
    validate_policy_payload(case)
    target = tokens(case["target_text"])
    candidates = {tie_key(item): item for item in case["candidates"]}
    relevance = {key: jaccard(target, tokens(item["surface_text"])) for key, item in candidates.items()}
    selected: list[str] = []
    pairwise = 0
    while len(selected) < len(candidates):
        rows = []
        for key, item in candidates.items():
            if key in selected:
                continue
            if not selected:
                novelty = Fraction(1)
            else:
                similarities = [
                    jaccard(tokens(item["surface_text"]), tokens(candidates[other]["surface_text"]))
                    for other in selected
                ]
                pairwise += len(similarities)
                novelty = Fraction(1) - max(similarities)
            score = Fraction(3, 4) * relevance[key] + Fraction(1, 4) * novelty
            rows.append((score, key))
        selected.append(sorted(rows, key=lambda row: (-row[0], row[1]))[0][1])
    return selected, {"candidate_score_evaluations": 4, "pairwise_similarity_evaluations": pairwise}


def random_remote_policy(case: dict[str, Any], seed: int) -> tuple[list[str], dict[str, int]]:
    validate_policy_payload(case)
    target_domain = case["target_domain"]
    rows = []
    for item in case["candidates"]:
        remote_group = 0 if item["domain"] != target_domain else 1
        random_key = sha256_bytes(f"{seed}|{tie_key(item)}".encode())
        rows.append((remote_group, random_key, tie_key(item)))
    ranking = [key for _, _, key in sorted(rows)]
    return ranking, {"candidate_score_evaluations": 4, "pairwise_similarity_evaluations": 0}


def analogy_policy(case: dict[str, Any]) -> tuple[list[str], dict[str, int]]:
    validate_policy_payload(case)
    need = case["need"]
    query = tokens(*(str(item) for item in (*need["representation_signature"], *need["failure_signature"])))
    rows = []
    for item in case["candidates"]:
        score = jaccard(query, tokens(item["surface_text"], item["domain"]))
        remote = item["domain"] != case["target_domain"]
        rows.append((score, remote, tie_key(item)))
    ranking = [key for _, _, key in sorted(rows, key=lambda row: (-row[0], -int(row[1]), row[2]))]
    return ranking, {"candidate_score_evaluations": 4, "pairwise_similarity_evaluations": 0}


def structural_need(case: dict[str, Any]) -> StructuralNeed:
    return StructuralNeed.from_mapping(
        need_id="des-saturation:public-need",
        source_object_id="des-saturation:public-target",
        source_object_digest=content_digest({"target_text": case["target_text"], "target_domain": case["target_domain"], "need": case["need"]}),
        coordinates=case["need"],
    )


def structural_candidate(item: dict[str, Any]) -> CandidateMethodSignature:
    return CandidateMethodSignature(
        candidate_id=item["content_key"],
        domain=item["domain"],
        assumptions=tuple(item["assumptions"]),
        invariants=tuple(item["invariants"]),
        effects=tuple(item["effects"]),
        reconstruction=item["reconstruction"],
        provenance_digest=f"sha256:{item['content_key']}",
    )


STATUS_ORDER = {
    StructuralCandidateStatus.CANDIDATE: 0,
    StructuralCandidateStatus.UNKNOWN: 1,
    StructuralCandidateStatus.OBSTRUCTION: 2,
}


def structural_policy(case: dict[str, Any]) -> tuple[list[str], dict[str, int]]:
    validate_policy_payload(case)
    need = structural_need(case)
    rows = []
    for item in case["candidates"]:
        candidate = structural_candidate(item)
        receipt = assess_structural_candidate(need, candidate)
        receipt.verify()
        score = Fraction(str(structural_match_score(need, candidate)))
        remote = item["domain"] != case["target_domain"]
        rows.append((STATUS_ORDER[receipt.status], score, remote, tie_key(item)))
    ranking = [key for _, _, _, key in sorted(rows, key=lambda row: (row[0], -row[1], -int(row[2]), row[3]))]
    return ranking, {"candidate_score_evaluations": 4, "pairwise_similarity_evaluations": 0}


POLICY_FUNCTIONS: dict[str, Callable[[dict[str, Any]], tuple[list[str], dict[str, int]]]] = {
    "nearest-neighbour": nearest_policy,
    "diversified": diversified_policy,
    "analogy": analogy_policy,
    "structural-jump": structural_policy,
}


def required_atoms(need: dict[str, Any]) -> frozenset[tuple[str, str]]:
    atoms: set[tuple[str, str]] = set()
    for field in ("assumptions", "invariants", "effects"):
        atoms.update((field, str(value)) for value in need[field])
    if need["reconstruction"] is not None:
        atoms.add(("reconstruction", str(need["reconstruction"])))
    return frozenset(atoms)


def candidate_atoms(candidate: dict[str, Any]) -> frozenset[tuple[str, str]]:
    atoms: set[tuple[str, str]] = set()
    for field in ("assumptions", "invariants", "effects"):
        atoms.update((field, str(value)) for value in candidate[field])
    if candidate["reconstruction"] is not None:
        atoms.add(("reconstruction", str(candidate["reconstruction"])))
    return frozenset(atoms)


def exact_structural_score(need: StructuralNeed, candidate: CandidateMethodSignature) -> tuple[StructuralCandidateStatus, Fraction]:
    receipt = assess_structural_candidate(need, candidate)
    receipt.verify()
    total = sum(bool(values) for values in (need.assumptions, need.invariants, need.effects)) + int(need.reconstruction is not None)
    if receipt.status is StructuralCandidateStatus.OBSTRUCTION:
        exact = Fraction(-1)
    elif total == 0:
        exact = Fraction(0)
    else:
        exact = Fraction(len(receipt.matched_coordinates), total)
        if receipt.status is StructuralCandidateStatus.UNKNOWN:
            exact -= Fraction(1, 4)
    observed = Fraction(str(structural_match_score(need, candidate)))
    if observed != exact:
        raise ValueError("bound structural_match_score disagrees with exact reconstruction")
    return receipt.status, exact


def gain_vector(public: dict[str, Any], prefix: Sequence[str], gold_key: str) -> dict[str, Fraction]:
    candidates = {item["content_key"]: item for item in public["candidates"]}
    selected = [candidates[key] for key in prefix]
    need_atoms = required_atoms(public["need"])
    covered_atoms = frozenset().union(*(candidate_atoms(item) for item in selected)) if selected else frozenset()
    coordinate_fields = {field for field, _ in need_atoms}
    covered_fields = {
        field
        for field in coordinate_fields
        if {atom for atom in need_atoms if atom[0] == field} <= covered_atoms
    }
    need = structural_need(public)
    statuses_scores = [exact_structural_score(need, structural_candidate(item)) for item in selected]
    support = any(status is StructuralCandidateStatus.CANDIDATE for status, _ in statuses_scores)
    remote_method = any(
        item["domain"] != public["target_domain"] and status is StructuralCandidateStatus.CANDIDATE
        for item, (status, _) in zip(selected, statuses_scores, strict=True)
    )
    frontier = max((Fraction(score + 1, 2) for _, score in statuses_scores), default=Fraction(0))
    top_obstruction = bool(statuses_scores and statuses_scores[0][0] is StructuralCandidateStatus.OBSTRUCTION)
    return {
        "validated_transfer_gain": Fraction(int(gold_key in prefix)),
        "coordinate_gain": Fraction(len(covered_fields), len(coordinate_fields)) if coordinate_fields else Fraction(0),
        "obligation_gain": Fraction(len(need_atoms & covered_atoms), len(need_atoms)) if need_atoms else Fraction(0),
        "support_gain": Fraction(int(support)),
        "remote_method_gain": Fraction(int(remote_method)),
        "frontier_gain": frontier,
        "false_analogy_harm": Fraction(int(top_obstruction)),
    }


def public_gain(vector: dict[str, Fraction]) -> tuple[Fraction, ...]:
    return tuple(vector[key] for key in ("coordinate_gain", "obligation_gain", "support_gain", "remote_method_gain", "frontier_gain"))


def mean_vectors(vectors: Sequence[dict[str, Fraction]]) -> dict[str, Fraction]:
    return {key: sum((item[key] for item in vectors), Fraction(0)) / len(vectors) for key in (*HIGHER_IS_BETTER, *LOWER_IS_BETTER)}


def ranking_complete(ranking: Sequence[str], public: dict[str, Any]) -> bool:
    expected = {item["content_key"] for item in public["candidates"]}
    return len(ranking) == len(expected) and set(ranking) == expected


def validate_substrate(panel: dict[str, Any], freeze: dict[str, Any]) -> list[dict[str, Any]]:
    checks: list[dict[str, Any]] = []
    cases = panel.get("cases", [])
    observed_ids = sorted(str(case.get("case_id", "")) for case in cases)
    checks.append({"check": "case_ids", "passed": observed_ids == sorted(freeze["substrate"]["case_ids"]), "observed": observed_ids})
    checks.append({"check": "case_count", "passed": len(cases) == 4, "observed": len(cases), "expected": 4})
    for case in cases:
        case_id = str(case.get("case_id", ""))
        candidates = case.get("candidates", [])
        checks.append({"check": f"{case_id}:candidate_count", "passed": len(candidates) == 4, "observed": len(candidates), "expected": 4})
        keys = [candidate_key(item) for item in candidates]
        checks.append({"check": f"{case_id}:candidate_public_uniqueness", "passed": len(keys) == len(set(keys)) == 4})
        try:
            donor_year = int(case["donor_primary_source"]["year"])
            transfer_year = int(case["transfer_validation_source"]["year"])
            cutoff_year = int(str(case["cutoff"])[:4])
            chronology = donor_year <= cutoff_year < transfer_year
        except (KeyError, TypeError, ValueError):
            chronology = False
        checks.append({"check": f"{case_id}:chronology", "passed": chronology})
        urls = bool(case.get("donor_primary_source", {}).get("url") and case.get("transfer_validation_source", {}).get("url"))
        checks.append({"check": f"{case_id}:source_urls", "passed": urls})
        try:
            public = sanitize_case(case)
            validate_policy_payload(public)
            payload_ok = True
        except Exception:
            payload_ok = False
        checks.append({"check": f"{case_id}:policy_payload", "passed": payload_ok})
    return checks


def git_bytes_at(commit: str, path: str) -> bytes:
    return subprocess.check_output(["git", "show", f"{commit}:{path}"], cwd=ROOT)


def hard_preconditions(panel: dict[str, Any], freeze: dict[str, Any]) -> dict[str, Any]:
    checks: list[dict[str, Any]] = []
    for path, expected in freeze["subject_bindings"].items():
        observed = sha256_bytes(git_bytes_at(SUBJECT_COMMIT, path))
        checks.append({"check": f"subject_binding:{path}", "passed": observed == expected, "expected": expected, "observed": observed})
    head = subprocess.check_output(["git", "rev-parse", "HEAD"], cwd=ROOT, text=True).strip()
    freeze_commits = subprocess.check_output(["git", "log", "--format=%H", "--", str(FREEZE_PATH.relative_to(ROOT))], cwd=ROOT, text=True).splitlines()
    freeze_commit = freeze_commits[-1] if freeze_commits else ""
    freeze_ancestor = bool(freeze_commit) and freeze_commit != head and subprocess.run(["git", "merge-base", "--is-ancestor", freeze_commit, head], cwd=ROOT, check=False).returncode == 0
    subject_ancestor = subprocess.run(["git", "merge-base", "--is-ancestor", SUBJECT_COMMIT, head], cwd=ROOT, check=False).returncode == 0
    checks.extend([
        {"check": "subject_commit_is_ancestor", "passed": subject_ancestor},
        {"check": "freeze_committed_before_execution", "passed": freeze_ancestor, "freeze_commit": freeze_commit, "execution_head": head},
        *validate_substrate(panel, freeze),
    ])
    return {"all_passed": all(item["passed"] for item in checks), "checks": checks, "execution_head_sha": head, "freeze_commit_sha": freeze_commit}


def reject_random_estimator(mode: str) -> None:
    if mode != "MEAN_ALL_FROZEN_SEEDS":
        raise ValueError("post-outcome random seed selection is forbidden")


def negative_controls(panel: dict[str, Any]) -> list[dict[str, Any]]:
    case = sorted(panel["cases"], key=lambda item: item["case_id"])[0]
    public = sanitize_case(case)
    controls: list[dict[str, Any]] = []

    for control_id, field in (("LEAK-GOLD", "gold_candidate_id"), ("LEAK-FAMILY", "family")):
        mutated = dict(public)
        mutated[field] = "forbidden"
        try:
            nearest_policy(mutated)
            passed = False
            observed = "ACCEPTED"
        except ValueError as exc:
            passed = True
            observed = f"REJECTED:{exc}"
        controls.append({"control_id": control_id, "passed": passed, "observed": observed})

    renamed = json.loads(json.dumps(case))
    renamed["case_id"] = "renamed-case"
    for index, candidate in enumerate(renamed["candidates"]):
        candidate["candidate_id"] = f"renamed-{index}"
    id_invariant = all(
        POLICY_FUNCTIONS[policy_id](sanitize_case(case))[0] == POLICY_FUNCTIONS[policy_id](sanitize_case(renamed))[0]
        for policy_id in POLICY_FUNCTIONS
    )
    controls.append({"control_id": "ID-RENAME", "passed": id_invariant, "observed": "RANKING_INVARIANT" if id_invariant else "RANKING_CHANGED"})

    reversed_case = json.loads(json.dumps(case))
    reversed_case["candidates"] = list(reversed(reversed_case["candidates"]))
    order_invariant = all(
        POLICY_FUNCTIONS[policy_id](sanitize_case(case))[0] == POLICY_FUNCTIONS[policy_id](sanitize_case(reversed_case))[0]
        for policy_id in POLICY_FUNCTIONS
    )
    order_invariant = order_invariant and all(
        random_remote_policy(sanitize_case(case), seed)[0] == random_remote_policy(sanitize_case(reversed_case), seed)[0]
        for seed in SEEDS
    )
    controls.append({"control_id": "ORDER-PERMUTE", "passed": order_invariant, "observed": "RANKING_INVARIANT" if order_invariant else "RANKING_CHANGED"})

    cutoff_bad = json.loads(json.dumps(case))
    cutoff_bad["cutoff"] = str(int(case["transfer_validation_source"]["year"]))
    cutoff_check = validate_substrate({"cases": [cutoff_bad, *[item for item in panel["cases"] if item["case_id"] != case["case_id"]]]}, json.loads(FREEZE_PATH.read_text()))
    cutoff_rejected = any(item["check"].endswith(":chronology") and not item["passed"] for item in cutoff_check)
    controls.append({"control_id": "CUTOFF-VIOLATION", "passed": cutoff_rejected, "observed": "PRECONDITION_REJECT" if cutoff_rejected else "ACCEPTED"})

    source_bad = json.loads(json.dumps(case))
    source_bad["donor_primary_source"]["url"] = ""
    source_check = validate_substrate({"cases": [source_bad, *[item for item in panel["cases"] if item["case_id"] != case["case_id"]]]}, json.loads(FREEZE_PATH.read_text()))
    source_rejected = any(item["check"].endswith(":source_urls") and not item["passed"] for item in source_check)
    controls.append({"control_id": "SOURCE-UNBOUND", "passed": source_rejected, "observed": "PRECONDITION_REJECT" if source_rejected else "ACCEPTED"})

    try:
        reject_random_estimator("BEST_SEED_AFTER_OUTCOMES")
        random_rejected = False
        observed = "ACCEPTED"
    except ValueError as exc:
        random_rejected = True
        observed = f"REJECTED:{exc}"
    controls.append({"control_id": "RANDOM-BEST-SEED", "passed": random_rejected, "observed": observed})
    return controls


def case_gold_key(case: dict[str, Any]) -> str:
    gold_id = case["gold_candidate_id"]
    raw = next(item for item in case["candidates"] if item["candidate_id"] == gold_id)
    return candidate_key(raw)


def rank_case(public: dict[str, Any], policy_id: str, seed: int | None) -> tuple[list[str], dict[str, int]]:
    if policy_id == "random-remote":
        if seed is None:
            raise ValueError("random-remote requires frozen seed")
        return random_remote_policy(public, seed)
    if seed is not None:
        raise ValueError("deterministic policy cannot receive seed")
    return POLICY_FUNCTIONS[policy_id](public)


def aggregate_curves(raw_observations: Sequence[dict[str, Any]]) -> dict[str, Any]:
    output: dict[str, Any] = {}
    for policy_id in POLICY_IDS:
        output[policy_id] = {}
        for budget in (1, 2, 3, 4):
            rows = [item for item in raw_observations if item["policy_id"] == policy_id and item["budget"] == budget]
            vectors = [{key: Fraction(value) for key, value in item["gain_vector"].items()} for item in rows]
            mean = mean_vectors(vectors)
            output[policy_id][str(budget)] = {
                "run_count": len(rows),
                "mean_gain_vector": {key: fraction_text(value) for key, value in mean.items()},
                "available_resource_vector": {
                    "candidate_records": 4,
                    "maximum_candidate_score_evaluations": 64,
                    "maximum_pairwise_similarity_evaluations": 64,
                    "candidate_acquisitions": budget,
                },
                "observed_max_candidate_score_evaluations": max(item["resources"]["candidate_score_evaluations"] for item in rows),
                "observed_max_pairwise_similarity_evaluations": max(item["resources"]["pairwise_similarity_evaluations"] for item in rows),
            }
        auc = {}
        for endpoint in (*HIGHER_IS_BETTER, *LOWER_IS_BETTER):
            values = [Fraction(output[policy_id][str(budget)]["mean_gain_vector"][endpoint]) for budget in (1, 2, 3, 4)]
            auc[endpoint] = fraction_text(sum(values, Fraction(0)) / 4)
        output[policy_id]["descriptive_endpoint_auc"] = auc
    return output


def policy_no_more_resources(left: dict[str, Any], right: dict[str, Any]) -> bool:
    return (
        left["observed_max_candidate_score_evaluations"] <= right["observed_max_candidate_score_evaluations"]
        and left["observed_max_pairwise_similarity_evaluations"] <= right["observed_max_pairwise_similarity_evaluations"]
    )


def vector_dominates(left: dict[str, Any], right: dict[str, Any]) -> bool:
    lvec = {key: Fraction(value) for key, value in left["mean_gain_vector"].items()}
    rvec = {key: Fraction(value) for key, value in right["mean_gain_vector"].items()}
    no_worse = all(lvec[key] >= rvec[key] for key in HIGHER_IS_BETTER) and all(lvec[key] <= rvec[key] for key in LOWER_IS_BETTER)
    strict = any(lvec[key] > rvec[key] for key in HIGHER_IS_BETTER) or any(lvec[key] < rvec[key] for key in LOWER_IS_BETTER)
    return no_worse and strict and policy_no_more_resources(left, right)


def executed_donor_assessment(curves: dict[str, Any]) -> tuple[dict[str, Any], list[str]]:
    structural = curves["structural-jump"]
    assessments = {}
    sufficient: list[str] = []
    for donor in ("nearest-neighbour", "diversified", "random-remote", "analogy"):
        per_budget = {}
        dominates_every = True
        transfer_no_worse_every = True
        resources_no_more_every = True
        for budget in (1, 2, 3, 4):
            drow, srow = curves[donor][str(budget)], structural[str(budget)]
            dominates = vector_dominates(drow, srow)
            transfer_no_worse = Fraction(drow["mean_gain_vector"]["validated_transfer_gain"]) >= Fraction(srow["mean_gain_vector"]["validated_transfer_gain"])
            resources_no_more = policy_no_more_resources(drow, srow)
            per_budget[str(budget)] = {"dominates": dominates, "validated_transfer_no_worse": transfer_no_worse, "resources_no_more": resources_no_more}
            dominates_every &= dominates
            transfer_no_worse_every &= transfer_no_worse
            resources_no_more_every &= resources_no_more
        donor_sufficient = dominates_every or (transfer_no_worse_every and resources_no_more_every)
        if donor_sufficient:
            sufficient.append(donor)
        assessments[donor] = {"per_budget": per_budget, "dominates_every_budget": dominates_every, "validated_transfer_no_worse_every_budget": transfer_no_worse_every, "resources_no_more_every_budget": resources_no_more_every, "local_or_donor_sufficient": donor_sufficient}
    return assessments, sufficient


def donor_frontiers(curves: dict[str, Any]) -> dict[str, Any]:
    donors = ("nearest-neighbour", "diversified", "random-remote", "analogy")
    output = {}
    for budget in (1, 2, 3, 4):
        frontier = []
        for donor in donors:
            if not any(other != donor and vector_dominates(curves[other][str(budget)], curves[donor][str(budget)]) for other in donors):
                frontier.append(donor)
        output[str(budget)] = sorted(frontier)
    return output


def saturation_results(panel: dict[str, Any]) -> list[dict[str, Any]]:
    results = []
    for case in sorted(panel["cases"], key=lambda item: item["case_id"]):
        public = sanitize_case(case)
        gold_key = case_gold_key(case)
        nearest, _ = nearest_policy(public)
        structural, _ = structural_policy(public)
        candidates = {item["content_key"]: item for item in public["candidates"]}
        saturation_step: int | None = None
        for budget in (1, 2, 3):
            prefix = nearest[:budget]
            base = public_gain(gain_vector(public, prefix, gold_key))
            remaining = [key for key in nearest if key not in prefix]
            if all(public_gain(gain_vector(public, [*prefix, key], gold_key)) == base for key in remaining):
                saturation_step = budget
                break
        if saturation_step is None:
            results.append({"case_id": case["case_id"], "local_saturation": "NOT_SATURATED_BEFORE_EXHAUSTION", "remote_jump_attempted": False, "hidden_validated_value": False})
            continue
        prefix = nearest[:saturation_step]
        jump_key = next(key for key in structural if key not in prefix)
        jump_item = candidates[jump_key]
        status, score = exact_structural_score(structural_need(public), structural_candidate(jump_item))
        hidden_value = jump_item["domain"] != public["target_domain"] and status is not StructuralCandidateStatus.OBSTRUCTION and gold_key not in prefix and jump_key == gold_key
        results.append({
            "case_id": case["case_id"],
            "local_saturation": "FINITE_PUBLIC_GAIN_SATURATED",
            "saturation_budget": saturation_step,
            "nearest_prefix_candidate_ids": [next(raw["candidate_id"] for raw in case["candidates"] if candidate_key(raw) == key) for key in prefix],
            "jump_candidate_id": next(raw["candidate_id"] for raw in case["candidates"] if candidate_key(raw) == jump_key),
            "jump_remote": jump_item["domain"] != public["target_domain"],
            "jump_status": status.value,
            "jump_structural_score": fraction_text(score),
            "remote_jump_attempted": True,
            "hidden_validated_value": hidden_value,
        })
    return results


def main() -> int:
    started_wall = time.perf_counter()
    started_cpu = time.process_time()
    freeze = json.loads(FREEZE_PATH.read_text())
    panel = json.loads(PANEL_PATH.read_text())
    summary = json.loads(SUMMARY_PATH.read_text())
    preconditions = hard_preconditions(panel, freeze)
    if not preconditions["all_passed"]:
        print(json.dumps({"job_id": "DES-SATURATION-01", "terminal": "CANNOT_CHECK_SUBSTRATE_PRECONDITION", "hard_preconditions": preconditions}, sort_keys=True))
        return 2

    controls = negative_controls(panel)
    leakage_clean = all(item["passed"] for item in controls)
    raw_observations: list[dict[str, Any]] = []
    ranking_receipts: list[dict[str, Any]] = []
    with RAW_PATH.open("w", encoding="utf-8", newline="\n") as handle:
        for case in sorted(panel["cases"], key=lambda item: item["case_id"]):
            public = sanitize_case(case)
            public_digest = sha256_bytes(canonical_bytes(public))
            gold_key = case_gold_key(case)
            key_to_id = {candidate_key(item): item["candidate_id"] for item in case["candidates"]}
            for policy_id in POLICY_IDS:
                seeds: Iterable[int | None] = SEEDS if policy_id == "random-remote" else (None,)
                for seed in seeds:
                    ranking, operations = rank_case(public, policy_id, seed)
                    complete = ranking_complete(ranking, public)
                    if not complete:
                        raise ValueError(f"incomplete ranking {case['case_id']} {policy_id} {seed}")
                    ranking_receipts.append({"case_id": case["case_id"], "policy_id": policy_id, "seed": seed, "public_payload_sha256": public_digest, "ranking_candidate_ids": [key_to_id[key] for key in ranking], "complete": complete, "resources": operations})
                    for budget in (1, 2, 3, 4):
                        vector = gain_vector(public, ranking[:budget], gold_key)
                        row = {
                            "case_id": case["case_id"],
                            "policy_id": policy_id,
                            "seed": seed,
                            "budget": budget,
                            "public_payload_sha256": public_digest,
                            "selected_candidate_ids": [key_to_id[key] for key in ranking[:budget]],
                            "gain_vector": {key: fraction_text(value) for key, value in vector.items()},
                            "resources": {**operations, "candidate_acquisitions": budget, "verification_calls": budget},
                            "outcome": "OBSERVED",
                        }
                        raw_observations.append(row)
                        handle.write(canonical_bytes(row).decode())

    reject_random_estimator("MEAN_ALL_FROZEN_SEEDS")
    curves = aggregate_curves(raw_observations)
    donor_assessment, sufficient_donors = executed_donor_assessment(curves)
    saturation = saturation_results(panel)
    hidden_jump_count = sum(item["hidden_validated_value"] for item in saturation)
    saturation_count = sum(item["local_saturation"] == "FINITE_PUBLIC_GAIN_SATURATED" for item in saturation)

    elapsed_wall = time.perf_counter() - started_wall
    elapsed_cpu = time.process_time() - started_cpu
    peak_raw = resource.getrusage(resource.RUSAGE_SELF).ru_maxrss
    peak_rss_bytes = peak_raw if sys.platform == "darwin" else peak_raw * 1024
    limits = freeze["resource_vector"]
    resource_censored = elapsed_wall > limits["wall_time_seconds_limit"] or peak_rss_bytes > limits["memory_bytes_limit"] or RAW_PATH.stat().st_size > limits["persistent_storage_bytes_limit"]
    material_missing = sorted(summary.get("unexecuted_strong_baselines", []))
    material_matches_freeze = material_missing == sorted(freeze["substrate"]["material_unexecuted_strong_donors"])

    if not material_matches_freeze:
        terminal = "CANNOT_CHECK_SUBSTRATE_PRECONDITION"
    elif not leakage_clean:
        terminal = "CANNOT_CHECK_LEAKAGE_OR_SHORTCUT"
    elif resource_censored:
        terminal = "CANNOT_CHECK_RESOURCE_CENSORED"
    elif sufficient_donors:
        terminal = "LOCAL_OR_DONOR_POLICY_SUFFICIENT"
    elif material_missing:
        terminal = "CANNOT_CHECK_MATERIAL_DONOR_UNAVAILABLE"
    else:
        terminal = "CANNOT_CHECK_PARETO_TRADEOFF_WITHOUT_PREFERENCE_VECTOR"

    raw_receipt = file_receipt(RAW_PATH)
    result = {
        "schema": "orion.dynamic-epistemic-state.search-saturation-and-remote-jump-result.v1",
        "job_id": "DES-SATURATION-01",
        "terminal": terminal,
        "substrate": {"protocol_id": panel["protocol_id"], "authority": panel["authority"], "case_count": len(panel["cases"]), "candidate_case_count": sum(len(item["candidates"]) for item in panel["cases"])},
        "semantic_yield_curves": curves,
        "executed_donor_assessment": donor_assessment,
        "sufficient_executed_donors": sufficient_donors,
        "finite_local_saturation": saturation,
        "finite_local_saturation_case_count": saturation_count,
        "remote_jump_hidden_validated_value_case_count": hidden_jump_count,
        "material_unexecuted_strong_donors": material_missing,
        "interpretation": {
            "finite_saturation_is_open_world_closure": False,
            "same_programme_internal_replay": True,
            "external_independence": False,
            "claim_ceiling": freeze["claim_ceiling"],
            "paper_authority_delta": "NONE",
        },
    }
    primary = {
        "schema": "orion.dynamic-epistemic-state.des-saturation-primary-result.v1",
        "job_id": "DES-SATURATION-01",
        "terminal": terminal,
        "case_denominator": 4,
        "candidate_case_denominator": 16,
        "policy_run_denominator": len(ranking_receipts),
        "case_budget_outcome_denominator": len(raw_observations),
        "deterministic_policy_runs": sum(item["seed"] is None for item in ranking_receipts),
        "random_remote_policy_runs": sum(item["seed"] is not None for item in ranking_receipts),
        "negative_controls_passed": sum(item["passed"] for item in controls),
        "negative_control_denominator": len(controls),
        "sufficient_executed_donors": sufficient_donors,
        "material_unexecuted_strong_donors": material_missing,
        "finite_local_saturation_case_count": saturation_count,
        "remote_jump_hidden_validated_value_case_count": hidden_jump_count,
        "resource_censored": resource_censored,
        "claim_ceiling": freeze["claim_ceiling"],
        "external_authority_state": "NONE",
    }
    donor_result = {
        "schema": "orion.dynamic-epistemic-state.des-saturation-ideal-donor-result.v1",
        "job_id": "DES-SATURATION-01",
        "executed_donor_frontier_by_budget": donor_frontiers(curves),
        "executed_donor_assessment": donor_assessment,
        "material_unexecuted_strong_donors": material_missing,
        "unavailable_donors_replaced_by_proxy": False,
        "ideal_donor_frontier_complete": False,
        "authority": "NONE",
    }
    negative = {
        "schema": "orion.dynamic-epistemic-state.des-saturation-negative-controls.v1",
        "job_id": "DES-SATURATION-01",
        "controls": controls,
        "passed": sum(item["passed"] for item in controls),
        "denominator": len(controls),
        "all_passed": leakage_clean,
    }
    transfer = {
        "schema": "orion.dynamic-epistemic-state.des-saturation-transfer-result.v1",
        "job_id": "DES-SATURATION-01",
        "status": "CANNOT_CHECK_NO_DISTINCT_HELD_OUT_TRANSFER_SUBSTRATE",
        "reason": "The bound panel is the full strongest fitting local substrate. Reusing an unrelated synthetic benchmark would be a weak-proxy substitution rather than matched transfer.",
        "external_authority": "NONE",
    }
    resources = {
        "schema": "orion.dynamic-epistemic-state.des-saturation-resource-ledger.v1",
        "job_id": "DES-SATURATION-01",
        "frozen_limit": limits,
        "observed": {
            "wall_time_seconds": elapsed_wall,
            "cpu_time_seconds": elapsed_cpu,
            "peak_rss_bytes": peak_rss_bytes,
            "raw_storage_bytes": RAW_PATH.stat().st_size,
            "worker_processes": 1,
            "gpu_count": 0,
            "network_access": False,
            "host": platform.node(),
            "python": platform.python_version(),
            "platform": platform.platform(),
        },
        "resource_censored": resource_censored,
    }
    raw_manifest = {
        "schema": "orion.dynamic-epistemic-state.des-saturation-raw-manifest.v1",
        "job_id": "DES-SATURATION-01",
        "raw_files": [raw_receipt],
        "raw_case_lines": len(raw_observations),
        "ranking_receipt_count": len(ranking_receipts),
        "ranking_receipts_sha256": sha256_bytes(canonical_bytes(ranking_receipts)),
        "all_positive_negative_null_tie_and_obstruction_outcomes_retained": True,
    }

    write_json(HERE / "SEARCH_SATURATION_AND_REMOTE_JUMP_RESULT_V1.json", result)
    write_json(HERE / "PRIMARY_RESULT_V1.json", primary)
    write_json(HERE / "IDEAL_DONOR_RESULT_V1.json", donor_result)
    write_json(HERE / "NEGATIVE_CONTROLS_V1.json", negative)
    write_json(HERE / "TRANSFER_RESULT_V1.json", transfer)
    write_json(HERE / "RESOURCE_LEDGER_V1.json", resources)
    write_json(HERE / "RAW_MANIFEST_V1.json", raw_manifest)

    bound_names = [
        "FREEZE_V1.json",
        "RAW_CASES_V1.jsonl",
        "RAW_MANIFEST_V1.json",
        "PRIMARY_RESULT_V1.json",
        "IDEAL_DONOR_RESULT_V1.json",
        "NEGATIVE_CONTROLS_V1.json",
        "RESOURCE_LEDGER_V1.json",
        "TRANSFER_RESULT_V1.json",
        "SEARCH_SATURATION_AND_REMOTE_JUMP_RESULT_V1.json",
        "execute_des_saturation_01.py",
    ]
    binding = {
        "schema": "orion.dynamic-epistemic-state.des-saturation-result-binding-packet.v1",
        "job_id": "DES-SATURATION-01",
        "base_sha": SUBJECT_COMMIT,
        "execution_subject_head_sha": preconditions["execution_head_sha"],
        "freeze_commit_sha": preconditions["freeze_commit_sha"],
        "bindings": [file_receipt(HERE / name) for name in bound_names],
        "all_case_level_outcomes": raw_receipt,
        "denominators": {
            "cases": 4,
            "candidate_cases": 16,
            "policy_runs": len(ranking_receipts),
            "case_budget_outcomes": len(raw_observations),
            "negative_controls": len(controls),
        },
        "hard_precondition_attainment": preconditions,
        "leakage": {"negative_controls": controls, "all_passed": leakage_clean, "policy_payload_gold_access": False, "policy_payload_family_access": False},
        "censoring": {"resource_censored": resource_censored, "outcomes_dropped": 0},
        "strongest_donor": {"executed_frontier": donor_frontiers(curves), "material_unexecuted": material_missing, "proxy_substitution": False},
        "resource_vector": resources,
        "transfer": transfer,
        "exact_terminal": terminal,
        "claim_ceiling": freeze["claim_ceiling"],
        "external_authority_state": "NONE",
        "manuscript_writing_owner": "P1_P15_REWRITE_LANE",
        "computation_session_paper_authority_delta": "NONE",
    }
    write_json(HERE / "RESULT_BINDING_PACKET_V1.json", binding)
    print(json.dumps({"job_id": "DES-SATURATION-01", "terminal": terminal, "cases": 4, "policy_runs": len(ranking_receipts), "case_budget_outcomes": len(raw_observations), "sufficient_executed_donors": sufficient_donors, "negative_controls": f"{sum(item['passed'] for item in controls)}/{len(controls)}"}, sort_keys=True))
    return 0 if terminal in {"REMOTE_STRUCTURAL_JUMP_PROSPECTIVE_VALUE_SUPPORTED", "LOCAL_OR_DONOR_POLICY_SUFFICIENT", "CANNOT_CHECK_MATERIAL_DONOR_UNAVAILABLE", "CANNOT_CHECK_PARETO_TRADEOFF_WITHOUT_PREFERENCE_VECTOR"} else 1


if __name__ == "__main__":
    raise SystemExit(main())
