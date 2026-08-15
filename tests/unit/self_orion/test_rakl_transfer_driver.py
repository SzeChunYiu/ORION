from orion.self_orion.development_driver import SelfDrivingStage, SelfOrionDevelopmentDriver
from orion.self_orion.rakl_transfer import RAKL_SOURCE_COMMIT


def test_rakl_transfer_answers_the_current_structural_frontier_without_claiming_empirical_closure():
    report = SelfOrionDevelopmentDriver().drive_local_transfer()
    assert report.before.mechanic_count == 59
    assert report.before.open_question_count == 472
    assert report.after.mechanic_count == 59
    assert report.after.open_question_count == 0
    assert report.after.ready_mechanic_count == 59
    assert report.structurally_closed_questions == 472
    assert report.transferred_mechanics == 59
    assert report.direct_rakl_mechanics == 49
    assert report.composed_orion_mechanics == 10
    assert report.stage is SelfDrivingStage.LIVE_EVIDENCE_REQUIRED
    assert report.can_drive_next_work_mechanically
    assert not report.can_self_promote
    assert report.empirical_work_items


def test_every_transfer_receipt_is_content_scoped_to_the_frozen_rakl_source_or_orion_composition():
    report = SelfOrionDevelopmentDriver().drive_local_transfer()
    assert len(report.transfer_receipts) == 59
    for receipt in report.transfer_receipts:
        assert receipt.source_commit == RAKL_SOURCE_COMMIT
        assert len(receipt.dimensions_closed) == 8
        assert "specification transfer only" in receipt.boundary
        assert receipt.source_paths


def test_empirical_frontier_remains_ranked_after_structural_transfer():
    driver = SelfOrionDevelopmentDriver()
    items = driver.plan_empirical_work(limit=25)
    assert len(items) == 25
    assert tuple(item.priority for item in items) == tuple(sorted((item.priority for item in items), reverse=True))
    assert all(item.coordinate for item in items)
