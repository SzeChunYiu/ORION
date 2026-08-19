import runpy
from pathlib import Path

from orion.knowledge.mechanism_assimilation import AssimilationVerdict
from orion.knowledge.nearest_work import AbsorptionDisposition


def _run_experiment():
    path = Path("research/assimilation-programme-v1/PROGRAMME_ASSIMILATION_EXPERIMENT_V1.py")
    namespace = runpy.run_path(str(path))
    return namespace["run_programme_assimilation_experiment"]()


def test_programme_experiment_executes_clean_adopt_adapt_compose() -> None:
    result = _run_experiment()
    assert result.dispositions == frozenset(
        {
            AbsorptionDisposition.ADOPT,
            AbsorptionDisposition.ADAPT,
            AbsorptionDisposition.COMPOSE,
        }
    )
    assert result.all_admitted is True
    assert result.grants_authority is False


def test_every_programme_receipt_is_full_text_structurally_bound_and_content_addressed() -> None:
    result = _run_experiment()
    for receipt in result.receipts:
        assert receipt.verdict is AssimilationVerdict.ADMITTED
        assert receipt.material_structural_donor is True
        assert receipt.structural_receipt_id.startswith("ssa:v1:")
        assert receipt.donor.access.value == "FULL_TEXT"
        assert receipt.content_hash
        assert receipt.self_authorizing is False
        assert receipt.grants_authority == "NONE"


def test_composition_has_real_evidence_and_does_not_launder_components() -> None:
    result = _run_experiment()
    compose = next(r for r in result.receipts if r.disposition is AbsorptionDisposition.COMPOSE)
    assert compose.claim.composed_with
    assert compose.claim.composition_evidence
    assert "programme hypothesis/input" in " ".join(compose.not_taken)
    assert not compose.hostile_findings
