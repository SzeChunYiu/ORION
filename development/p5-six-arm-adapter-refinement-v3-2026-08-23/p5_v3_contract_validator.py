#!/usr/bin/env python3
"""Validate the P5 V3 refined contract on its declared synthetic domain.

The program performs schema, fibre-constancy, front-registry, invariance,
native-terminal retention, and resource-preflight checks.  It never imports or
executes comparator code and never reads native, benchmark, public, protected,
or performance outputs.
"""

from __future__ import annotations

import hashlib
import json
from collections import Counter, defaultdict
from copy import deepcopy
from pathlib import Path
from typing import Any

HERE = Path(__file__).resolve().parent
HEX = set("0123456789abcdef")
COMPLETE = "COMPLETE_SUCCESS"
UNRESOLVED = "UNRESOLVED"


def load(name: str) -> dict:
    return json.loads((HERE / name).read_text())


def dump(name: str, obj: object) -> None:
    (HERE / name).write_text(json.dumps(obj, indent=2, sort_keys=True) + "\n")


def sha_bytes(data: bytes) -> str:
    return hashlib.sha256(data).hexdigest()


def sha_text(text: str) -> str:
    return sha_bytes(text.encode())


def sha_file(name: str) -> str:
    return sha_bytes((HERE / name).read_bytes())


def canonical(obj: Any) -> str:
    return json.dumps(obj, sort_keys=True, separators=(",", ":"), ensure_ascii=True)


def is_sha(value: Any) -> bool:
    return isinstance(value, str) and len(value) == 64 and all(c in HEX for c in value)


def exact_keys(value: Any, keys: set[str]) -> bool:
    return isinstance(value, dict) and set(value) == keys


def make_certificate(arm: str, cls: str, token: str) -> dict:
    return {
        "schema_version": "orion.p5.candidate-visible-class-certificate.v3",
        "certificate_id": f"P5V3-CERT-{token}",
        "arm_id": arm,
        "observation_id": f"P5V3-OBS-{token}",
        "declared_class": cls,
        "issuance": {
            "issuer_role": "HOST_INPUT_VALIDATOR",
            "phase": "BEFORE_CANDIDATE_ACTION",
            "candidate_visible": True,
            "input_native": True,
            "native_output_access": False,
            "protected_outcome_access": False,
            "sequence": 0,
        },
        "basis": {
            "predicate_id": f"SYNTHETIC_{token}",
            "source_ref_sha256": [sha_text(f"source::{token}")],
            "domain_scope_sha256": sha_text("P5.V3.DECLARED.SYNTHETIC.OUTCOME.FREE.DOMAIN"),
            "fibre_constancy_attestation": {
                "status": "PROVED_ON_DECLARED_SYNTHETIC_DOMAIN",
                "declared_class": cls,
                "proof_ref_sha256": sha_text(f"proof::{token}::{cls}"),
            },
        },
        "complete": True,
    }


def make_action(arm: str, cls: str, token: str, roots: dict[str, str], classes: list[str]) -> dict:
    snapshots = []
    for front in classes:
        before = sha_text(f"front-before::{token}::{front}")
        after = sha_text(f"front-after::{token}::{front}") if front == cls else before
        snapshots.append({
            "class": front,
            "before_sha256": before,
            "after_sha256": after,
            "changed": front == cls,
        })
    mutations = [{
        "mutation_id": f"MUT-{token}",
        "operation": "UPDATE",
        "target_uri": roots[cls] + "candidate-visible-synthetic-object",
        "registry_front": cls,
        "before_sha256": sha_text(f"mutation-before::{token}::{cls}"),
        "after_sha256": sha_text(f"mutation-after::{token}::{cls}"),
    }]
    return {
        "schema_version": "orion.p5.complete-action-write-surface.v3",
        "action_id": f"P5V3-ACT-{token}",
        "arm_id": arm,
        "observation_id": f"P5V3-OBS-{token}",
        "certificate_id": f"P5V3-CERT-{token}",
        "selected_front": cls,
        "declared_complete": True,
        "mutations": mutations,
        "front_snapshots": snapshots,
        "write_set_sha256": sha_text(canonical(mutations)),
        "protected_surface_touched": False,
        "external_scorer_surface_touched": False,
        "arm_specific_guards": {
            "solver_bytes_unchanged": arm == "C5_EVALUATOR_ONLY__DOUBLE_RATCHET_METRIC_ONLY",
            "evaluator_only_mutation": arm == "C5_EVALUATOR_ONLY__DOUBLE_RATCHET_METRIC_ONLY",
            "development_validity_passed": arm == "C5_EVALUATOR_ONLY__DOUBLE_RATCHET_METRIC_ONLY",
        },
    }


def terminal(arm: str, status: str, token: str) -> dict:
    return {
        "arm_id": arm,
        "status": status,
        "native_code": f"SYNTHETIC_NATIVE_{status}",
        "payload_sha256": sha_text(f"synthetic-native-payload::{token}::{status}"),
    }


