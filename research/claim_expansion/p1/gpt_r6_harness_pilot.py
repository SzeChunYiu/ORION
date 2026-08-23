from __future__ import annotations

import json
import tempfile
from pathlib import Path

from orion_research_harness.protocol import CapabilityRequest
from orion_research_harness.runner import run_problem
from orion_research_harness.workspace import ResearchWorkspace
from orion.self_orion.revision_gate import RevisionGateStatus, assess_revision_gate
from orion.transfer.v2.epistemic_responsibility import (
    ResponsibilityStatus,
    assess_responsibility,
    build_responsibility_hypothesis,
)
from orion.transfer.v2.higher_order_epistemic_mechanics import (
    AssessmentStatus,
    ObligationState,
    assess_mechanic,
    build_mechanic,
)
from orion.transfer.v2.interface_adequacy import (
    InterfaceAdequacyStatus,
    InterfaceCheckState,
    assess_interface_adequacy,
    build_interface_check,
)

DOSSIER = (
    "A random-effects meta-analysis uses study summaries from studies with modest participant "
    "counts. Individual participant records exist, while the inferential model, estimand, and "
    "study collection are otherwise unchanged."
)
SOURCE = (
    "Min & Zhang, Relative Efficiency of Using Summary Versus Individual Data in Random-Effects "
    "Meta-Analysis, Biometrics 2020, DOI 10.1111/biom.13238. The source reports asymptotic "
    "equivalence but appreciable summary-data efficiency loss when sample sizes are not sufficiently large."
)


def service(workspace: ResearchWorkspace, request: CapabilityRequest) -> None:
    p = request.payload
    if request.capability == "LLM_COMPLETE":
        task = p["task"]
        if task == "plan_search":
            content = json.dumps(
                {
                    "queries": [
                        {
                            "query_id": "frozen-search-p1",
                            "text": "frozen SEARCH-P1 source",
                            "route_id": "frozen-r4",
                            "route_kind": "FRESHNESS",
                            "domain_hint": "meta_analysis",
                        }
                    ]
                }
            )
        elif task == "interpret":
            content = json.dumps(
                {
                    "contribution_id": "p1-r6-search-p1",
                    "text": (
                        "The fixed source indicates an evidence/information sufficiency limitation "
                        "without changing the scientific objective or population boundary."
                    ),
                    "assimilation": "COMPLEMENTARY_FACET",
                    "discovered_domain_ids": ["meta_analysis"],
                    "representation_ids": [],
                    "contradicts_claim_ids": [],
                    "related_claim_ids": [],
                    "context_ids": [],
                    "referent_bindings": [],
                    "representation_mappings": [],
                    "assumption_ids": [],
                }
            )
        elif task == "reconstruct":
            content = json.dumps(
                {
                    "summary": (
                        "The visible evidence supports a lower-level evidence/information "
                        "responsibility; high-level objective/boundary reformulation is not supported."
                    )
                }
            )
        elif task == "diagnose":
            content = json.dumps(
                {
                    "responsibilities": ["SEARCH"],
                    "rationale": (
                        "The fixed source points to evidence/information sufficiency rather than "
                        "objective or boundary failure."
                    ),
                }
            )
        elif task == "propose_reframe":
            content = json.dumps(
                {
                    "add_domain_ids": [],
                    "add_representation_ids": [],
                    "note": "Do not escalate to a high-level reformulation.",
                }
            )
        elif task == "compose_answer":
            content = json.dumps(
                {
                    "answer": (
                        "Preserve the scientific objective and boundary; repair "
                        "evidence/information sufficiency first."
                    )
                }
            )
        else:
            raise AssertionError(f"unexpected LLM task: {task}")
        workspace.ingest_result(
            request.request_id,
            success=True,
            output={"content": content, "model_id": "p1-r6-frozen-pilot"},
            executor="p1-r6-pilot",
        )
        return
    if request.capability == "WEB_SEARCH":
        workspace.ingest_result(
            request.request_id,
            success=True,
            output={
                "items": [
                    {
                        "item_id": "doi:10.1111/biom.13238",
                        "content": SOURCE,
                        "source_uri": "https://doi.org/10.1111/biom.13238",
                        "domain_ids": ["meta_analysis"],
                    }
                ]
            },
            executor="p1-r6-frozen-corpus",
        )
        return
    if request.capability == "VERIFY_EVIDENCE":
        workspace.ingest_result(
            request.request_id,
            success=True,
            output={
                "passed": True,
                "certificate_ids": ["certificate:p1-r6:search-p1"],
                "reason": "Contribution is directly supported by the frozen source statement.",
            },
            executor="p1-r6-independent-check",
        )
        return
    raise AssertionError(f"unexpected capability: {request.capability}")


