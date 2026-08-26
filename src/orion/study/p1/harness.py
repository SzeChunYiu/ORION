"""Run harness for the ORION-P1 study.

Three obligations from the frozen protocol are enforced here rather than
trusted to discipline:

1. **The access boundary is the call site.** A system is handed
   ``case.public_view`` and nothing else. The ``HiddenShiftCase`` — with its
   ``protected_gold`` and its family label — never leaves this module. The type
   signature of ``SystemUnderTest`` states the rule; this is the one place that
   could break it, so this is where it is tested.

2. **Nothing is dropped.** ``exclusion_policy`` forbids excluding a
   candidate-caused failure, timeout, malformed action, abstention or wrong
   reframe. A raised exception becomes a ``CANDIDATE_FAILURE`` record with the
   error text and a null trace; a provider refusal becomes ``CANNOT_CHECK``.
   Both are archived. A run that disappears cannot be distinguished from a run
   that never happened, which is how a failure rate quietly becomes a success
   rate.

3. **Every record is bound to what produced it.** The suite fingerprint (which
   hashes the gold as well as the public fields) and the subject git revision
   are written onto every line. The protocol's ``execution_bindings`` are
   ``UNBOUND`` until exactly these values are supplied, and an unbound result is
   unverifiable.

The harness measures wall-clock time itself and records it on the archive
record, not inside ``SystemTrace``: elapsed time is a property of this run on
this machine, while the trace is the system's answer and must reproduce for a
given seed.

**Two notes carried here for whoever scores these records**, because both are
properties of the archive rather than of any one system, and a number that
lives only in a conversation is a number nobody scoring P1-4 will ever see.

1. *Reopen F1 must not be scored against full reset alone.* On the frozen suite
   a blind policy — reopen the largest closure component, no diagnosis, never
   read the prompt, random tie-break — earns expected reopen F1 **0.792**
   (PILOT) / **0.823** (TEST), against full reset's 0.722 / 0.719 and
   dependency-directed's 1.000. Survivor chains are single closures while
   reopened chains run 1-3 long, so component size carries signal. The
   mechanism-free floor is therefore ~0.82, not ~0.72: a reopen result between
   those two numbers is graph shape, not dependency-directed reasoning. The
   suite author measured this independently and pinned it as
   ``test_the_mechanism_free_reopen_floor_is_the_blind_largest_component``.

2. *Cost lives here, not on the trace.* ``trace.resources.wallclock_seconds`` is
   0.0 for every mechanical system by construction; the measured figure is
   ``RunRecord.elapsed_seconds``. A success-cost frontier built on the trace
   field will be flat at zero.
"""

from __future__ import annotations

import json
import subprocess
from collections.abc import Iterable, Sequence
from dataclasses import asdict, dataclass, field
from enum import Enum
from pathlib import Path
from time import perf_counter

from .baselines import budget_for
from .cases import HiddenShiftCase, PublicView, suite_fingerprint
from .provider import ProviderUnavailable
from .systems import SystemTrace, SystemUnderTest

PROTOCOL_PATH = (
    Path(__file__).resolve().parents[4]
    / "papers"
    / "orion-11-recursive-epistemic-reconstruction"
    / "protocol"
    / "PROTOCOL_V1.json"
)

REPO_ROOT = Path(__file__).resolve().parents[4]

UNBOUND = "UNBOUND"

# Fallback only. `stochastic_repeats_from_protocol` is the binding source.
DEFAULT_STOCHASTIC_REPEATS = 5


class RunStatus(str, Enum):
    """What happened to one (case, system, seed) cell.

    ``CANNOT_CHECK`` is not a score. It records that the apparatus could not
    produce an answer — a missing credential, an unavailable provider — and it
    must never be collapsed into a failed or zero-scoring run.
    """

    OK = "OK"
    CANDIDATE_FAILURE = "CANDIDATE_FAILURE"
    CANNOT_CHECK = "CANNOT_CHECK"


