"""Publication tables for the ORION-P1 hidden-formulation study (issue #98, step 7).

Emits the two frozen result tables named in `PROTOCOL_V1.json`:

* ``P1-T2_baseline_ablation_results`` - system x family, the rate with its
  Wilson 95% interval, and the paired difference against the strongest matched
  baseline with a bootstrap interval, effect size and hypothesis verdict;
* ``P1-T3_failure_taxonomy`` - failure modes by frequency with representative
  **blinded** case ids.

(``P1-T1_nearest_work_matrix`` is the nearest-work matrix and is not built here.)

Two hard rules shape this module:

**Archived records only.** Every number comes from raw records on disk written
by the study run. Nothing here imports a case, reads protected gold, or executes
a system. If the archive is absent, empty or incoherent the tables are emitted
with ``status: CANNOT_CHECK`` and no numbers, and the process exits
``EXIT_CANNOT_CHECK`` (3) — a code distinct from both success and error, because
"could not check" is not "checked and fine".

**No figures.** JSON and markdown only. There is no plotting code in this
package and none should be added: the numbers are the artifact.
"""

from __future__ import annotations

import argparse
import json
import math
import sys
import tempfile
from collections.abc import Callable, Iterable, Sequence
from dataclasses import dataclass
from datetime import UTC, datetime
from pathlib import Path

from . import statistics as stats
from .cases import TaskFamily
from .metrics import (
    CaseScore,
    ScoreStatus,
    SystemAggregate,
    SystemRole,
    aggregate,
    blinded_case_id,
    case_score_from_record,
    matched_units,
)

EXIT_OK = 0
EXIT_ERROR = 2
EXIT_CANNOT_CHECK = 3

TABLE_T2 = "P1-T2_baseline_ablation_results"
TABLE_T3 = "P1-T3_failure_taxonomy"

DEFAULT_ARCHIVE = Path("papers/paper-01-recursive-epistemic-reconstruction/results/raw")
DEFAULT_OUTPUT = Path("papers/paper-01-recursive-epistemic-reconstruction/results")
DEFAULT_BOOTSTRAP_SEED = 20260815
DEFAULT_REPRESENTATIVES = 3
DEFAULT_DESIGN_MANIFEST = Path(
    "papers/paper-01-recursive-epistemic-reconstruction/protocol/P1_TEST_ARCHIVE_DESIGN_V1.json"
)

SCOPE_ALL = "ALL"
SCOPE_HIDDEN_SHIFT = "HIDDEN_SHIFT_SUBSET"
SCOPE_CONTROLS = "NEGATIVE_CONTROLS"

CONTROL_SCOPES = frozenset(
    {
        SCOPE_CONTROLS,
        TaskFamily.EVIDENCE_ONLY_CONTROL.value,
        TaskFamily.EXECUTION_ONLY_CONTROL.value,
    }
)


STATUS_OK = "OK"
STATUS_PARTIAL = "PARTIAL"
STATUS_CANNOT_CHECK = "CANNOT_CHECK"
STATUS_NOT_APPLICABLE = "NOT_APPLICABLE"
STATUS_DESCRIPTIVE_ONLY = "DESCRIPTIVE_ONLY"

HIDDEN_SHIFT_SCOPES = frozenset(
    {
        SCOPE_HIDDEN_SHIFT,
        TaskFamily.HIDDEN_PARENT_DOMAIN.value,
        TaskFamily.HIDDEN_REPRESENTATION.value,
        TaskFamily.HIDDEN_DECOMPOSITION.value,
        TaskFamily.HIDDEN_MEASUREMENT.value,
    }
)

CONTROL_ONLY_METRICS = frozenset(
    {
        "control_abstention",
        "control_correct_restraint",
        "unnecessary_reframe",
    }
)

HIDDEN_SHIFT_ONLY_METRICS = frozenset(
    {
        "hidden_shift_success",
        "reframe_target_accuracy",
        "stale_closure_survival",
    }
)

UNIVERSAL_RATE_METRICS = frozenset(
    {
        "authority_violation",
        "depth_adequacy",
        "invariant_violation",
        "root_success",
        "trace_fidelity",
    }
)

REGISTERED_RATE_METRICS = CONTROL_ONLY_METRICS | HIDDEN_SHIFT_ONLY_METRICS | UNIVERSAL_RATE_METRICS
REGISTERED_SCOPES = HIDDEN_SHIFT_SCOPES | CONTROL_SCOPES | {SCOPE_ALL}


def _scopes() -> tuple[tuple[str, Callable[[CaseScore], bool]], ...]:
    """Reporting scopes, in table order: overall, the two protocol subsets, then families."""

    scopes: list[tuple[str, Callable[[CaseScore], bool]]] = [
        (SCOPE_ALL, lambda score: True),
        (SCOPE_HIDDEN_SHIFT, lambda score: score.is_hidden_shift),
        (SCOPE_CONTROLS, lambda score: score.is_control),
    ]
    for family in TaskFamily:
        scopes.append((family.value, lambda score, value=family.value: score.task_family == value))
    return tuple(scopes)


def _primary_metric(scope: str) -> tuple[str, stats.HypothesisDirection, float, str]:
    """The frozen primary metric for a scope, with its direction and margin.

    Root success everywhere except the negative-control scopes, where the frozen
    primary is the unnecessary-reframe rate read as non-inferiority within +0.02.
    """

    if scope in CONTROL_SCOPES:
        return (
            "unnecessary_reframe",
            stats.HypothesisDirection.NON_INFERIORITY,
            stats.H2_NON_INFERIORITY_MARGIN,
            "lower_is_better",
        )
    return (
        "root_success",
        stats.HypothesisDirection.SUPERIORITY,
        stats.H1_SUPERIORITY_MARGIN,
        "higher_is_better",
    )


# --- archive loading -----------------------------------------------------------


def load_records(path: Path) -> tuple[dict, ...]:
    """Read raw records from a `.jsonl`/`.json` file or a directory of them.

    Files are read in sorted order so the output is deterministic. A malformed
    file or record raises: silently skipping an unreadable record would turn an
    incomplete archive into confident numbers.
    """

    if not path.exists():
        return ()
    files = [path] if path.is_file() else sorted(p for p in path.rglob("*") if p.suffix in {".json", ".jsonl"})
    records: list[dict] = []
    for file in files:
        text = file.read_text()
        if file.suffix == ".jsonl":
            for number, line in enumerate(text.splitlines(), start=1):
                if not line.strip():
                    continue
                try:
                    payload = json.loads(line)
                except json.JSONDecodeError as error:
                    raise ValueError(f"{file}:{number} is not valid JSON: {error}") from error
                if not isinstance(payload, dict):
                    raise ValueError(f"{file}:{number} is not a record object")
                records.append(payload)
            continue
        payload = json.loads(text)
        items = payload if isinstance(payload, list) else [payload]
        for index, item in enumerate(items):
            if not isinstance(item, dict):
                raise ValueError(f"{file}[{index}] is not a record object")
            records.append(item)
    return tuple(records)


