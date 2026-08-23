from __future__ import annotations

import importlib.util
import json
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[3]
NATIVE_PATH = ROOT / "research" / "claim_expansion" / "p1" / "gpt_r6" / "native_orion.py"
PROTOCOL_PATH = NATIVE_PATH.parent / "NATIVE_PROTOCOL_V1.json"
REGISTRY_PATH = ROOT / "src" / "orion" / "registry.py"


def load_native():
    name = "p1_u_r6_native_orion"
    spec = importlib.util.spec_from_file_location(name, NATIVE_PATH)
    assert spec and spec.loader
    module = importlib.util.module_from_spec(spec)
    sys.modules[name] = module
    try:
        spec.loader.exec_module(module)
    except Exception:
        sys.modules.pop(name, None)
        raise
    return module


def all_probes(native, *, support: str | None = None, unresolved: bool = False):
    values = {}
    for probe, cls in native.PROBE_TO_CLASS.items():
        if unresolved:
            values[probe] = "INCONCLUSIVE"
        elif cls == support:
            values[probe] = "SUPPORT"
        else:
            values[probe] = "REFUTE"
    return values


def episode(native, *, episode_id: str, dossier: str, support: str | None = None, unresolved: bool = False):
    return {
        "id": episode_id,
        "actual_domain": "synthetic-pre-outcome",
        "dossier": dossier,
        "probes": all_probes(native, support=support, unresolved=unresolved),
        "gold_class": "THIS_FIELD_MUST_BE_IGNORED",
        "pair_role": "THIS_FIELD_MUST_BE_IGNORED",
        "source_id": "THIS_FIELD_MUST_BE_IGNORED",
    }


def test_root_execution_uses_canonical_runtime_and_native_responsibility_enum():
    n = load_native()
    root = n.run_root_runtime(
        episode_id="root-representation",
        dossier="A coordinate transformation and schema mapping remain uncertain for the same scientific target.",
        domain="synthetic",
    )
    required = set(n.PROTOCOL["root_runtime"]["required_operator_ids"])
    assert required <= set(root.operator_ids)
    assert root.result.trace.trace_id.startswith("trace:p1-r6-root:root-representation:")
    assert "EVIDENCE" in root.provider_responsibilities
    assert "REPRESENTATION" in root.provider_responsibilities
    assert not any(value in n.PROBE_TO_CLASS.values() for value in root.provider_responsibilities)


def test_native_probe_runs_through_verified_runtime_evidence():
    n = load_native()
    case = episode(
        n,
        episode_id="probe-representation",
        dossier="A coordinate transformation and representation mapping fail while the scientific target remains fixed.",
        support="REPRESENTATION_OR_INTERFACE",
    )
    result = n.run_native_ard(case, evidence_note="synthetic pre-outcome native smoke evidence")
    assert result["choice"] == "REPRESENTATION_OR_INTERFACE"
    assert result["probe_accesses"] == ["P_SEARCH_COVERAGE", "P_REPRESENTATION_ROUNDTRIP"]
    assert len(result["probe_executions"]) == 2
    required = set(n.PROTOCOL["probe_runtime"]["required_operator_ids"])
    for execution in result["probe_executions"]:
        assert required <= set(execution["operator_ids"])
        assert execution["evidence_id"].startswith("evidence:p1-r6:")
        assert execution["trace_id"].startswith("trace:p1-r6-probe:")
    assert result["revision_gate_status"] == "CANDIDATE_SELECTED"
    assert result["selected_mechanic_id"] == "P1_NATIVE_INTERFACE_REPAIR.v1"
    assert result["grants_adoption_authority"] is False
    assert result["grants_promotion_authority"] is False
    assert result["grants_merge_authority"] is False