@dataclass(frozen=True)
class RunRecord:
    """One archived raw record."""

    case_id: str
    system_id: str
    seed: int
    status: RunStatus
    trace: SystemTrace | None
    elapsed_seconds: float
    suite_fingerprint: str
    subject_revision: str
    protocol_id: str
    budget_class: str
    error: str = ""
    integrity: tuple[str, ...] = ()
    # No code path sets this. The protocol permits exclusion only for a
    # symmetric, predeclared infrastructure outage applied to every system, and
    # even then the record stays archived. The field exists so an exclusion, if
    # one is ever declared, is visible in the data rather than implicit in a
    # missing line.
    excluded: bool = False
    exclusion_reason: str = ""

    def to_json(self) -> str:
        payload = {
            "case_id": self.case_id,
            "system_id": self.system_id,
            "seed": self.seed,
            "status": self.status.value,
            "trace": _trace_payload(self.trace),
            "elapsed_seconds": self.elapsed_seconds,
            "suite_fingerprint": self.suite_fingerprint,
            "subject_revision": self.subject_revision,
            "protocol_id": self.protocol_id,
            "budget_class": self.budget_class,
            "error": self.error,
            "integrity": list(self.integrity),
            "excluded": self.excluded,
            "exclusion_reason": self.exclusion_reason,
        }
        return json.dumps(payload, sort_keys=True)


@dataclass(frozen=True)
class StudyArchive:
    """Every record produced by one study run, plus its bindings."""

    records: tuple[RunRecord, ...]
    suite_fingerprint: str
    subject_revision: str
    protocol_id: str
    seeds: tuple[int, ...]
    archive_path: Path | None = None
    system_ids: tuple[str, ...] = field(default_factory=tuple)

    @property
    def failures(self) -> tuple[RunRecord, ...]:
        return tuple(
            item for item in self.records if item.status is RunStatus.CANDIDATE_FAILURE
        )

    @property
    def cannot_check(self) -> tuple[RunRecord, ...]:
        return tuple(
            item for item in self.records if item.status is RunStatus.CANNOT_CHECK
        )

    def traces(self) -> tuple[SystemTrace, ...]:
        return tuple(item.trace for item in self.records if item.trace is not None)


def _trace_payload(trace: SystemTrace | None) -> dict | None:
    if trace is None:
        return None
    payload = asdict(trace)
    payload["resources"] = asdict(trace.resources)
    return payload


def stochastic_repeats_from_protocol(path: Path = PROTOCOL_PATH) -> int:
    """Read the frozen repeat count rather than restating it."""

    try:
        payload = json.loads(path.read_text())
    except (OSError, json.JSONDecodeError):
        return DEFAULT_STOCHASTIC_REPEATS
    statistics = payload.get("statistics", {})
    return int(statistics.get("stochastic_repeats", DEFAULT_STOCHASTIC_REPEATS))


def protocol_id(path: Path = PROTOCOL_PATH) -> str:
    try:
        payload = json.loads(path.read_text())
    except (OSError, json.JSONDecodeError):
        return UNBOUND
    return str(payload.get("protocol_id", UNBOUND))


def default_seeds(path: Path = PROTOCOL_PATH) -> tuple[int, ...]:
    return tuple(range(stochastic_repeats_from_protocol(path)))


def subject_revision(root: Path = REPO_ROOT) -> str:
    """The subject commit, marked dirty when the tree is.

    Returns the protocol's own ``UNBOUND`` sentinel when the revision cannot be
    read, because writing an empty string would look like a bound value.
    """

    try:
        head = subprocess.run(
            ["git", "rev-parse", "HEAD"],
            cwd=root,
            capture_output=True,
            text=True,
            check=True,
            timeout=15,
        ).stdout.strip()
    except (OSError, subprocess.SubprocessError):
        return UNBOUND
    if not head:
        return UNBOUND
    try:
        dirty = subprocess.run(
            ["git", "status", "--porcelain"],
            cwd=root,
            capture_output=True,
            text=True,
            check=True,
            timeout=30,
        ).stdout.strip()
    except (OSError, subprocess.SubprocessError):
        return f"{head}+dirty-unknown"
    return f"{head}+dirty" if dirty else head


def _integrity_flags(
    trace: SystemTrace,
    *,
    view: PublicView,
    system_id: str,
    seed: int,
) -> tuple[str, ...]:
    """Malformed answers are flagged and kept, never discarded.

    The protocol's exclusion policy names malformed actions explicitly as
    non-excludable, so these flags annotate a record; they do not remove it.
    """

    flags: list[str] = []
    if trace.case_id != view.case_id:
        flags.append("case_id_mismatch")
    if trace.system_id != system_id:
        flags.append("system_id_mismatch")
    if trace.seed != seed:
        flags.append("seed_mismatch")
    if trace.target_coordinates and not trace.reframed:
        flags.append("target_without_reframe")
    if trace.reframed and trace.abstained:
        flags.append("reframed_while_abstaining")
    budget = budget_for(view)
    if trace.resources.tool_calls > budget.tool_calls:
        flags.append("tool_call_budget_exceeded")
    if trace.resources.search_queries > budget.search_queries:
        flags.append("search_budget_exceeded")
    if trace.resources.model_tokens > budget.model_tokens:
        flags.append("token_budget_exceeded")
    return tuple(flags)