@dataclass(frozen=True)
class ArchiveIntegrity:
    """Whether the archive can carry a publishable comparison at all."""

    record_count: int
    suite_fingerprints: tuple[str, ...]
    subject_revisions: tuple[str, ...]
    system_ids: tuple[str, ...]
    expected_repeats: int
    blockers: tuple[str, ...]

    @property
    def coherent(self) -> bool:
        return not self.blockers

    def as_dict(self) -> dict:
        return {
            "record_count": self.record_count,
            "suite_fingerprints": list(self.suite_fingerprints),
            "subject_revisions": list(self.subject_revisions),
            "system_ids": list(self.system_ids),
            "expected_repeats": self.expected_repeats,
            "coherent": self.coherent,
            "blockers": list(self.blockers),
        }


def load_archive_design(path: Path | None) -> dict | None:
    if path is None:
        return None
    if not path.is_file():
        raise ValueError(f"archive design manifest is absent: {path}")
    payload = json.loads(path.read_text(encoding="utf-8"))
    if not isinstance(payload, dict) or payload.get("schema_version") != "orion.p1.archive-design.v1":
        raise ValueError(f"{path} is not an orion.p1.archive-design.v1 object")
    required = {"suite_fingerprint", "subject_revision", "system_ids", "case_ids", "seeds", "expected_record_count"}
    missing = sorted(required - set(payload))
    if missing:
        raise ValueError(f"archive design manifest missing {missing}")
    for key in ("system_ids", "case_ids", "seeds"):
        values = payload[key]
        if not isinstance(values, list) or not values or len(set(values)) != len(values):
            raise ValueError(f"archive design {key} must be a non-empty unique list")
    expected = len(payload["system_ids"]) * len(payload["case_ids"]) * len(payload["seeds"])
    if int(payload["expected_record_count"]) != expected:
        raise ValueError("archive design expected_record_count does not match its Cartesian grid")
    return payload


def check_archive(
    scores: Sequence[CaseScore],
    *,
    expected_repeats: int,
    expected_design: dict | None = None,
) -> ArchiveIntegrity:
    """Refuse to publish from an archive that cannot bind its own numbers.

    Blocking conditions, all of which make a published table unverifiable rather
    than merely imprecise:

    * no records at all;
    * records carrying no suite fingerprint — nothing binds them to a frozen
      suite, so the result cannot be reproduced or audited;
    * records spanning more than one suite fingerprint or subject revision —
      pooling two revisions produces a number that describes neither;
    * any (system, case) group whose repeat count differs from the frozen
      `stochastic_repeats`, which would silently compare systems run at
      different effort.
    """

    fingerprints = tuple(sorted({score.suite_fingerprint for score in scores if score.suite_fingerprint}))
    revisions = tuple(sorted({score.subject_revision for score in scores if score.subject_revision}))
    system_ids = tuple(sorted({score.system_id for score in scores}))

    blockers: list[str] = []
    if not scores:
        blockers.append("archive contains no records")
    else:
        if not fingerprints:
            blockers.append("records carry no suite_fingerprint; results are not bound to a frozen suite")
        if len(fingerprints) > 1:
            blockers.append(f"records span {len(fingerprints)} suite fingerprints: {list(fingerprints)}")
        if len(revisions) > 1:
            blockers.append(f"records span {len(revisions)} subject revisions: {list(revisions)}")

        counts: dict[tuple[str, str], int] = {}
        for score in scores:
            key = (score.system_id, score.case_id)
            counts[key] = counts.get(key, 0) + 1
        offenders = sorted(key for key, count in counts.items() if count != expected_repeats)
        if offenders:
            shown = ", ".join(f"{system}/{case}={counts[(system, case)]}" for system, case in offenders[:5])
            blockers.append(
                f"{len(offenders)} (system, case) group(s) do not carry the frozen {expected_repeats} stochastic repeats: {shown}"
                + (" ..." if len(offenders) > 5 else "")
            )

        if expected_design is not None:
            expected_systems = set(map(str, expected_design["system_ids"]))
            expected_cases = set(map(str, expected_design["case_ids"]))
            expected_seeds = {int(seed) for seed in expected_design["seeds"]}
            if len(expected_seeds) != expected_repeats:
                blockers.append(
                    "archive design seed count does not equal the frozen stochastic repeats"
                )
            expected_fingerprint = str(expected_design["suite_fingerprint"])
            expected_revision = str(expected_design["subject_revision"])
            if set(fingerprints) != {expected_fingerprint}:
                blockers.append("archive suite_fingerprint does not match the expected design")
            if set(revisions) != {expected_revision}:
                blockers.append("archive subject_revision does not match the expected design")

            observed_systems = {score.system_id for score in scores}
            observed_cases = {score.case_id for score in scores}
            observed_seeds = {score.seed for score in scores}
            for label, missing, unexpected in (
                ("systems", expected_systems - observed_systems, observed_systems - expected_systems),
                ("cases", expected_cases - observed_cases, observed_cases - expected_cases),
                ("seeds", expected_seeds - observed_seeds, observed_seeds - expected_seeds),
            ):
                if missing:
                    shown = sorted(missing)
                    if label == "cases":
                        shown = [
                            blinded_case_id(case_id, suite_fingerprint=expected_fingerprint)
                            for case_id in shown
                        ]
                    blockers.append(f"archive missing expected {label}: {shown[:5]}")
                if unexpected:
                    blockers.append(f"archive contains unexpected {label}: {sorted(unexpected)[:5]}")

            tuple_counts: dict[tuple[str, str, int], int] = {}
            for score in scores:
                key = (score.system_id, score.case_id, score.seed)
                tuple_counts[key] = tuple_counts.get(key, 0) + 1
            expected_tuples = {
                (system_id, case_id, seed)
                for system_id in expected_systems
                for case_id in expected_cases
                for seed in expected_seeds
            }
            missing_tuples = sorted(expected_tuples - set(tuple_counts))
            duplicate_tuples = sorted(key for key, count in tuple_counts.items() if count != 1)
            if missing_tuples:
                shown = [
                    f"{system}/{blinded_case_id(case, suite_fingerprint=expected_fingerprint)}/seed={seed}"
                    for system, case, seed in missing_tuples[:5]
                ]
                blockers.append(
                    f"archive missing {len(missing_tuples)} expected (system, blinded-case, seed) row(s): {shown}"
                )
            if duplicate_tuples:
                shown = [
                    f"{system}/{blinded_case_id(case, suite_fingerprint=expected_fingerprint)}/seed={seed}={tuple_counts[(system, case, seed)]}"
                    for system, case, seed in duplicate_tuples[:5]
                ]
                blockers.append(
                    f"archive has {len(duplicate_tuples)} non-unique (system, blinded-case, seed) row(s): {shown}"
                )
            if len(scores) != int(expected_design["expected_record_count"]):
                blockers.append(
                    f"archive has {len(scores)} records; expected {expected_design['expected_record_count']}"
                )

    return ArchiveIntegrity(
        record_count=len(scores),
        suite_fingerprints=fingerprints,
        subject_revisions=revisions,
        system_ids=system_ids,
        expected_repeats=expected_repeats,
        blockers=tuple(blockers),
    )


