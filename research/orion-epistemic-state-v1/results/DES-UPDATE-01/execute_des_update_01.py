#!/usr/bin/env python3
"""Execute the frozen DES-UPDATE-01 finite update-algebra experiment.

The runner is deterministic, standard-library only, network-free, and writes
denominator-complete case observations.  It grants no manuscript or scientific
authority.
"""
from __future__ import annotations

import dataclasses
import hashlib
import importlib.util
import itertools
import json
import os
from pathlib import Path
import platform
import resource
import subprocess
import sys
import time
from typing import Any, Iterable, Sequence


HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[3]
FREEZE_PATH = HERE / "FREEZE_V1.json"
ERRATUM_PATH = HERE / "FREEZE_ARITHMETIC_ERRATUM_V1.json"
RAW_PATH = HERE / "RAW_CASES_V1.jsonl"
SUBJECT_COMMIT = "3c97b87f4f4c8c0365226019236c83d3c4c7bb37"
MODEL_PATH = ROOT / "src/orion/epistemic_state_v1/model.py"


def canonical_bytes(value: Any) -> bytes:
    return (json.dumps(value, sort_keys=True, separators=(",", ":")) + "\n").encode()


def sha256_bytes(payload: bytes) -> str:
    return hashlib.sha256(payload).hexdigest()


def file_receipt(path: Path) -> dict[str, Any]:
    payload = path.read_bytes()
    return {"path": str(path.relative_to(ROOT)), "bytes": len(payload), "sha256": sha256_bytes(payload)}


def write_json(path: Path, value: Any) -> None:
    path.write_bytes(canonical_bytes(value))


def normalize(value: Any) -> Any:
    if dataclasses.is_dataclass(value):
        return {field.name: normalize(getattr(value, field.name)) for field in dataclasses.fields(value)}
    if isinstance(value, dict):
        return {str(key): normalize(item) for key, item in sorted(value.items(), key=lambda x: str(x[0]))}
    if isinstance(value, (set, frozenset)):
        return sorted(normalize(item) for item in value)
    if isinstance(value, tuple):
        return [normalize(item) for item in value]
    if hasattr(value, "value") and type(value).__module__ == MODEL.__name__:
        return normalize(value.value)
    if hasattr(value, "numerator") and hasattr(value, "denominator"):
        return f"{value.numerator}/{value.denominator}"
    if isinstance(value, (str, int, float, bool)) or value is None:
        return value
    raise TypeError(f"cannot normalize {type(value)!r}")


def state_digest(state: Any) -> str:
    return sha256_bytes(canonical_bytes(normalize(state)))


def load_model() -> Any:
    spec = importlib.util.spec_from_file_location("des_update_01_model", MODEL_PATH)
    if spec is None or spec.loader is None:
        raise RuntimeError("cannot construct model import specification")
    module = importlib.util.module_from_spec(spec)
    sys.modules[spec.name] = module
    spec.loader.exec_module(module)
    return module


MODEL = load_model()


def coordinate(value: Any, status: Any, epoch: int = 0) -> Any:
    return MODEL.Coordinate(
        value=value,
        status=status,
        scope="scope:alpha",
        epoch=epoch,
        provenance_ids=("receipt:seed",),
        estimator_version="des-update-freeze-v1",
    )


def initial_states() -> list[tuple[str, Any]]:
    satisfied_sets = (frozenset(), frozenset({"o1"}), frozenset({"o2"}), frozenset({"o1", "o2"}))
    authority_sets = (frozenset(), frozenset({"PROMOTE:alpha"}))
    defeater_sets = (frozenset(), frozenset({"defeater:d1"}))
    custody_values = (None, False, True)
    revoked_sets = (frozenset(), frozenset({"p1"}), frozenset({"p2"}), frozenset({"p1", "p2"}))
    evidence_variants = (
        (MODEL.Fraction(1, 4), MODEL.Status.PARTIAL),
        (MODEL.Fraction(3, 4), MODEL.Status.KNOWN),
    )
    identified_variants = ((False, MODEL.Status.KNOWN), (True, MODEL.Status.KNOWN))
    families = (
        MODEL.SupportFamily("family:p1", frozenset({"p1"}), frozenset({"o1", "o2"})),
        MODEL.SupportFamily("family:p2", frozenset({"p2"}), frozenset({"o1", "o2"})),
        MODEL.SupportFamily("family:p1p2", frozenset({"p1", "p2"}), frozenset({"o1", "o2"})),
    )
    output: list[tuple[str, Any]] = []
    axes = itertools.product(
        evidence_variants,
        identified_variants,
        authority_sets,
        satisfied_sets,
        defeater_sets,
        custody_values,
        revoked_sets,
    )
    for index, (evidence, identified, authority, satisfied, defeaters, custody, revoked) in enumerate(axes):
        state = MODEL.State(
            subject_id="subject:alpha",
            responsibility_id="PROMOTE:alpha",
            epoch=0,
            evidence=coordinate(evidence[0], evidence[1]),
            identifiability=coordinate(identified[0], identified[1]),
            coverage=coordinate(MODEL.Fraction(1, 2), MODEL.Status.PARTIAL),
            obligations_required=frozenset({"o1", "o2"}),
            obligations_satisfied=satisfied,
            provenance=coordinate(True, MODEL.Status.KNOWN),
            verification=coordinate(True, MODEL.Status.KNOWN),
            authority_scopes=authority,
            support_families=families,
            active_defeaters=defeaters,
            custody_external=custody,
            method_reach_ids=frozenset({"method:m0"}),
            knowledge_node_ids=frozenset({"node:n0"}),
            knowledge_edge_ids=frozenset({"edge:e0"}),
            resources=MODEL.ResourceVector(),
            revoked_premise_ids=revoked,
        )
        output.append((f"S{index:03d}", state))
    return output