def run_one(
    case: HiddenShiftCase,
    system: SystemUnderTest,
    *,
    seed: int,
    fingerprint: str,
    revision: str,
    protocol: str,
) -> RunRecord:
    """Execute one cell and return its record, whatever happened.

    The system receives ``case.public_view``. It is handed no case object, no
    protected gold and no family label — the access-control boundary is this
    argument, and nothing downstream can widen it.
    """

    view = case.public_view
    started = perf_counter()
    try:
        trace = system.run(view, seed=seed)
    except ProviderUnavailable as error:
        return RunRecord(
            case_id=case.case_id,
            system_id=system.system_id,
            seed=seed,
            status=RunStatus.CANNOT_CHECK,
            trace=None,
            elapsed_seconds=perf_counter() - started,
            suite_fingerprint=fingerprint,
            subject_revision=revision,
            protocol_id=protocol,
            budget_class=view.budget_class,
            error=f"{error.status.value}: {error.detail}",
        )
    except Exception as error:  # noqa: BLE001 - a candidate failure is data
        return RunRecord(
            case_id=case.case_id,
            system_id=system.system_id,
            seed=seed,
            status=RunStatus.CANDIDATE_FAILURE,
            trace=None,
            elapsed_seconds=perf_counter() - started,
            suite_fingerprint=fingerprint,
            subject_revision=revision,
            protocol_id=protocol,
            budget_class=view.budget_class,
            error=f"{type(error).__name__}: {error}",
        )
    elapsed = perf_counter() - started
    return RunRecord(
        case_id=case.case_id,
        system_id=system.system_id,
        seed=seed,
        status=RunStatus.OK,
        trace=trace,
        elapsed_seconds=elapsed,
        suite_fingerprint=fingerprint,
        subject_revision=revision,
        protocol_id=protocol,
        budget_class=view.budget_class,
        integrity=_integrity_flags(trace, view=view, system_id=system.system_id, seed=seed),
    )


def run_study(
    cases: Sequence[HiddenShiftCase],
    systems: Sequence[SystemUnderTest],
    *,
    seeds: Iterable[int] | None = None,
    archive_path: Path | None = None,
    protocol_path: Path = PROTOCOL_PATH,
    repo_root: Path = REPO_ROOT,
) -> StudyArchive:
    """Run every system on every case for every seed, and archive all of it.

    `seeds` defaults to the protocol's ``stochastic_repeats``. Records are
    emitted in a fixed (case, system, seed) order so two runs of the same study
    produce byte-identical archives apart from measured elapsed time.
    """

    frozen_cases = tuple(cases)
    frozen_systems = tuple(systems)
    seed_values = tuple(seeds) if seeds is not None else default_seeds(protocol_path)
    fingerprint = suite_fingerprint(frozen_cases)
    revision = subject_revision(repo_root)
    protocol = protocol_id(protocol_path)

    records: list[RunRecord] = []
    for case in frozen_cases:
        for system in frozen_systems:
            for seed in seed_values:
                records.append(
                    run_one(
                        case,
                        system,
                        seed=seed,
                        fingerprint=fingerprint,
                        revision=revision,
                        protocol=protocol,
                    )
                )

    if archive_path is not None:
        archive_path.parent.mkdir(parents=True, exist_ok=True)
        archive_path.write_text(
            "".join(f"{record.to_json()}\n" for record in records), encoding="utf-8"
        )

    return StudyArchive(
        records=tuple(records),
        suite_fingerprint=fingerprint,
        subject_revision=revision,
        protocol_id=protocol,
        seeds=seed_values,
        archive_path=archive_path,
        system_ids=tuple(system.system_id for system in frozen_systems),
    )


def read_archive(path: Path) -> tuple[dict, ...]:
    """Read back a JSONL archive, one dict per record."""

    return tuple(
        json.loads(line) for line in path.read_text(encoding="utf-8").splitlines() if line
    )


__all__ = [
    "DEFAULT_STOCHASTIC_REPEATS",
    "PROTOCOL_PATH",
    "REPO_ROOT",
    "UNBOUND",
    "RunRecord",
    "RunStatus",
    "StudyArchive",
    "default_seeds",
    "protocol_id",
    "read_archive",
    "run_one",
    "run_study",
    "stochastic_repeats_from_protocol",
    "subject_revision",
]
