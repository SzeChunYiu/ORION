from __future__ import annotations

import re
from collections import Counter
from collections.abc import Callable, Mapping, Sequence
from dataclasses import dataclass, field
from enum import Enum

_TOKEN = re.compile(r"[A-Za-z0-9_]+")
_IDENTIFIER_NAME = re.compile(r"(^|_)(id|ids|name|key|slug|label|case|title)($|_)", re.I)


class DegeneracyStatus(str, Enum):
    """Whether a benchmark surface measures the competence it claims to.

    CANNOT_CHECK is a distinct outcome: an unlabelled or single-label panel
    yields no verdict, and reporting a clean 1.0 on such a panel is precisely
    the meaningless score this probe exists to refuse.
    """

    CLEAN = "CLEAN"
    SUSPECT = "SUSPECT"
    DEGENERATE = "DEGENERATE"
    CANNOT_CHECK = "CANNOT_CHECK"


class CouplingKind(str, Enum):
    CORRELATED = "CORRELATED"
    DETERMINISTIC = "DETERMINISTIC"
    AUTHORED_FROM_LABEL = "AUTHORED_FROM_LABEL"


@dataclass(frozen=True)
class LabeledRecord:
    """One graded item, reduced to features plus the value being graded."""

    record_id: str
    features: Mapping[str, object] = field(default_factory=dict)
    label: object = None


@dataclass(frozen=True)
class DegeneracyFinding:
    probe: str
    surface: str
    detail: str
    coupling: CouplingKind
    status: DegeneracyStatus
    coverage: float | None = None
    baseline: float | None = None


@dataclass(frozen=True)
class ProbeReport:
    surface: str
    status: DegeneracyStatus
    findings: tuple[DegeneracyFinding, ...] = ()
    reasons: tuple[str, ...] = ()
    records_probed: int = 0

    @property
    def permits_score_as_evidence(self) -> bool:
        return self.status is DegeneracyStatus.CLEAN


def _hashable(value: object) -> object:
    if isinstance(value, (list, tuple, set, frozenset)):
        return tuple(sorted(str(item) for item in value))
    return value


def _label_tokens_in_value(value: str, label: object) -> bool:
    """True when a field's text carries the label's own vocabulary.

    Both sides are split identically so a verdict such as
    `PREDICTION_NOT_MECHANISM` matches `prediction-not-mechanism` inside an
    identifier, while an opaque suffix like `a3f9` does not.
    """

    def parts(text: str) -> set[str]:
        out: set[str] = set()
        for token in _TOKEN.findall(text.replace("-", "_")):
            lowered = token.lower()
            out.add(lowered)
            out |= {piece for piece in lowered.split("_") if len(piece) > 2}
        return out

    label_words = {p for p in parts(str(label)) if "_" not in p}
    return bool(label_words) and label_words <= parts(value)


def _majority_baseline(labels: Sequence[object]) -> float:
    return Counter(labels).most_common(1)[0][1] / len(labels) if labels else 0.0


def _looks_like_identifier(name: str, values: Sequence[object]) -> bool:
    """Identifier-ness is about the field's name and string-ness, never
    uniqueness alone — near-unique values also describe every real-valued
    measurement, and RAKL's earlier revision flagged all of them."""

    return all(isinstance(v, str) for v in values) and bool(_IDENTIFIER_NAME.search(name))