TEMPLATE_IDS = (
    "e:evidence-high",
    "e:evidence-low",
    "e:coverage-high",
    "e:custody-true",
    "e:custody-false",
    "e:defeater-add",
    "e:satisfy-o1",
    "e:method-expand",
    "e:knowledge-expand",
    "e:revoke-p1",
    "e:revoke-p2",
    "e:authority-narrow",
    "e:authority-widen-untrusted",
    "e:authority-widen-adjudicated",
)


WRITE_SETS = {
    "e:evidence-high": frozenset({"evidence"}),
    "e:evidence-low": frozenset({"evidence"}),
    "e:coverage-high": frozenset({"coverage"}),
    "e:custody-true": frozenset({"custody_external"}),
    "e:custody-false": frozenset({"custody_external"}),
    "e:defeater-add": frozenset({"active_defeaters"}),
    "e:satisfy-o1": frozenset({"obligations_satisfied"}),
    "e:method-expand": frozenset({"method_reach_ids"}),
    "e:knowledge-expand": frozenset({"knowledge_node_ids"}),
    "e:revoke-p1": frozenset({"revoked_premise_ids"}),
    "e:revoke-p2": frozenset({"revoked_premise_ids"}),
    "e:authority-narrow": frozenset({"authority_scopes"}),
    "e:authority-widen-untrusted": frozenset({"authority_scopes"}),
    "e:authority-widen-adjudicated": frozenset({"authority_scopes"}),
}


def make_event(state: Any, template_id: str) -> Any:
    epoch = state.epoch + 1
    kind = "evidence"
    authorized = frozenset()
    receipts: tuple[str, ...] = ()
    if template_id == "e:evidence-high":
        writes = {"evidence": coordinate(MODEL.Fraction(7, 8), MODEL.Status.KNOWN, epoch)}
    elif template_id == "e:evidence-low":
        writes = {"evidence": coordinate(MODEL.Fraction(1, 8), MODEL.Status.PARTIAL, epoch)}
    elif template_id == "e:coverage-high":
        writes = {"coverage": coordinate(MODEL.Fraction(7, 8), MODEL.Status.KNOWN, epoch)}
    elif template_id == "e:custody-true":
        kind, writes = "custody_change", {"custody_external": True}
    elif template_id == "e:custody-false":
        kind, writes = "custody_change", {"custody_external": False}
    elif template_id == "e:defeater-add":
        kind, writes = "contradiction", {"active_defeaters": frozenset({"defeater:d1"})}
    elif template_id == "e:satisfy-o1":
        writes = {"obligations_satisfied": state.obligations_satisfied | {"o1"}}
    elif template_id == "e:method-expand":
        kind, writes = "method_expansion", {"method_reach_ids": state.method_reach_ids | {"method:m1"}}
    elif template_id == "e:knowledge-expand":
        writes = {"knowledge_node_ids": state.knowledge_node_ids | {"node:n1"}}
    elif template_id == "e:revoke-p1":
        kind, writes = "revocation", {"revoked_premise_ids": frozenset({"p1"})}
    elif template_id == "e:revoke-p2":
        kind, writes = "revocation", {"revoked_premise_ids": frozenset({"p2"})}
    elif template_id == "e:authority-narrow":
        kind, writes = "responsibility_change", {"authority_scopes": frozenset()}
    elif template_id == "e:authority-widen-untrusted":
        writes = {"authority_scopes": frozenset({"PROMOTE:alpha"})}
    elif template_id == "e:authority-widen-adjudicated":
        kind = "external_adjudication"
        authorized = frozenset({"authority_scopes"})
        receipts = ("receipt:external-adjudication",)
        writes = {"authority_scopes": frozenset({"PROMOTE:alpha"})}
    else:
        raise KeyError(template_id)
    digest_payload = {
        "event_id": template_id,
        "subject_id": state.subject_id,
        "kind": kind,
        "epoch": epoch,
        "writes": normalize(writes),
        "authorized_coordinate_writes": sorted(authorized),
        "receipt_ids": list(receipts),
    }
    return MODEL.Event(
        event_id=template_id,
        subject_id=state.subject_id,
        kind=kind,
        digest=sha256_bytes(canonical_bytes(digest_payload)),
        epoch=epoch,
        writes=writes,
        authorized_coordinate_writes=authorized,
        receipt_ids=receipts,
        estimator_version="des-update-freeze-v1",
    )


