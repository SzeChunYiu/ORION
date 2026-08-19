from __future__ import annotations

import inspect

from orion.discovery import zero_error_jump_benchmark_v2
from orion.discovery import zero_error_jump_independent_v2


def test_v2_independent_verifier_does_not_import_or_call_main_scorers() -> None:
    source = inspect.getsource(zero_error_jump_independent_v2)

    assert "score_split" not in source
    assert "build_zero_error_jump_benchmark_report" not in source
    assert "_score_proposal" not in source


def test_candidate_evidence_policy_core_does_not_read_protected_case_state() -> None:
    source = inspect.getsource(zero_error_jump_benchmark_v2._evidence_based_proposal)

    assert "is_jump_case" not in source
    assert "family_id" not in source
    assert "gold_representation_move" not in source
    assert "protected_full_contract_signature" not in source
    assert "protected_novel_consequence_token" not in source
    assert "gold_old_solution_id" not in source


def test_public_probe_selector_accepts_only_public_case_and_opaque_relevance() -> None:
    signature = inspect.signature(zero_error_jump_benchmark_v2.select_registered_probe)
    assert tuple(signature.parameters) == ("public",)

    source = inspect.getsource(zero_error_jump_benchmark_v2.select_registered_probe)
    assert "open_discriminator_ids" in source
    assert "covered_discriminator_ids" in source
    assert "family_id" not in source
    assert "is_jump_case" not in source
    assert "gold_" not in source
