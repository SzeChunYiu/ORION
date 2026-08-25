from __future__ import annotations

import pytest

from orion.discovery.knowledge_web import (
    AuthorityClass,
    ClaimDelta,
    ContractError,
    CostVector,
    EdgeKind,
    KnowledgeEdge,
    KnowledgeNode,
    KnowledgeWeb,
    NodeKind,
    ProofMethod,
    ProofObligation,
    ProofOption,
    SelfApplicationContract,
    SelfApplicationState,
    SupportFamily,
    TransferContract,
    TransferState,
    assess_self_application,
    assess_transfer,
    derive_change_impact,
    pareto_minimal_proof_plans,
    select_proof_plan_with_explicit_weights,
)


def node(node_id: str, kind: NodeKind) -> KnowledgeNode:
    return KnowledgeNode(node_id, kind, "test", node_id.replace("-", " "), f"sha:{node_id}")


def test_support_requires_one_complete_conjunctive_family() -> None:
    web = KnowledgeWeb(
        nodes=(
            node("question", NodeKind.QUESTION),
            node("lemma-a", NodeKind.INVARIANT),
            node("lemma-b", NodeKind.INVARIANT),
            node("experiment", NodeKind.EXPERIMENT),
            node("claim", NodeKind.CLAIM),
        ),
        edges=(
            KnowledgeEdge("a-claim", "lemma-a", "claim", EdgeKind.DERIVES, True),
            KnowledgeEdge("b-claim", "lemma-b", "claim", EdgeKind.DERIVES, True),
            KnowledgeEdge("e-claim", "experiment", "claim", EdgeKind.VALIDATES, True),
        ),
        support_families=(
            SupportFamily("formal-family", "claim", ("question", "lemma-a", "lemma-b"), ("a-claim", "b-claim")),
            SupportFamily("empirical-family", "claim", ("question", "experiment"), ("e-claim",)),
        ),
    )

    partial = web.support_status("claim", {"question", "lemma-a"})
    assert partial.supported is False
    assert partial.best_missing_count == 1

    empirical = web.support_status("claim", {"question", "experiment"})
    assert empirical.supported is True
    assert [status.complete for status in empirical.family_statuses] == [False, True]


def test_one_path_does_not_substitute_for_missing_ingredient() -> None:
    web = KnowledgeWeb(
        nodes=(node("a", NodeKind.ASSUMPTION), node("b", NodeKind.MECHANISM), node("c", NodeKind.CLAIM)),
        edges=(
            KnowledgeEdge("a-c", "a", "c", EdgeKind.DERIVES, True),
            KnowledgeEdge("b-c", "b", "c", EdgeKind.DERIVES, True),
        ),
        support_families=(SupportFamily("both", "c", ("a", "b"), ("a-c", "b-c")),),
    )
    status = web.support_status("c", {"a"})
    assert status.supported is False
    assert status.family_statuses[0].missing_node_ids == ("b",)


def test_unknown_endpoints_and_duplicate_ids_fail_closed() -> None:
    with pytest.raises(ContractError, match="duplicate knowledge node"):
        KnowledgeWeb(nodes=(node("x", NodeKind.QUESTION), node("x", NodeKind.CLAIM)), edges=())

    with pytest.raises(ContractError, match="unknown endpoint"):
        KnowledgeWeb(
            nodes=(node("x", NodeKind.QUESTION),),
            edges=(KnowledgeEdge("bad", "x", "missing", EdgeKind.DERIVES),),
        )


def test_load_bearing_ancestor_closure_finds_all_upstream_ingredients() -> None:
    web = KnowledgeWeb(
        nodes=(
            node("donor", NodeKind.DONOR),
            node("representation", NodeKind.REPRESENTATION),
            node("method", NodeKind.METHOD),
            node("proof", NodeKind.EVIDENCE),
            node("claim", NodeKind.CLAIM),
        ),
        edges=(
            KnowledgeEdge("d-r", "donor", "representation", EdgeKind.REFINES, True),
            KnowledgeEdge("r-m", "representation", "method", EdgeKind.DEPENDS_ON, True),
            KnowledgeEdge("m-p", "method", "proof", EdgeKind.DERIVES, True),
            KnowledgeEdge("p-c", "proof", "claim", EdgeKind.VALIDATES, True),
        ),
    )
    assert web.load_bearing_ancestors("claim") == (
        "claim",
        "donor",
        "method",
        "proof",
        "representation",
    )


