"""Fail-closed freeze utilities for the ORION-P5 hidden-cause study.

The protected suite contains root-cause truth, fresh-task payloads, evaluator
bindings, rubrics, negative variants, and opening nonces.  It must remain under
external/protected custody.  This module derives two safe-to-share artifacts:

* a candidate packet containing only development-visible information; and
* a commitment manifest binding the protected material without disclosing it.

The commitment is not empirical evidence and cannot promote a P5 result.
"""

from __future__ import annotations

import hashlib
import json
import secrets
from dataclasses import dataclass
from pathlib import Path, PurePosixPath
from typing import Any, Mapping, Sequence

SCHEMA_VERSION = "orion.p5.protected-hidden-cause-suite.v1"
CANDIDATE_SCHEMA_VERSION = "orion.p5.candidate-hidden-cause-packet.v1"
COMMITMENT_SCHEMA_VERSION = "orion.p5.protected-suite-commitment.v1"

ROOT_CAUSES = frozenset(
    {
        "RETRIEVAL_MISS",
        "ROUTING_PLANNING_MISS",
        "IMPLEMENTATION_BUG",
        "ENVIRONMENT_DEPENDENCY_TOOL_FAILURE",
        "EVALUATOR_METRIC_BUG",
        "REPRESENTATION_GAP",
        "MEASUREMENT_SPECIFICATION_GAP",
        "METHOD_BASIS_GAP",
    }
)

ALLOWED_CHANGED_AXES = frozenset({"TASK", "DOMAIN", "MODEL", "ENVIRONMENT", "DATA", "TOOL"})
INDEPENDENT_CHANGED_AXES = frozenset({"TASK", "DOMAIN", "MODEL", "ENVIRONMENT"})
_HEX = frozenset("0123456789abcdef")


def _canonical_json(value: Any) -> bytes:
    return json.dumps(
        value,
        sort_keys=True,
        separators=(",", ":"),
        ensure_ascii=False,
        allow_nan=False,
    ).encode("utf-8")


def sha256_json(value: Any) -> str:
    """Return a deterministic SHA-256 digest for JSON-compatible ``value``."""

    return hashlib.sha256(_canonical_json(value)).hexdigest()


def _protected_commitment(value: Any, nonce: str, *, kind: str) -> str:
    """Bind protected content without publishing a dictionary-attackable raw hash."""

    return sha256_json({"kind": kind, "payload_hash": sha256_json(value), "nonce": nonce})


def _require_mapping(value: Any, field: str) -> Mapping[str, Any]:
    if not isinstance(value, Mapping):
        raise ValueError(f"{field} must be an object")
    return value


def _require_nonempty_string(value: Any, field: str) -> str:
    if not isinstance(value, str) or not value.strip():
        raise ValueError(f"{field} must be a non-empty string")
    return value


def _require_string_list(value: Any, field: str, *, min_items: int = 1) -> list[str]:
    if not isinstance(value, list) or len(value) < min_items:
        raise ValueError(f"{field} must contain at least {min_items} item(s)")
    result: list[str] = []
    for index, item in enumerate(value):
        result.append(_require_nonempty_string(item, f"{field}[{index}]"))
    if len(result) != len(set(result)):
        raise ValueError(f"{field} contains duplicate values")
    return result


def _require_sha256(value: Any, field: str) -> str:
    digest = _require_nonempty_string(value, field)
    if digest != digest.lower() or len(digest) != 64 or any(char not in _HEX for char in digest):
        raise ValueError(f"{field} must be a 64-character lowercase SHA-256 hex digest")
    return digest


#: The root-cause commitment binds one of eight public enum labels. Eight digests
#: exhaust that message space, so every bit of protection the scheme has lives in
#: the nonce, and the nonce is the one field no schema can inspect for entropy:
#: `0...01` and a CSPRNG draw are both 64 hex characters, both unique across a
#: suite, both non-zero. The shipped PROTECTED_SUITE_V1 used `int(nonce, 16)`
#: values 1 through 24, and the 24 commitments a freeze of it would publish open
#: in 108 SHA-256 evaluations. See
#: research/failures/2026-08-invertible-commitment-vacuous-custody/.
#:
#: A magnitude floor alone does not repair that. `f"{2**255 + ordinal:064x}"`
#: clears any floor and is enumerated as cheaply as the ordinal was. The rule
#: below is therefore shaped as "reject what a declared cheap adversary
#: enumerates", not "reject what looks small", and
#: `orion.study.p5.hidden_cause_custody` builds its disclosure probes from the
#: same generators so the two cannot drift apart.
_MIN_NONCE_VALUE = 1 << 64

