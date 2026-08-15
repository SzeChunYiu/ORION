from __future__ import annotations

import multiprocessing
import os
import stat
from collections.abc import Callable
from pathlib import Path
from queue import Empty
from typing import Any

import pytest

import orion.kernel.store as store_module
from orion.kernel.store import EntryKind, LedgerStore


def _append_after_barrier(
    root: str,
    barrier: Any,
    result_queue: Any,
    writer_id: int,
    expected_head: str | None | object,
) -> None:
    """Run one real append in a spawned process after all writers are ready."""

    store = LedgerStore(Path(root))
    barrier.wait(timeout=20)
    try:
        if expected_head == "__UNCONDITIONAL__":
            entry = store.append(EntryKind.ANSWER, {"writer_id": writer_id})
        else:
            entry = store.append(
                EntryKind.ANSWER,
                {"writer_id": writer_id},
                expected_head=expected_head,
            )
    except BaseException as error:  # process boundary: return structured evidence
        result_queue.put(("error", writer_id, type(error).__name__, str(error)))
    else:
        result_queue.put(("ok", writer_id, entry.sequence, entry.entry_hash))


def _run_writers(
    root: Path,
    count: int,
    *,
    expected_head: str | None | object = "__UNCONDITIONAL__",
) -> list[tuple[Any, ...]]:
    context = multiprocessing.get_context("spawn")
    barrier = context.Barrier(count)
    result_queue = context.Queue()
    processes = [
        context.Process(
            target=_append_after_barrier,
            args=(str(root), barrier, result_queue, writer_id, expected_head),
        )
        for writer_id in range(count)
    ]
    for process in processes:
        process.start()
    try:
        for process in processes:
            process.join(timeout=30)
        assert all(not process.is_alive() for process in processes)
        assert all(process.exitcode == 0 for process in processes)
        results = []
        for _ in processes:
            try:
                results.append(result_queue.get(timeout=5))
            except Empty:
                pytest.fail("writer exited without returning an append result")
        return results
    finally:
        for process in processes:
            if process.is_alive():
                process.terminate()
                process.join(timeout=5)
        result_queue.close()
        result_queue.join_thread()


def test_sixteen_barrier_released_writers_form_one_valid_chain(tmp_path: Path) -> None:
    root = tmp_path / "state"

    results = _run_writers(root, 16)

    assert [result for result in results if result[0] == "error"] == []
    store = LedgerStore(root)
    entries = store.entries()
    assert store.verify() == ()
    assert len(entries) == 16
    assert {entry.sequence for entry in entries} == set(range(16))
    assert {entry.payload["writer_id"] for entry in entries} == set(range(16))


def test_same_expected_head_is_compare_and_swap(tmp_path: Path) -> None:
    root = tmp_path / "state"
    store = LedgerStore(root)
    expected_head = store.append(EntryKind.ROUND, {"round_index": 0}).entry_hash

    results = _run_writers(root, 2, expected_head=expected_head)

    successes = [result for result in results if result[0] == "ok"]
    failures = [result for result in results if result[0] == "error"]
    assert len(successes) == 1
    assert len(failures) == 1
    assert failures[0][2] == "StaleLedgerHead"
    assert store.verify() == ()
    assert len(store.entries()) == 2


def test_none_expected_head_means_genesis_not_no_precondition(tmp_path: Path) -> None:
    store = LedgerStore(tmp_path / "state")
    store.append(EntryKind.ROUND, {"round_index": 0}, expected_head=None)

    with pytest.raises(store_module.StaleLedgerHead):
        store.append(EntryKind.ROUND, {"round_index": 1}, expected_head=None)

    assert store.verify() == ()
    assert len(store.entries()) == 1


def test_replace_failure_preserves_old_valid_ledger(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    store = LedgerStore(tmp_path / "state")
    original = store.append(EntryKind.ROUND, {"round_index": 0})
    old_bytes = store.path.read_bytes()

    def fail_replace(source: str | os.PathLike[str], target: str | os.PathLike[str]) -> None:
        raise OSError("injected failure before replace")

    monkeypatch.setattr(os, "replace", fail_replace)

    with pytest.raises(OSError, match="injected failure before replace"):
        store.append(EntryKind.ROUND, {"round_index": 1})

    assert store.path.read_bytes() == old_bytes
    assert store.entries() == (original,)
    assert store.verify() == ()
    assert tuple(store.root.glob(".ledger.jsonl.*.tmp")) == ()


def test_successful_transaction_replaces_from_same_directory(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    store = LedgerStore(tmp_path / "state")
    real_replace: Callable[[Any, Any], None] = os.replace
    replacements: list[tuple[Path, Path]] = []

    def record_replace(source: str | os.PathLike[str], target: str | os.PathLike[str]) -> None:
        replacements.append((Path(source), Path(target)))
        real_replace(source, target)

    monkeypatch.setattr(os, "replace", record_replace)

    appended = store.append(EntryKind.ROUND, {"round_index": 0})

    assert len(replacements) == 1
    source, target = replacements[0]
    assert source.parent == store.root
    assert target == store.path
    assert store.entries() == (appended,)
    assert store.verify() == ()


def test_transaction_fsyncs_file_before_replace_and_directory_afterward(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    store = LedgerStore(tmp_path / "state")
    real_fsync = os.fsync
    real_replace = os.replace
    events: list[str] = []

    def record_fsync(descriptor: int) -> None:
        mode = os.fstat(descriptor).st_mode
        if stat.S_ISREG(mode):
            events.append("fsync:file")
        elif stat.S_ISDIR(mode):
            events.append("fsync:directory")
        else:
            events.append("fsync:other")
        real_fsync(descriptor)

    def record_replace(source: str | os.PathLike[str], target: str | os.PathLike[str]) -> None:
        events.append("replace")
        real_replace(source, target)

    monkeypatch.setattr(os, "fsync", record_fsync)
    monkeypatch.setattr(os, "replace", record_replace)

    store.append(EntryKind.ROUND, {"round_index": 0})

    assert events == ["fsync:file", "replace", "fsync:directory"]
    assert store.verify() == ()


def test_stale_same_directory_temporary_file_is_cleaned_under_next_append(
    tmp_path: Path,
) -> None:
    store = LedgerStore(tmp_path / "state")
    abandoned = store.root / ".ledger.jsonl.abandoned.tmp"
    abandoned.write_text("partial transaction", encoding="utf-8")

    store.append(EntryKind.ROUND, {"round_index": 0})

    assert not abandoned.exists()
    assert store.verify() == ()
