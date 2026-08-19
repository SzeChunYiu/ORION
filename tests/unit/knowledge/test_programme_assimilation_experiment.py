import importlib.util
from pathlib import Path

from orion.knowledge.mechanism_assimilation import AssimilationVerdict
from orion.knowledge.nearest_work import AbsorptionDisposition


def _module():
    path = Path("research/assimilation-programme-v1/PROGRAMME_ASSIMILATION_EXPERIMENT_V1.py")
    spec = importlib.util.spec_from_file_location("programme_assimilation_v1", path)
    assert spec is not None and spec.loader is not None
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


def test_programme_experiment_executes_clean_adopt_adapt_compose() -> None:
    result = _module().run_programme_assimilation_experiment()
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
    result = _module().run_programme_assimilation_experiment()
    for receipt in result.receipts:
        assert receipt.verdict is AssimilationVerdict.ADMITTED
        assert receipt.material_structural_donor is True
        assert receipt.structural_receipt_id.startswith("ssa:v1:")
        assert receipt.donor.access.value == "FULL_TEXT"
        assert receipt.content_hash
        assert receipt.self_authorizing is False
        assert receipt.grants_authority == "NONE"


def test_composition_has_real_evidence_and_does_not_launder_components() -> None:
    result = _module().run_programme_assimilation_experiment()
    compose = next(r for r in result.receipts if r.disposition is AbsorptionDisposition.COMPOSE)
    assert compose.claim.composed_with
    assert compose.claim.composition_evidence
    assert "programme hypothesis/input" in " ".join(compose.not_taken)
    assert not compose.hostile_findings