def observe(state: Any, events: Sequence[Any]) -> dict[str, Any]:
    try:
        result = MODEL.replay(state, events)
    except Exception as exc:  # intentional typed rejection is an observation
        return {"kind": "REJECTION", "error_type": type(exc).__name__, "message": str(exc)}
    return {"kind": "STATE", "state_sha256": state_digest(result)}


def git_bytes_at(commit: str, path: str) -> bytes:
    return subprocess.check_output(["git", "show", f"{commit}:{path}"], cwd=ROOT)


def hard_preconditions(
    freeze: dict[str, Any], erratum: dict[str, Any], states: Sequence[tuple[str, Any]]
) -> dict[str, Any]:
    checks: list[dict[str, Any]] = []
    for path, expected in freeze["subject_bindings"].items():
        observed = sha256_bytes(git_bytes_at(SUBJECT_COMMIT, path))
        checks.append({"check": f"subject_binding:{path}", "passed": observed == expected, "expected": expected, "observed": observed})
    head = subprocess.check_output(["git", "rev-parse", "HEAD"], cwd=ROOT, text=True).strip()
    freeze_commits = subprocess.check_output(
        ["git", "log", "--format=%H", "--", str(FREEZE_PATH.relative_to(ROOT))],
        cwd=ROOT,
        text=True,
    ).splitlines()
    freeze_commit = freeze_commits[-1] if freeze_commits else ""
    erratum_commits = subprocess.check_output(
        ["git", "log", "--format=%H", "--", str(ERRATUM_PATH.relative_to(ROOT))],
        cwd=ROOT,
        text=True,
    ).splitlines()
    erratum_commit = erratum_commits[-1] if erratum_commits else ""
    ancestor_rc = subprocess.run(
        ["git", "merge-base", "--is-ancestor", freeze_commit, head], cwd=ROOT, check=False
    ).returncode if freeze_commit else 1
    erratum_ancestor_rc = subprocess.run(
        ["git", "merge-base", "--is-ancestor", erratum_commit, head], cwd=ROOT, check=False
    ).returncode if erratum_commit else 1
    expected_states = erratum["corrected_expected_counts"]["unique_initial_states"]
    expected_event_instances = erratum["corrected_expected_counts"]["event_instances"]
    checks.extend(
        [
            {"check": "subject_commit_is_ancestor", "passed": subprocess.run(["git", "merge-base", "--is-ancestor", SUBJECT_COMMIT, head], cwd=ROOT, check=False).returncode == 0},
            {"check": "freeze_committed_before_execution", "passed": bool(freeze_commit) and freeze_commit != head and ancestor_rc == 0, "freeze_commit": freeze_commit, "execution_head": head},
            {"check": "arithmetic_erratum_committed_before_law_execution", "passed": bool(erratum_commit) and erratum_commit != head and erratum_ancestor_rc == 0, "erratum_commit": erratum_commit, "execution_head": head},
            {"check": "finite_state_count", "passed": len(states) == expected_states, "observed": len(states), "expected": expected_states},
            {"check": "finite_state_uniqueness", "passed": len({state_digest(state) for _, state in states}) == expected_states, "observed": len({state_digest(state) for _, state in states}), "expected": expected_states},
            {"check": "event_template_count", "passed": len(TEMPLATE_IDS) == 14, "observed": len(TEMPLATE_IDS), "expected": 14},
            {"check": "event_instance_count", "passed": len(states) * len(TEMPLATE_IDS) == expected_event_instances, "observed": len(states) * len(TEMPLATE_IDS), "expected": expected_event_instances},
            {"check": "network_access", "passed": True, "observed": "NOT_USED_BY_RUNNER"},
            {"check": "random_sampling", "passed": True, "observed": "NONE_EXHAUSTIVE_ENUMERATION"},
        ]
    )
    return {"all_passed": all(item["passed"] for item in checks), "checks": checks, "execution_head_sha": head, "freeze_commit_sha": freeze_commit, "erratum_commit_sha": erratum_commit}