def case(case_id: str, family: str, arm: str, oracle: str, native: dict,
         certificates: list[dict], action: dict | None, expected: str) -> dict:
    return {
        "case_id": case_id,
        "family": family,
        "arm_id": arm,
        "synthetic_oracle_minimal_class": oracle,
        "native_terminal": native,
        "certificates": certificates,
        "action": action,
        "expected_terminal": expected,
    }


def other_class(cls: str, classes: list[str]) -> str:
    return next(x for x in classes if x != cls)


def generate_cases(domain: dict, registry: dict) -> list[dict]:
    classes = [f["class"] for f in registry["fronts"] if f["actionable"]]
    roots = {f["class"]: f["synthetic_root"] for f in registry["fronts"] if f["actionable"]}
    rows: list[dict] = []

    # Two authored worlds per arm share one raw-visible fibre but disagree.
    for index, (arm, meta) in enumerate(domain["arms"].items(), 1):
        token = f"RAW{index}"
        native = terminal(arm, COMPLETE, token)
        for world, oracle in enumerate(meta["mixed_pair"], 1):
            rows.append(case(f"RAW-{index}-W{world}", "RAW_MIXED_FIBRE", arm, oracle,
                             deepcopy(native), [], None, UNRESOLVED))

    # Two worlds for each supported arm-class cell establish nontrivial constant fibres.
    support_index = 0
    for arm, meta in domain["arms"].items():
        for cls in meta["support"]:
            support_index += 1
            token = f"SUP{support_index}_{cls}"
            cert = make_certificate(arm, cls, token)
            action = make_action(arm, cls, token, roots, classes)
            native = terminal(arm, COMPLETE, token)
            for world in (1, 2):
                rows.append(case(f"SUP-{support_index}-W{world}", "SUPPORTED_CONSTANT_FIBRE", arm, cls,
                                 deepcopy(native), [deepcopy(cert)], deepcopy(action), cls))

    # A superficially valid certificate cannot rescue a mixed declared fibre.
    mixed_index = 0
    for arm, meta in domain["arms"].items():
        if not meta["support"]:
            continue
        mixed_index += 1
        declared = meta["support"][0]
        latent_other = other_class(declared, classes)
        token = f"MIXCERT{mixed_index}"
        cert = make_certificate(arm, declared, token)
        action = make_action(arm, declared, token, roots, classes)
        native = terminal(arm, COMPLETE, token)
        for world, oracle in enumerate((declared, latent_other), 1):
            rows.append(case(f"MIXCERT-{mixed_index}-W{world}", "MISCERTIFIED_MIXED_FIBRE", arm, oracle,
                             deepcopy(native), [deepcopy(cert)], deepcopy(action), UNRESOLVED))

    # Every unsupported arm-class cell receives one otherwise valid synthetic object.
    unsupported_index = 0
    for arm, meta in domain["arms"].items():
        for cls in classes:
            if cls in meta["support"]:
                continue
            unsupported_index += 1
            token = f"UNSUP{unsupported_index}_{cls}"
            rows.append(case(f"UNSUP-{unsupported_index}", "UNSUPPORTED_CLASS", arm, cls,
                             terminal(arm, COMPLETE, token), [make_certificate(arm, cls, token)],
                             make_action(arm, cls, token, roots, classes), UNRESOLVED))

    certificate_variants = ["MISSING", "NONUNIQUE", "INVALID_ISSUER", "LATE", "PROTECTED_ACCESS", "NO_FIBRE_PROOF", "CLASS_MISMATCH"]
    cert_index = 0
    for arm, meta in domain["arms"].items():
        cls = meta["support"][0] if meta["support"] else classes[0]
        for variant in certificate_variants:
            cert_index += 1
            token = f"CERTDEF{cert_index}_{variant}"
            cert = make_certificate(arm, cls, token)
            certs = [cert]
            if variant == "MISSING":
                certs = []
            elif variant == "NONUNIQUE":
                second = deepcopy(cert)
                second["certificate_id"] += ".SECOND"
                certs = [cert, second]
            elif variant == "INVALID_ISSUER":
                cert["issuance"]["issuer_role"] = "CANDIDATE"
            elif variant == "LATE":
                cert["issuance"]["phase"] = "AFTER_CANDIDATE_ACTION"
            elif variant == "PROTECTED_ACCESS":
                cert["issuance"]["protected_outcome_access"] = True
            elif variant == "NO_FIBRE_PROOF":
                cert["basis"]["fibre_constancy_attestation"]["status"] = "UNPROVED"
            elif variant == "CLASS_MISMATCH":
                cert["basis"]["fibre_constancy_attestation"]["declared_class"] = other_class(cls, classes)
            rows.append(case(f"CERTDEF-{cert_index}", "CERTIFICATE_DEFECT", arm, cls,
                             terminal(arm, COMPLETE, token), certs,
                             make_action(arm, cls, token, roots, classes), UNRESOLVED))

    action_variants = ["MISSING", "INCOMPLETE", "MULTI_FRONT", "NONSELECTED_DRIFT", "PATH_OUTSIDE_REGISTRY", "FRONT_MISMATCH", "PROTECTED_SURFACE_TOUCH", "EXTERNAL_SCORER_TOUCH", "HASH_NO_CHANGE", "OBSERVATION_MISMATCH", "CERTIFICATE_MISMATCH"]
    action_index = 0
    for arm, meta in domain["arms"].items():
        cls = meta["support"][0] if meta["support"] else classes[0]
        for variant in action_variants:
            action_index += 1
            token = f"ACTDEF{action_index}_{variant}"
            action = make_action(arm, cls, token, roots, classes)
            if variant == "MISSING":
                action = None
            elif variant == "INCOMPLETE":
                action["declared_complete"] = False
            elif variant == "MULTI_FRONT":
                second = other_class(cls, classes)
                snap = next(x for x in action["front_snapshots"] if x["class"] == second)
                snap["after_sha256"] = sha_text(f"second-front::{token}")
                snap["changed"] = True
                second_mutation = deepcopy(action["mutations"][0])
                second_mutation["mutation_id"] += ".SECOND"
                second_mutation["registry_front"] = second
                second_mutation["target_uri"] = roots[second] + "second-object"
                action["mutations"].append(second_mutation)
            elif variant == "NONSELECTED_DRIFT":
                second = other_class(cls, classes)
                snap = next(x for x in action["front_snapshots"] if x["class"] == second)
                snap["after_sha256"] = sha_text(f"drift::{token}")
                snap["changed"] = True
            elif variant == "PATH_OUTSIDE_REGISTRY":
                action["mutations"][0]["target_uri"] = "synthetic://unregistered/object"
            elif variant == "FRONT_MISMATCH":
                action["mutations"][0]["registry_front"] = other_class(cls, classes)
            elif variant == "PROTECTED_SURFACE_TOUCH":
                action["protected_surface_touched"] = True
            elif variant == "EXTERNAL_SCORER_TOUCH":
                action["external_scorer_surface_touched"] = True
            elif variant == "HASH_NO_CHANGE":
                snap = next(x for x in action["front_snapshots"] if x["class"] == cls)
                snap["after_sha256"] = snap["before_sha256"]
                snap["changed"] = False
                action["mutations"][0]["after_sha256"] = action["mutations"][0]["before_sha256"]
            elif variant == "OBSERVATION_MISMATCH":
                action["observation_id"] += ".OTHER"
            elif variant == "CERTIFICATE_MISMATCH":
                action["certificate_id"] += ".OTHER"
            rows.append(case(f"ACTDEF-{action_index}", "ACTION_OR_INVARIANCE_DEFECT", arm, cls,
                             terminal(arm, COMPLETE, token), [make_certificate(arm, cls, token)],
                             action, UNRESOLVED))

    # All six noncomplete native statuses dominate otherwise absent action records.
    native_index = 0
    for arm in domain["arms"]:
        for status in domain["native_statuses"]:
            if status == COMPLETE:
                continue
            native_index += 1
            token = f"NATIVE{native_index}_{status}"
            rows.append(case(f"NATIVE-{native_index}", "NATIVE_NONCOMPLETE_TERMINAL", arm, UNRESOLVED,
                             terminal(arm, status, token), [], None, UNRESOLVED))

    dr_arm = "C5_EVALUATOR_ONLY__DOUBLE_RATCHET_METRIC_ONLY"
    for index, variant in enumerate(("SOLVER_DRIFT", "NON_EVALUATOR_MUTATION", "DEVELOPMENT_VALIDITY_FAILED"), 1):
        token = f"DRGUARD{index}_{variant}"
        cert = make_certificate(dr_arm, "EVALUATOR_REPAIR", token)
        action = make_action(dr_arm, "EVALUATOR_REPAIR", token, roots, classes)
        if variant == "SOLVER_DRIFT":
            action["arm_specific_guards"]["solver_bytes_unchanged"] = False
        elif variant == "NON_EVALUATOR_MUTATION":
            action["arm_specific_guards"]["evaluator_only_mutation"] = False
        else:
            action["arm_specific_guards"]["development_validity_passed"] = False
        rows.append(case(f"DRGUARD-{index}", "DOUBLE_RATCHET_GUARD_DEFECT", dr_arm, "EVALUATOR_REPAIR",
                         terminal(dr_arm, COMPLETE, token), [cert], action, UNRESOLVED))

    return rows