def test_change_impact_propagates_only_over_registered_reopen_edges() -> None:
    web = KnowledgeWeb(
        nodes=(
            node("theory", NodeKind.THEORY),
            node("code", NodeKind.CODE),
            node("harness", NodeKind.HARNESS),
            node("paper", NodeKind.PAPER),
            node("authority", NodeKind.AUTHORITY),
            node("unrelated", NodeKind.PAPER),
        ),
        edges=(
            KnowledgeEdge("t-c", "theory", "code", EdgeKind.SYNCHRONIZES, reopen_on_change=True),
            KnowledgeEdge("c-h", "code", "harness", EdgeKind.SYNCHRONIZES, reopen_on_change=True),
            KnowledgeEdge("h-p", "harness", "paper", EdgeKind.SYNCHRONIZES, reopen_on_change=True),
            KnowledgeEdge("p-a", "paper", "authority", EdgeKind.SYNCHRONIZES, reopen_on_change=True),
            KnowledgeEdge("u-p", "unrelated", "paper", EdgeKind.ANALOGOUS_TO, reopen_on_change=False),
        ),
    )
    assert web.impact_closure({"theory"}) == ("authority", "code", "harness", "paper", "theory")

    no_delta = derive_change_impact(web, {"theory"})
    assert no_delta.claim_bearing_paper_update_allowed is False
    assert no_delta.required_sync_surfaces == (
        NodeKind.THEORY,
        NodeKind.CODE,
        NodeKind.HARNESS,
        NodeKind.PAPER,
        NodeKind.AUTHORITY,
    )

    earned = derive_change_impact(
        web,
        {"theory"},
        claim_delta=ClaimDelta.THEOREM_EXTENDED,
        authority_receipt_present=True,
    )
    assert earned.claim_bearing_paper_update_allowed is True


def test_scope_note_does_not_authorize_claim_bearing_paper_rewrite() -> None:
    web = KnowledgeWeb(
        nodes=(node("theory", NodeKind.THEORY), node("paper", NodeKind.PAPER)),
        edges=(KnowledgeEdge("sync", "theory", "paper", EdgeKind.SYNCHRONIZES, reopen_on_change=True),),
    )
    receipt = derive_change_impact(
        web,
        {"theory"},
        claim_delta=ClaimDelta.SCOPE_NOTE_ONLY,
        authority_receipt_present=True,
    )
    assert receipt.claim_bearing_paper_update_allowed is False


def test_proof_economy_retains_only_pareto_adequate_plans() -> None:
    dims = ("compute", "human_review", "external_access")
    obligations = (
        ProofObligation(
            "refute-universal",
            frozenset({ProofMethod.COUNTEREXAMPLE, ProofMethod.EXHAUSTIVE_ENUMERATION}),
            frozenset({AuthorityClass.LOCAL_EXACT}),
        ),
        ProofObligation(
            "novelty",
            frozenset({ProofMethod.EXTERNAL_REVIEW}),
            frozenset({AuthorityClass.EXTERNAL_NOVELTY}),
        ),
    )
    options = (
        ProofOption(
            "one-counterexample",
            ProofMethod.COUNTEREXAMPLE,
            AuthorityClass.LOCAL_EXACT,
            frozenset({"refute-universal"}),
            CostVector(dims, (1, 1, 0)),
            "one valid counterexample refutes the registered universal",
        ),
        ProofOption(
            "full-enumeration",
            ProofMethod.EXHAUSTIVE_ENUMERATION,
            AuthorityClass.LOCAL_EXACT,
            frozenset({"refute-universal"}),
            CostVector(dims, (20, 1, 0)),
            "finite registered class",
        ),
        ProofOption(
            "external-novelty-review",
            ProofMethod.EXTERNAL_REVIEW,
            AuthorityClass.EXTERNAL_NOVELTY,
            frozenset({"novelty"}),
            CostVector(dims, (0, 2, 1)),
            "atomic novelty residual",
        ),
    )
    result = pareto_minimal_proof_plans(obligations, options)
    assert len(result.adequate_plans) == 3
    assert [plan.option_ids for plan in result.pareto_plans] == [
        ("external-novelty-review", "one-counterexample")
    ]
    assert result.pareto_plans[0].cost.values == (1, 3, 1)


def test_no_universal_cheapest_plan_without_explicit_resource_preferences() -> None:
    dims = ("compute", "human")
    obligations = (
        ProofObligation(
            "prove-finite",
            frozenset({ProofMethod.EXHAUSTIVE_ENUMERATION, ProofMethod.FORMAL_PROOF}),
            frozenset({AuthorityClass.LOCAL_EXACT, AuthorityClass.SAME_PROGRAMME}),
        ),
    )
    options = (
        ProofOption(
            "enumerate",
            ProofMethod.EXHAUSTIVE_ENUMERATION,
            AuthorityClass.LOCAL_EXACT,
            frozenset({"prove-finite"}),
            CostVector(dims, (100, 1)),
            "finite class",
        ),
        ProofOption(
            "formalize",
            ProofMethod.FORMAL_PROOF,
            AuthorityClass.SAME_PROGRAMME,
            frozenset({"prove-finite"}),
            CostVector(dims, (1, 100)),
            "same-programme proof object",
        ),
    )
    result = pareto_minimal_proof_plans(obligations, options)
    assert len(result.pareto_plans) == 2
    assert select_proof_plan_with_explicit_weights(result.pareto_plans, {"compute": 1.0, "human": 0.01}).option_ids == (
        "formalize",
    )
    assert select_proof_plan_with_explicit_weights(result.pareto_plans, {"compute": 0.01, "human": 1.0}).option_ids == (
        "enumerate",
    )
    with pytest.raises(ContractError, match="cover every"):
        select_proof_plan_with_explicit_weights(result.pareto_plans, {"compute": 1.0})


