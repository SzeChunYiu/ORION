"""Independent hostile-review regressions for the strict deadline migration.

This checker is intentionally outside the immutable 120-node oracle and the
frozen 233-node combined denominator.  It closes post-publication review gaps
without changing either denominator or editing the oracle.
"""

from __future__ import annotations

import importlib.util
import sys
from concurrent.futures import ThreadPoolExecutor
from dataclasses import replace
from functools import cache
from pathlib import Path
from types import ModuleType

import pytest

import orion.kernel.process_receipt as process_receipt
from orion.kernel.process_receipt import (
    Channel,
    ChannelEof,
    DescriptorAcquired,
    EmptyReadyObserved,
    EventPhase,
    FinalizationBegin,
    ProcessStage,
    ProcessTarget,
    RetryKind,
)


@cache
def _oracle() -> ModuleType:
    root = Path(__file__).resolve().parents[4]
    path = root / "tests/unit/kernel/test_process_receipt_v3_deadline_hostile.py"
    name = "_orion_frozen_deadline_oracle_helpers"
    spec = importlib.util.spec_from_file_location(name, path)
    assert spec is not None and spec.loader is not None
    module = importlib.util.module_from_spec(spec)
    sys.modules[name] = module
    spec.loader.exec_module(module)
    return module


@pytest.mark.parametrize("kind", ("channel_eof", "empty_ready"))
def test_strict_main_result_payloads_cannot_bypass_protocol_in_finalize(
    kind: str,
) -> None:
    oracle = _oracle()
    subject = oracle._subject()
    invocation = oracle._invocation(subject)
    _binding, _child, events = oracle._status_registered_prefix(
        subject,
        invocation,
    )
    events = oracle._append(
        events,
        FinalizationBegin(),
        phase=EventPhase.FINALIZE,
    )
    payload = (
        ChannelEof(Channel.STATUS, effect_occurrence_id=oracle.HEX_C)
        if kind == "channel_eof"
        else EmptyReadyObserved(effect_occurrence_id=oracle.HEX_C)
    )
    events = oracle._append(events, payload, phase=EventPhase.FINALIZE)

    with pytest.raises(
        ValueError,
        match=r"(?i)(?:FINALIZE|MAIN|result|transaction|effect)",
    ):
        oracle._reduce_strict(subject, invocation, events)


def test_deadline_completion_construction_has_no_module_global_history() -> None:
    assert not hasattr(process_receipt, "_STRICT_ADMISSION_OBSERVED_BY_EFFECT")


def test_same_digest_admissions_retain_distinct_value_local_observations() -> None:
    oracle = _oracle()
    subject = oracle._subject()
    invocation = oracle._invocation(subject)
    binding, child, events = oracle._started(subject, invocation)
    earlier = oracle._admission(
        events,
        invocation,
        binding,
        child,
        ProcessStage.SELECTOR_CREATE,
        ProcessTarget.SELECTOR,
        oracle.START_NS + 10,
    )
    later = oracle._admission(
        events,
        invocation,
        binding,
        child,
        ProcessStage.SELECTOR_CREATE,
        ProcessTarget.SELECTOR,
        oracle.START_NS + 20,
    )

    assert earlier.effect_occurrence_id == later.effect_occurrence_id
    assert str(earlier.effect_occurrence_id) == str(later.effect_occurrence_id)
    assert earlier.effect_occurrence_id is not later.effect_occurrence_id

    earlier_events = oracle._append(events, earlier)
    earlier_events = oracle._append(
        earlier_events,
        oracle._effect_attempt(
            ProcessStage.SELECTOR_CREATE,
            ProcessTarget.SELECTOR,
            earlier,
        ),
    )
    oracle._completion(
        earlier_events,
        binding,
        child,
        earlier,
        oracle.START_NS + 15,
    )
    with pytest.raises(ValueError, match=r"(?i)(?:clock|regress|admission)"):
        oracle._completion(
            earlier_events,
            binding,
            child,
            later,
            oracle.START_NS + 15,
        )