def validate_certificate(cert: Any, arms: set[str], classes: set[str]) -> list[str]:
    errors = []
    top = {"schema_version", "certificate_id", "arm_id", "observation_id", "declared_class", "issuance", "basis", "complete"}
    if not exact_keys(cert, top):
        return ["CERTIFICATE_SHAPE"]
    if cert["schema_version"] != "orion.p5.candidate-visible-class-certificate.v3": errors.append("CERTIFICATE_SCHEMA_VERSION")
    if not isinstance(cert["certificate_id"], str) or not cert["certificate_id"].startswith("P5V3-CERT-"): errors.append("CERTIFICATE_ID")
    if cert["arm_id"] not in arms: errors.append("CERTIFICATE_ARM")
    if not isinstance(cert["observation_id"], str) or not cert["observation_id"].startswith("P5V3-OBS-"): errors.append("CERTIFICATE_OBSERVATION")
    if cert["declared_class"] not in classes: errors.append("CERTIFICATE_CLASS")
    if cert["complete"] is not True: errors.append("CERTIFICATE_INCOMPLETE")
    issuance_keys = {"issuer_role", "phase", "candidate_visible", "input_native", "native_output_access", "protected_outcome_access", "sequence"}
    issuance = cert["issuance"]
    if not exact_keys(issuance, issuance_keys):
        errors.append("ISSUANCE_SHAPE")
    else:
        expected = {
            "issuer_role": "HOST_INPUT_VALIDATOR", "phase": "BEFORE_CANDIDATE_ACTION",
            "candidate_visible": True, "input_native": True,
            "native_output_access": False, "protected_outcome_access": False,
        }
        for key, value in expected.items():
            if issuance[key] != value: errors.append(f"ISSUANCE_{key.upper()}")
        if not isinstance(issuance["sequence"], int) or issuance["sequence"] < 0: errors.append("ISSUANCE_SEQUENCE")
    basis_keys = {"predicate_id", "source_ref_sha256", "domain_scope_sha256", "fibre_constancy_attestation"}
    basis = cert["basis"]
    if not exact_keys(basis, basis_keys):
        errors.append("BASIS_SHAPE")
    else:
        if not isinstance(basis["predicate_id"], str) or not basis["predicate_id"].startswith("SYNTHETIC_"): errors.append("PREDICATE_ID")
        refs = basis["source_ref_sha256"]
        if not isinstance(refs, list) or not refs or len(set(refs)) != len(refs) or not all(is_sha(x) for x in refs): errors.append("SOURCE_REFS")
        if not is_sha(basis["domain_scope_sha256"]): errors.append("DOMAIN_SCOPE")
        att = basis["fibre_constancy_attestation"]
        if not exact_keys(att, {"status", "declared_class", "proof_ref_sha256"}):
            errors.append("FIBRE_ATTESTATION_SHAPE")
        else:
            if att["status"] != "PROVED_ON_DECLARED_SYNTHETIC_DOMAIN": errors.append("FIBRE_ATTESTATION_STATUS")
            if att["declared_class"] != cert["declared_class"]: errors.append("FIBRE_ATTESTATION_CLASS")
            if not is_sha(att["proof_ref_sha256"]): errors.append("FIBRE_ATTESTATION_PROOF")
    return errors


