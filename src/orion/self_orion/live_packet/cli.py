"""Section 10 -- preflight, the execution manifest and the one command.

The live provider stack is imported inside `_run_live` and nowhere else, so
importing this package builds no live stack and needs no credential.
"""

from __future__ import annotations

import argparse
import json
import os
import sys
from collections.abc import Sequence
from dataclasses import dataclass
from pathlib import Path

from orion.self_orion.live_trial import ShadowLiveTrialRunner

from .authority import BoundedSaturationState, pre_execution_saturation_state
from .constants import (
    EXIT_CANNOT_CHECK,
    EXIT_OK,
    LIVE_RUNNER,
    LIVE_STACK_CONSTRUCTOR,
    PROTOCOL_PATH,
    SUCCESS_BOUNDARY,
    UNBOUND,
    _sha256,
)
from .identity import CREDENTIAL_ENV_VARS
from .mechanic_cells import FIBRE_PROVIDER_ROLES
from .packet import FrozenLiveResearchPacket, frozen_live_research_packet, write_packet_document
from .question_surface import emit_open_questions, question_surface_summary
from .refusal import (
    blocked_mechanic_ids,
    failure_pattern_candidates,
    missing_credential_env_vars,
    refusal_episodes,
)


@dataclass(frozen=True)
class LiveTrialPreflight:
    packet_fingerprint: str
    missing_credential_env_vars: tuple[str, ...]
    blocked_mechanic_ids: tuple[str, ...]
    runnable_mechanic_ids: tuple[str, ...]
    corpus_revision: str
    open_question_count: int
    epoch_conflict: str
    saturation: BoundedSaturationState
    blockers: tuple[str, ...]

    @property
    def runnable(self) -> bool:
        return not self.blockers

    @property
    def boundary(self) -> str:
        return SUCCESS_BOUNDARY


def preflight(packet: FrozenLiveResearchPacket | None = None) -> LiveTrialPreflight:
    """Everything knowable about the trial without executing it.

    Two independent classes of blocker are reported separately on purpose. The
    credential blocker is not ours to clear; the unbound corpus revision is, and
    collapsing them into one "not ready" would hide a task the operator can
    actually do.
    """

    resolved = packet or frozen_live_research_packet()
    missing = missing_credential_env_vars()
    blocked = blocked_mechanic_ids(missing)
    env_epoch = os.environ.get("ORION_PHASE2_EVALUATION_EPOCH_ID", "")
    conflict = (
        ""
        if not env_epoch or env_epoch == resolved.evaluation_epoch_id
        else (
            f"environment evaluation epoch {env_epoch!r} differs from the frozen "
            f"epoch {resolved.evaluation_epoch_id!r}"
        )
    )
    blockers: list[str] = []
    if missing:
        blockers.append(
            "missing credential environment variables: " + ", ".join(missing)
        )
    if resolved.corpus_revision == UNBOUND:
        blockers.append(
            "deep-target corpus revision is UNBOUND; bind it with --corpus-revision"
        )
    if conflict:
        blockers.append(conflict)
    return LiveTrialPreflight(
        packet_fingerprint=resolved.fingerprint,
        missing_credential_env_vars=missing,
        blocked_mechanic_ids=blocked,
        runnable_mechanic_ids=tuple(
            sorted(set(FIBRE_PROVIDER_ROLES) - set(blocked))
        ),
        corpus_revision=resolved.corpus_revision,
        open_question_count=len(emit_open_questions()),
        epoch_conflict=conflict,
        saturation=pre_execution_saturation_state(),
        blockers=tuple(blockers),
    )