# --- aggregation over the archive ----------------------------------------------


def _aggregates(
    scores: Sequence[CaseScore],
    *,
    expected_repeats: int,
) -> dict[tuple[str, str], SystemAggregate]:
    by_system: dict[str, list[CaseScore]] = {}
    for score in scores:
        by_system.setdefault(score.system_id, []).append(score)

    built: dict[tuple[str, str], SystemAggregate] = {}
    for system_id, system_scores in by_system.items():
        for scope, predicate in _scopes():
            subset = [score for score in system_scores if predicate(score)]
            if not subset:
                continue
            built[(system_id, scope)] = aggregate(subset, scope=scope, expected_repeats=expected_repeats)
    return built


def select_comparator(aggregates: dict[tuple[str, str], SystemAggregate]) -> tuple[str | None, str]:
    """The strongest matched **baseline**, chosen once and reused for every row.

    Only `SystemRole.BASELINE` systems are eligible: an ORION ablation is the
    comparator for H3/H4, never for H1's "strongest matched baseline". Selection
    is on overall root success (scope ALL) so the difference column does not
    change comparator between families; ties break on `system_id` so the choice
    is deterministic.
    """

    candidates = [
        (item.root_success.value, system_id)
        for (system_id, scope), item in aggregates.items()
        if scope == SCOPE_ALL and item.system_role is SystemRole.BASELINE and item.root_success.value is not None
    ]
    if not candidates:
        return None, "no system with role BASELINE carries a scorable overall root-success rate"
    best = max(value for value, _ in candidates)
    winner = min(system_id for value, system_id in candidates if value == best)
    return winner, f"highest overall root_success ({best:.4f}) among BASELINE systems, ties broken on system_id"


def _metric_applicable(scope: str, metric: str) -> bool:
    """Whether a frozen P1 metric is defined for a reporting scope.

    Applicability is an independent schema dimension. It cannot be inferred from
    an empty denominator because an applicable metric can also have ``n == 0``
    when evidence is missing. The aggregate ``ALL`` scope contains both hidden
    shifts and controls, so both metric families are defined there.
    """

    if scope not in REGISTERED_SCOPES:
        raise ValueError(f"unregistered P1 reporting scope: {scope}")
    if metric not in REGISTERED_RATE_METRICS:
        raise ValueError(f"unregistered P1 binary-rate metric: {metric}")
    if scope == SCOPE_ALL:
        return True
    if metric in CONTROL_ONLY_METRICS:
        return scope in CONTROL_SCOPES
    if metric in HIDDEN_SHIFT_ONLY_METRICS:
        return scope in HIDDEN_SHIFT_SCOPES
    return metric in UNIVERSAL_RATE_METRICS


def _rate_block(rate, *, label: str, scope: str = SCOPE_ALL) -> dict:
    payload = {"metric": label, **rate.as_dict(), "interval": None}
    if not _metric_applicable(scope, label):
        payload["status"] = STATUS_NOT_APPLICABLE
        payload["reason"] = f"{label} is outside its frozen applicability domain for scope {scope}"
        return payload
    if rate.n > 0 and rate.unit == "case":
        payload["interval"] = stats.wilson_interval(rate.successes, rate.n).as_dict()
    elif rate.n == 0:
        payload["status"] = STATUS_CANNOT_CHECK
    return payload


def _mechanistic_block(item: SystemAggregate, *, scope: str) -> dict:
    return {
        "responsibility_macro_f1": item.responsibility_macro_f1,
        "responsibility_labels": list(item.responsibility_labels),
        "reframe_target_accuracy": _rate_block(
            item.reframe_target_accuracy,
            label="reframe_target_accuracy",
            scope=scope,
        ),
        "reopen": item.reopen.as_dict(),
        "reopen_by_dependency_depth": [
            {"dependency_depth": depth, **comparison.as_dict()} for depth, comparison in item.reopen_by_depth
        ],
        "stale_closure_survival": _rate_block(
            item.stale_closure_survival,
            label="stale_closure_survival",
            scope=scope,
        ),
        "invariant_violation": _rate_block(
            item.invariant_violation,
            label="invariant_violation",
            scope=scope,
        ),
        "authority_violation": _rate_block(
            item.authority_violation,
            label="authority_violation",
            scope=scope,
        ),
        "trace_fidelity": _rate_block(item.trace_fidelity, label="trace_fidelity", scope=scope),
        "trace_fidelity_by_dependency_depth": [
            {"dependency_depth": depth, **rate.as_dict()} for depth, rate in item.trace_fidelity_by_depth
        ],
        "depth_adequacy": _rate_block(item.depth_adequacy, label="depth_adequacy", scope=scope),
        "control_abstention": _rate_block(
            item.control_abstention,
            label="control_abstention",
            scope=scope,
        ),
        "control_correct_restraint": _rate_block(
            item.control_correct_restraint,
            label="control_correct_restraint",
            scope=scope,
        ),
        "hidden_shift_success": _rate_block(
            item.hidden_shift_success,
            label="hidden_shift_success",
            scope=scope,
        ),
        "root_success": _rate_block(item.root_success, label="root_success", scope=scope),
        "unnecessary_reframe": _rate_block(
            item.unnecessary_reframe,
            label="unnecessary_reframe",
            scope=scope,
        ),
        "resources": item.resources.as_dict(),
    }