def validate_action(action: Any, arms: set[str], classes: list[str], roots: dict[str, str]) -> list[str]:
    errors = []
    top = {"schema_version", "action_id", "arm_id", "observation_id", "certificate_id", "selected_front", "declared_complete", "mutations", "front_snapshots", "write_set_sha256", "protected_surface_touched", "external_scorer_surface_touched", "arm_specific_guards"}
    if not exact_keys(action, top):
        return ["ACTION_SHAPE"]
    if action["schema_version"] != "orion.p5.complete-action-write-surface.v3": errors.append("ACTION_SCHEMA_VERSION")
    if not isinstance(action["action_id"], str) or not action["action_id"].startswith("P5V3-ACT-"): errors.append("ACTION_ID")
    if action["arm_id"] not in arms: errors.append("ACTION_ARM")
    if action["selected_front"] not in classes: errors.append("ACTION_SELECTED_FRONT")
    if action["declared_complete"] is not True: errors.append("ACTION_INCOMPLETE")
    if action["protected_surface_touched"] is not False: errors.append("PROTECTED_SURFACE_TOUCHED")
    if action["external_scorer_surface_touched"] is not False: errors.append("EXTERNAL_SCORER_SURFACE_TOUCHED")
    mutations = action["mutations"]
    if not isinstance(mutations, list) or not mutations:
        errors.append("MUTATIONS_EMPTY")
    else:
        for mutation in mutations:
            keys = {"mutation_id", "operation", "target_uri", "registry_front", "before_sha256", "after_sha256"}
            if not exact_keys(mutation, keys):
                errors.append("MUTATION_SHAPE"); continue
            if mutation["registry_front"] != action["selected_front"]: errors.append("MUTATION_FRONT_MISMATCH")
            if mutation["registry_front"] not in roots or not mutation["target_uri"].startswith(roots.get(mutation["registry_front"], "<none>")): errors.append("MUTATION_PATH_OUTSIDE_REGISTRY")
            if not is_sha(mutation["before_sha256"]) or not is_sha(mutation["after_sha256"]): errors.append("MUTATION_HASH")
            if mutation["before_sha256"] == mutation["after_sha256"]: errors.append("MUTATION_NO_CHANGE")
        if action["write_set_sha256"] != sha_text(canonical(mutations)): errors.append("WRITE_SET_HASH_MISMATCH")
    snapshots = action["front_snapshots"]
    if not isinstance(snapshots, list) or len(snapshots) != len(classes) or {x.get("class") for x in snapshots if isinstance(x, dict)} != set(classes):
        errors.append("FRONT_SNAPSHOT_COVERAGE")
    else:
        changed = []
        for snap in snapshots:
            if not exact_keys(snap, {"class", "before_sha256", "after_sha256", "changed"}): errors.append("FRONT_SNAPSHOT_SHAPE"); continue
            if not is_sha(snap["before_sha256"]) or not is_sha(snap["after_sha256"]): errors.append("FRONT_SNAPSHOT_HASH")
            actual = snap["before_sha256"] != snap["after_sha256"]
            if snap["changed"] is not actual: errors.append("FRONT_CHANGED_FLAG")
            if actual: changed.append(snap["class"])
        if changed != [action["selected_front"]]: errors.append("NONSELECTED_FRONT_INVARIANCE")
    guards = action["arm_specific_guards"]
    if not exact_keys(guards, {"solver_bytes_unchanged", "evaluator_only_mutation", "development_validity_passed"}) or not all(isinstance(v, bool) for v in guards.values()):
        errors.append("ARM_GUARD_SHAPE")
    elif action["arm_id"] == "C5_EVALUATOR_ONLY__DOUBLE_RATCHET_METRIC_ONLY":
        if not guards["solver_bytes_unchanged"]: errors.append("DOUBLE_RATCHET_SOLVER_DRIFT")
        if not guards["evaluator_only_mutation"]: errors.append("DOUBLE_RATCHET_NON_EVALUATOR_MUTATION")
        if not guards["development_validity_passed"]: errors.append("DOUBLE_RATCHET_DEVELOPMENT_VALIDITY")
    return errors