def _print_status(packet: FrozenLiveResearchPacket) -> None:
    report = preflight(packet)
    surface = question_surface_summary()
    print(f"packet          : {packet.packet_id}")
    print(f"fingerprint     : {report.packet_fingerprint}")
    print(f"outcome accessed: {packet.outcome_accessed}")
    print(f"corpus revision : {report.corpus_revision}")
    print("tasks           :")
    for task in sorted(packet.tasks, key=lambda item: item.task_id):
        print(f"  - {task.kind.value:<16} {task.task_id}")
    print(
        f"question surface: {surface['open_questions_issue_8']} open across the eight "
        f"named dimensions ({surface['open_questions_total']} open in total), "
        f"provider_required={surface['provider_required']}"
    )
    for dimension, count in sorted(surface["by_dimension"].items()):  # type: ignore[union-attr]
        print(f"  - {dimension:<20} {count}")
    print(f"saturation      : {report.saturation.outcome.value} (outcome, not failure)")
    print(f"blocked fibres  : {', '.join(report.blocked_mechanic_ids) or 'none'}")
    print(f"runnable fibres : {', '.join(report.runnable_mechanic_ids) or 'none'}")
    if report.blockers:
        print("blockers        :")
        for item in report.blockers:
            print(f"  - {item}")
    print(f"\nboundary        : {report.boundary}")


EXECUTION_MANIFEST_SCHEMA = "orion.self-orion.live-trial-execution-manifest.v1"


def execution_manifest(
    packet: FrozenLiveResearchPacket,
    *,
    report_path: Path | str,
    report_document_hash: str,
) -> dict[str, object]:
    """Bind a written trial report to the exact frozen packet that produced it.

    `FrozenLiveTrialPacket` -- the runtime object the runner consumes -- carries
    no corpus revision, so the revision preflight insisted on would otherwise
    never reach the run record. A deep-target result written against an
    unrecorded corpus is unverifiable after the fact, which is the failure the
    UNBOUND sentinel exists to prevent; the manifest is where the outer freeze
    meets the written outcome.
    """

    if not report_document_hash.strip():
        raise ValueError("an execution manifest requires the report's document hash")
    if packet.corpus_revision == UNBOUND:
        raise ValueError(
            "refusing to bind a run to an UNBOUND corpus revision; the deep-target "
            "result would not be reproducible"
        )
    body = {
        "schema": EXECUTION_MANIFEST_SCHEMA,
        "packet_id": packet.packet_id,
        "packet_fingerprint": packet.fingerprint,
        "trial_fingerprint": packet.trial.fingerprint,
        "evaluation_epoch_id": packet.evaluation_epoch_id,
        "corpus_revision": packet.corpus_revision,
        "provider_manifest_hash": packet.trial.provider_manifest_hash,
        "evaluator_artifact_hash": packet.evaluator.artifact_hash,
        "baseline_id": packet.baseline.baseline_id,
        "resource_limits": packet.limits.payload,
        "report_path": str(report_path),
        "report_document_hash": report_document_hash,
        "outcome_accessed_at_freeze": False,
        "success_boundary": SUCCESS_BOUNDARY,
    }
    return {**body, "manifest_hash": _sha256(body)}