def _difference_block(
    subject: SystemAggregate,
    comparator: SystemAggregate,
    *,
    metric: str,
    direction: stats.HypothesisDirection,
    margin: float,
    seed: int,
    resamples: int,
    hypothesis_id: str,
    min_units: int,
    inferential: bool,
) -> dict:
    values_a, values_b, matched, unmatched = matched_units(subject, comparator, metric)
    cannot_check_units = len(unmatched) + subject.cannot_check_cases + comparator.cannot_check_cases
    if not values_a:
        if inferential:
            assessment = stats.assess_hypothesis(
                hypothesis_id=hypothesis_id,
                direction=direction,
                margin=margin,
                difference=None,
                cannot_check_units=cannot_check_units,
            ).as_dict()
        else:
            assessment = {
                "hypothesis_id": hypothesis_id,
                "verdict": STATUS_DESCRIPTIVE_ONLY,
                "direction": direction.value,
                "margin": margin,
                "rationale": "NO_REGISTERED_HYPOTHESIS: descriptive comparator contrast only",
                "difference": None,
            }
        return {
            "metric": metric,
            "comparator_system_id": comparator.system_id,
            "matched_units": 0,
            "unmatched_blinded_case_ids": list(subject.blinded(unmatched)),
            "cannot_check_units": cannot_check_units,
            "difference": None,
            "cohens_h": None,
            "assessment": assessment,
            "status": STATUS_CANNOT_CHECK,
        }

    difference = stats.paired_bootstrap_difference(values_a, values_b, resamples=resamples, seed=seed)
    subject_rate = getattr(subject, metric).value
    comparator_rate = getattr(comparator, metric).value
    effect_h = (
        stats.cohens_h(subject_rate, comparator_rate)
        if subject_rate is not None and comparator_rate is not None
        else None
    )
    if inferential:
        assessment = stats.assess_hypothesis(
            hypothesis_id=hypothesis_id,
            direction=direction,
            margin=margin,
            difference=difference,
            cannot_check_units=cannot_check_units,
            min_units=min_units,
            subject_abstention_rate=subject.control_abstention.value if direction is stats.HypothesisDirection.NON_INFERIORITY else None,
            comparator_abstention_rate=comparator.control_abstention.value if direction is stats.HypothesisDirection.NON_INFERIORITY else None,
        ).as_dict()
    else:
        assessment = {
            "hypothesis_id": hypothesis_id,
            "verdict": STATUS_DESCRIPTIVE_ONLY,
            "direction": direction.value,
            "margin": margin,
            "rationale": "NO_REGISTERED_HYPOTHESIS: descriptive comparator contrast only",
            "difference": difference.as_dict(),
        }
    # Diagnostic companion on the per-case seed means. Same resampling unit (the
    # case), but it keeps the within-case resolution that the frozen majority
    # reduction discards, so a real per-seed gap between two systems that both
    # reduce to the same case-level rate remains visible. It is a diagnostic:
    # the frozen `difference` above is what the hypothesis verdict reads.
    # Indexed by the frozen `matched` list, not re-paired, so the diagnostic is
    # structurally guaranteed to cover exactly the same units as the difference
    # it accompanies.
    seed_mean_a = subject.per_case_metrics.get(f"{metric}_seed_mean", {})
    seed_mean_b = comparator.per_case_metrics.get(f"{metric}_seed_mean", {})
    seed_mean_difference = None
    if all(case_id in seed_mean_a and case_id in seed_mean_b for case_id in matched):
        seed_mean_difference = stats.paired_bootstrap_difference(
            [seed_mean_a[case_id] for case_id in matched],
            [seed_mean_b[case_id] for case_id in matched],
            resamples=resamples,
            seed=seed,
        ).as_dict()

    return {
        "metric": metric,
        "comparator_system_id": comparator.system_id,
        "matched_units": len(matched),
        "unmatched_blinded_case_ids": list(subject.blinded(unmatched)),
        "cannot_check_units": cannot_check_units,
        "difference": difference.as_dict(),
        "absolute_effect": difference.point,
        "seed_mean_difference": seed_mean_difference,
        "seed_mean_note": "diagnostic only: the same matched cases resampled on per-case seed means rather than the frozen majority reduction; the verdict reads `difference`",
        "cohens_h": effect_h,
        "cohens_h_note": "secondary, unpaired proportion effect size; the frozen margins are absolute, so the headline effect is `absolute_effect`",
        "assessment": assessment,
        "status": STATUS_OK if not cannot_check_units else STATUS_PARTIAL,
    }


def build_t2(
    scores: Sequence[CaseScore],
    integrity: ArchiveIntegrity,
    *,
    expected_repeats: int,
    bootstrap_seed: int,
    resamples: int,
    min_units: int = 0,
) -> dict:
    """Build ``P1-T2_baseline_ablation_results`` from archived records."""

    provenance = _provenance(integrity, bootstrap_seed=bootstrap_seed, resamples=resamples, expected_repeats=expected_repeats)
    if not integrity.coherent:
        return {
            "table_id": TABLE_T2,
            "status": STATUS_CANNOT_CHECK,
            "reason": "; ".join(integrity.blockers),
            "provenance": provenance,
            "comparator": {"system_id": None, "basis": "not selected: archive is not publishable"},
            "rows": [],
            "multiplicity": None,
        }

    aggregates = _aggregates(scores, expected_repeats=expected_repeats)
    comparator_id, comparator_basis = select_comparator(aggregates)

    rows: list[dict] = []
    secondary_pvalues: list[tuple[str, float]] = []
    partial = False

    for system_id in sorted({key[0] for key in aggregates}):
        for scope, _ in _scopes():
            item = aggregates.get((system_id, scope))
            if item is None:
                continue
            metric, direction, margin, sense = _primary_metric(scope)
            rate = getattr(item, metric)
            row: dict = {
                "system_id": system_id,
                "system_role": item.system_role.value,
                "scope": scope,
                "primary_metric": metric,
                "sense": sense,
                "practical_margin": margin,
                "n_cases_scored": item.n_cases_scored,
                "n_trials_scored": item.n_trials_scored,
                "cannot_check_cases": item.cannot_check_cases,
                "cannot_check_blinded_case_ids": list(item.blinded(item.cannot_check_case_ids)),
                "repeat_coverage_ok": item.repeat_coverage_ok,
                "rate": _rate_block(rate, label=metric),
                "mechanistic": _mechanistic_block(item, scope=scope),
                "difference_vs_comparator": None,
            }
            if item.cannot_check_cases or not item.repeat_coverage_ok or rate.n == 0:
                partial = True

            comparator_item = aggregates.get((comparator_id, scope)) if comparator_id else None
            if comparator_item is not None and system_id != comparator_id:
                is_subject = item.system_role is SystemRole.SUBJECT
                if is_subject and scope == SCOPE_ALL:
                    hypothesis_id = "P1.H1"
                elif is_subject and scope in CONTROL_SCOPES:
                    hypothesis_id = "P1.H2"
                elif is_subject:
                    hypothesis_id = f"P1.secondary:{scope}"
                else:
                    hypothesis_id = f"descriptive:{system_id}:{scope}"
                block = _difference_block(
                    item,
                    comparator_item,
                    metric=metric,
                    direction=direction,
                    margin=margin,
                    seed=bootstrap_seed,
                    resamples=resamples,
                    hypothesis_id=hypothesis_id,
                    min_units=min_units,
                    inferential=is_subject,
                )
                row["difference_vs_comparator"] = block
                if block["status"] != STATUS_OK:
                    partial = True
                if (
                    is_subject
                    and hypothesis_id.startswith("P1.")
                    and hypothesis_id not in {"P1.H1"}
                    and block["difference"] is not None
                ):
                    secondary_pvalues.append((f"{hypothesis_id}", block["difference"]["two_sided_p"]))
            rows.append(row)

    multiplicity = _multiplicity(secondary_pvalues)
    return {
        "table_id": TABLE_T2,
        "status": STATUS_PARTIAL if partial else STATUS_OK,
        "reason": "",
        "provenance": provenance,
        "comparator": {"system_id": comparator_id, "basis": comparator_basis},
        "rows": rows,
        "multiplicity": multiplicity,
    }


