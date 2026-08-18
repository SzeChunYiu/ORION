from __future__ import annotations

import json
import os
import stat
import subprocess
import sys
from collections.abc import Callable
from pathlib import Path
from typing import Any

import pytest

import orion.kernel.store as store_module
from orion.kernel.store import EntryKind, LedgerStore


_WRITER_SOURCE = """
import json, os, sys, time
from pathlib import Path

from orion.kernel.store import EntryKind, LedgerStore

root = Path(sys.argv[1])
ready_dir = Path(sys.argv[2])
count = int(sys.argv[3])
writer_id = int(sys.argv[4])
expected_head = json.loads(sys.argv[5])

store = LedgerStore(root)

# File barrier. Every writer announces itself, then spins until all of them
# have, so the appends collide instead of queueing behind process startup.
(ready_dir / str(writer_id)).write_text("ready", encoding="utf-8")
deadline = time.monotonic() + 30.0
while len(list(ready_dir.iterdir())) < count:
    if time.monotonic() > deadline:
        print(json.dumps(["error", writer_id, "BarrierTimeout", "peers never arrived"]))
        raise SystemExit(0)
    time.sleep(0.002)

try:
    if expected_head == "__UNCONDITIONAL__":
        entry = store.append(EntryKind.ANSWER, {"writer_id": writer_id})
    else:
        entry = store.append(
            EntryKind.ANSWER, {"writer_id": writer_id}, expected_head=expected_head
        )
except BaseException as error:  # process boundary: return structured evidence
    print(json.dumps(["error", writer_id, type(error).__name__, str(error)]))
else:
    print(json.dumps(["ok", writer_id, entry.sequence, entry.entry_hash]))
"""


def _run_writers(
    root: Path,
    count: int,
    *,
    expected_head: str | None | object = "__UNCONDITIONAL__",
) -> list[tuple[Any, ...]]:
    """Run `count` genuinely independent processes that append at the same moment.

    Deliberately subprocess rather than `multiprocessing`. The spawn start
    method pickles the worker by qualified module name, and this suite runs
    under `--import-mode=importlib`, which does not put the repository root on
    `sys.path` -- so every child died with `No module named 'tests'` before
    reaching the barrier, the parent saw a non-zero exitcode, and the failure
    read as a broken ledger rather than a test-harness import problem. A child
    that imports only the installed `orion` package cannot fail that way, and
    separate interpreters are a stronger contention test than forked ones.
    """

    ready_dir = root.parent / f"ready-{root.name}"
    ready_dir.mkdir(parents=True, exist_ok=True)
    for stale in ready_dir.iterdir():
        stale.unlink()
    processes = [
        subprocess.Popen(
            [
                sys.executable,
                "-c",
                _WRITER_SOURCE,
                str(root),
                str(ready_dir),
                str(count),
                str(writer_id),
                json.dumps(expected_head),
            ],
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            text=True,
        )
        for writer_id in range(count)
    ]
    try:
        outputs: list[tuple[str, str, int]] = []
        for process in processes:
            stdout, stderr = process.communicate(timeout=60)
            outputs.append((stdout, stderr, process.returncode))
        results = []
        for stdout, stderr, returncode in outputs:
            if returncode != 0:
                pytest.fail(f"writer exited {returncode}: {stderr.strip()}")
            line = stdout.strip().splitlines()[-1] if stdout.strip() else ""
            if not line:
                pytest.fail(f"writer exited without returning an append result: {stderr.strip()}")
            results.append(tuple(json.loads(line)))
        return results
    finally:
        for process in processes:
            if process.poll() is None:
                process.kill()
                process.wait(timeout=5)


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