def probe_single_feature(
    records: Sequence[LabeledRecord], *, surface: str = "records"
) -> tuple[DegeneracyFinding, ...]:
    """Does any single feature reproduce the label above the majority baseline?

    A feature that partitions the labels perfectly is DEGENERATE if it looks
    like an identifier carrying the answer's own vocabulary — that is
    authorship, not signal — and SUSPECT otherwise, since a deterministic
    feature→label map may be a legitimate hard rule or a leak.
    """

    if not records:
        return ()
    labels = [_hashable(r.label) for r in records]
    baseline = _majority_baseline(labels)
    names = sorted({name for r in records for name in r.features})
    findings: list[DegeneracyFinding] = []
    for name in names:
        raw = [r.features.get(name) for r in records]
        # Authorship check first, independent of partitioning: an identifier
        # whose text carries the answer's own vocabulary is a leak even when
        # every id is unique — uniqueness is what ids are for.
        if _looks_like_identifier(name, raw) and any(
            isinstance(v, str) and _label_tokens_in_value(v, lab)
            for v, lab in zip(raw, labels)
        ):
            findings.append(
                DegeneracyFinding(
                    probe="identifier_carries_label",
                    surface=surface,
                    detail=f"identifier field {name!r} carries the label's own vocabulary",
                    coupling=CouplingKind.AUTHORED_FROM_LABEL,
                    status=DegeneracyStatus.DEGENERATE,
                    baseline=baseline,
                )
            )
            continue
        values = [_hashable(v) for v in raw]
        by_value: dict[object, set[object]] = {}
        for value, label in zip(values, labels):
            by_value.setdefault(value, set()).add(label)
        # A feature with a distinct value per record is an identity map, not a
        # shortcut — it partitions nothing. Only a feature that groups records
        # and still fixes the label is a determining shortcut.
        deterministic = len(by_value) < len(records) and all(
            len(s) == 1 for s in by_value.values()
        )
        if not deterministic:
            continue
        if 1.0 <= baseline:
            continue
        findings.append(
            DegeneracyFinding(
                probe="single_feature_determines_label",
                surface=surface,
                detail=(
                    f"feature {name!r} determines the label for every record "
                    f"(baseline {baseline:.3f}); a hard rule or a leak"
                ),
                coupling=CouplingKind.DETERMINISTIC,
                status=DegeneracyStatus.SUSPECT,
                coverage=1.0,
                baseline=baseline,
            )
        )
    return tuple(findings)


def probe_blind_responder(
    records: Sequence[LabeledRecord],
    responder: Callable[[LabeledRecord], object],
    *,
    responder_name: str,
    surface: str = "records",
    margin: float = 0.05,
) -> tuple[DegeneracyFinding, ...]:
    """Score a responder that reads only a restricted view of each record.

    If it beats the majority baseline while reading no substantive content, the
    surface rewards a shortcut rather than the competence it claims to measure.
    """

    if not records:
        return ()
    labels = [_hashable(r.label) for r in records]
    baseline = _majority_baseline(labels)
    accuracy = sum(_hashable(responder(r)) == lab for r, lab in zip(records, labels)) / len(records)
    if accuracy <= baseline + margin:
        return ()
    return (
        DegeneracyFinding(
            probe="blind_responder_ceiling",
            surface=surface,
            detail=(
                f"blind responder {responder_name!r} scores {accuracy:.3f} against a "
                f"majority baseline of {baseline:.3f} while reading no substantive content"
            ),
            coupling=CouplingKind.AUTHORED_FROM_LABEL,
            status=DegeneracyStatus.DEGENERATE,
            coverage=accuracy,
            baseline=baseline,
        ),
    )


def probe_records(
    records: Sequence[LabeledRecord],
    *,
    surface: str = "records",
    blind_responders: Mapping[str, Callable[[LabeledRecord], object]] = {},
) -> ProbeReport:
    """Run every probe and fold to the worst status, never to a pass by default."""

    if not records:
        return ProbeReport(surface, DegeneracyStatus.CANNOT_CHECK, reasons=("no records",))
    labels = {_hashable(r.label) for r in records}
    if len(labels) < 2:
        return ProbeReport(
            surface,
            DegeneracyStatus.CANNOT_CHECK,
            reasons=("single-label panel: any responder scores 1.0, so nothing is measured",),
            records_probed=len(records),
        )
    findings = list(probe_single_feature(records, surface=surface))
    for name, responder in sorted(blind_responders.items()):
        findings.extend(
            probe_blind_responder(records, responder, responder_name=name, surface=surface)
        )
    order = [DegeneracyStatus.DEGENERATE, DegeneracyStatus.SUSPECT]
    status = next((s for s in order if any(f.status is s for f in findings)), DegeneracyStatus.CLEAN)
    return ProbeReport(surface, status, tuple(findings), records_probed=len(records))