def _run_live(packet: FrozenLiveResearchPacket) -> int:
    """Execute the frozen trial, or refuse in a typed, actionable way.

    Refusal is checked before anything is constructed. Starting a trial whose
    every live cell would record CANNOT_CHECK spends the mechanical fibres'
    run too, and a half-live archive is harder to reason about than none --
    the same reason `orion.study.p1.run_trial` refuses up front.
    """

    report = preflight(packet)
    if report.blockers:
        print("refusing to start the live trial:", file=sys.stderr)
        for item in report.blockers:
            print(f"  - {item}", file=sys.stderr)
        print(
            f"\nEvery blocked fibre ({', '.join(report.blocked_mechanic_ids) or 'none'}) "
            "would record CANNOT_CHECK rather than a score.\n"
            f"Build the stack with {LIVE_STACK_CONSTRUCTOR} once these are exported:\n"
            + "".join(f"  {name}\n" for name in CREDENTIAL_ENV_VARS)
            + f"then this command runs {LIVE_RUNNER} against packet "
            f"{report.packet_fingerprint}.",
            file=sys.stderr,
        )
        episodes = refusal_episodes(packet)
        print(
            f"recorded {len(episodes)} immutable CANNOT_CHECK episode(s); "
            f"{len(failure_pattern_candidates(episodes))} candidate failure "
            "pattern(s) available for later matching.",
            file=sys.stderr,
        )
        return EXIT_CANNOT_CHECK

    # Imported here, not at module scope. Everything above this line -- the
    # packet, the question surface, the trace model, the episodes, the frozen
    # evaluator -- resolves without the module that builds a live stack ever
    # being imported, which is what makes "runs with no provider" checkable
    # rather than asserted.
    from orion.providers.live_phase2 import build_phase2_live_provider_stack_from_env
    from orion.self_orion.baseline import SimpleLLMRetrievalBaseline
    from orion.self_orion.trial_io import write_shadow_live_trial_report

    model = os.environ.get("ORION_P5_REASONER_MODEL", "")
    if not model:
        print(
            "refusing to start: ORION_P5_REASONER_MODEL is not set, so the frozen "
            "provider identity cannot be bound to a specific model.",
            file=sys.stderr,
        )
        return EXIT_CANNOT_CHECK
    stack = build_phase2_live_provider_stack_from_env(reasoner_model=model)
    baseline = SimpleLLMRetrievalBaseline(llm=stack.llm, retrieval=stack.retrieval)
    runner = ShadowLiveTrialRunner.from_providers(
        llm=stack.llm,
        retrieval=stack.retrieval,
        verification=stack.verification,
        baseline=baseline,
        evaluator_artifact_hash=stack.evaluator_artifact_hash,
    )
    result = runner.run(packet.trial)
    out = PROTOCOL_PATH.parent.parent / "results"
    out.mkdir(parents=True, exist_ok=True)
    report_path = out / "shadow_live_trial_report.json"
    write_shadow_live_trial_report(result, report_path)
    written = json.loads(report_path.read_text(encoding="utf-8"))
    manifest = execution_manifest(
        packet,
        report_path=report_path,
        report_document_hash=str(written.get("document_hash", "")),
    )
    manifest_path = out / "shadow_live_execution_manifest.json"
    manifest_path.write_text(
        json.dumps(manifest, indent=2, sort_keys=True) + "\n", encoding="utf-8"
    )
    print(f"trial complete. report -> {report_path}")
    print(f"bound to packet {packet.fingerprint} -> {manifest_path}")
    print(f"boundary: {SUCCESS_BOUNDARY}")
    return EXIT_OK


def main(argv: Sequence[str] | None = None) -> int:
    parser = argparse.ArgumentParser(
        description=(
            "Frozen Shadow Self-ORION live research packet (issue #8). Prints the "
            "frozen packet and its mechanical question surface with no provider; "
            "--live executes the trial or refuses in a typed way."
        )
    )
    parser.add_argument(
        "--emit-protocol",
        nargs="?",
        const=str(PROTOCOL_PATH),
        default=None,
        help="write the frozen packet JSON (default: the checked-in protocol path)",
    )
    parser.add_argument(
        "--questions",
        action="store_true",
        help="print every open question across the eight named dimensions",
    )
    parser.add_argument(
        "--corpus-revision",
        default=UNBOUND,
        help="bind the deep-target corpus revision at execution time",
    )
    parser.add_argument(
        "--live",
        action="store_true",
        help="execute the frozen trial; refuses with exit 3 while any blocker stands",
    )
    args = parser.parse_args(argv)

    packet = frozen_live_research_packet(corpus_revision=args.corpus_revision)
    if args.emit_protocol is not None:
        written = write_packet_document(args.emit_protocol, packet=packet)
        print(f"wrote {written}")
        print(f"fingerprint: {packet.fingerprint}")
        return EXIT_OK
    if args.questions:
        for question in emit_open_questions():
            print(f"{question.question_id}\n    {question.question}")
        return EXIT_OK
    _print_status(packet)
    if args.live:
        return _run_live(packet)
    return EXIT_OK