def native_revision_contract() -> dict[str, object]:
    """Exercise the exact native #723 responsibility/interface/mechanic/gate substrate.

    The discriminator outcome is derived from the frozen source statement above; no evaluator
    gold class or pair-role field is supplied to these objects.
    """

    claim_id = "p1-r6-search-p1-adverse"
    hypotheses = (
        build_responsibility_hypothesis(
            hypothesis_id="responsibility:evidence",
            claim_id=claim_id,
            expected_observations={"D_PRIMARY_FAILURE": ("EVIDENCE_INSUFFICIENT",)},
            support_evidence_ids=("doi:10.1111/biom.13238",),
        ),
        build_responsibility_hypothesis(
            hypothesis_id="responsibility:objective",
            claim_id=claim_id,
            expected_observations={"D_PRIMARY_FAILURE": ("OBJECTIVE_MISMATCH",)},
        ),
        build_responsibility_hypothesis(
            hypothesis_id="responsibility:boundary",
            claim_id=claim_id,
            expected_observations={"D_PRIMARY_FAILURE": ("BOUNDARY_MISMATCH",)},
        ),
    )
    responsibility = assess_responsibility(
        hypotheses,
        observed_outcomes={"D_PRIMARY_FAILURE": "EVIDENCE_INSUFFICIENT"},
    )
    assert responsibility.status is ResponsibilityStatus.IDENTIFIED
    assert responsibility.identified_hypothesis_id == "responsibility:evidence"
    assert responsibility.grants_revision_authority is False

    interface = assess_interface_adequacy(
        (
            build_interface_check(
                check_id="interface:frozen-source-binding",
                scope="evidence_source_binding",
                state=InterfaceCheckState.PASS,
                evidence_ids=("doi:10.1111/biom.13238",),
            ),
            build_interface_check(
                check_id="interface:verification-certificate",
                scope="evidence_verification",
                state=InterfaceCheckState.PASS,
                evidence_ids=("certificate:p1-r6:search-p1",),
            ),
        )
    )
    assert interface.status is InterfaceAdequacyStatus.ADEQUATE
    assert interface.grants_scientific_authority is False

    evidence_repair = build_mechanic(
        mechanic_id="p1:repair-evidence",
        claim_id=claim_id,
        kind="EVIDENCE_REPAIR",
        read_coordinates=("K:evidence", "W:objective", "W:boundary"),
        write_coordinates=("K:evidence",),
        preconditions=("RESPONSIBILITY_IDENTIFIED", "INTERFACE_ADEQUATE"),
        preservation_obligations=("PRESERVE_OBJECTIVE", "PRESERVE_BOUNDARY"),
        cost=1.0,
    )
    objective_revision = build_mechanic(
        mechanic_id="p1:revise-objective",
        claim_id=claim_id,
        kind="OBJECTIVE_REVISION",
        read_coordinates=("K:evidence", "W:objective", "W:boundary"),
        write_coordinates=("K:evidence", "W:objective"),
        preconditions=("RESPONSIBILITY_IDENTIFIED", "INTERFACE_ADEQUATE"),
        preservation_obligations=("PRESERVE_BOUNDARY",),
        cost=2.0,
    )
    boundary_revision = build_mechanic(
        mechanic_id="p1:revise-boundary",
        claim_id=claim_id,
        kind="BOUNDARY_REVISION",
        read_coordinates=("K:evidence", "W:objective", "W:boundary"),
        write_coordinates=("K:evidence", "W:objective", "W:boundary"),
        preconditions=("RESPONSIBILITY_IDENTIFIED", "INTERFACE_ADEQUATE"),
        preservation_obligations=(),
        cost=3.0,
    )
    mechanics = (evidence_repair, objective_revision, boundary_revision)
    obligation_states = {
        "RESPONSIBILITY_IDENTIFIED": ObligationState.SATISFIED,
        "INTERFACE_ADEQUATE": ObligationState.SATISFIED,
    }
    assessments = tuple(
        assess_mechanic(mechanic, obligation_states=obligation_states) for mechanic in mechanics
    )
    assert all(item.status is AssessmentStatus.ADMISSIBLE for item in assessments)

    gate = assess_revision_gate(
        responsibility=responsibility,
        interface=interface,
        mechanics=mechanics,
        assessments=assessments,
        responsibility_bindings={
            "responsibility:evidence": (
                "p1:repair-evidence",
                "p1:revise-objective",
                "p1:revise-boundary",
            )
        },
    )
    assert gate.status is RevisionGateStatus.CANDIDATE_SELECTED
    assert gate.selected_mechanic_id == "p1:repair-evidence"
    assert gate.grants_adoption_authority is False
    assert gate.grants_promotion_authority is False
    assert gate.grants_merge_authority is False
    return {
        "responsibility_digest": responsibility.digest,
        "interface_digest": interface.digest,
        "mechanic_digests": [item.digest for item in mechanics],
        "assessment_digests": [item.digest for item in assessments],
        "revision_gate_digest": gate.digest,
        "selected_mechanic_id": gate.selected_mechanic_id,
    }


def main() -> None:
    with tempfile.TemporaryDirectory() as td:
        root = Path(td)
        ws = ResearchWorkspace.initialize(root / "ws", project_root=root)
        problem = {
            "problem_id": "p1-r6-search-p1-adverse",
            "question": "What revision level is warranted for this scientific failure?",
            "scope": (
                DOSSIER
                + " Use only the fixed 2020 R4 source universe. Do not change the objective or "
                "boundary unless evidence requires it."
            ),
            "initial_domain_ids": ["meta_analysis"],
            "success_criteria": ["Preserve uncertainty.", "Do not escalate beyond evidence."],
        }
        for _ in range(24):
            outcome = run_problem(ws, problem, max_iterations=2, require_verified_answer=True)
            if outcome["status"] == "COMPLETE":
                break
            if outcome["status"] == "HOST_CAPABILITY_FAILED":
                raise AssertionError(outcome)
            service(ws, CapabilityRequest.from_dict(outcome["request"]))
        else:
            raise AssertionError("harness did not terminate")
        assert outcome["status"] == "COMPLETE"
        assert ws.run_ids(), "completed run was not persisted"
        ops = set(outcome["operator_sequence"])
        assert {"FRAME", "SEARCH", "ABSORB"}.issubset(ops), outcome
        native = native_revision_contract()
        print(
            "P1_R6_HARNESS_PILOT="
            + json.dumps({"harness": outcome, "native": native}, sort_keys=True)
        )


if __name__ == "__main__":
    main()