def test_native_ard_reaches_each_registered_p1_family_control_and_unresolved():
    n = load_native()
    cases = [
        (
            "SEARCH_OR_EVIDENCE",
            "Sparse detections and missing values leave insufficient observations and sample-size coverage.",
        ),
        (
            "REPRESENTATION_OR_INTERFACE",
            "A coordinate transformation, schema mapping and representation mismatch block the same target.",
        ),
        (
            "IMPLEMENTATION_OR_ENVIRONMENT",
            "A software implementation on a different machine suffers precision and rounding error.",
        ),
        (
            "MEASUREMENT_OR_EVALUATOR",
            "Instrument calibration and optical signal measurement bias distort the same scientific quantity.",
        ),
        (
            "OBJECTIVE_OR_MODEL_CLASS",
            "A misspecified structural model and loss remain inadequate under the mechanistic interaction regime.",
        ),
        (
            "PROBLEM_BOUNDARY",
            "Transport beyond the trial population and an open-system boundary change the relevant problem scope.",
        ),
    ]
    for i, (expected, dossier) in enumerate(cases):
        case = episode(n, episode_id=f"family-{i}", dossier=dossier, support=expected)
        result = n.run_native_ard(case, evidence_note="synthetic pre-outcome family reachability")
        assert result["choice"] == expected, (expected, result)
        assert len(result["probe_accesses"]) <= int(n.PROTOCOL["budget"])
        assert result["responsibility_status"] == "IDENTIFIED"
        assert result["revision_gate_status"] == "CANDIDATE_SELECTED"

    control = episode(
        n,
        episode_id="control",
        dossier="A coordinate transformation and schema mapping are used in an adequate matched regime for the same target.",
        support=None,
    )
    control_result = n.run_native_ard(control, evidence_note="synthetic pre-outcome control")
    assert control_result["choice"] == n.CONTROL
    assert control_result["selected_mechanic_id"] == "P1_NATIVE_KEEP_CURRENT.v1"

    unresolved = episode(
        n,
        episode_id="unresolved",
        dossier="Multiple causal explanations and representation alternatives remain plausible from the available comparison.",
        unresolved=True,
    )
    unresolved_result = n.run_native_ard(unresolved, evidence_note="synthetic pre-outcome unresolved")
    assert unresolved_result["choice"] == n.UNRESOLVED
    assert unresolved_result["responsibility_status"] in {"AMBIGUOUS", "UNRESOLVED"}
    assert unresolved_result["revision_gate_status"] == "UNRESOLVED"


def test_native_base_is_real_ablation_and_ard_materially_changes_ambiguous_family():
    n = load_native()
    case = episode(
        n,
        episode_id="base-v-ard",
        dossier="A coordinate transformation and schema representation mismatch remain possible while evidence insufficiency also remains plausible.",
        support="REPRESENTATION_OR_INTERFACE",
    )
    base = n.run_native_base(case)
    ard = n.run_native_ard(case, evidence_note="synthetic pre-outcome base-v-ard")
    assert base["arm"] == "ORION_NATIVE_BASE"
    assert base["probe_accesses"] == []
    assert base["choice"] == n.UNRESOLVED
    assert ard["choice"] == "REPRESENTATION_OR_INTERFACE"
    assert ard["choice"] != base["choice"]


def test_gold_source_and_pair_metadata_cannot_change_native_decision():
    n = load_native()
    base_case = episode(
        n,
        episode_id="leakage",
        dossier="A software implementation and machine precision error affect an otherwise fixed scientific model.",
        support="IMPLEMENTATION_OR_ENVIRONMENT",
    )
    first = n.run_native_ard(base_case, evidence_note="same visible evidence")
    mutated = dict(base_case)
    mutated["gold_class"] = "PROBLEM_BOUNDARY"
    mutated["pair_role"] = "CONTROL"
    mutated["source_id"] = "secret:changed"
    second = n.run_native_ard(mutated, evidence_note="same visible evidence")
    # Runtime UUID trace identities differ; compare the scientific/native path only.
    assert first["choice"] == second["choice"]
    assert first["probe_accesses"] == second["probe_accesses"]
    assert first["responsibility_status"] == second["responsibility_status"]
    assert first["selected_mechanic_id"] == second["selected_mechanic_id"]


def test_native_candidate_has_no_doctrine_policy_import_and_registry_is_unmodified():
    text = NATIVE_PATH.read_text()
    assert "gpt_r2.policy" not in text
    assert "orion_r2_policy" not in text
    registry = REGISTRY_PATH.read_text()
    assert "P1_NATIVE_SEARCH_REPAIR.v1" not in registry
    assert "P1_NATIVE_INTERFACE_REPAIR.v1" not in registry
    assert "P1_NATIVE_METHOD_ESCALATION.v1" not in registry


def test_protocol_forbids_authority_and_registry_promotion_before_evidence():
    protocol = json.loads(PROTOCOL_PATH.read_text())
    assert protocol["self_authorization"] is False
    assert protocol["registry_mutation_before_primary_and_replication_pass"] is False
    assert protocol["native_base_ablation_required"] is True
    assert protocol["native_ard_must_materially_differ_from_base"] is True