def _multiplicity(pvalues: Sequence[tuple[str, float]]) -> dict | None:
    """Holm correction over the inferential secondary family.

    The protocol declares a single primary hypothesis (H1), which is therefore
    uncorrected; every other subject-versus-comparator p-value enters one Holm
    family here.
    """

    if not pvalues:
        return None
    labels = [label for label, _ in pvalues]
    raw = [value for _, value in pvalues]
    entries = stats.holm_correction(raw, labels=labels)
    return {
        "method": "holm_bonferroni",
        "family": "inferential secondary comparisons (the single primary hypothesis P1.H1 is uncorrected)",
        "alpha": 1.0 - stats.PROTOCOL_CONFIDENCE,
        "entries": [entry.as_dict() for entry in entries],
    }


def build_t3(
    scores: Sequence[CaseScore],
    integrity: ArchiveIntegrity,
    *,
    expected_repeats: int,
    bootstrap_seed: int,
    resamples: int,
    representatives: int = DEFAULT_REPRESENTATIVES,
) -> dict:
    """Build ``P1-T3_failure_taxonomy`` from archived records.

    Case ids are emitted **blinded only** (`metrics.blinded_case_id`): the
    published taxonomy names failure modes and representative cases without
    handing a reader the host-owned suite.
    """

    provenance = _provenance(integrity, bootstrap_seed=bootstrap_seed, resamples=resamples, expected_repeats=expected_repeats)
    if not integrity.coherent:
        return {
            "table_id": TABLE_T3,
            "status": STATUS_CANNOT_CHECK,
            "reason": "; ".join(integrity.blockers),
            "provenance": provenance,
            "rows": [],
        }

    scored = [score for score in scores if score.status is ScoreStatus.SCORED]
    unscorable = [score for score in scores if score.status is ScoreStatus.CANNOT_CHECK]
    trials_by_system: dict[str, int] = {}
    for score in scored:
        trials_by_system[score.system_id] = trials_by_system.get(score.system_id, 0) + 1

    buckets: dict[tuple[str, str], list[CaseScore]] = {}
    for score in scored:
        buckets.setdefault((score.system_id, score.failure_mode.value), []).append(score)
    for score in unscorable:
        buckets.setdefault((score.system_id, score.failure_mode.value), []).append(score)

    rows: list[dict] = []
    for (system_id, mode), members in buckets.items():
        denominator = trials_by_system.get(system_id, 0)
        blinded = sorted({member.blinded_case_id for member in members})
        rows.append(
            {
                "system_id": system_id,
                "system_role": members[0].system_role.value,
                "failure_mode": mode,
                "trials": len(members),
                "distinct_cases": len(blinded),
                "share_of_scored_trials": (len(members) / denominator) if denominator else None,
                "share_denominator": denominator,
                "share_unit": "scored trial (case x seed)",
                "representative_blinded_case_ids": blinded[:representatives],
                "example_faults": sorted({fault for member in members for fault in member.trace_fidelity_faults})[:representatives],
            }
        )
    rows.sort(key=lambda row: (-row["trials"], row["system_id"], row["failure_mode"]))

    totals: dict[str, dict] = {}
    for row in rows:
        entry = totals.setdefault(
            row["failure_mode"],
            {"failure_mode": row["failure_mode"], "trials": 0, "systems": set(), "representative_blinded_case_ids": []},
        )
        entry["trials"] += row["trials"]
        entry["systems"].add(row["system_id"])
        entry["representative_blinded_case_ids"].extend(row["representative_blinded_case_ids"])
    rollup = [
        {
            "failure_mode": entry["failure_mode"],
            "trials": entry["trials"],
            "systems": len(entry["systems"]),
            "share_of_all_scored_trials": (entry["trials"] / len(scored)) if scored else None,
            "representative_blinded_case_ids": sorted(set(entry["representative_blinded_case_ids"]))[:representatives],
        }
        for entry in totals.values()
    ]
    rollup.sort(key=lambda entry: (-entry["trials"], entry["failure_mode"]))

    return {
        "table_id": TABLE_T3,
        "status": STATUS_OK if scored else STATUS_CANNOT_CHECK,
        "reason": "" if scored else "no scored trials in the archive",
        "provenance": provenance,
        "attribution_policy": "one primary failure mode per trial by the precedence in metrics.classify_failure (authority > invariant > trace integrity > abstention > control selectivity > diagnosis > targeting > reopening > terminal outcome); every mode that fired is retained on the record",
        "rows": rows,
        "rollup_by_failure_mode": rollup,
    }


def _provenance(integrity: ArchiveIntegrity, *, bootstrap_seed: int, resamples: int, expected_repeats: int) -> dict:
    return {
        "protocol_id": stats.PROTOCOL_ID,
        "generated_utc": datetime.now(UTC).isoformat(timespec="seconds"),
        "record_schema": "orion.p1.case-record.v1",
        "source": "archived raw records only; no live case, gold label or system execution",
        "suite_fingerprints": list(integrity.suite_fingerprints),
        "subject_revisions": list(integrity.subject_revisions),
        "record_count": integrity.record_count,
        "system_ids": list(integrity.system_ids),
        "stochastic_repeats": expected_repeats,
        "confidence": stats.PROTOCOL_CONFIDENCE,
        "interval_method": "wilson_score for standalone binary rates; paired percentile bootstrap for matched differences",
        "bootstrap_seed": bootstrap_seed,
        "bootstrap_resamples": resamples,
        "unit_of_analysis": "frozen case; the stochastic repeats are reduced per case before any interval is taken",
        "integrity": integrity.as_dict(),
    }


