
from orion.kernel.migration import (
    MigrationStatus,
    build_legacy_migration_plan,
    inspect_migration_status,
    write_archive_copy,
)
from orion.kernel.store import EntryKind, LedgerStore


def test_empty_ledger_needs_no_migration(tmp_path):
    store = LedgerStore(tmp_path)
    assert inspect_migration_status(store) is MigrationStatus.EMPTY
    plan = build_legacy_migration_plan(store)
    assert plan.status is MigrationStatus.EMPTY
    assert not plan.prior_authority_discarded
    assert not plan.grants_authority


def test_legacy_answer_grading_round_rows_require_migration_and_never_preserve_authority(tmp_path):
    store = LedgerStore(tmp_path)
    answer = store.append(EntryKind.ANSWER, {"record_id": "legacy-r1", "authority": "VERIFIED"})
    store.append(EntryKind.GRADING, {"record_id": "legacy-r1", "authority": "VERIFIED"})
    store.append(EntryKind.ROUND, {"round": 1, "verified": True})
    assert inspect_migration_status(store) is MigrationStatus.MIGRATION_REQUIRED
    plan = build_legacy_migration_plan(store)
    assert plan.prior_authority_discarded
    assert len(plan.proposal_imports) == 1
    imported = plan.proposal_imports[0]
    assert imported.source_entry_hash == answer.entry_hash
    assert imported.source_payload["record_id"] == "legacy-r1"
    assert not imported.grants_authority
    assert "legacy_grading_or_verified_labels_are_not_authority" in plan.reasons


def test_migration_plan_is_deterministic_and_binds_original_chain(tmp_path):
    store = LedgerStore(tmp_path)
    store.append(EntryKind.ANSWER, {"record_id": "legacy-r1"})
    first = build_legacy_migration_plan(store)
    second = build_legacy_migration_plan(store)
    assert first.plan_id == second.plan_id
    assert first.archive_sha256 == second.archive_sha256
    store.append(EntryKind.RESIDUAL, {"residual": "new"})
    changed = build_legacy_migration_plan(store)
    assert changed.plan_id != first.plan_id
    assert changed.archive_sha256 != first.archive_sha256


def test_archive_copy_is_exact_and_source_is_not_modified(tmp_path):
    store = LedgerStore(tmp_path / "run")
    store.append(EntryKind.ANSWER, {"record_id": "legacy-r1"})
    before = store.path.read_bytes()
    destination = tmp_path / "archive" / "legacy.jsonl"
    digest = write_archive_copy(store, destination)
    assert destination.read_bytes() == before
    assert store.path.read_bytes() == before
    assert digest == build_legacy_migration_plan(store).archive_sha256


def test_protected_store_status_is_not_legacy_migration_required(tmp_path):
    # Transition-store behavior is covered by transaction tests. Here we only
    # ensure the status function does not infer protection from an ANSWER label.
    store = LedgerStore(tmp_path)
    store.append(EntryKind.ANSWER, {"kind": "TRANSITION", "authority": "VERIFIED"})
    assert inspect_migration_status(store) is MigrationStatus.MIGRATION_REQUIRED
