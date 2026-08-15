from orion.self_orion.development_driver import SelfOrionDevelopmentDriver
from orion.self_orion.development_fibre import compile_development_fibre, rank_development_fibres


def test_transferred_development_fibre_has_no_structural_questions_but_retains_empirical_work():
    cells = SelfOrionDevelopmentDriver().local_transfer_cells()
    fibre = compile_development_fibre("SEARCH.QUERY.v0", cells)
    assert fibre.open_questions == ()
    assert fibre.transfer_receipt is not None
    assert fibre.empirical_work
    assert "empirical_frontier_open" in fibre.unresolved_warnings
    assert len(fibre.snapshot_hash) == 64


def test_development_fibre_ranker_prioritizes_high_priority_empirical_work():
    cells = SelfOrionDevelopmentDriver().local_transfer_cells()
    fibres = rank_development_fibres(cells, limit=10)
    assert len(fibres) == 10
    priorities = [max((item.priority for item in fibre.empirical_work), default=0) for fibre in fibres]
    assert priorities == sorted(priorities, reverse=True)