# --- markdown rendering --------------------------------------------------------


def _fmt(value: float | None, digits: int = 4) -> str:
    return "CANNOT_CHECK" if value is None else f"{value:.{digits}f}"


def _fmt_interval(payload: dict | None) -> str:
    if not payload:
        return "CANNOT_CHECK"
    return f"[{payload['low']:.4f}, {payload['high']:.4f}]"


def _md_table(headers: Sequence[str], rows: Iterable[Sequence[str]]) -> str:
    lines = ["| " + " | ".join(headers) + " |", "|" + "|".join(["---"] * len(headers)) + "|"]
    lines.extend("| " + " | ".join(cell for cell in row) + " |" for row in rows)
    return "\n".join(lines)


def render_t2_markdown(table: dict) -> str:
    header = [
        f"# {table['table_id']}",
        "",
        f"**Status:** `{table['status']}`",
    ]
    if table["reason"]:
        header.append(f"**Reason:** {table['reason']}")
    provenance = table["provenance"]
    header += [
        "",
        f"Suite fingerprint(s): `{', '.join(provenance['suite_fingerprints']) or 'UNBOUND'}` · "
        f"subject revision(s): `{', '.join(provenance['subject_revisions']) or 'UNBOUND'}` · "
        f"records: {provenance['record_count']} · repeats/case: {provenance['stochastic_repeats']}",
        f"Intervals: Wilson {provenance['confidence']:.0%} on the case unit; matched differences by paired percentile bootstrap "
        f"({provenance['bootstrap_resamples']} resamples, seed {provenance['bootstrap_seed']}).",
        f"Comparator: `{table['comparator']['system_id'] or 'CANNOT_CHECK'}` — {table['comparator']['basis']}.",
        "",
    ]
    if not table["rows"]:
        header.append("_No rows: the archive carries no publishable records._")
        return "\n".join(header) + "\n"

    rows = []
    for row in table["rows"]:
        difference = row["difference_vs_comparator"]
        diff_payload = difference["difference"] if difference else None
        rows.append(
            [
                f"`{row['system_id']}`",
                row["system_role"],
                row["scope"],
                row["primary_metric"],
                str(row["n_cases_scored"]),
                _fmt(row["rate"]["value"]),
                _fmt_interval(row["rate"]["interval"]),
                _fmt(diff_payload["point"]) if diff_payload else "—",
                _fmt_interval(diff_payload) if diff_payload else "—",
                _fmt(difference["cohens_h"]) if difference else "—",
                (f"{diff_payload['two_sided_p']:.4f}" if diff_payload and diff_payload["two_sided_p"] > diff_payload["p_floor"] else (f"<{diff_payload['p_floor']:.4f}" if diff_payload else "—")),
                difference["assessment"]["verdict"] if difference else "—",
                str(row["cannot_check_cases"]),
            ]
        )
    body = _md_table(
        [
            "system",
            "role",
            "scope",
            "metric",
            "n cases",
            "rate",
            "95% CI",
            "Δ vs comparator",
            "Δ 95% CI",
            "Cohen's h",
            "p (2-sided)",
            "verdict",
            "CANNOT_CHECK cases",
        ],
        rows,
    )

    mechanistic_rows = []
    for row in table["rows"]:
        if row["scope"] != SCOPE_ALL:
            continue
        mechanistic = row["mechanistic"]
        mechanistic_rows.append(
            [
                f"`{row['system_id']}`",
                _fmt(mechanistic["responsibility_macro_f1"]),
                _fmt(mechanistic["reframe_target_accuracy"]["value"]),
                _fmt(mechanistic["reopen"]["precision"]),
                _fmt(mechanistic["reopen"]["recall"]),
                _fmt(mechanistic["reopen"]["f1"]),
                _fmt(mechanistic["stale_closure_survival"]["value"]),
                _fmt(mechanistic["invariant_violation"]["value"]),
                _fmt(mechanistic["authority_violation"]["value"]),
                _fmt(mechanistic["trace_fidelity"]["value"]),
                _fmt(mechanistic["resources"]["wallclock_seconds_mean"], 2),
                _fmt(mechanistic["resources"]["model_tokens_mean"], 1),
                _fmt(mechanistic["resources"]["tool_calls_mean"], 2),
            ]
        )
    mechanistic_table = _md_table(
        [
            "system",
            "responsibility macro-F1",
            "reframe-target acc.",
            "reopen P",
            "reopen R",
            "reopen F1",
            "stale-closure survival",
            "invariant viol.",
            "authority viol.",
            "trace fidelity",
            "wallclock s/trial",
            "tokens/trial",
            "tool calls/trial",
        ],
        mechanistic_rows,
    )

    parts = ["\n".join(header), body, "", "## Mechanistic metrics (scope ALL)", "", mechanistic_table]
    if table["multiplicity"]:
        multiplicity_rows = [
            [entry["label"], f"{entry['raw_p']:.4f}", f"{entry['adjusted_p']:.4f}", "yes" if entry["rejected"] else "no"]
            for entry in table["multiplicity"]["entries"]
        ]
        parts += [
            "",
            "## Multiplicity (Holm, inferential secondary family)",
            "",
            _md_table(["comparison", "raw p", "Holm-adjusted p", f"rejected at α={table['multiplicity']['alpha']:.2f}"], multiplicity_rows),
        ]
    parts += [
        "",
        "_Rates use the frozen case as the unit; the 5 stochastic repeats are reduced per case before any interval is taken. "
        "`CANNOT_CHECK` marks a quantity that was not observed and is never rendered as 0._",
        "",
    ]
    return "\n".join(parts)


def render_t3_markdown(table: dict) -> str:
    header = [f"# {table['table_id']}", "", f"**Status:** `{table['status']}`"]
    if table["reason"]:
        header.append(f"**Reason:** {table['reason']}")
    header += ["", f"_Attribution:_ {table.get('attribution_policy', '')}", ""]
    if not table["rows"]:
        header.append("_No rows: the archive carries no publishable records._")
        return "\n".join(header) + "\n"

    rows = [
        [
            f"`{row['system_id']}`",
            row["system_role"],
            row["failure_mode"],
            str(row["trials"]),
            str(row["distinct_cases"]),
            _fmt(row["share_of_scored_trials"]),
            ", ".join(f"`{case_id}`" for case_id in row["representative_blinded_case_ids"]) or "—",
        ]
        for row in table["rows"]
    ]
    body = _md_table(
        ["system", "role", "failure mode", "trials", "distinct cases", "share of scored trials", "representative blinded cases"],
        rows,
    )
    rollup_rows = [
        [
            entry["failure_mode"],
            str(entry["trials"]),
            str(entry["systems"]),
            _fmt(entry["share_of_all_scored_trials"]),
            ", ".join(f"`{case_id}`" for case_id in entry["representative_blinded_case_ids"]) or "—",
        ]
        for entry in table["rollup_by_failure_mode"]
    ]
    return "\n".join(
        [
            "\n".join(header),
            body,
            "",
            "## Roll-up by failure mode (all systems)",
            "",
            _md_table(["failure mode", "trials", "systems", "share of all scored trials", "representative blinded cases"], rollup_rows),
            "",
            "_Case ids are blinded pseudonyms derived from the host-owned suite fingerprint; the raw suite is never published._",
            "",
        ]
    )