def test_precondition_empty_proof_option_is_not_counted() -> None:
    dims = ("compute",)
    obligations = (
        ProofObligation(
            "hard-stratum",
            frozenset({ProofMethod.EXHAUSTIVE_ENUMERATION}),
            frozenset({AuthorityClass.LOCAL_EXACT}),
        ),
    )
    option = ProofOption(
        "needs-unsat",
        ProofMethod.EXHAUSTIVE_ENUMERATION,
        AuthorityClass.LOCAL_EXACT,
        frozenset({"hard-stratum"}),
        CostVector(dims, (10,)),
        "SAT/UNSAT family",
        frozenset({"UNSAT_PRESENT"}),
    )
    assert not pareto_minimal_proof_plans(obligations, (option,)).adequate_plans
    assert pareto_minimal_proof_plans(obligations, (option,), {"UNSAT_PRESENT"}).adequate_plans


def valid_self_contract(**overrides: object) -> SelfApplicationContract:
    data: dict[str, object] = {
        "subject_version": "ORION@abc",
        "problem_identity": "orion-self-study-v1",
        "proposer_principal": "proposal-cell",
        "evaluator_principal": "protected-evaluator",
        "adopter_principal": "external-owner",
        "proposal_origin_sealed": True,
        "old_closure_sealed": True,
        "hidden_consequence_ids": ("held-out-1",),
        "registered_alternative_ids": ("no-change", "donor-product"),
        "positive_terminal": "SELF_STUDY_SUPPORTED",
        "negative_terminal": "SELF_STUDY_REFUTED",
        "cannot_check_terminal": "SELF_STUDY_CANNOT_CHECK",
    }
    data.update(overrides)
    return SelfApplicationContract(**data)  # type: ignore[arg-type]


def test_orion_self_application_requires_separated_proposal_evaluation_and_adoption() -> None:
    assert assess_self_application(valid_self_contract()) == SelfApplicationState.VALID_FOR_FROZEN_EXECUTION
    assert assess_self_application(
        valid_self_contract(evaluator_principal="proposal-cell")
    ) == SelfApplicationState.SELF_EVALUATION_INVALID
    assert assess_self_application(
        valid_self_contract(adopter_principal="protected-evaluator")
    ) == SelfApplicationState.SELF_ADOPTION_INVALID
    assert assess_self_application(
        valid_self_contract(proposal_origin_sealed=False)
    ) == SelfApplicationState.ORIGIN_UNSEALED
    assert assess_self_application(
        valid_self_contract(old_closure_sealed=False)
    ) == SelfApplicationState.OLD_CLOSURE_UNSEALED


def test_quantum_transfer_requires_relational_correspondence_target_validation_and_no_authority_transfer() -> None:
    valid = TransferContract(
        source_domain="ORION-Q exact finite quantum structures",
        target_domain="discovery navigation",
        relational_correspondence_ids=("obstruction-to-language-edit", "pareto-resource-accounting"),
        target_validator_id="discovery-validator-v1",
        donor_first_refusal_completed=True,
        resource_contract_id="matched-vector-budget-v1",
        authority_nontransfer=True,
    )
    assert assess_transfer(valid) == TransferState.STRUCTURAL_TRANSFER_CANDIDATE
    assert assess_transfer(
        TransferContract("quantum", "biology", (), "validator", True, "budget", True)
    ) == TransferState.SURFACE_ANALOGY_ONLY
    assert assess_transfer(
        TransferContract("quantum", "biology", ("relation",), None, True, "budget", True)
    ) == TransferState.TARGET_VALIDATOR_MISSING
    assert assess_transfer(
        TransferContract("quantum", "biology", ("relation",), "validator", True, "budget", False)
    ) == TransferState.AUTHORITY_LAUNDERING_INVALID


def test_open_move_class_can_be_represented_without_forcing_a_known_morphology() -> None:
    web = KnowledgeWeb(nodes=(node("unknown-move", NodeKind.OPEN_MOVE_CLASS),), edges=())
    assert web.node("unknown-move").kind is NodeKind.OPEN_MOVE_CLASS