#: A run of 32 identical hex characters is what padding leaves; 32 CSPRNG bytes
#: produce one with probability below 2**-119.
_MAX_IDENTICAL_RUN = 32

#: 32 bytes drawn from a CSPRNG take about 30 distinct values. Taking fewer than
#: twelve has probability near 3e-15 and is the signature of a nonce assembled
#: from a short alphabet -- `"ab" * 24` plus a counter, say, which clears both the
#: magnitude floor and the run limit while carrying about 16 bits.
_MIN_DISTINCT_BYTES = 12

#: Two independent 256-bit draws agree in their first 16 hex characters with
#: probability 2**-64. Agreement at that length across a suite means one salt
#: varied by an index, which is a single secret with a public offset rather than
#: a per-case one.
_MAX_SHARED_NONCE_AFFIX = 16


def mint_root_cause_nonce() -> str:
    """Draw one opening nonce: 256 bits from the OS CSPRNG, per case, never reused.

    The error raised by :func:`nonce_weakness` used to be the only place that
    said how to produce a correct nonce, which left every caller to implement
    the one line that carries the scheme's entire security. This is that line.
    """

    return secrets.token_hex(32)


def constant_nonces() -> frozenset[str]:
    """Fixed nonces a generator leaves behind when it never drew one.

    Placeholders, not guesses: each is a value a fixture, template or default
    argument writes into the field, and a commitment opened by one was never
    protected by anything.
    """

    values = {digit * 64 for digit in "0123456789abcdef"}
    blocks = ("01", "0f", "de", "ad", "beef", "dead", "deadbeef", "cafebabe", "0123456789abcdef")
    for block in blocks:
        values.add(block * (64 // len(block)))
    for seed in (b"", b"nonce", b"changeme", b"placeholder", b"secret", b"seed", b"0"):
        values.add(hashlib.sha256(seed).hexdigest())
    values.add(sha256_json(""))
    values.add(sha256_json({}))
    values.add(sha256_json(None))
    values.add(sha256_json(0))
    return frozenset(values)


def published_field_nonces(
    case: Mapping[str, Any], *, ordinal: int, suite_id: str = ""
) -> frozenset[str]:
    """Nonces derivable from what the manifest publishes beside the commitment.

    A nonce computed from the case id, the case's position or the visible
    symptom is published in full the moment the manifest is, whatever its
    entropy looks like. ``ordinal`` is the case's 1-based position in the suite
    as emitted.
    """

    seeds: list[str] = [
        str(case.get("case_id", "")),
        str(ordinal),
        f"{ordinal:064x}",
        str(case.get("visible_symptom", "")),
        suite_id,
        f"{suite_id}|{case.get('case_id', '')}",
        f"{case.get('case_id', '')}|{ordinal}",
    ]
    values: set[str] = set()
    for seed in seeds:
        if not seed:
            continue
        values.add(hashlib.sha256(seed.encode("utf-8")).hexdigest())
        values.add(sha256_json(seed))
        values.add(hashlib.sha512(seed.encode("utf-8")).hexdigest()[:64])
    values.add(sha256_json(ordinal))
    return frozenset(values)


def _max_identical_run(nonce: str) -> int:
    best = run = 1
    for previous, char in zip(nonce, nonce[1:]):
        run = run + 1 if char == previous else 1
        best = max(best, run)
    return best


def nonce_weakness(
    nonce: str,
    *,
    case: Mapping[str, Any] | None = None,
    ordinal: int | None = None,
    suite_id: str = "",
) -> str | None:
    """Name the cheap enumeration that finds ``nonce``, or ``None`` if none does.

    Returns a sentence rather than a boolean because the caller has to be able
    to say *which* attack the nonce fell to; "invalid nonce" is not a finding an
    operator can act on. ``case`` and ``ordinal`` are optional so the shape rules
    can be applied to a bare nonce, but a suite validation supplies them, since
    the derived-from-published-field family cannot be checked without them.
    """

    value = int(nonce, 16)
    if value == 0:
        return "the all-zero nonce"
    if value < _MIN_NONCE_VALUE:
        return "below 2**64, the range a counter, an ordinal or a small integer occupies"
    if value > (1 << 256) - _MIN_NONCE_VALUE:
        return "within 2**64 of 2**256, the range a counter run down from the top occupies"
    run = _max_identical_run(nonce)
    if run >= _MAX_IDENTICAL_RUN:
        return (
            f"padded with a run of {run} identical hex characters, leaving {64 - run} "
            "characters of anything at all"
        )
    for block in (1, 2, 4, 8, 16, 32):
        if nonce == nonce[:block] * (64 // block):
            return f"a {block}-character block repeated {64 // block} times"
    distinct = len({nonce[index : index + 2] for index in range(0, 64, 2)})
    if distinct < _MIN_DISTINCT_BYTES:
        return (
            f"assembled from {distinct} distinct bytes where 32 CSPRNG bytes take about 30"
        )
    if nonce in constant_nonces():
        return "a fixed placeholder a generator leaves behind"
    if case is not None and ordinal is not None:
        if nonce in published_field_nonces(case, ordinal=ordinal, suite_id=suite_id):
            return "derived from a field the manifest publishes beside the commitment"
    return None


def _require_nonce(
    value: Any,
    field: str,
    *,
    case: Mapping[str, Any] | None = None,
    ordinal: int | None = None,
    suite_id: str = "",
) -> str:
    nonce = _require_sha256(value, field)
    weakness = nonce_weakness(nonce, case=case, ordinal=ordinal, suite_id=suite_id)
    if weakness is not None:
        raise ValueError(
            f"{field} is {weakness} and is therefore enumerable; the protected root "
            "cause has only eight possible values, so a guessable nonce leaves the "
            "commitment openable by brute force. Draw nonces from "
            "orion.study.p5.freeze.mint_root_cause_nonce()."
        )
    return nonce


def _surface_parts(value: str, field: str) -> tuple[str, ...]:
    path = PurePosixPath(value)
    if path.is_absolute() or ".." in path.parts:
        raise ValueError(f"{field} must be a relative non-traversing surface")
    parts = tuple(part for part in path.parts if part not in ("", "."))
    if not parts:
        raise ValueError(f"{field} must identify a concrete surface")
    return parts


def _surface_sets_conflict(allowed: list[str], protected: list[str], *, prefix: str) -> bool:
    allowed_parts = [
        _surface_parts(value, f"{prefix}.allowed_change_surface[{index}]")
        for index, value in enumerate(allowed)
    ]
    protected_parts = [
        _surface_parts(value, f"{prefix}.protected_surface[{index}]")
        for index, value in enumerate(protected)
    ]
    for left in allowed_parts:
        for right in protected_parts:
            if left == right[: len(left)] or right == left[: len(right)]:
                return True
    return False


#: The custody rule names the fields a freeze may publish and the fields it must
#: withhold. It does not name the *order* the cases are emitted in, and neither
#: did the nine conditions below until this one was added --- so a suite could
#: satisfy every stated rule and still hand a candidate the answer key, because
#: the answer was a function of a number printed on every case.
#:
#: PROTECTED_SUITE_V1 was exactly that suite. Its twenty-four cases are eight
#: root-cause families in eight consecutive blocks of three, so
#: `family = order[(ordinal - 1) // 3]` reproduces all twenty-four labels from
#: the case ids alone. Its opening nonces were separately broken, and the freeze
#: now refuses them; had they been sound, this validator would still have passed
#: a suite whose commitments no candidate needed to open.
#:
#: "Not recoverable from the ordinal" is not decidable in general -- every
#: assignment is *some* function of the ordinal. So the condition is shaped the
#: way the rest of this programme shapes its guards: declare the adversary, then
#: check that this suite defeats it. `ORDINAL_FAMILY_ORDERINGS` x block sizes x
#: strides is a stated, enumerable family of deciding rules; a suite reproduced
#: exactly by any one of them is rejected and named. A suite that survives is not
#: thereby proved independent of the ordinal --- it is proved to defeat these
#: rules, which is what the check claims and all it claims.
_ORDINAL_MIN_BLOCK = 2


@dataclass(frozen=True)
class OrdinalRule:
    """One declared way of predicting a case's family from its ordinal.

    ``openings`` are the 0-based positions the rule had to be *told* before it
    could predict anything --- the price the adversary pays to instantiate the
    ordering. They are excluded from scoring. Without that exclusion the family
    is vacuous: on a suite with one case per family, the rule that reads families
    off their own first appearances "recovers" every case while predicting none
    of them, and the guard would reject every suite it was shown.
    """

    name: str
    predicted: tuple[str, ...]
    openings: frozenset[int]

    def scored_positions(self, length: int) -> tuple[int, ...]:
        return tuple(index for index in range(length) if index not in self.openings)

    def agreement(self, assignment: Sequence[str]) -> tuple[int, int]:
        """Return (cases predicted correctly, cases predicted at all)."""

        scored = self.scored_positions(len(assignment))
        correct = sum(1 for index in scored if self.predicted[index] == assignment[index])
        return correct, len(scored)

    def recovers(self, assignment: Sequence[str]) -> bool:
        correct, scored = self.agreement(assignment)
        return scored > 0 and correct == scored


def _family_orderings(assignment: Sequence[str]) -> dict[str, tuple[tuple[str, ...], frozenset[int]]]:
    """The orderings an adversary can put the families in, and what each costs.

    Alphabetical order is free: the eight labels are a public enum, so every case
    is a prediction. First-appearance order is not free --- the adversary opens a
    case to learn each family's slot --- so those openings are charged against it
    and only the cases after them count as predictions.
    """

    first_seen: list[str] = []
    openings: list[int] = []
    for index, family in enumerate(assignment):
        if family not in first_seen:
            first_seen.append(family)
            openings.append(index)
    paid = frozenset(openings)
    free: frozenset[int] = frozenset()
    forwards = tuple(first_seen)
    alphabetical = tuple(sorted(first_seen))
    return {
        "first-appearance": (forwards, paid),
        "first-appearance-reversed": (tuple(reversed(forwards)), paid),
        "alphabetical": (alphabetical, free),
        "alphabetical-reversed": (tuple(reversed(alphabetical)), free),
    }


def _gcd(left: int, right: int) -> int:
    while right:
        left, right = right, left % right
    return left


def ordinal_reading_rules(assignment: Sequence[str]) -> tuple[OrdinalRule, ...]:
    """Return every declared ordinal-reading rule, instantiated for ``assignment``.

    Each rule maps a 1-based ordinal to a family using nothing but the ordinal,
    the suite length, the eight public labels and the openings charged to it.
    Rules are named so a rejection can quote the rule that read the suite rather
    than saying only that something did.
    """

    length = len(assignment)
    if length == 0:
        return ()
    rules: list[OrdinalRule] = []
    for ordering_name, (order, openings) in _family_orderings(assignment).items():
        count = len(order)
        if count == 0:
            continue
        for block in range(_ORDINAL_MIN_BLOCK, length // 2 + 1):
            if length % block:
                continue
            rules.append(
                OrdinalRule(
                    name=f"{ordering_name}/blocks-of-{block}",
                    predicted=tuple(order[(index // block) % count] for index in range(length)),
                    openings=openings,
                )
            )
        for stride in range(1, count):
            if _gcd(stride, count) != 1:
                continue
            rules.append(
                OrdinalRule(
                    name=f"{ordering_name}/stride-{stride}",
                    predicted=tuple(order[(index * stride) % count] for index in range(length)),
                    openings=openings,
                )
            )
    return tuple(rules)


def repeated_family_in_block(assignment: Sequence[str], *, block_size: int) -> int | None:
    """Return the 1-based ordinal opening the first block that repeats a family."""

    if block_size < _ORDINAL_MIN_BLOCK:
        return None
    for start in range(0, len(assignment), block_size):
        window = assignment[start : start + block_size]
        if len(set(window)) != len(window):
            return start + 1
    return None


def _even_family_block(assignment: Sequence[str]) -> int | None:
    """The block size implied by an evenly covered suite, or ``None``."""

    counts: dict[str, int] = {}
    for family in assignment:
        counts[family] = counts.get(family, 0) + 1
    sizes = set(counts.values())
    if len(sizes) != 1:
        return None
    per_family = sizes.pop()
    return per_family if per_family >= _ORDINAL_MIN_BLOCK else None


def ordinal_independence_report(assignment: Sequence[str]) -> dict[str, Any]:
    """Measure how far ``assignment`` is from being readable off the ordinal."""

    rules = ordinal_reading_rules(assignment)
    recovering = sorted(rule.name for rule in rules if rule.recovers(assignment))
    block_size = _even_family_block(assignment)
    repeated_at = (
        None if block_size is None else repeated_family_in_block(assignment, block_size=block_size)
    )
    worst_name = ""
    worst_correct = 0
    worst_scored = 0
    for rule in rules:
        correct, scored = rule.agreement(assignment)
        if scored and (correct, -scored) > (worst_correct, -worst_scored):
            worst_name, worst_correct, worst_scored = rule.name, correct, scored
    return {
        "cases": len(assignment),
        "families": len(set(assignment)),
        "rules_declared": len(rules),
        "rules_recovering_every_predicted_case": recovering,
        "strongest_rule": worst_name,
        "strongest_rule_correct": worst_correct,
        "strongest_rule_predicted": worst_scored,
        "even_block_size": block_size,
        "first_block_repeating_a_family": repeated_at,
        "independent": not recovering and repeated_at is None,
    }


def require_ordinal_independence(assignment: Sequence[str], *, surface: str) -> None:
    """Fail closed when the family assignment is readable off the case ordinal."""

    report = ordinal_independence_report(assignment)
    recovering = report["rules_recovering_every_predicted_case"]
    if recovering:
        raise ValueError(
            f"the {surface} case order hands over every family it was not shown: "
            f"rule {recovering[0]!r} predicts the remaining "
            f"{report['strongest_rule_predicted']} of {report['cases']} cases from the "
            "ordinal alone and gets every one right, so those commitments protect nothing"
        )
    repeated_at = report["first_block_repeating_a_family"]
    if repeated_at is not None:
        # A realised correlation is a realised leak whatever drew it: an adversary
        # handed one opening inside this block has the rest of it above chance.
        # The cost of the rule is that it rejects most honest uniform draws --
        # eight families of three land two in a block about five times in six --
        # and the remedy is to redraw the assignment, not to argue that this one
        # was innocent.
        raise ValueError(
            f"the {surface} case order repeats a root cause inside the block of "
            f"{report['even_block_size']} opening at ordinal {repeated_at}; one opening "
            "in that block predicts the others above chance. Redraw the assignment"
        )


def _protected_case_index(suite: Mapping[str, Any]) -> dict[str, Mapping[str, Any]]:
    raw_cases = suite.get("cases")
    if not isinstance(raw_cases, list) or not raw_cases:
        raise ValueError("cases must be a non-empty array")
    result: dict[str, Mapping[str, Any]] = {}
    for index, raw_case in enumerate(raw_cases):
        case = _require_mapping(raw_case, f"cases[{index}]")
        case_id = _require_nonempty_string(case.get("case_id"), f"cases[{index}].case_id")
        if case_id in result:
            raise ValueError(f"duplicate case_id: {case_id}")
        result[case_id] = case
    return result


def validate_protected_suite(raw_suite: Mapping[str, Any]) -> None:
    """Validate a private P5 suite and fail closed on freshness/integrity gaps."""

    suite = _require_mapping(raw_suite, "suite")
    if suite.get("schema_version") != SCHEMA_VERSION:
        raise ValueError(f"schema_version must be {SCHEMA_VERSION!r}")
    suite_id = _require_nonempty_string(suite.get("suite_id"), "suite_id")
    if suite.get("created_before_outcome_access") is not True:
        raise ValueError("created_before_outcome_access must be true")
    _require_sha256(suite.get("evaluator_hash"), "evaluator_hash")

    fresh_payloads = _require_mapping(suite.get("fresh_task_payloads"), "fresh_task_payloads")
    negative_payloads = _require_mapping(
        suite.get("negative_variant_payloads"), "negative_variant_payloads"
    )
    cases = _protected_case_index(suite)

    observed_causes: set[str] = set()
    used_nonces: set[str] = set()
    referenced_fresh: set[str] = set()
    referenced_nonfresh: set[str] = set()
    referenced_negative: set[str] = set()
    allowed_surfaces: list[str] = []
    protected_surfaces: list[str] = []

    emitted_assignment: list[str] = []
    family_by_case_id: dict[str, str] = {}

    for ordinal, (case_id, case) in enumerate(cases.items(), start=1):
        prefix = f"case {case_id}"
        _require_nonempty_string(case.get("visible_symptom"), f"{prefix}.visible_symptom")
        _require_mapping(case.get("candidate_visible_context"), f"{prefix}.candidate_visible_context")

        root = _require_nonempty_string(case.get("protected_root_cause"), f"{prefix}.protected_root_cause")
        if root not in ROOT_CAUSES:
            raise ValueError(f"{prefix}.protected_root_cause is not a registered root cause")
        observed_causes.add(root)
        emitted_assignment.append(root)
        family_by_case_id[case_id] = root

        nonce = _require_nonce(
            case.get("root_cause_nonce"),
            f"{prefix}.root_cause_nonce",
            case=case,
            ordinal=ordinal,
            suite_id=suite_id,
        )
        if nonce in used_nonces:
            raise ValueError("root_cause_nonce values must be unique across cases")
        # Distinct is not independent. One salt varied by an index shares its head
        # or its tail with every other case, so opening any one case opens the
        # scheme; the affix rule is what makes the salt per-case rather than
        # per-suite. Two real draws collide on 16 hex characters at 2**-64.
        for seen in used_nonces:
            if nonce[:_MAX_SHARED_NONCE_AFFIX] == seen[:_MAX_SHARED_NONCE_AFFIX]:
                raise ValueError(
                    f"{prefix}.root_cause_nonce shares its first "
                    f"{_MAX_SHARED_NONCE_AFFIX} characters with another case; that is one "
                    "salt with a per-case offset, not a per-case salt, and opening either "
                    "case opens both"
                )
            if nonce[-_MAX_SHARED_NONCE_AFFIX:] == seen[-_MAX_SHARED_NONCE_AFFIX:]:
                raise ValueError(
                    f"{prefix}.root_cause_nonce shares its last "
                    f"{_MAX_SHARED_NONCE_AFFIX} characters with another case; that is one "
                    "salt with a per-case offset, not a per-case salt, and opening either "
                    "case opens both"
                )
        used_nonces.add(nonce)

        competing = _require_string_list(
            case.get("competing_cause_set"), f"{prefix}.competing_cause_set", min_items=2
        )
        if root not in competing:
            raise ValueError(f"{prefix}.competing_cause_set must include protected_root_cause")

        motivating = _require_string_list(case.get("motivating_tasks"), f"{prefix}.motivating_tasks")
        replay = _require_string_list(case.get("replay_tasks"), f"{prefix}.replay_tasks")
        referenced_nonfresh.update(motivating)
        referenced_nonfresh.update(replay)
        allowed = _require_string_list(
            case.get("allowed_change_surface"), f"{prefix}.allowed_change_surface"
        )
        protected = _require_string_list(case.get("protected_surface"), f"{prefix}.protected_surface")
        if _surface_sets_conflict(allowed, protected, prefix=prefix):
            raise ValueError(f"{prefix} allowed_change_surface overlaps protected_surface")
        allowed_surfaces.extend(allowed)
        protected_surfaces.extend(protected)
        _require_nonempty_string(case.get("success_rubric"), f"{prefix}.success_rubric")
        _require_nonempty_string(case.get("harm_rubric"), f"{prefix}.harm_rubric")

        fresh_tasks = case.get("fresh_tasks")
        if not isinstance(fresh_tasks, list) or not fresh_tasks:
            raise ValueError(f"{prefix}.fresh_tasks must be a non-empty array")
        fresh_ids_for_case: set[str] = set()
        for fresh_index, raw_fresh in enumerate(fresh_tasks):
            fresh = _require_mapping(raw_fresh, f"{prefix}.fresh_tasks[{fresh_index}]")
            task_id = _require_nonempty_string(
                fresh.get("task_id"), f"{prefix}.fresh_tasks[{fresh_index}].task_id"
            )
            if task_id in referenced_fresh:
                raise ValueError(f"fresh task_id must be globally unique: {task_id}")
            referenced_fresh.add(task_id)
            fresh_ids_for_case.add(task_id)

            axes = _require_string_list(
                fresh.get("changed_axes"), f"{prefix}.fresh_tasks[{fresh_index}].changed_axes"
            )
            unknown_axes = set(axes) - ALLOWED_CHANGED_AXES
            if unknown_axes:
                raise ValueError(f"{prefix} fresh task {task_id} has unknown changed axes")
            if not (set(axes) & INDEPENDENT_CHANGED_AXES):
                raise ValueError(
                    f"{prefix} fresh task {task_id} must change TASK, DOMAIN, MODEL, or ENVIRONMENT"
                )

            expected_hash = _require_sha256(
                fresh.get("content_hash"), f"{prefix}.fresh_tasks[{fresh_index}].content_hash"
            )
            if task_id not in fresh_payloads:
                raise ValueError(f"missing protected fresh payload: {task_id}")
            actual_hash = sha256_json(fresh_payloads[task_id])
            if actual_hash != expected_hash:
                raise ValueError(f"fresh payload hash mismatch: {task_id}")

        if (set(motivating) | set(replay)) & fresh_ids_for_case:
            raise ValueError(f"{prefix} motivating/replay task ids overlap the fresh set")

        negative_ids = _require_string_list(
            case.get("negative_variant_ids"), f"{prefix}.negative_variant_ids"
        )
        for variant_id in negative_ids:
            if variant_id in referenced_negative:
                raise ValueError(f"negative variant id must be globally unique: {variant_id}")
            referenced_negative.add(variant_id)
            if variant_id not in negative_payloads:
                raise ValueError(f"missing retained negative variant payload: {variant_id}")

    global_split_overlap = referenced_nonfresh & referenced_fresh
    if global_split_overlap:
        raise ValueError(
            "motivating/replay task ids must be globally disjoint from fresh task ids: "
            f"{sorted(global_split_overlap)}"
        )
    if _surface_sets_conflict(allowed_surfaces, protected_surfaces, prefix="suite"):
        raise ValueError("allowed_change_surface overlaps protected_surface across cases")

    if observed_causes != ROOT_CAUSES:
        missing = sorted(ROOT_CAUSES - observed_causes)
        extra = sorted(observed_causes - ROOT_CAUSES)
        raise ValueError(f"suite must cover all eight root-cause families; missing={missing}, extra={extra}")

    # The ordinal a candidate can read is the position in the *published* packet,
    # which freeze_protected_suite emits in sorted case_id order; the ordinal an
    # author works in is the position in the `cases` array. A suite has to be
    # independent of both, and when the two permutations agree the second check
    # is free.
    require_ordinal_independence(emitted_assignment, surface="emitted")
    published_assignment = [family_by_case_id[case_id] for case_id in sorted(family_by_case_id)]
    if published_assignment != emitted_assignment:
        require_ordinal_independence(published_assignment, surface="published")

    orphan_fresh = set(fresh_payloads) - referenced_fresh
    if orphan_fresh:
        raise ValueError(f"unreferenced fresh payloads are forbidden: {sorted(orphan_fresh)}")
    orphan_negative = set(negative_payloads) - referenced_negative
    if orphan_negative:
        raise ValueError(f"unreferenced negative variants are forbidden: {sorted(orphan_negative)}")


def _root_commitment(root: str, nonce: str) -> str:
    # The nonce stays only in the protected opening material. Hashing one of eight
    # public enum labels without a nonce would be brute-force disclosure.
    return sha256_json({"protected_root_cause": root, "nonce": nonce})


def freeze_protected_suite(raw_suite: Mapping[str, Any]) -> tuple[dict[str, Any], dict[str, Any]]:
    """Return a candidate-safe packet and a protected-suite commitment manifest."""

    validate_protected_suite(raw_suite)
    suite = dict(raw_suite)
    fresh_payloads = _require_mapping(suite["fresh_task_payloads"], "fresh_task_payloads")
    negative_payloads = _require_mapping(
        suite["negative_variant_payloads"], "negative_variant_payloads"
    )
    cases = _protected_case_index(suite)

    candidate_cases: list[dict[str, Any]] = []
    committed_cases: list[dict[str, Any]] = []
    motivating_replay_split: list[dict[str, Any]] = []
    fresh_split: list[dict[str, Any]] = []

    for case_id in sorted(cases):
        case = cases[case_id]
        motivating = list(case["motivating_tasks"])
        replay = list(case["replay_tasks"])
        fresh_tasks = sorted(case["fresh_tasks"], key=lambda item: item["task_id"])
        negative_ids = sorted(case["negative_variant_ids"])

        candidate_cases.append(
            {
                "case_id": case_id,
                "visible_symptom": case["visible_symptom"],
                "candidate_visible_context": case["candidate_visible_context"],
                "motivating_tasks": motivating,
                "replay_tasks": replay,
                "allowed_change_surface": list(case["allowed_change_surface"]),
            }
        )

        nonce = case["root_cause_nonce"]
        fresh_commitments = [
            {
                "task_id": fresh["task_id"],
                "changed_axes": sorted(fresh["changed_axes"]),
                "content_commitment": _protected_commitment(
                    fresh_payloads[fresh["task_id"]],
                    nonce,
                    kind=f"fresh-task:{fresh['task_id']}",
                ),
            }
            for fresh in fresh_tasks
        ]
        negative_commitments = [
            {
                "variant_id": variant_id,
                "content_commitment": _protected_commitment(
                    negative_payloads[variant_id], nonce, kind=f"negative-variant:{variant_id}"
                ),
            }
            for variant_id in negative_ids
        ]
        committed_cases.append(
            {
                "case_id": case_id,
                "case_artifact_commitment": _protected_commitment(
                    case, nonce, kind=f"case:{case_id}"
                ),
                "root_cause_commitment": _root_commitment(
                    case["protected_root_cause"], nonce
                ),
                "fresh_tasks": fresh_commitments,
                "negative_variants": negative_commitments,
                "protected_surface_commitment": _protected_commitment(
                    sorted(case["protected_surface"]), nonce, kind="protected-surface"
                ),
                "success_rubric_commitment": _protected_commitment(
                    case["success_rubric"], nonce, kind="success-rubric"
                ),
                "harm_rubric_commitment": _protected_commitment(
                    case["harm_rubric"], nonce, kind="harm-rubric"
                ),
            }
        )
        motivating_replay_split.append(
            {"case_id": case_id, "motivating_tasks": motivating, "replay_tasks": replay}
        )
        fresh_split.append({"case_id": case_id, "fresh_tasks": fresh_commitments})

    candidate_packet: dict[str, Any] = {
        "schema_version": CANDIDATE_SCHEMA_VERSION,
        "suite_id": suite["suite_id"],
        "empirical_authority": "NONE",
        "cases": candidate_cases,
    }
    commitment_manifest: dict[str, Any] = {
        "schema_version": COMMITMENT_SCHEMA_VERSION,
        "suite_id": suite["suite_id"],
        "created_before_outcome_access": True,
        "empirical_authority": "CANNOT_CHECK",
        "full_protected_suite_hash": sha256_json(suite),
        "candidate_packet_hash": sha256_json(candidate_packet),
        "evaluator_hash": suite["evaluator_hash"],
        "motivating_replay_split_hash": sha256_json(motivating_replay_split),
        "fresh_transfer_split_hash": sha256_json(fresh_split),
        "fresh_payload_commitment_set_hash": sha256_json(fresh_split),
        "negative_variant_commitment_set_hash": sha256_json(
            [
                {"case_id": case["case_id"], "negative_variants": case["negative_variants"]}
                for case in committed_cases
            ]
        ),
        "root_cause_family_count": len(ROOT_CAUSES),
        "case_count": len(cases),
        "cases": committed_cases,
    }
    return candidate_packet, commitment_manifest


def _write_json(path: Path, value: Mapping[str, Any]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(value, indent=2, sort_keys=True) + "\n", encoding="utf-8")


def main(argv: list[str] | None = None) -> int:
    # Import lazily: freeze_cli imports the frozen semantic API from this module.
    # Delaying the import until execution avoids a module-import cycle while
    # ensuring every executable entrypoint uses the same custody-safe wrapper.
    from .freeze_cli import main as secure_main

    return secure_main(argv)


if __name__ == "__main__":
    raise SystemExit(main())