def visible_signature(row: dict) -> str:
    visible = {
        "arm_id": row["arm_id"],
        "native_terminal": row["native_terminal"],
        "certificates": row["certificates"],
        "action": row["action"],
    }
    return sha_text(canonical(visible))


def evaluate(row: dict, fibre_classes: set[str], support: dict[str, set[str]],
             arms: set[str], classes: list[str], roots: dict[str, str]) -> tuple[str, str, list[str]]:
    native = row["native_terminal"]
    terminal_errors = []
    if not exact_keys(native, {"arm_id", "status", "native_code", "payload_sha256"}): terminal_errors.append("NATIVE_TERMINAL_SHAPE")
    elif native["arm_id"] != row["arm_id"] or not is_sha(native["payload_sha256"]): terminal_errors.append("NATIVE_TERMINAL_IDENTITY")
    if terminal_errors:
        return UNRESOLVED, "INVALID_NATIVE_TERMINAL", terminal_errors
    if native["status"] != COMPLETE:
        return UNRESOLVED, "NATIVE_TERMINAL_PRESERVED", []
    if len(fibre_classes) != 1:
        return UNRESOLVED, "FIBRE_NOT_CONSTANT", []
    certificates = row["certificates"]
    if not isinstance(certificates, list) or len(certificates) != 1:
        return UNRESOLVED, "CERTIFICATE_NOT_UNIQUE", []
    cert_errors = validate_certificate(certificates[0], arms, set(classes))
    if cert_errors:
        return UNRESOLVED, "CERTIFICATE_SCHEMA_OR_AUTHORITY_FAILURE", cert_errors
    if row["action"] is None:
        return UNRESOLVED, "ACTION_MISSING", []
    action_errors = validate_action(row["action"], arms, classes, roots)
    if action_errors:
        if any(x.startswith("DOUBLE_RATCHET_") for x in action_errors):
            return UNRESOLVED, "DOUBLE_RATCHET_GUARD_FAILURE", action_errors
        return UNRESOLVED, "ACTION_SCHEMA_OR_INVARIANCE_FAILURE", action_errors
    cert = certificates[0]
    action = row["action"]
    if cert["arm_id"] != row["arm_id"] or action["arm_id"] != row["arm_id"]:
        return UNRESOLVED, "ARM_MISMATCH", []
    if cert["observation_id"] != action["observation_id"]:
        return UNRESOLVED, "OBSERVATION_MISMATCH", []
    if cert["certificate_id"] != action["certificate_id"]:
        return UNRESOLVED, "CERTIFICATE_ACTION_MISMATCH", []
    if cert["declared_class"] != action["selected_front"]:
        return UNRESOLVED, "CLASS_MISMATCH", []
    declared = cert["declared_class"]
    if declared not in support[row["arm_id"]]:
        return UNRESOLVED, "UNSUPPORTED_ARM_CLASS", []
    if fibre_classes != {declared}:
        return UNRESOLVED, "FIBRE_CLASS_DISAGREEMENT", []
    return declared, "DECLARED_SYNTHETIC_FIBRE_CONSTANT_AND_NONSELECTED_FRONTS_INVARIANT", []