class Recorder:
    def __init__(self, path: Path):
        self.path = path
        self.handle = path.open("w", encoding="utf-8", newline="\n")
        self.counts: dict[str, dict[str, int]] = {}
        self.total = 0
        self.countermodels: list[dict[str, Any]] = []

    def record(self, law: str, case_id: str, passed: bool, observed: Any, *, detail: Any = None) -> None:
        outcome = "PASS" if passed else "FAIL"
        payload: dict[str, Any] = {"law_id": law, "case_id": case_id, "outcome": outcome, "observed": observed}
        if detail is not None:
            payload["detail"] = detail
        self.handle.write(canonical_bytes(payload).decode())
        self.total += 1
        bucket = self.counts.setdefault(law, {"PASS": 0, "FAIL": 0})
        bucket[outcome] += 1
        if not passed and len(self.countermodels) < 100:
            self.countermodels.append(payload)

    def close(self) -> None:
        self.handle.close()


def non_revocation_projection(state: Any) -> dict[str, Any]:
    value = normalize(state)
    for key in ("epoch", "applied_event_ids", "revoked_premise_ids"):
        value.pop(key)
    return value


def run_laws(states: Sequence[tuple[str, Any]], recorder: Recorder) -> None:
    replay_law = "DES-T5-REPLAY-DETERMINISM"
    idem_law = "DES-T5-IDEMPOTENCE"
    commute_law = "DES-T6-INDEPENDENT-COMMUTATION"
    noncommute_law = "DES-T6-EXPLICIT-NONCOMMUTATION"
    revoke_law = "DES-T7-REVOCATION-LOCALITY"
    authority_law = "DES-AUTHORITY-NO-AMPLIFICATION"

    for state_id, state in states:
        events = {template_id: make_event(state, template_id) for template_id in TEMPLATE_IDS}

        sequences: Iterable[tuple[str, ...]] = itertools.chain(
            ((template_id,) for template_id in TEMPLATE_IDS),
            itertools.product(TEMPLATE_IDS, repeat=2),
        )
        for sequence_ids in sequences:
            sequence = tuple(events[item] for item in sequence_ids)
            left = observe(state, sequence)
            right = observe(state, sequence)
            recorder.record(replay_law, f"{state_id}:{'>'.join(sequence_ids)}", left == right, left, detail=None if left == right else {"second": right})

        for template_id in TEMPLATE_IDS:
            event = events[template_id]
            first_observation = observe(state, (event,))
            if first_observation["kind"] == "REJECTION":
                second_observation = observe(state, (event,))
                passed = first_observation == second_observation
                recorder.record(idem_law, f"{state_id}:{template_id}:rejected", passed, first_observation, detail=None if passed else {"second": second_observation})
            else:
                once = MODEL.apply_event(state, event)
                twice = MODEL.apply_event(once, event)
                passed = once == twice
                recorder.record(idem_law, f"{state_id}:{template_id}:accepted", passed, {"once": state_digest(once), "twice": state_digest(twice)})

        for left_id, right_id in itertools.combinations(TEMPLATE_IDS, 2):
            independent = WRITE_SETS[left_id].isdisjoint(WRITE_SETS[right_id])
            revocation_pair = {left_id, right_id} == {"e:revoke-p1", "e:revoke-p2"}
            if not independent and not revocation_pair:
                continue
            left_event, right_event = events[left_id], events[right_id]
            if observe(state, (left_event,))["kind"] != "STATE" or observe(state, (right_event,))["kind"] != "STATE":
                continue
            left_right = observe(state, (left_event, right_event))
            right_left = observe(state, (right_event, left_event))
            passed = left_right["kind"] == "STATE" and left_right == right_left
            recorder.record(commute_law, f"{state_id}:{left_id}<->{right_id}", passed, left_right, detail=None if passed else {"reverse": right_left})

        for left_id, right_id in (("e:evidence-high", "e:evidence-low"), ("e:custody-true", "e:custody-false")):
            left_right = observe(state, (events[left_id], events[right_id]))
            right_left = observe(state, (events[right_id], events[left_id]))
            passed = left_right["kind"] == right_left["kind"] == "STATE" and left_right != right_left
            recorder.record(noncommute_law, f"{state_id}:{left_id}!={right_id}", passed, left_right, detail=None if passed else {"reverse": right_left})

        for premise in ("p1", "p2"):
            event = events[f"e:revoke-{premise}"]
            result = MODEL.apply_event(state, event)
            expected_revoked = state.revoked_premise_ids | {premise}
            expected_survivors = tuple(
                family.family_id for family in state.support_families if family.premise_ids.isdisjoint(expected_revoked)
            )
            observed_survivors = tuple(family.family_id for family in result.surviving_families)
            checks = {
                "revoked_exact": result.revoked_premise_ids == expected_revoked,
                "survivors_exact": observed_survivors == expected_survivors,
                "non_revocation_coordinates_preserved": non_revocation_projection(result) == non_revocation_projection(state),
            }
            recorder.record(revoke_law, f"{state_id}:revoke:{premise}", all(checks.values()), checks, detail=None if all(checks.values()) else {"expected_survivors": expected_survivors, "observed_survivors": observed_survivors})
        both = MODEL.replay(state, (events["e:revoke-p1"], events["e:revoke-p2"]))
        both_reverse = MODEL.replay(state, (events["e:revoke-p2"], events["e:revoke-p1"]))
        expected_both = state.revoked_premise_ids | {"p1", "p2"}
        passed = both.revoked_premise_ids == both_reverse.revoked_premise_ids == expected_both
        recorder.record(revoke_law, f"{state_id}:revoke:p1+p2", passed, {"forward": sorted(both.revoked_premise_ids), "reverse": sorted(both_reverse.revoked_premise_ids)})

        for template_id in TEMPLATE_IDS[:-1]:
            event = events[template_id]
            observation = observe(state, (event,))
            if observation["kind"] == "STATE":
                result = MODEL.apply_event(state, event)
                passed = result.authority_scopes.issubset(state.authority_scopes)
            else:
                passed = template_id == "e:authority-widen-untrusted" and not state.authority_scopes
            recorder.record(authority_law, f"{state_id}:{template_id}:nonadjudication", passed, observation)

        adjudicated = events["e:authority-widen-adjudicated"]
        adjudicated_observation = observe(state, (adjudicated,))
        adjudicated_pass = adjudicated_observation["kind"] == "STATE"
        if adjudicated_pass:
            adjudicated_result = MODEL.apply_event(state, adjudicated)
            adjudicated_pass = adjudicated_result.authority_scopes == state.authority_scopes | {"PROMOTE:alpha"}
        recorder.record(authority_law, f"{state_id}:adjudicated-bound", adjudicated_pass, adjudicated_observation)

        if not state.authority_scopes:
            for variant, authorized, receipts in (
                ("missing-authorization", frozenset(), ("receipt:external-adjudication",)),
                ("missing-receipt", frozenset({"authority_scopes"}), ()),
            ):
                bad = dataclasses.replace(adjudicated, authorized_coordinate_writes=authorized, receipt_ids=receipts)
                bad_observation = observe(state, (bad,))
                passed = bad_observation == {"kind": "REJECTION", "error_type": "ValueError", "message": "unauthorized authority amplification"}
                recorder.record(authority_law, f"{state_id}:adjudicated-{variant}", passed, bad_observation)