# --- entry point ---------------------------------------------------------------


def generate(
    archive: Path,
    output: Path,
    *,
    expected_repeats: int = stats.PROTOCOL_STOCHASTIC_REPEATS,
    bootstrap_seed: int = DEFAULT_BOOTSTRAP_SEED,
    resamples: int = stats.PROTOCOL_RESAMPLES,
    min_units: int = 0,
    representatives: int = DEFAULT_REPRESENTATIVES,
    design_manifest: Path | None = None,
) -> tuple[dict, dict]:
    """Regenerate both tables from an archive and write JSON + markdown."""

    records = load_records(archive)
    scores = [case_score_from_record(record) for record in records]
    integrity = check_archive(
        scores,
        expected_repeats=expected_repeats,
        expected_design=load_archive_design(design_manifest),
    )

    t2 = build_t2(
        scores,
        integrity,
        expected_repeats=expected_repeats,
        bootstrap_seed=bootstrap_seed,
        resamples=resamples,
        min_units=min_units,
    )
    t3 = build_t3(
        scores,
        integrity,
        expected_repeats=expected_repeats,
        bootstrap_seed=bootstrap_seed,
        resamples=resamples,
        representatives=representatives,
    )

    output.mkdir(parents=True, exist_ok=True)
    (output / f"{TABLE_T2}.json").write_text(json.dumps(t2, indent=2, sort_keys=True) + "\n")
    (output / f"{TABLE_T2}.md").write_text(render_t2_markdown(t2))
    (output / f"{TABLE_T3}.json").write_text(json.dumps(t3, indent=2, sort_keys=True) + "\n")
    (output / f"{TABLE_T3}.md").write_text(render_t3_markdown(t3))
    return t2, t3


#: The one field that cannot reproduce. Everything else in `provenance` is derived from
#: the archive, so excluding the wall clock is what makes the byte comparison meaningful
#: rather than impossible: the two committed tables were written a second apart, so no
#: single pinned timestamp reproduces both.
_NON_REPRODUCIBLE_PROVENANCE = ("generated_utc",)


def _without_clock(table: dict) -> dict:
    provenance = {
        key: value
        for key, value in table.get("provenance", {}).items()
        if key not in _NON_REPRODUCIBLE_PROVENANCE
    }
    return {**table, "provenance": provenance}


#: Tolerance for "the same computation, run on a different CPU".
#:
#: IEEE754 double arithmetic is not bit-reproducible across platforms: summation
#: order, libm, and FMA contraction all differ between macOS arm64 and the Linux
#: x86-64 CI runner. The committed tables were generated on one and are checked on
#: the other, and 20 bootstrap interval bounds differed in their last bits -- the
#: largest delta 5.551e-17, which is 2 ULP near 0.19. The markdown renderings, which
#: round to four digits and are compared byte-for-byte, matched exactly; the numbers
#: are the same numbers.
#:
#: These bounds come from a 10,000-resample percentile bootstrap, whose Monte Carlo
#: error is on the order of 1e-3. Asserting bit-equality on them asserts something
#: that is neither true of the arithmetic nor meaningful about the science.
#:
#: The band is deliberately wide of the noise and far below anything real. Platform
#: noise sits at ~3e-16 relative; a changed seed, changed archive or changed
#: estimator moves these values by ~1e-3. There is no realistic edit that lands in
#: between, so nothing real hides here.
#:
#: abs_tol exists for one observed case: a bound computed as 6.938893903907228e-18 on
#: one platform and exactly 0.0 on the other. Relative comparison against zero is
#: undefined, and these are probabilities in [0, 1] where 1e-15 absolute is nothing.
_FLOAT_REL_TOL = 1e-12
_FLOAT_ABS_TOL = 1e-15


def _near(committed: float, regenerated: float) -> bool:
    """Same value to within cross-platform floating-point noise."""

    return math.isclose(committed, regenerated, rel_tol=_FLOAT_REL_TOL, abs_tol=_FLOAT_ABS_TOL)


def _differences(
    committed: object, regenerated: object, path: str = ""
) -> tuple[list[str], list[str]]:
    """Leaves where two table payloads disagree, split by whether it matters.

    Returns ``(hard, soft)``. ``hard`` is real drift and fails the check. ``soft`` is
    float difference within :data:`_FLOAT_REL_TOL` -- reported, never silent, but not
    a failure.

    A drift detector that only says "something changed" makes the next reader
    re-derive the diff by hand, and cross-platform float drift is invisible in the
    markdown rendering because that rounds to four digits. Reporting the pointer and
    both values is what turns a red run into a diagnosis.
    """

    if isinstance(committed, dict) and isinstance(regenerated, dict):
        hard: list[str] = []
        soft: list[str] = []
        for key in sorted(set(committed) | set(regenerated)):
            if key not in committed:
                hard.append(f"{path}/{key}: absent in committed, regenerated={regenerated[key]!r}")
            elif key not in regenerated:
                hard.append(f"{path}/{key}: committed={committed[key]!r}, absent in regeneration")
            else:
                sub_hard, sub_soft = _differences(committed[key], regenerated[key], f"{path}/{key}")
                hard.extend(sub_hard)
                soft.extend(sub_soft)
        return hard, soft
    if isinstance(committed, list) and isinstance(regenerated, list):
        if len(committed) != len(regenerated):
            return [f"{path}: length {len(committed)} vs {len(regenerated)}"], []
        hard, soft = [], []
        for index, (left, right) in enumerate(zip(committed, regenerated, strict=True)):
            sub_hard, sub_soft = _differences(left, right, f"{path}/{index}")
            hard.extend(sub_hard)
            soft.extend(sub_soft)
        return hard, soft
    if committed == regenerated:
        return [], []
    if isinstance(committed, float) and isinstance(regenerated, float):
        detail = f"{path}: {committed!r} vs {regenerated!r} (delta {regenerated - committed:+.3e})"
        if _near(committed, regenerated):
            return [], [detail]
        return [detail], []
    return [f"{path}: {committed!r} vs {regenerated!r}"], []