def main() -> None:
    protocol = load("P5_V3_REFINED_ADAPTER_PROTOCOL.json")
    domain = load("P5_V3_DECLARED_SYNTHETIC_DOMAIN.json")
    registry = load("P5_V3_EIGHT_CLASS_FRONT_REGISTRY.json")
    terminal_rules = load("P5_V3_NATIVE_TERMINAL_RETENTION_RULES.json")
    manifest = load("P5_V3_MATCHED_RESOURCE_MANIFEST_TEMPLATE.json")
    certificate_schema = load("P5_V3_CANDIDATE_VISIBLE_CERTIFICATE_SCHEMA.json")
    action_schema = load("P5_V3_ACTION_WRITE_SURFACE_SCHEMA.json")

    assert protocol["outcome_boundary"] == {
        "comparators_or_models_executed": False,
        "fixtures": "prospectively generated synthetic contract objects only",
        "native_comparator_output_examples_accessed": False,
        "performance_tables_accessed": False,
        "protected_data_accessed": False,
        "public_or_protected_outcome_rows_accessed": False,
    }
    assert domain["native_examples_used"] is False
    assert domain["outcome_rows_used"] is False
    assert domain["performance_examples_used"] is False
    classes = [f["class"] for f in registry["fronts"] if f["actionable"]]
    outputs = classes + [UNRESOLVED]
    roots = {f["class"]: f["synthetic_root"] for f in registry["fronts"] if f["actionable"]}
    arms = set(domain["arms"])
    assert len(arms) == 6 and len(classes) == 7 and len(outputs) == 8
    assert set(certificate_schema["properties"]["arm_id"]["enum"]) == arms
    assert certificate_schema["properties"]["declared_class"]["enum"] == classes
    assert set(action_schema["properties"]["arm_id"]["enum"]) == arms
    assert action_schema["properties"]["selected_front"]["enum"] == classes
    assert action_schema["properties"]["mutations"]["items"]["properties"]["registry_front"]["enum"] == classes
    assert set(protocol["arm_support_sets"]) == arms == set(registry["arm_support_sets"])
    assert registry["raw_native_singletons_licensed"] == 0
    assert registry["arm_support_sets"]["C6_MODERN_SOURCE_GROUNDED__SCIENCECLAW"] == []
    assert terminal_rules["native_status_vocabulary"] == domain["native_statuses"]

    rows = generate_cases(domain, registry)
    family_counts = Counter(row["family"] for row in rows)
    expected_family_counts = {
        "RAW_MIXED_FIBRE": 12,
        "SUPPORTED_CONSTANT_FIBRE": 40,
        "MISCERTIFIED_MIXED_FIBRE": 10,
        "UNSUPPORTED_CLASS": 22,
        "CERTIFICATE_DEFECT": 42,
        "ACTION_OR_INVARIANCE_DEFECT": 66,
        "NATIVE_NONCOMPLETE_TERMINAL": 36,
        "DOUBLE_RATCHET_GUARD_DEFECT": 3,
    }
    assert dict(family_counts) == expected_family_counts
    assert len(rows) == 231
    assert len({row["case_id"] for row in rows}) == len(rows)

    fibres: dict[str, set[str]] = defaultdict(set)
    for row in rows:
        fibres[visible_signature(row)].add(row["synthetic_oracle_minimal_class"])

    support = {arm: set(values) for arm, values in registry["arm_support_sets"].items()}
    records = []
    unhandled = []
    for row in rows:
        try:
            observed, reason, details = evaluate(row, fibres[visible_signature(row)], support, arms, classes, roots)
        except Exception as exc:  # fail closed and report totality failure
            observed, reason, details = UNRESOLVED, "UNHANDLED_EXCEPTION", [f"{type(exc).__name__}: {exc}"]
            unhandled.append(row["case_id"])
        retained = deepcopy(row["native_terminal"])
        records.append({
            "case_id": row["case_id"],
            "family": row["family"],
            "arm_id": row["arm_id"],
            "expected_terminal": row["expected_terminal"],
            "observed_terminal": observed,
            "reason": reason,
            "validation_details": details,
            "native_terminal_retained": retained,
            "native_terminal_exact": retained == row["native_terminal"],
            "output_in_eight_class_vocabulary": observed in outputs,
            "synthetic_contract_expectation_met": observed == row["expected_terminal"],
        })

    assert not unhandled
    assert all(r["native_terminal_exact"] for r in records)
    assert all(r["output_in_eight_class_vocabulary"] for r in records)
    assert all(r["synthetic_contract_expectation_met"] for r in records)
    output_counts = Counter(r["observed_terminal"] for r in records)
    assert output_counts[UNRESOLVED] == 191
    assert sum(output_counts[c] for c in classes) == 40

    mixed_fibres = sum(1 for values in fibres.values() if len(values) > 1)
    constant_fibres = sum(1 for values in fibres.values() if len(values) == 1)
    supported_constant_fibres = sum(len(meta["support"]) for meta in domain["arms"].values())
    assert mixed_fibres == 11  # six raw plus five deliberately miscertified fibres
    assert supported_constant_fibres == 20

    receipt = {
        "schema_version": "orion.p5.refined-adapter-synthetic-conformance-receipt.v3",
        "protocol_id": protocol["protocol_id"],
        "authority": "FINITE_DECLARED_SYNTHETIC_DOMAIN_TOTALITY_AND_CONFORMANCE_ONLY__NOT_PERFORMANCE",
        "artifact_hashes": {
            name: sha_file(name) for name in [
                "P5_V3_CANDIDATE_VISIBLE_CERTIFICATE_SCHEMA.json",
                "P5_V3_ACTION_WRITE_SURFACE_SCHEMA.json",
                "P5_V3_EIGHT_CLASS_FRONT_REGISTRY.json",
                "P5_V3_NATIVE_TERMINAL_RETENTION_RULES.json",
                "P5_V3_REFINED_ADAPTER_PROTOCOL.json",
                "P5_V3_DECLARED_SYNTHETIC_DOMAIN.json",
                "P5_V3_MATCHED_RESOURCE_MANIFEST_TEMPLATE.json",
            ]
        },
        "outcome_boundary": {
            "native_comparator_output_examples_accessed": False,
            "public_or_protected_outcome_rows_accessed": False,
            "comparators_or_models_executed": False,
            "performance_tables_accessed": False,
            "protected_data_accessed": False,
        },
        "declared_domain": {
            "cases": len(records),
            "case_family_counts": dict(sorted(family_counts.items())),
            "adapter_visible_fibres": len(fibres),
            "constant_fibres": constant_fibres,
            "mixed_fibres": mixed_fibres,
            "supported_constant_fibres": supported_constant_fibres,
        },
        "totality": {
            "cases_evaluated": len(records),
            "unhandled_exceptions": len(unhandled),
            "outputs_outside_eight_class_vocabulary": sum(not r["output_in_eight_class_vocabulary"] for r in records),
            "native_terminal_retention_failures": sum(not r["native_terminal_exact"] for r in records),
            "synthetic_contract_expectation_failures": sum(not r["synthetic_contract_expectation_met"] for r in records),
            "total_on_declared_synthetic_domain": True,
        },
        "outputs": {
            "counts": dict(sorted(output_counts.items())),
            "singleton_cases": sum(output_counts[c] for c in classes),
            "unresolved_cases": output_counts[UNRESOLVED],
            "supported_singleton_fibres": supported_constant_fibres,
            "raw_native_singleton_licences": 0,
            "scienceclaw_supported_singletons": 0,
        },
        "reason_counts": dict(sorted(Counter(r["reason"] for r in records).items())),
        "case_records": records,
        "interpretation": "The refined adapter is a total deterministic contract on exactly the 231 frozen fictional cases. Forty case records in twenty constant supported fibres emit a class; 191 remain UNRESOLVED. These are schema/fibre/invariance conformance records, not comparator outcomes, scientific units, performance, correctness, preservation, transfer, harm, or superiority.",
        "terminal": "P5_V3_REFINED_CONTRACT_TOTAL_ON_DECLARED_SYNTHETIC_DOMAIN__ZERO_RAW_SINGLETON_LICENCES__NOT_COMPARATOR_PERFORMANCE",
    }
    dump("P5_V3_SYNTHETIC_CONFORMANCE_RECEIPT.json", receipt)

    blocker_rows = []
    readiness = {}
    required_paths = {path for path, spec in manifest["field_definitions"].items() if spec["required_for_execution"]}
    for arm in manifest["arm_manifests"]:
        assert set(arm["fields"]) == required_paths
        arm_blockers = []
        for path in sorted(required_paths):
            state = arm["fields"][path]["state"]
            if state != "BOUND":
                row = {
                    "arm_id": arm["arm_id"], "arm_name": arm["name"], "field_path": path,
                    "state": state, "cause": arm["fields"][path]["blocker_reason"],
                    "residual": "Execution cannot be licensed from a template, freezable value, unresolved right, unsupported selector, or unverified custody assertion.",
                    "next_discriminator": "Freeze a lawful content-addressed value before any outcome access, then rerun outcome-free preflight; for UNSUPPORTED ScienceClaw selector, preregister a separately named successor method rather than relabeling the native interface.",
                }
                blocker_rows.append(row)
                arm_blockers.append(path)
        readiness[arm["arm_id"]] = {
            "ready": len(arm_blockers) == 0,
            "blocking_field_count": len(arm_blockers),
            "blocking_fields": arm_blockers,
        }
    assert sum(v["ready"] for v in readiness.values()) == 0
    assert all(v["blocking_field_count"] == 18 for v in readiness.values())
    assert len(blocker_rows) == 108

    blocker_ledger = {
        "schema_version": "orion.p5.execution-blocker-ledger.v3",
        "protocol_id": protocol["protocol_id"],
        "authority": "OUTCOME_FREE_RESOURCE_RIGHTS_AND_CUSTODY_PREFLIGHT_ONLY",
        "manifest_sha256": sha_file("P5_V3_MATCHED_RESOURCE_MANIFEST_TEMPLATE.json"),
        "generic_contract_sha256": sha_file("P5_V3_REFINED_ADAPTER_PROTOCOL.json"),
        "generic_contract_total_on_declared_synthetic_domain": True,
        "generic_contract_is_not_arm_native_execution_binding": True,
        "confirmatory_ready_arms": 0,
        "total_arms": 6,
        "blocking_field_instances": len(blocker_rows),
        "readiness_by_arm": readiness,
        "blockers": blocker_rows,
        "preserved_terminal": "P5_SIX_ARM_EXECUTION_CONFIG_RESOURCE_RIGHTS_AND_EIGHT_CLASS_ADAPTERS_CANNOT_CHECK",
        "next_discriminator": "Bind every listed field without opening outcomes. Then independently verify rights and protected-score custody. Do not execute any arm while a required field is UNBOUND, CANNOT_CHECK or UNSUPPORTED.",
    }
    dump("P5_V3_EXECUTION_BLOCKER_LEDGER.json", blocker_ledger)

    result = {
        "schema_version": "orion.p5.six-arm-adapter-refinement-result.v3",
        "protocol_id": protocol["protocol_id"],
        "authority": "FORMAL_CONTRACT_AND_SYNTHETIC_CONFORMANCE_ONLY",
        "terminal": "P5_V3_REFINED_ADAPTER_CONTRACT_TOTAL_ON_DECLARED_SYNTHETIC_DOMAIN__ZERO_RAW_SINGLETONS__ZERO_OF_SIX_EXECUTION_READY__P5_COMPARATOR_PERFORMANCE_AND_SUPERIORITY_CANNOT_CHECK",
        "contract_result": {
            "total_on_declared_synthetic_domain": True,
            "synthetic_cases": len(records),
            "supported_singleton_case_records": sum(output_counts[c] for c in classes),
            "supported_singleton_fibres": supported_constant_fibres,
            "unresolved_case_records": output_counts[UNRESOLVED],
            "failures": 0,
            "raw_native_singleton_licences": 0,
            "scienceclaw_supported_singletons": 0,
            "receipt_path": "P5_V3_SYNTHETIC_CONFORMANCE_RECEIPT.json",
            "receipt_sha256": sha_file("P5_V3_SYNTHETIC_CONFORMANCE_RECEIPT.json"),
        },
        "execution_result": {
            "confirmatory_ready_arms": 0,
            "required_arms": 6,
            "blocking_field_instances": len(blocker_rows),
            "blocking_fields_per_arm": {arm: row["blocking_field_count"] for arm, row in readiness.items()},
            "blocker_ledger_path": "P5_V3_EXECUTION_BLOCKER_LEDGER.json",
            "blocker_ledger_sha256": sha_file("P5_V3_EXECUTION_BLOCKER_LEDGER.json"),
            "terminal": "P5_SIX_ARM_EXECUTION_CONFIG_RESOURCE_RIGHTS_AND_EIGHT_CLASS_ADAPTERS_CANNOT_CHECK",
        },
        "preserved_claims": {
            "H1": "CANNOT_CHECK", "H2": "CANNOT_CHECK", "H3": "CANNOT_CHECK", "H4": "CANNOT_CHECK",
            "protected_freshness": "CANNOT_CHECK", "performance": "CANNOT_CHECK", "harm": "CANNOT_CHECK", "superiority": "CANNOT_CHECK",
            "top_tier_publication_readiness": "NOT_ESTABLISHED",
        },
        "nonclaims": "No conformance count is a performance estimate or scientific outcome. No arm was executed. No comparator output was observed.",
        "next_discriminator": "Resolve the 108 arm-field blocker instances prospectively, beginning with a lawful exact P5 case packet and an arm-native parser/write-isolation binding. ScienceClaw requires a separately named successor selector or remains UNRESOLVED. Independent custody must then freeze a fresh protected panel and one-shot no-feedback scorer before any confirmatory execution.",
    }
    dump("P5_RESULT_V3.json", result)
    print(json.dumps({
        "terminal": result["terminal"],
        "cases": len(records),
        "supported_case_records": result["contract_result"]["supported_singleton_case_records"],
        "supported_fibres": supported_constant_fibres,
        "unresolved_case_records": result["contract_result"]["unresolved_case_records"],
        "failures": result["contract_result"]["failures"],
        "confirmatory_ready": "0/6",
        "blocking_field_instances": len(blocker_rows),
    }, indent=2))


if __name__ == "__main__":
    main()