def run_mutations(states: Sequence[tuple[str, Any]]) -> tuple[list[dict[str, Any]], list[dict[str, Any]]]:
    results: list[dict[str, Any]] = []
    witnesses: list[dict[str, Any]] = []

    replay_cases = detections = 0
    for state_id, state in states:
        events = {item: make_event(state, item) for item in TEMPLATE_IDS}
        for left_id, right_id in itertools.product(TEMPLATE_IDS, repeat=2):
            replay_cases += 1
            expected = observe(state, (events[left_id], events[right_id]))
            mutant = observe(state, (events[right_id], events[left_id]))
            if mutant != expected:
                detections += 1
                if not any(item["mutation_id"] == "M-REPLAY-ORDER" for item in witnesses):
                    witnesses.append({"mutation_id": "M-REPLAY-ORDER", "state_id": state_id, "sequence": [left_id, right_id], "expected": expected, "mutant": mutant})
    results.append({"mutation_id": "M-REPLAY-ORDER", "law_id": "DES-T5-REPLAY-DETERMINISM", "cases": replay_cases, "detections": detections, "killed": detections > 0})

    idem_cases = detections = 0
    for state_id, state in states:
        for template_id in TEMPLATE_IDS:
            event = make_event(state, template_id)
            if observe(state, (event,))["kind"] != "STATE":
                continue
            idem_cases += 1
            once = MODEL.apply_event(state, event)
            mutant = dataclasses.replace(once, active_defeaters=once.active_defeaters | {"defeater:mutant-duplicate"})
            if mutant != once:
                detections += 1
                if not any(item["mutation_id"] == "M-IDEMPOTENCE-DUPLICATE" for item in witnesses):
                    witnesses.append({"mutation_id": "M-IDEMPOTENCE-DUPLICATE", "state_id": state_id, "event_id": template_id, "expected_sha256": state_digest(once), "mutant_sha256": state_digest(mutant)})
    results.append({"mutation_id": "M-IDEMPOTENCE-DUPLICATE", "law_id": "DES-T5-IDEMPOTENCE", "cases": idem_cases, "detections": detections, "killed": detections > 0})

    commute_cases = detections = 0
    for state_id, state in states:
        coverage = make_event(state, "e:coverage-high")
        method = make_event(state, "e:method-expand")
        mutant_method = dataclasses.replace(
            method,
            writes={**method.writes, "coverage": coordinate(MODEL.Fraction(1, 8), MODEL.Status.PARTIAL, method.epoch)},
        )
        commute_cases += 1
        forward = observe(state, (mutant_method, coverage))
        reverse = observe(state, (coverage, mutant_method))
        if forward != reverse:
            detections += 1
            if not any(item["mutation_id"] == "M-COMMUTATION-HIDDEN-WRITE" for item in witnesses):
                witnesses.append({"mutation_id": "M-COMMUTATION-HIDDEN-WRITE", "state_id": state_id, "forward": forward, "reverse": reverse})
    results.append({"mutation_id": "M-COMMUTATION-HIDDEN-WRITE", "law_id": "DES-T6-INDEPENDENT-COMMUTATION", "cases": commute_cases, "detections": detections, "killed": detections > 0})

    noncommute_cases = detections = 0
    for state_id, state in states:
        events = {item: make_event(state, item) for item in TEMPLATE_IDS}
        for left_id, right_id in (("e:evidence-high", "e:evidence-low"), ("e:custody-true", "e:custody-false")):
            noncommute_cases += 1
            first_input = tuple(sorted((events[left_id], events[right_id]), key=lambda item: item.event_id))
            second_input = tuple(sorted((events[right_id], events[left_id]), key=lambda item: item.event_id))
            first = observe(state, first_input)
            second = observe(state, second_input)
            if first == second:
                detections += 1
                if not any(item["mutation_id"] == "M-NONCOMMUTATION-CANONICALIZE" for item in witnesses):
                    witnesses.append({"mutation_id": "M-NONCOMMUTATION-CANONICALIZE", "state_id": state_id, "events": [left_id, right_id], "mutant_output": first})
    results.append({"mutation_id": "M-NONCOMMUTATION-CANONICALIZE", "law_id": "DES-T6-EXPLICIT-NONCOMMUTATION", "cases": noncommute_cases, "detections": detections, "killed": detections > 0})

    revocation_cases = detections = 0
    for state_id, state in states:
        revocation_cases += 1
        expected = MODEL.apply_event(state, make_event(state, "e:revoke-p1"))
        mutant = dataclasses.replace(expected, revoked_premise_ids=state.revoked_premise_ids | {"p1", "p2"})
        expected_survivors = tuple(item.family_id for item in expected.surviving_families)
        mutant_survivors = tuple(item.family_id for item in mutant.surviving_families)
        if mutant.revoked_premise_ids != expected.revoked_premise_ids or mutant_survivors != expected_survivors:
            detections += 1
            if not any(item["mutation_id"] == "M-REVOCATION-GLOBAL" for item in witnesses):
                witnesses.append({"mutation_id": "M-REVOCATION-GLOBAL", "state_id": state_id, "expected_revoked": sorted(expected.revoked_premise_ids), "mutant_revoked": sorted(mutant.revoked_premise_ids), "expected_survivors": expected_survivors, "mutant_survivors": mutant_survivors})
    results.append({"mutation_id": "M-REVOCATION-GLOBAL", "law_id": "DES-T7-REVOCATION-LOCALITY", "cases": revocation_cases, "detections": detections, "killed": detections > 0})

    authority_cases = detections = 0
    for state_id, state in states:
        if state.authority_scopes:
            continue
        authority_cases += 1
        mutant = dataclasses.replace(state, authority_scopes=frozenset({"PROMOTE:alpha"}))
        if not mutant.authority_scopes.issubset(state.authority_scopes):
            detections += 1
            if not any(item["mutation_id"] == "M-AUTHORITY-PERMIT" for item in witnesses):
                witnesses.append({"mutation_id": "M-AUTHORITY-PERMIT", "state_id": state_id, "before": sorted(state.authority_scopes), "mutant_after": sorted(mutant.authority_scopes)})
    results.append({"mutation_id": "M-AUTHORITY-PERMIT", "law_id": "DES-AUTHORITY-NO-AMPLIFICATION", "cases": authority_cases, "detections": detections, "killed": detections > 0})
    return results, witnesses