def _check(args: argparse.Namespace) -> int:
    """Compare a live regeneration against the committed tables.

    `git diff --exit-code` cannot be used on P1 the way it is used on P3, P5 and P4:
    `provenance.generated_utc` is a wall clock, so following REPRODUCE.md always drifts a
    package whose tables are content-hash-bound. Comparing every field except that one
    states the claim that is actually true and actually useful -- given the same archive,
    every published number reproduces exactly.
    """

    with tempfile.TemporaryDirectory(prefix="p1-tables-check-") as scratch:
        try:
            regenerated = generate(
                args.archive,
                Path(scratch),
                expected_repeats=args.expected_repeats,
                bootstrap_seed=args.bootstrap_seed,
                resamples=args.resamples,
                min_units=args.min_units,
                representatives=args.representatives,
                design_manifest=args.design_manifest,
            )
        except ValueError as error:
            print(f"P1 tables: archive is malformed and was not used: {error}", file=sys.stderr)
            return EXIT_ERROR

        drifted: list[str] = []
        missing: list[str] = []
        for table in regenerated:
            name = f'{table["table_id"]}.json'
            committed_path = args.out / name
            if not committed_path.is_file():
                missing.append(str(committed_path))
                continue
            committed = json.loads(committed_path.read_text(encoding="utf-8"))
            hard, soft = _differences(_without_clock(committed), _without_clock(table))
            if soft:
                # Never silent: a reader must be able to see that the bytes are not
                # identical even when the numbers are.
                print(
                    f"P1 tables: {name}: {len(soft)} field(s) differ within floating-point "
                    f"tolerance (rel {_FLOAT_REL_TOL:g}); treated as reproduced, not as drift.",
                    file=sys.stderr,
                )
                for line in soft[:5]:
                    print(f"P1 tables:   near-equal {name}{line}", file=sys.stderr)
            if hard:
                drifted.append(name)
                for line in hard[:20]:
                    print(f"P1 tables: {name}{line}", file=sys.stderr)

            # The markdown renderings carry no clock, so they get the strict comparison
            # the JSON cannot have. If they ever drift while the JSON matches, the
            # renderer changed without the data changing, which is worth catching.
            rendered_name = f'{table["table_id"]}.md'
            committed_md = args.out / rendered_name
            scratch_md = Path(scratch) / rendered_name
            if not committed_md.is_file():
                missing.append(str(committed_md))
            elif committed_md.read_text(encoding="utf-8") != scratch_md.read_text(encoding="utf-8"):
                drifted.append(rendered_name)

    if missing:
        # Absent is not the same as different, and neither is a pass.
        for path in missing:
            print(f"P1 tables: CANNOT_CHECK — committed table absent: {path}", file=sys.stderr)
        return EXIT_CANNOT_CHECK
    if drifted:
        for name in drifted:
            print(f"P1 tables: DRIFT — {name} does not match a live regeneration", file=sys.stderr)
        return EXIT_ERROR

    names = ", ".join(f'{table["table_id"]}.json' for table in regenerated)
    print(f"P1 tables: {names} reproduce exactly, ignoring provenance.generated_utc")
    if STATUS_CANNOT_CHECK in {table["status"] for table in regenerated}:
        print(
            "P1 tables: CANNOT_CHECK — the committed tables match, but they carry no "
            "publishable numbers without an archived study run.",
            file=sys.stderr,
        )
        return EXIT_CANNOT_CHECK
    return EXIT_OK


def main(argv: Sequence[str] | None = None) -> int:
    parser = argparse.ArgumentParser(
        prog="python -m orion.study.p1.tables",
        description="Regenerate the ORION-P1 publication tables from archived raw records. JSON and markdown only; no figures.",
    )
    parser.add_argument("--archive", type=Path, default=DEFAULT_ARCHIVE, help="raw record file or directory")
    parser.add_argument("--out", type=Path, default=DEFAULT_OUTPUT, help="output directory for the tables")
    parser.add_argument("--expected-repeats", type=int, default=stats.PROTOCOL_STOCHASTIC_REPEATS)
    parser.add_argument("--bootstrap-seed", type=int, default=DEFAULT_BOOTSTRAP_SEED)
    parser.add_argument("--resamples", type=int, default=stats.PROTOCOL_RESAMPLES)
    parser.add_argument("--min-units", type=int, default=0, help="declared prospective N; below it an inconclusive result reads UNDERPOWERED. No frozen default exists.")
    parser.add_argument("--representatives", type=int, default=DEFAULT_REPRESENTATIVES)
    parser.add_argument(
        "--design-manifest",
        type=Path,
        default=DEFAULT_DESIGN_MANIFEST,
        help="immutable expected system x case x seed design; pass an explicit path for another frozen split",
    )
    parser.add_argument(
        "--check",
        action="store_true",
        help=(
            "regenerate into a scratch directory and compare against the committed tables, "
            "ignoring provenance.generated_utc; write nothing"
        ),
    )
    args = parser.parse_args(argv)

    if args.check:
        return _check(args)

    try:
        t2, t3 = generate(
            args.archive,
            args.out,
            expected_repeats=args.expected_repeats,
            bootstrap_seed=args.bootstrap_seed,
            resamples=args.resamples,
            min_units=args.min_units,
            representatives=args.representatives,
            design_manifest=args.design_manifest,
        )
    except ValueError as error:
        print(f"P1 tables: archive is malformed and was not used: {error}", file=sys.stderr)
        return EXIT_ERROR

    for table in (t2, t3):
        print(f"P1 tables: {table['table_id']} -> {table['status']}" + (f" ({table['reason']})" if table["reason"] else ""))
    print(f"P1 tables: written to {args.out}")

    if STATUS_CANNOT_CHECK in {t2["status"], t3["status"]}:
        print(
            "P1 tables: CANNOT_CHECK — no publishable numbers were produced. "
            "This is the expected result without a live provider credential and an archived study run.",
            file=sys.stderr,
        )
        return EXIT_CANNOT_CHECK
    return EXIT_OK


if __name__ == "__main__":  # pragma: no cover
    raise SystemExit(main())


__all__ = [
    "DEFAULT_ARCHIVE",
    "DEFAULT_OUTPUT",
    "EXIT_CANNOT_CHECK",
    "EXIT_ERROR",
    "EXIT_OK",
    "STATUS_CANNOT_CHECK",
    "STATUS_OK",
    "STATUS_PARTIAL",
    "TABLE_T2",
    "TABLE_T3",
    "ArchiveIntegrity",
    "build_t2",
    "build_t3",
    "check_archive",
    "generate",
    "load_records",
    "main",
    "render_t2_markdown",
    "render_t3_markdown",
    "select_comparator",
]