def test_same_digest_admissions_are_thread_isolated() -> None:
    oracle = _oracle()
    subject = oracle._subject()
    invocation = oracle._invocation(subject)
    binding, child, prefix = oracle._started(subject, invocation)

    def lane(admission_ns: int) -> tuple[tuple[object, ...], object]:
        admission = oracle._admission(
            prefix,
            invocation,
            binding,
            child,
            ProcessStage.SELECTOR_CREATE,
            ProcessTarget.SELECTOR,
            admission_ns,
        )
        events = oracle._append(prefix, admission)
        events = oracle._append(
            events,
            oracle._effect_attempt(
                ProcessStage.SELECTOR_CREATE,
                ProcessTarget.SELECTOR,
                admission,
            ),
        )
        return events, admission

    earlier_events, earlier = lane(oracle.START_NS + 10)
    later_events, later = lane(oracle.START_NS + 20)
    assert earlier.effect_occurrence_id == later.effect_occurrence_id

    def complete(events: tuple[object, ...], admission: object) -> str:
        try:
            oracle._completion(
                events,
                binding,
                child,
                admission,
                oracle.START_NS + 15,
            )
        except ValueError:
            return "REJECTED"
        return "ACCEPTED"

    with ThreadPoolExecutor(max_workers=2) as executor:
        futures = (
            executor.submit(complete, earlier_events, earlier),
            executor.submit(complete, later_events, later),
        )
        assert tuple(future.result() for future in futures) == (
            "ACCEPTED",
            "REJECTED",
        )


def test_value_local_effect_id_preserves_plain_string_event_identity() -> None:
    oracle = _oracle()
    subject = oracle._subject()
    invocation = oracle._invocation(subject)
    binding, child, events = oracle._started(subject, invocation)
    admission = oracle._admission(
        events,
        invocation,
        binding,
        child,
        ProcessStage.SELECTOR_CREATE,
        ProcessTarget.SELECTOR,
        oracle.START_NS + 10,
    )
    plain_admission = replace(
        admission,
        effect_occurrence_id=str(admission.effect_occurrence_id),
    )
    assert type(plain_admission.effect_occurrence_id) is str
    assert plain_admission.deadline_admission_hash == admission.deadline_admission_hash

    token_event = oracle._append(events, admission)[-1]
    plain_event = oracle._append(events, plain_admission)[-1]
    assert token_event.event_hash == plain_event.event_hash


def test_plain_string_replay_defers_clock_chronology_to_reducer() -> None:
    oracle = _oracle()
    subject = oracle._subject()
    invocation = oracle._invocation(subject)
    binding, child, events = oracle._started(subject, invocation)
    admission = oracle._admission(
        events,
        invocation,
        binding,
        child,
        ProcessStage.SELECTOR_CREATE,
        ProcessTarget.SELECTOR,
        oracle.START_NS + 20,
    )
    plain_admission = replace(
        admission,
        effect_occurrence_id=str(admission.effect_occurrence_id),
    )
    events = oracle._append(events, plain_admission)
    events = oracle._append(
        events,
        oracle._effect_attempt(
            ProcessStage.SELECTOR_CREATE,
            ProcessTarget.SELECTOR,
            plain_admission,
        ),
    )
    completion = oracle._completion(
        events,
        binding,
        child,
        plain_admission,
        oracle.START_NS + 19,
    )
    events = oracle._append(events, completion)

    with pytest.raises(ValueError, match=r"(?i)(?:clock|regress|chronology)"):
        oracle._reduce_strict(subject, invocation, events)


def test_retry_observation_must_immediately_follow_its_completed_effect() -> None:
    oracle = _oracle()
    subject = oracle._subject()
    invocation = oracle._invocation(subject)
    binding, child, events = oracle._started(subject, invocation)
    events, _create, _create_completion = oracle._append_effect(
        events,
        invocation,
        binding,
        child,
        ProcessStage.SELECTOR_CREATE,
        ProcessTarget.SELECTOR,
        admission_ns=oracle.START_NS + 1,
        completion_ns=oracle.START_NS + 1,
    )
    events, select_admission, _select_completion = oracle._append_effect(
        events,
        invocation,
        binding,
        child,
        ProcessStage.SELECT,
        ProcessTarget.SELECTOR,
        admission_ns=oracle.START_NS + 2,
        completion_ns=oracle.START_NS + 3,
        result="EMPTY_READY",
    )
    events = oracle._append(events, DescriptorAcquired(Channel.STATUS))
    events = oracle._append(
        events,
        oracle._retry_with_deadline(
            ProcessStage.SELECT,
            ProcessTarget.SELECTOR,
            RetryKind.EMPTY_READY,
            1,
            select_admission.effect_occurrence_id,
        ),
    )

    with pytest.raises(
        ValueError,
        match=r"(?i)(?:retry|immediate|intervening|completed effect)",
    ):
        oracle._reduce_strict(subject, invocation, events)