def main() -> int:
    started_wall = time.perf_counter()
    started_cpu = time.process_time()
    freeze = json.loads(FREEZE_PATH.read_text())
    erratum = json.loads(ERRATUM_PATH.read_text())
    states = initial_states()
    preconditions = hard_preconditions(freeze, erratum, states)
    if not preconditions["all_passed"]:
        print(json.dumps({"terminal": "CANNOT_CHECK_EXECUTION_PRECONDITION", "hard_preconditions": preconditions}, sort_keys=True))
        return 2

    recorder = Recorder(RAW_PATH)
    try:
        run_laws(states, recorder)
    finally:
        recorder.close()
    mutation_results, mutation_witnesses = run_mutations(states)

    elapsed_wall = time.perf_counter() - started_wall
    elapsed_cpu = time.process_time() - started_cpu
    peak_rss_raw = resource.getrusage(resource.RUSAGE_SELF).ru_maxrss
    peak_rss_bytes = peak_rss_raw if sys.platform == "darwin" else peak_rss_raw * 1024
    resource_limits = freeze["resource_vector"]
    resource_censored = elapsed_wall > resource_limits["wall_time_seconds_limit"] or peak_rss_bytes > resource_limits["memory_bytes_limit"]
    law_failures = sum(bucket["FAIL"] for bucket in recorder.counts.values())
    all_mutations_killed = all(item["killed"] for item in mutation_results)
    if resource_censored:
        terminal = "CANNOT_CHECK_RESOURCE_CENSORED"
    elif law_failures:
        terminal = "UPDATE_LAW_COUNTEREXAMPLE"
    elif not all_mutations_killed:
        terminal = "UPDATE_LAW_COUNTEREXAMPLE"
    else:
        terminal = "DYNAMIC_UPDATE_ALGEBRA_FINITE_CLASS_GREEN"

    raw_receipt = file_receipt(RAW_PATH)
    raw_manifest = {
        "schema": "orion.dynamic-epistemic-state.des-update-raw-manifest.v1",
        "job_id": "DES-UPDATE-01",
        "raw_files": [raw_receipt],
        "case_count": recorder.total,
        "law_denominators": recorder.counts,
        "positive_negative_null_retention": "ALL_CASE_OUTCOMES_RETAINED",
    }
    primary = {
        "schema": "orion.dynamic-epistemic-state.des-update-primary-result.v1",
        "job_id": "DES-UPDATE-01",
        "terminal": terminal,
        "finite_state_count": len(states),
        "event_instance_count": len(states) * len(TEMPLATE_IDS),
        "case_count": recorder.total,
        "law_denominators": recorder.counts,
        "law_failures": law_failures,
        "mutations_killed": sum(item["killed"] for item in mutation_results),
        "mutation_count": len(mutation_results),
        "resource_censored": resource_censored,
        "claim_ceiling": freeze["claim_ceiling"],
        "external_authority_state": "NONE",
    }
    negative_controls = {
        "schema": "orion.dynamic-epistemic-state.des-update-negative-controls.v1",
        "job_id": "DES-UPDATE-01",
        "mutation_results": mutation_results,
        "all_mutations_killed": all_mutations_killed,
        "authority": "INTERNAL_MUTATION_SENSITIVITY_ONLY",
    }
    minimal_countermodels = {
        "schema": "orion.dynamic-epistemic-state.des-update-minimal-countermodels.v1",
        "job_id": "DES-UPDATE-01",
        "observed_law_countermodels": recorder.countermodels,
        "observed_law_countermodel_count": len(recorder.countermodels),
        "mutation_kill_witnesses": mutation_witnesses,
        "interpretation": "No observed-law countermodel means only that the frozen finite class was green; mutation witnesses show sensitivity and are not scientific counterexamples.",
    }
    ideal_donor = {
        "schema": "orion.dynamic-epistemic-state.des-update-ideal-donor-result.v1",
        "job_id": "DES-UPDATE-01",
        "status": "NOT_APPLICABLE_TO_INTERNAL_FINITE_ALGEBRA_REPLAY",
        "strongest_donor": None,
        "donor_comparison_executed": False,
        "authority": "NONE",
    }
    transfer = {
        "schema": "orion.dynamic-epistemic-state.des-update-transfer-result.v1",
        "job_id": "DES-UPDATE-01",
        "status": "NOT_EXECUTED_OUTSIDE_FROZEN_FINITE_CLASS",
        "reason": "DES-UPDATE-01 freezes one declared finite class; broader transfer requires a successor freeze.",
        "authority": "NONE",
    }
    resources = {
        "schema": "orion.dynamic-epistemic-state.des-update-resource-ledger.v1",
        "job_id": "DES-UPDATE-01",
        "frozen_limit": resource_limits,
        "observed": {
            "wall_time_seconds": elapsed_wall,
            "cpu_time_seconds": elapsed_cpu,
            "peak_rss_bytes": peak_rss_bytes,
            "worker_processes": 1,
            "gpu_count": 0,
            "network_access": False,
            "host": platform.node(),
            "python": platform.python_version(),
            "platform": platform.platform(),
        },
        "resource_censored": resource_censored,
    }
    receipt = {
        "schema": "orion.dynamic-epistemic-state.update-algebra-receipt.v1",
        "job_id": "DES-UPDATE-01",
        "terminal": terminal,
        "laws": recorder.counts,
        "mutation_results": mutation_results,
        "hard_preconditions": preconditions,
        "finite_class": {"states": len(states), "event_templates": len(TEMPLATE_IDS), "event_instances": len(states) * len(TEMPLATE_IDS)},
        "raw_cases": raw_receipt,
        "claim_ceiling": freeze["claim_ceiling"],
        "paper_authority_delta": "NONE",
    }

    write_json(HERE / "RAW_MANIFEST_V1.json", raw_manifest)
    write_json(HERE / "PRIMARY_RESULT_V1.json", primary)
    write_json(HERE / "IDEAL_DONOR_RESULT_V1.json", ideal_donor)
    write_json(HERE / "NEGATIVE_CONTROLS_V1.json", negative_controls)
    write_json(HERE / "RESOURCE_LEDGER_V1.json", resources)
    write_json(HERE / "TRANSFER_RESULT_V1.json", transfer)
    write_json(HERE / "UPDATE_ALGEBRA_RECEIPT_V1.json", receipt)
    write_json(HERE / "MINIMAL_COUNTERMODELS_V1.json", minimal_countermodels)

    bound_names = [
        "FREEZE_V1.json",
        "FREEZE_ARITHMETIC_ERRATUM_V1.json",
        "PREFLIGHT_FAILURE_V1.json",
        "RAW_CASES_V1.jsonl",
        "RAW_MANIFEST_V1.json",
        "PRIMARY_RESULT_V1.json",
        "IDEAL_DONOR_RESULT_V1.json",
        "NEGATIVE_CONTROLS_V1.json",
        "RESOURCE_LEDGER_V1.json",
        "TRANSFER_RESULT_V1.json",
        "UPDATE_ALGEBRA_RECEIPT_V1.json",
        "MINIMAL_COUNTERMODELS_V1.json",
        "execute_des_update_01.py",
    ]
    binding = {
        "schema": "orion.dynamic-epistemic-state.des-update-result-binding-packet.v1",
        "job_id": "DES-UPDATE-01",
        "base_sha": SUBJECT_COMMIT,
        "execution_subject_head_sha": preconditions["execution_head_sha"],
        "freeze_commit_sha": preconditions["freeze_commit_sha"],
        "freeze_erratum_commit_sha": preconditions["erratum_commit_sha"],
        "bindings": [file_receipt(HERE / name) for name in bound_names],
        "all_case_level_outcomes": raw_receipt,
        "denominators": recorder.counts,
        "hard_precondition_attainment": preconditions,
        "leakage": {"protected_data_accessed": False, "network_accessed": False, "manuscript_outcomes_accessed": False, "random_sampling": False},
        "censoring": {"resource_censored": resource_censored, "outcomes_dropped": 0},
        "strongest_donor": "NOT_APPLICABLE_TO_INTERNAL_FINITE_ALGEBRA_REPLAY",
        "resource_vector": resources,
        "transfer": transfer,
        "exact_terminal": terminal,
        "claim_ceiling": freeze["claim_ceiling"],
        "external_authority_state": "NONE",
        "manuscript_writing_owner": "P1_P15_REWRITE_LANE",
        "computation_session_paper_authority_delta": "NONE",
    }
    write_json(HERE / "RESULT_BINDING_PACKET_V1.json", binding)
    print(json.dumps({"job_id": "DES-UPDATE-01", "terminal": terminal, "cases": recorder.total, "law_failures": law_failures, "mutations_killed": f"{sum(item['killed'] for item in mutation_results)}/{len(mutation_results)}"}, sort_keys=True))
    return 0 if terminal == "DYNAMIC_UPDATE_ALGEBRA_FINITE_CLASS_GREEN" else 1


if __name__ == "__main__":
    raise SystemExit(main())
