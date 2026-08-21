from __future__ import annotations

import importlib.util
import sys
from pathlib import Path

from orion.core.solution import SolutionStatus

_IMPL_PATH = Path(__file__).with_name("native_orion_core_v1.py")
_SPEC = importlib.util.spec_from_file_location("p1_u_r6_native_core_v1", _IMPL_PATH)
if _SPEC is None or _SPEC.loader is None:
    raise RuntimeError("cannot load frozen P1-R6 native core")
_CORE = importlib.util.module_from_spec(_SPEC)
sys.modules[_SPEC.name] = _CORE
try:
    _SPEC.loader.exec_module(_CORE)
except Exception:
    sys.modules.pop(_SPEC.name, None)
    raise

# Re-export the frozen pre-outcome implementation, then replace only the child
# discriminator acquisition adapter.  The scientific policy, probe ordering,
# budget, responsibility logic, revision gates, comparator and thresholds remain
# byte-identical in native_orion_core_v1.py.
for _name, _value in vars(_CORE).items():
    if not _name.startswith("__"):
        globals()[_name] = _value


def _execute_probe_with_verified_evidence(self, probe_id: str):
    if probe_id not in self._hidden:
        raise KeyError(probe_id)
    if probe_id in self.accessed:
        raise RuntimeError("native discriminator cannot be acquired twice")
    if len(self.accessed) >= _CORE.BUDGET:
        raise RuntimeError("native discriminator budget exceeded")

    observation = str(self._hidden[probe_id])
    if observation not in set(_CORE.PROTOCOL["probe_observations"]):
        raise ValueError("invalid hidden probe observation")
    self.accessed.append(probe_id)

    query_text = f"p1-r6-native-probe:{self.episode_id}:{probe_id}"
    item_id = f"evidence:p1-r6:{self.episode_id}:{probe_id}"
    item = _CORE.RetrievedItem(
        item_id=item_id,
        content=(
            f"P1_NATIVE_DISCRIMINATOR={probe_id}; OBSERVATION={observation}; "
            f"SOURCE_GROUNDED_NOTE={self._evidence_note}"
        ),
        source_uri=f"p1-r6://{self.episode_id}/{probe_id}",
        domain_ids=("p1-r6-protected-discriminator",),
    )
    host = _CORE.FrozenNativeProviderHost(mode="probe", probe_query_text=query_text)
    cfg = _CORE.PROTOCOL["probe_runtime"]
    runtime = _CORE._runtime(
        provider_host=host,
        retrieval=_CORE.InMemoryRetrievalProvider({query_text: (item,)}),
        verification=_CORE.InMemoryVerificationProvider(frozenset({item_id})),
        max_iterations=int(cfg["max_iterations"]),
    )
    result = runtime.solve(
        _CORE.Problem(
            problem_id=f"p1-r6-probe:{self.episode_id}:{probe_id}",
            question=f"Acquire and verify the selected discriminator {probe_id}.",
            scope="Protected P1 discriminator acquisition. No evaluator gold is available.",
            initial_domain_ids=("p1-r6-protected-discriminator",),
            success_criteria=("Return only verified selected-discriminator evidence.",),
        ),
        evaluation_epoch_id=str(cfg["evaluation_epoch_id"]),
        split_id=str(cfg["split_id"]),
    )
    _CORE._require_operator_ids(result, tuple(cfg["required_operator_ids"]))

    # A one-iteration child acquisition is intentionally not allowed to claim
    # global bounded saturation.  On the canonical solver it therefore ends
    # CANNOT_CHECK at the solve level.  The ARD controller consumes only the
    # independently verified evidence record, whose authority must be bound both
    # in the final knowledge state and in the ABSORB receipt provenance.
    if result.solution.status not in {
        SolutionStatus.CANNOT_CHECK,
        SolutionStatus.SOLVED_VERIFIED,
    }:
        raise AssertionError(
            f"native probe runtime ended in inadmissible status: {result.solution.status.value}"
        )
    if (
        result.solution.status is SolutionStatus.CANNOT_CHECK
        and not str(result.solution.answer).startswith(
            "Resource bound reached before bounded saturation."
        )
    ):
        raise AssertionError("native probe CANNOT_CHECK was not the expected bounded-saturation stop")

    verified_claim = next(
        (
            claim
            for claim in result.final_state.knowledge.claims
            if item_id in claim.evidence_ids and claim.authority.value == "VERIFIED"
        ),
        None,
    )
    if verified_claim is None:
        raise AssertionError("native probe item is not bound to a VERIFIED claim")
    expected_certificate = f"verify:{item_id}:{verified_claim.claim_id}"
    if expected_certificate not in set(verified_claim.certificate_ids):
        raise AssertionError("native probe verified claim lacks the protected verifier certificate")
    absorb_receipts = tuple(
        event.receipt
        for event in result.trace.events
        if event.receipt.mechanic_id == "ABSORB.v1"
        and item_id in event.receipt.evidence_ids
    )
    if not absorb_receipts or not any(
        expected_certificate in set(receipt.provenance_ids)
        for receipt in absorb_receipts
    ):
        raise AssertionError("native probe ABSORB trace does not bind verifier provenance")

    record = next(
        (
            record
            for record in result.final_state.knowledge.evidence
            if record.evidence_id == item_id
        ),
        None,
    )
    if record is None:
        raise AssertionError("native probe evidence missing from returned runtime state")
    match = _CORE.re.search(r"OBSERVATION=(SUPPORT|REFUTE|INCONCLUSIVE)", record.content)
    if match is None:
        raise AssertionError("native probe runtime evidence lacks encoded observation")
    execution = _CORE.NativeProbeExecution(
        probe_id=probe_id,
        observation=match.group(1),
        trace_id=result.trace.trace_id,
        operator_ids=_CORE._trace_operator_ids(result),
        receipt_ids=_CORE._trace_receipt_ids(result),
        evidence_id=item_id,
    )
    self.executions.append(execution)
    return execution


_CORE.NativeProbeHost.execute_probe = _execute_probe_with_verified_evidence
NativeProbeHost = _CORE.NativeProbeHost

# The frozen functions resolve NativeProbeHost in the core module at call time,
# so the adapter above is used by run_native_ard without altering any decision
# rule or scientific gate.
run_native_ard = _CORE.run_native_ard
run_native_base = _CORE.run_native_base
run_root_runtime = _CORE.run_root_runtime

__all__ = [
    "CONTROL",
    "NATIVE_TO_P1",
    "NativeProbeHost",
    "PROTOCOL",
    "UNRESOLVED",
    "run_native_ard",
    "run_native_base",
    "run_root_runtime",
]
